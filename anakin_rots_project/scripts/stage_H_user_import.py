"""Variant 7 — transplant the user's hand-edited v6.fbx (Blender 5.2 export, meshes only) onto the game asset.
The user's vertex positions are taken as-is; topology, vertex order and UVs are verified identical to the original, so the
skeleton, skin weights and UVs of the asset carry over unchanged. Hair normals are re-transferred from the scalp as in
every other stage. Run after import_user_fbx.py: python3 scripts/stage_H_user_import.py"""
import numpy as np, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get('RAW', os.path.join(PROJ, 'working', 'user_v6_raw.npz')); OUTN = os.environ.get('OUTN', 'H')
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); U = np.load(RAW); log = []
for k in ('hair', 'cap'):
    if k + '_co' not in U: continue
    assert U[k + '_co'].shape == G[k + '_co'].shape and (U[k + '_faces'] == G[k + '_faces']).all(), k + ': topology/vertex order differs'
    assert np.abs(U[k + '_uv'] - G[k + '_uv']).max() < 1e-6, k + ': UVs differ'
    log.append('%s: topology, vertex order and UVs identical to the original' % k)
co = U['hair_co']; cap = U['cap_co'] if 'cap_co' in U else G['cap_co']
capn = G['cap_cnrm'] if np.abs(cap - G['cap_co']).max() < 1e-6 else vertex_normals(cap, G['cap_faces'])
log.append('cap: max move vs original %.5f m' % np.abs(cap - G['cap_co']).max())
for s in ('F', 'G'):
    p = os.path.join(PROJ, 'working', 'positions_%s.npz' % s)
    if os.path.exists(p):
        d = np.linalg.norm(co - np.load(p)['hair_co'], axis=1); log.append('hair vs stage %s: mean %.4f max %.4f m' % (s, d.mean(), d.max()))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
s, _, _ = head.signed(co); s0, _, _ = head.signed(G['hair_co'])
log.append('hair-to-skin signed distance 1st/5th/50th pct (mm): original %.1f/%.1f/%.1f -> H %.1f/%.1f/%.1f; below -1 mm: %d (original %d)' % (
    *(np.percentile(s0, [1, 5, 50]) * 1000), *(np.percentile(s, [1, 5, 50]) * 1000), (s < -0.001).sum(), (s0 < -0.001).sum()))
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_%s.npz' % OUTN), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn,
         meta=json.dumps({'stage': OUTN, 'mirrored': False, 'source': 'input/user_edit_v6.fbx', 'log': log}))
print('\n'.join(log))
