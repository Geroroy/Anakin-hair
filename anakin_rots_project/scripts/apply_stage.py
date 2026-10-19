"""Blender: apply a positions npz produced by a NumPy stage to the meshes, regenerate scalp-transferred normals,
save an incremental .blend and render the six comparison views.
Run: blender -b -P scripts/apply_stage.py -- <stage_name> [light_preset]
"""
import bpy, bmesh, os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
stage = argv[0]; preset = argv[1] if len(argv) > 1 else 'neutral'
src = os.path.join(common.PROJ, 'working', 'positions_%s.npz' % stage)
D = np.load(src); meta = json.loads(str(D['meta'])) if 'meta' in D else {}
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '01_original_with_head_materials.blend'))
hair = bpy.data.objects['HairPlanes_M']; cap = bpy.data.objects['hair_cap']; head = bpy.data.objects['HEAD_REF']
for m in list(bpy.data.materials):
    if m.name.startswith('M_Hair'): bpy.data.materials.remove(m)
common.assign_materials(hair, cap, head)   # rebuild with the current preview shading values

def apply(obj, co, nrm, mirrored):
    me = obj.data
    assert len(me.vertices) == len(co), (obj.name, len(me.vertices), len(co))
    inv = obj.matrix_world.inverted()
    for v, p in zip(me.vertices, co): v.co = inv @ __import__('mathutils').Vector(p)
    if mirrored:
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.reverse_faces(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
        for g in obj.vertex_groups:
            if '_L_' in g.name: g.name = g.name.replace('_L_', '_R_') + '__tmp'
        for g in obj.vertex_groups:
            if '_R_' in g.name and not g.name.endswith('__tmp'): g.name = g.name.replace('_R_', '_L_')
        for g in obj.vertex_groups:
            if g.name.endswith('__tmp'): g.name = g.name[:-5]
    me.update()
    if nrm is not None:
        me.normals_split_custom_set_from_vertices([tuple(n) for n in nrm])
    me.update()

apply(hair, D['hair_co'], D['hair_nrm'], bool(meta.get('mirrored', False)))
apply(cap, D['cap_co'], D['cap_nrm'], bool(meta.get('mirrored', False)))
print('vertex groups hair:', [g.name for g in hair.vertex_groups])
out_blend = os.path.join(common.PROJ, 'working', '%s.blend' % stage)
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
common.clear_render_rig(); cams = common.setup_cameras(); common.setup_lights(preset); common.setup_render(res=1024, samples=32)
rd = os.path.join(common.PROJ, 'renders', stage)
common.render_views(rd, stage, cams)
# contact sheet via system python (PIL is not bundled with Blender)
import subprocess
subprocess.run(['python3', os.path.join(common.PROJ, 'scripts', 'make_sheet.py'), rd, stage], check=False)
print('stage', stage, 'done ->', out_blend)
