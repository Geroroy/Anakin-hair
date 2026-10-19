import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add()
cam=bpy.data.cameras.new('c'); co=bpy.data.objects.new('c',cam); bpy.context.scene.collection.objects.link(co); co.location=(4,-4,3); co.rotation_euler=(1.1,0,0.8); bpy.context.scene.camera=co
s=bpy.context.scene; s.render.resolution_x=64; s.render.resolution_y=64
s.render.engine='BLENDER_EEVEE_NEXT'; s.render.filepath='/tmp/claude-0/-home-user-Anakin-hair/83ae4209-2b74-5dc0-bf76-11de1b38cd90/scratchpad/eevee_test.png'
try:
    bpy.ops.render.render(write_still=True); print('EEVEE OK')
except Exception as e: print('EEVEE FAIL', e)
s.render.engine='BLENDER_WORKBENCH'; s.render.filepath='/tmp/claude-0/-home-user-Anakin-hair/83ae4209-2b74-5dc0-bf76-11de1b38cd90/scratchpad/wb_test.png'
try:
    bpy.ops.render.render(write_still=True); print('WORKBENCH OK')
except Exception as e: print('WORKBENCH FAIL', e)
