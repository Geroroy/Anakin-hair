"""Stage 02: baseline renders of the untouched original hair, with the head placed for reference.
Run: blender -b -P scripts/02_render_original.py"""
import bpy, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '00_original_import.blend'))
hair = bpy.data.objects['HairPlanes_M']; cap = bpy.data.objects['hair_cap']
head = [o for o in bpy.data.objects if o.name.startswith('mat_head')][0]
head.name = 'HEAD_REF'
# The user's Blender re-export of the head carries a +35.19 cm X offset that the Frosty hair does not; zero it.
print('head location before', tuple(head.location)); head.location = (0, 0, 0)
common.assign_materials(hair, cap, head)
f = common.detect_front(head); print('FRONT detected as', tuple(f))
# print head/hair bbox after alignment for the report
import numpy as np
for o in (hair, cap, head):
    co = np.array([o.matrix_world @ v.co for v in o.data.vertices]); print(o.name, 'world bbox', co.min(0).round(4), co.max(0).round(4))
common.clear_render_rig(); cams = common.setup_cameras(); common.setup_lights('neutral'); common.setup_render(res=1024, samples=32)
common.render_views(os.path.join(common.PROJ, 'renders', '00_original'), 'orig', cams)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(common.PROJ, 'working', '01_original_with_head_materials.blend'))
print('done')
