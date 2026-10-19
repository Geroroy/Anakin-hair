"""Final QA renders for stage C and the original with the same rig: neutral (6 views), strong side light,
Mustafar-style warm light, elevated third-person camera, and a reduced gameplay-size render."""
import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['C']
stage = argv[0]
OUT = os.path.join(common.PROJ, 'renders', 'final_' + stage); os.makedirs(OUT, exist_ok=True)
def rig(blend):
    bpy.ops.wm.open_mainfile(filepath=blend)
    common.clear_render_rig(); cams = common.setup_cameras(); common.setup_render(res=1024, samples=32); return cams
for label, blend in (('final', os.path.join(common.PROJ, 'working', '%s.blend' % stage)), ('original', os.path.join(common.PROJ, 'working', '01_original_with_head_materials.blend'))):
    cams = rig(blend)
    common.setup_lights('neutral'); common.render_views(OUT, label + '_neutral', cams)
    common.setup_lights('side'); common.render_views(OUT, label + '_side', cams, views=['front', 'right', 'three_quarter'])
    common.setup_lights('mustafar'); common.render_views(OUT, label + '_mustafar', cams, views=['front', 'three_quarter', 'elevated'])
    # gameplay distance: perspective camera, character head ~45 px tall in a 1920x1080 frame (typical 3rd-person)
    common.setup_lights('neutral')
    f = common.FRONT; r = Vector((f.y, -f.x, 0))
    cam = common.add_camera('CAM_gameplay', (f * 0.8 + r * 0.5 + Vector((0, 0, 0.35))).normalized(), ortho=False, dist=4.2, lens=35)
    s = bpy.context.scene; s.render.resolution_x = 1920; s.render.resolution_y = 1080; s.camera = cam
    s.render.filepath = os.path.join(OUT, label + '_gameplay_1080p.png'); bpy.ops.render.render(write_still=True)
print('final renders done')
