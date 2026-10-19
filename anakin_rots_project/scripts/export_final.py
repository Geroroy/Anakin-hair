"""Export the final stage to output/: FBX (meshes + skeleton + skin weights + custom normals + tangents) and .blend.
Run: blender -b -P scripts/export_final.py -- <stage>"""
import bpy, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['C']
stage = argv[0]; outdir = argv[1] if len(argv) > 1 else 'output'
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '%s.blend' % stage))
OUT = os.path.join(common.PROJ, outdir); os.makedirs(OUT, exist_ok=True)
hair = bpy.data.objects['HairPlanes_M']; cap = bpy.data.objects['hair_cap']; arm = bpy.data.objects['Reference']; root = bpy.data.objects['hair_anakin_01_mesh_lod0']
head = bpy.data.objects.get('HEAD_REF')
# the preview materials are Blender-only; Frosty ignores them but keep the slot names tidy
# remove render rig / head from the export selection
for o in bpy.data.objects: o.select_set(False)
for o in (hair, cap, arm, root): o.select_set(True)
# the skeleton bones are children of the armature; export selected only
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, 'anakin_rots_hair_final.fbx'), use_selection=True,
                         object_types={'ARMATURE', 'MESH', 'EMPTY'}, mesh_smooth_type='OFF', use_tspace=True,
                         use_custom_props=False, add_leaf_bones=False, bake_anim=False, use_armature_deform_only=False,
                         apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y',
                         path_mode='STRIP', embed_textures=False, use_mesh_modifiers=False)
# blend: keep head reference + materials + render rig for the user, but hide the head from render by default
if head: head.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'anakin_rots_hair_final.blend'))
print('exported', os.listdir(OUT))
