"""Mirror-only test stages to validate the normals/winding pipeline: A0a = mirrored original custom normals,
A0b = scalp-transferred normals (nearest cap vertex)."""
import numpy as np, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz'))
hair = G['hair_co'].copy(); cap = G['cap_co'].copy(); capn = G['cap_cnrm'].copy(); hn = G['hair_cnrm'].copy()
hair[:, 0] *= -1; cap[:, 0] *= -1; capn[:, 0] *= -1; hn[:, 0] *= -1
np.savez(os.path.join(PROJ, 'working', 'positions_A0a.npz'), hair_co=hair, hair_nrm=hn, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': 'A0a', 'mirrored': True}))
sn = scalp_normals(hair, cap, capn)
print('scalp-transferred vs mirrored original custom normals: mean dot %.3f' % (sn * hn).sum(1).mean())
np.savez(os.path.join(PROJ, 'working', 'positions_A0b.npz'), hair_co=hair, hair_nrm=sn, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': 'A0b', 'mirrored': True}))
