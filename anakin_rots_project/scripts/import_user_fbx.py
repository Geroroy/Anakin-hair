"""Blender: read a hand-edited FBX (same 11 662 triangles / vertex order as the asset, no skeleton) and dump the world-space
hair and cap positions for stage H. Run: blender -b -P scripts/import_user_fbx.py -- <fbx> <out npz>"""
import bpy, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards
argv = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=argv[0])
out = {}
for name, k in (('HairPlanes_M', 'hair'), ('hair_cap', 'cap')):
    o = bpy.data.objects.get(name)
    if o is None: continue
    out[k + '_co'] = np.array([o.matrix_world @ v.co for v in o.data.vertices])
    out[k + '_faces'] = np.array([p.vertices[:] for p in o.data.polygons]); out[k + '_uv'] = cards.vertex_uvs(o)
np.savez(argv[1], **out); print('dumped', list(out))
