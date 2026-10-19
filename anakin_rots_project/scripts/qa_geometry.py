"""Geometry integrity + export round-trip QA. Run: blender -b -P scripts/qa_geometry.py -- <stage>"""
import bpy, bmesh, os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['C']
stage = argv[0]
rep = {}
def mesh_stats(o):
    me = o.data; me.calc_loop_triangles()
    co = np.array([v.co for v in me.vertices])
    d = {'verts': len(me.vertices), 'edges': len(me.edges), 'faces': len(me.polygons), 'tris': len(me.loop_triangles),
         'nonfinite': int((~np.isfinite(co)).sum()), 'uv_layers': [u.name for u in me.uv_layers], 'materials': [m.name if m else None for m in me.materials],
         'vertex_groups': [g.name for g in o.vertex_groups], 'has_custom_normals': me.has_custom_normals,
         'bbox_min': co.min(0).tolist(), 'bbox_max': co.max(0).tolist()}
    # degenerate triangles
    deg = 0
    for t in me.loop_triangles:
        a, b, c = [me.vertices[i].co for i in t.vertices]
        if (b - a).cross(c - a).length < 1e-10: deg += 1
    d['degenerate_tris'] = deg
    # duplicate vertices (exact)
    d['duplicate_vertex_positions'] = int(len(co) - len(np.unique(np.round(co, 7), axis=0)))
    # UV validity
    if me.uv_layers:
        uv = np.array([l.uv for l in me.uv_layers.active.data]); d['uv_min'] = uv.min(0).tolist(); d['uv_max'] = uv.max(0).tolist(); d['uv_nonfinite'] = int((~np.isfinite(uv)).sum())
    # weights
    sums = [sum(g.weight for g in v.groups) for v in me.vertices]; d['weight_sum_min'] = min(sums) if sums else None; d['weight_sum_max'] = max(sums) if sums else None
    d['unweighted_verts'] = int(sum(1 for v in me.vertices if len(v.groups) == 0))
    d['matrix_world_is_identity'] = o.matrix_world == __import__('mathutils').Matrix.Identity(4)
    d['modifiers'] = [(m.name, m.type) for m in o.modifiers]
    return d
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '%s.blend' % stage))
rep['stage_blend'] = {o.name: mesh_stats(o) for o in bpy.data.objects if o.type == 'MESH' and o.name != 'HEAD_REF'}
# compare UVs / topology with the original import
orig_uv = {}; orig_faces = {}
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '00_original_import.blend'))
for name in ('HairPlanes_M', 'hair_cap'):
    me = bpy.data.objects[name].data
    orig_uv[name] = np.array([l.uv for l in me.uv_layers.active.data]); orig_faces[name] = [tuple(p.vertices) for p in me.polygons]
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '%s.blend' % stage))
rep['vs_original'] = {}
for name in ('HairPlanes_M', 'hair_cap'):
    me = bpy.data.objects[name].data
    uv = np.array([l.uv for l in me.uv_layers.active.data])
    faces = [tuple(p.vertices) for p in me.polygons]
    # mirrored meshes have reversed winding -> compare as sets of vertex triples
    same_faces = all(set(a) == set(b) for a, b in zip(faces, orig_faces[name]))
    # per-vertex UV compare (loops reorder with reversed winding: compare via vertex->uv map)
    vuv = {}; ouv = {}
    for p in me.polygons:
        for li in p.loop_indices: vuv[me.loops[li].vertex_index] = tuple(np.round(uv[li], 6))
    rep['vs_original'][name] = {'face_count_equal': len(faces) == len(orig_faces[name]), 'face_vertex_sets_equal': same_faces,
                                'uv_loop_count_equal': len(uv) == len(orig_uv[name]), 'uv_max_abs_diff_sorted': float(np.abs(np.sort(uv.ravel()) - np.sort(orig_uv[name].ravel())).max())}
# round-trip: re-import the exported FBX into a clean scene
fbx = os.path.join(common.PROJ, 'output', 'anakin_rots_hair_final.fbx')
if os.path.exists(fbx):
    stage_co = {name: np.array([bpy.data.objects[name].matrix_world @ v.co for v in bpy.data.objects[name].data.vertices]) for name in ('HairPlanes_M', 'hair_cap')}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx, use_custom_normals=True)
    rt = {}
    for name in ('HairPlanes_M', 'hair_cap'):
        o = bpy.data.objects.get(name)
        if o is None: rt[name] = 'MISSING'; continue
        co = np.array([o.matrix_world @ v.co for v in o.data.vertices])
        rt[name] = {'verts': len(co), 'faces': len(o.data.polygons), 'max_abs_position_diff_vs_stage': float(np.abs(co - stage_co[name]).max()) if len(co) == len(stage_co[name]) else 'count mismatch',
                    'vertex_groups': len(o.vertex_groups), 'uv_layers': [u.name for u in o.data.uv_layers], 'has_custom_normals': o.data.has_custom_normals,
                    'armature_modifier': [m.object.name for m in o.modifiers if m.type == 'ARMATURE' and m.object]}
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    rt['armature'] = {'name': arm[0].name, 'bones': len(arm[0].data.bones), 'has_Head': 'Head' in arm[0].data.bones} if arm else 'MISSING'
    rt['objects'] = sorted(o.name for o in bpy.data.objects)
    rep['fbx_roundtrip'] = rt
with open(os.path.join(common.PROJ, 'reports', 'qa_geometry_%s.json' % stage), 'w') as f: json.dump(rep, f, indent=1, default=str)
print(json.dumps(rep, indent=1, default=str))
