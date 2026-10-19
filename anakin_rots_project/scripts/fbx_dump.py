"""Minimal pure-Python binary FBX reader used for pre-Blender asset inspection.
Usage: python3 -I fbx_dump.py <file.fbx>
"""
import sys, struct, zlib

def read_fbx(path):
    data = open(path, 'rb').read()
    assert data[:21] == b'Kaydara FBX Binary  \x00'
    version = struct.unpack('<I', data[23:27])[0]
    pos = 27
    is64 = version >= 7500
    def read_node(pos):
        if is64:
            end, nprops, plen = struct.unpack_from('<QQQ', data, pos); pos += 24
        else:
            end, nprops, plen = struct.unpack_from('<III', data, pos); pos += 12
        nlen = data[pos]; pos += 1
        if end == 0:
            return None, pos
        name = data[pos:pos+nlen].decode('latin1'); pos += nlen
        props = []
        for _ in range(nprops):
            t = chr(data[pos]); pos += 1
            if t in 'YCIFDL':
                fmt = {'Y':'<h','C':'<?','I':'<i','F':'<f','D':'<d','L':'<q'}[t]
                v = struct.unpack_from(fmt, data, pos)[0]; pos += struct.calcsize(fmt); props.append(v)
            elif t in 'fdlibc':
                alen, enc, clen = struct.unpack_from('<III', data, pos); pos += 12
                raw = data[pos:pos+clen]; pos += clen
                if enc == 1: raw = zlib.decompress(raw)
                fmt = {'f':'f','d':'d','l':'q','i':'i','b':'?','c':'B'}[t]
                props.append(list(struct.unpack('<%d%s' % (alen, fmt), raw)))
            elif t in 'SR':
                l = struct.unpack_from('<I', data, pos)[0]; pos += 4
                v = data[pos:pos+l]; pos += l
                props.append(v.decode('latin1', 'replace') if t == 'S' else v)
            else:
                raise ValueError('unknown prop type %r at %d' % (t, pos))
        children = []
        while pos < end:
            child, pos = read_node(pos)
            if child is None: break
        
            children.append(child)
        return (name, props, children), end
    nodes = []
    while pos < len(data):
        node, pos = read_node(pos)
        if node is None: break
        nodes.append(node)
    return version, nodes

def find(nodes, name):
    return [n for n in nodes if n[0] == name]

def short(v):
    if isinstance(v, list):
        return '[%d items] %s' % (len(v), v[:6])
    s = repr(v)
    return s if len(s) < 120 else s[:120] + '...'

def dump(node, depth=0, maxdepth=6):
    name, props, children = node
    print('  ' * depth + name, *[short(p) for p in props])
    if depth < maxdepth:
        for c in children: dump(c, depth + 1, maxdepth)

if __name__ == '__main__':
    version, nodes = read_fbx(sys.argv[1])
    print('FBX version', version)
    for n in nodes:
        if n[0] in ('FBXHeaderExtension', 'GlobalSettings', 'Definitions'):
            dump(n, 0, 4)
    objs = find(nodes, 'Objects')[0]
    print('\n=== OBJECTS ===')
    for o in objs[2]:
        name, props, ch = o
        print(name, [short(p) for p in props])
        for c in ch:
            if c[0] in ('Properties70',):
                for p in c[2]: print('     P', [short(x) for x in p[1]])
            elif c[0] in ('Vertices','PolygonVertexIndex','Edges'):
                print('     ', c[0], len(c[1][0]))
            elif c[0] in ('LayerElementNormal','LayerElementUV','LayerElementMaterial','LayerElementColor','LayerElementTangent','LayerElementBinormal','LayerElementSmoothing'):
                info = {cc[0]: (short(cc[1][0]) if cc[1] else '') for cc in c[2]}
                print('     ', c[0], c[1], info)
            elif c[0] in ('Indexes','Weights','Transform','TransformLink','Version','GeometryVersion','Layer'):
                print('     ', c[0], [short(p) for p in c[1]])
            else:
                print('     ', c[0], [short(p) for p in c[1]])
    print('\n=== CONNECTIONS ===')
    cons = find(nodes, 'Connections')[0]
    for c in cons[2]:
        print(c[0], c[1])
