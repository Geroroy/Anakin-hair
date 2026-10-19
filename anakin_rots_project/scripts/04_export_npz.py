import bpy, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common, cards
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '01_original_with_head_materials.blend'))
hair = bpy.data.objects['HairPlanes_M']; cap = bpy.data.objects['hair_cap']; head = bpy.data.objects['HEAD_REF']
def arr(o, with_uv=True):
    me = o.data
    co = np.array([o.matrix_world @ v.co for v in me.vertices], dtype=np.float64)
    faces = np.array([p.vertices[:] for p in me.polygons], dtype=np.int32)
    nrm = np.array([v.normal for v in me.vertices], dtype=np.float64)
    # custom (split) normals averaged per vertex
    me.calc_normals_split() if hasattr(me, 'calc_normals_split') else None
    cn = np.zeros((len(me.vertices), 3)); cnt = np.zeros(len(me.vertices))
    for l in me.loops: cn[l.vertex_index] += np.array(l.normal); cnt[l.vertex_index] += 1
    cn /= np.maximum(cnt, 1)[:, None]
    uv = cards.vertex_uvs(o) if with_uv else None
    return co, faces, nrm, cn, uv
hc, hf, hn, hcn, huv = arr(hair); cc, cf, cn, ccn, cuv = arr(cap); dc, df, dn, dcn, _ = arr(head, False)
np.savez(os.path.join(common.PROJ, 'working', 'geometry_original.npz'), hair_co=hc, hair_faces=hf, hair_nrm=hn, hair_cnrm=hcn, hair_uv=huv,
         cap_co=cc, cap_faces=cf, cap_nrm=cn, cap_cnrm=ccn, cap_uv=cuv, head_co=dc, head_faces=df, head_nrm=dn)
# are the hair custom normals scalp-transferred? compare to nearest cap vertex normal and to radial direction
from mathutils import Vector
from mathutils.kdtree import KDTree
kd = KDTree(len(cap.data.vertices))
for i, v in enumerate(cap.data.vertices): kd.insert(cap.matrix_world @ v.co, i)
kd.balance()
dots_cap = []; dots_face = []
for i, v in enumerate(hair.data.vertices):
    loc, idx, d = kd.find(Vector(hc[i]))
    dots_cap.append(float(np.dot(hcn[i], ccn[idx])))
    dots_face.append(float(np.dot(hcn[i], hn[i])))
dots_cap = np.array(dots_cap); dots_face = np.array(dots_face)
print('hair custom normal . nearest cap normal: mean %.3f  frac>0.8 %.2f | custom . own face normal: mean |dot| %.3f frac |dot|>0.8 %.2f' % (dots_cap.mean(), (dots_cap > 0.8).mean(), np.abs(dots_face).mean(), (np.abs(dots_face) > 0.8).mean()))
rad = hc - np.array(common.HEAD_CENTER); rad[:, 2] *= 0.6; rad /= np.linalg.norm(rad, axis=1, keepdims=True)
print('hair custom normal . radial: mean %.3f frac>0.8 %.2f' % ((hcn * rad).sum(1).mean(), ((hcn * rad).sum(1) > 0.8).mean()))
print('exported', hc.shape, cc.shape, dc.shape)
