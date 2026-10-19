import bpy, os, sys, numpy as np, bmesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '01_original_with_head_materials.blend'))
head = bpy.data.objects['HEAD_REF']; me = head.data
if me.has_custom_normals:
    # custom split normals from the Blender 5.2 export; drop them so face winding drives shading/collision
    try: bpy.ops.mesh.customdata_custom_splitnormals_clear({'object': head}) 
    except Exception as e: print('clear custom normals (ctx) failed:', e)
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
co = np.array([head.matrix_world @ v.co for v in me.vertices]); faces = np.array([p.vertices[:] for p in me.polygons], dtype=np.int32)
fn = np.cross(co[faces[:, 1]] - co[faces[:, 0]], co[faces[:, 2]] - co[faces[:, 0]]); fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12
vn = np.zeros_like(co)
for k in range(3): np.add.at(vn, faces[:, k], fn)
vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12
c = np.array((0, -0.03, 1.69)); cen = co[faces].mean(1)
print('after recalc: inward faces', (((cen - c) * fn).sum(1) < 0).sum(), '/', len(faces), '| top verts normal z mean %.3f' % vn[co[:, 2] > 1.79][:, 2].mean())
G = dict(np.load(os.path.join(common.PROJ, 'working', 'geometry_original.npz')))
G['head_co'] = co; G['head_faces'] = faces; G['head_nrm'] = vn; G['head_fnrm'] = fn
np.savez(os.path.join(common.PROJ, 'working', 'geometry_original.npz'), **G)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(common.PROJ, 'working', '01_original_with_head_materials.blend'))
print('head normals fixed and re-exported')
