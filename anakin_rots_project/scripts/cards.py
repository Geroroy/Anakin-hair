"""Hair-card analysis helpers: islands, root/tip, region classification, scalp distance (bpy)."""
import bpy, bmesh, numpy as np, json, os, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def islands_of(obj):
    me = obj.data
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    seen = set(); islands = []
    for v in bm.verts:
        if v.index in seen: continue
        stack = [v]; comp = []; seen.add(v.index)
        while stack:
            cur = stack.pop(); comp.append(cur.index)
            for e in cur.link_edges:
                o = e.other_vert(cur)
                if o.index not in seen: seen.add(o.index); stack.append(o)
        islands.append(sorted(comp))
    bm.free()
    return islands

def vertex_uvs(obj):
    """Per-vertex UV (the Frosty export is ByVertice so every loop of a vertex shares one UV)."""
    me = obj.data; uv = me.uv_layers.active.data
    out = np.zeros((len(me.vertices), 2))
    for poly in me.polygons:
        for li in poly.loop_indices:
            out[me.loops[li].vertex_index] = uv[li].uv
    return out

def head_bvh(head_obj):
    bm = bmesh.new(); bm.from_mesh(head_obj.data); bm.transform(head_obj.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free(); return t

def card_table(obj, head_obj=None, front=Vector((0, -1, 0)), center=Vector((0, -0.03, 1.69))):
    me = obj.data
    co = np.array([obj.matrix_world @ v.co for v in me.vertices])
    uvs = vertex_uvs(obj)
    isl = islands_of(obj)
    bvh = head_bvh(head_obj) if head_obj else None
    f = np.array(front); up = np.array((0, 0, 1.)); r = np.cross(f, up)   # character's right
    rows = []
    for ci, comp in enumerate(isl):
        c = co[comp]; u = uvs[comp]
        vmax, vmin = u[:, 1].max(), u[:, 1].min()
        root = c[u[:, 1] >= vmax - 1e-4].mean(0); tip = c[u[:, 1] <= vmin + 1e-4].mean(0)
        d = tip - root; L = np.linalg.norm(d)
        rel = root - np.array(center)
        az = math.degrees(math.atan2(np.dot(rel, r), np.dot(rel, f)))   # 0 = front, +90 = right, 180 = back
        el = math.degrees(math.atan2(rel[2], np.linalg.norm(rel[:2])))
        dist = None
        if bvh:
            loc, nrm, idx, dd = bvh.find_nearest(Vector(root))
            dist = float(dd) if loc else None
        rows.append({'id': ci, 'verts': comp, 'n': len(comp), 'root': root.tolist(), 'tip': tip.tolist(), 'length': float(L),
                     'dir': (d / max(L, 1e-9)).tolist(), 'az': az, 'el': el, 'u0': float(u[:, 0].min()), 'u1': float(u[:, 0].max()),
                     'v0': float(vmin), 'v1': float(vmax), 'root_scalp_dist': dist,
                     'region': classify(az, el, root[2])})
    return rows

def classify(az, el, z):
    a = abs(az)
    if el > 55: return 'crown'
    if a < 35: return 'front' if el > 10 else 'fringe'
    if a < 110: return 'temple' if el > 20 else 'side'
    if a < 145: return 'back_side'
    return 'nape' if el < -5 else 'back'

def save_table(rows, path):
    with open(path, 'w') as fp: json.dump(rows, fp)
