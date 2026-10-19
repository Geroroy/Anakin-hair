import bpy, os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common, cards
from collections import Counter
bpy.ops.wm.open_mainfile(filepath=os.path.join(common.PROJ, 'working', '01_original_with_head_materials.blend'))
hair = bpy.data.objects['HairPlanes_M']; cap = bpy.data.objects['hair_cap']; head = bpy.data.objects['HEAD_REF']
# rebuild materials with the tweaked settings
for m in list(bpy.data.materials):
    if m.name.startswith('M_Hair'): bpy.data.materials.remove(m)
common.assign_materials(hair, cap, head)
rows = cards.card_table(hair, head, common.FRONT, common.HEAD_CENTER)
cards.save_table(rows, os.path.join(common.PROJ, 'reports', 'card_table_original.json'))
print('regions', Counter(r['region'] for r in rows))
import statistics
for reg in sorted(set(r['region'] for r in rows)):
    rs = [r for r in rows if r['region'] == reg]
    print('  %-10s n=%3d  len mean %.3f max %.3f  root-scalp-dist mean %.4f max %.4f  tip z mean %.3f' % (reg, len(rs), statistics.mean(r['length'] for r in rs), max(r['length'] for r in rs), statistics.mean(r['root_scalp_dist'] for r in rs), max(r['root_scalp_dist'] for r in rs), statistics.mean(r['tip'][2] for r in rs)))
# cap-to-head distance
bvh = cards.head_bvh(head)
d = [bvh.find_nearest(cap.matrix_world @ v.co)[3] for v in cap.data.vertices]
print('cap vertex to head surface distance: min %.4f mean %.4f max %.4f' % (min(d), sum(d) / len(d), max(d)))
# signed: is cap outside the head? use normal dot
import mathutils
inside = 0
for v in cap.data.vertices:
    p = cap.matrix_world @ v.co; loc, nrm, idx, dd = bvh.find_nearest(p)
    if (p - loc).dot(nrm) < 0: inside += 1
print('cap verts inside head surface:', inside, '/', len(cap.data.vertices))
# head landmarks: chin bottom, nose tip, ear positions, top
co = np.array([head.matrix_world @ v.co for v in head.data.vertices])
print('head top z %.3f, bottom z %.3f, nose tip (min y) %s, chin region z at y<-0.05: %.3f' % (co[:, 2].max(), co[:, 2].min(), co[co[:, 1].argmin()].round(3), co[(co[:, 1] < -0.05)][:, 2].min()))
ear = co[(np.abs(co[:, 0]) > 0.06)]; print('ear-ish extreme x verts: x max %.3f at z %.3f' % (np.abs(co[:, 0]).max(), co[np.abs(co[:, 0]).argmax()][2]))
common.clear_render_rig(); cams = common.setup_cameras(); common.setup_lights('neutral'); common.setup_render(res=1024, samples=32)
common.render_views(os.path.join(common.PROJ, 'renders', '00_original'), 'orig', cams)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(common.PROJ, 'working', '01_original_with_head_materials.blend'))
print('done')
