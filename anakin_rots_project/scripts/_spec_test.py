import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', 'C.blend'))
for m in bpy.data.materials:
    if m.name.startswith('M_Hair'):
        b = m.node_tree.nodes['Principled BSDF']; b.inputs['Specular IOR Level'].default_value = 0.0
        for n in m.node_tree.nodes:
            if n.type == 'MAP_RANGE': n.inputs['To Min'].default_value = 0.9; n.inputs['To Max'].default_value = 0.7
common.clear_render_rig(); cams = common.setup_cameras(); common.setup_lights('neutral'); common.setup_render(res=1024, samples=32)
common.render_views(os.path.join(common.PROJ, 'renders', 'spec_test'), 'nospec', cams, views=['right'])
