"""Stage 01: import the original Frosty FBX + head FBX into a clean scene, inspect, and save working/00_original.blend.
Run: blender -b -P scripts/01_inspect_original.py
"""
import bpy, bmesh, json, os, sys, math
from mathutils import Vector
from collections import Counter, defaultdict

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.read_factory_settings(use_empty=True)

hair_path = os.path.join(PROJ, 'input', 'hair_anakin_01_mesh.fbx')
head_path = os.path.join(PROJ, 'input', 'head.fbx')

bpy.ops.import_scene.fbx(filepath=hair_path, use_custom_normals=True, ignore_leaf_bones=False, automatic_bone_orientation=False)
hair_objs = list(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=head_path, use_custom_normals=True)
head_objs = [o for o in bpy.context.scene.objects if o not in hair_objs]

report = {'blender': bpy.app.version_string, 'objects': []}

def island_stats(obj):
    me = obj.data
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    seen = set(); islands = []
    for v in bm.verts:
        if v.index in seen: continue
        stack = [v]; comp = []
        seen.add(v.index)
        while stack:
            cur = stack.pop(); comp.append(cur.index)
            for e in cur.link_edges:
                o = e.other_vert(cur)
                if o.index not in seen:
                    seen.add(o.index); stack.append(o)
        islands.append(comp)
    sizes = Counter(len(c) for c in islands)
    uv = bm.loops.layers.uv.active
    facecount = Counter(len(f.verts) for f in bm.faces)
    # per-island bbox + uv bbox
    isl = []
    for comp in islands:
        vs = [bm.verts[i].co for i in comp]
        mn = Vector(map(min, zip(*vs))); mx = Vector(map(max, zip(*vs)))
        faces = set(f for i in comp for f in bm.verts[i].link_faces)
        uvs = [l[uv].uv for f in faces for l in f.loops] if uv else []
        umn = Vector(map(min, zip(*uvs))) if uvs else None; umx = Vector(map(max, zip(*uvs))) if uvs else None
        isl.append({'nverts': len(comp), 'nfaces': len(faces), 'bbox_min': list(mn), 'bbox_max': list(mx),
                    'uv_min': list(umn) if umn else None, 'uv_max': list(umx) if umx else None})
    bm.free()
    return len(islands), dict(sizes), dict(facecount), isl

for o in bpy.context.scene.objects:
    d = {'name': o.name, 'type': o.type, 'parent': o.parent.name if o.parent else None,
         'location': list(o.location), 'rotation_euler_deg': [math.degrees(a) for a in o.rotation_euler],
         'scale': list(o.scale), 'matrix_world': [list(r) for r in o.matrix_world]}
    if o.type == 'MESH':
        me = o.data
        me.calc_loop_triangles()
        d.update({'verts': len(me.vertices), 'edges': len(me.edges), 'faces': len(me.polygons), 'tris': len(me.loop_triangles),
                  'uv_layers': [u.name for u in me.uv_layers], 'materials': [m.name if m else None for m in me.materials],
                  'vertex_groups': [g.name for g in o.vertex_groups], 'modifiers': [(m.name, m.type, getattr(m, 'object', None).name if getattr(m, 'object', None) else None) for m in o.modifiers],
                  'has_custom_normals': me.has_custom_normals,
                  'bbox_world_min': list(Vector(map(min, zip(*[o.matrix_world @ Vector(c) for c in o.bound_box])))),
                  'bbox_world_max': list(Vector(map(max, zip(*[o.matrix_world @ Vector(c) for c in o.bound_box])))),
                  'bbox_local_min': list(Vector(map(min, zip(*[Vector(c) for c in o.bound_box])))),
                  'bbox_local_max': list(Vector(map(max, zip(*[Vector(c) for c in o.bound_box]))))})
        n_isl, sizes, fc, isl = island_stats(o)
        d['islands'] = n_isl; d['island_size_hist'] = sizes; d['face_vertex_count_hist'] = fc
        d['island_detail'] = isl
        # vertex group weight stats
        vg = {}
        for g in o.vertex_groups:
            ws = []
            for v in me.vertices:
                for ge in v.groups:
                    if ge.group == g.index: ws.append(ge.weight)
            vg[g.name] = {'count': len(ws), 'min': min(ws) if ws else None, 'max': max(ws) if ws else None}
        d['vertex_group_stats'] = vg
        # unweighted verts / weight sum
        sums = [sum(ge.weight for ge in v.groups) for v in me.vertices]
        d['weight_sum_min'] = min(sums); d['weight_sum_max'] = max(sums)
    if o.type == 'ARMATURE':
        d['bones'] = len(o.data.bones)
        chain = []
        b = o.data.bones.get('Head')
        while b: chain.append((b.name, list(b.head_local), list(b.tail_local))); b = b.parent
        d['head_chain'] = chain[:6]
    report['objects'].append(d)

report['scene_unit'] = {'system': bpy.context.scene.unit_settings.system, 'scale_length': bpy.context.scene.unit_settings.scale_length}
with open(os.path.join(PROJ, 'reports', 'asset_inspection.json'), 'w') as f:
    json.dump(report, f, indent=1)
# compact summary to stdout
for d in report['objects']:
    if d['type'] == 'MESH':
        print('MESH', d['name'], 'verts', d['verts'], 'faces', d['faces'], 'tris', d['tris'], 'islands', d['islands'], 'uv', d['uv_layers'], 'mats', d['materials'], 'vg', len(d['vertex_groups']), 'mods', d['modifiers'])
        print('   bbox world', [round(x, 4) for x in d['bbox_world_min']], [round(x, 4) for x in d['bbox_world_max']], 'loc', d['location'], 'rot', d['rotation_euler_deg'], 'scale', d['scale'])
        print('   island size hist', sorted(d['island_size_hist'].items())[:20], 'facevert hist', d['face_vertex_count_hist'], 'wsum', d['weight_sum_min'], d['weight_sum_max'])
    elif d['type'] == 'ARMATURE':
        print('ARMATURE', d['name'], 'bones', d['bones'], 'loc', d['location'], 'rot', d['rotation_euler_deg'], 'scale', d['scale'])
        for c in d['head_chain']: print('   ', c)
    else:
        print(d['type'], d['name'], 'parent', d['parent'])
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, 'working', '00_original_import.blend'))
print('saved')
