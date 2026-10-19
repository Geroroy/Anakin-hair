"""Iteration C — fine reconstruction: more ear coverage on his left, grouped layer lengths at the back hem,
slightly stronger S-waves behind the ears, gentle forward fall of the loose strands left of the part."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.environ.get('MIRROR', '1') == '1'; SUF = '' if MIRROR else 'n'   # MIRROR=0 builds the un-mirrored variant (stages A n/B n/C n)
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); B = np.load(os.path.join(PROJ, 'working', 'positions_B%s.npz' % SUF))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = B['hair_co'].copy(); cap = B['cap_co']; capn = B['cap_nrm']
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
caz = np.abs(C.card_az); saz = C.card_az; cel = C.card_el; N = len(rows); log = []
hm = G['hair_co'].copy()
if MIRROR: hm[:, 0] *= -1
s_orig, _, _ = head.signed(hm); clear = np.minimum(s_orig, 0.004)
rng = np.random.default_rng(23)
# 1. ear coverage (both sides): cards rooted above the ears are lengthened so their tips reach the ear-lobe level
#    (z ~ 1.655) and draped forward over the ear; the film covers the upper two thirds of both ears ----------------------
n = 0; k_ear = np.ones(N)
for i in range(N):
    if not (62 < caz[i] < 122 and 15 < cel[i] < 52): continue
    T, R = card_tip_root(co, C, i)
    if T[2] >= R[2] - 0.02: continue
    k_ear[i] = float(np.clip((R[2] - 1.655) / max(R[2] - T[2], 1e-3), 1.0, 1.28))
    n += 1
co = C.scale_about_root(co, k_ear)
for i in range(N):
    if k_ear[i] == 1.0 and not (62 < caz[i] < 122 and 15 < cel[i] < 52): continue
    T, R = card_tip_root(co, C, i)
    sgn = 1 if saz[i] > 0 else -1
    bend_toward(co, C, i, T + np.array((0, -0.06, -0.03)), math.radians(9 if sgn > 0 else 7), tpow=1.5)
log.append('ear coverage: %d cards above the ears lengthened (x%.2f max) to reach the lobe level and draped 7-9 deg forward' % (n, k_ear.max()))
# 2. grouped layer lengths at the back: low-frequency variation so neighbouring cards form layers -----------------------
k = np.ones(N)
for i in range(N):
    w = smoothstep(115, 140, caz[i]) * (1 - smoothstep(5, 25, cel[i]))
    if w < 0.05: continue
    layer = math.sin(saz[i] / 14.0) * 0.5 + math.sin(C.card_root[i][2] * 120.0) * 0.5    # ~3-4 adjacent cards per lobe
    k[i] = 1 + 0.07 * layer * w
co = C.scale_about_root(co, k)
log.append('back layers: low-frequency +-7%% length modulation on %d back cards' % int((k != 1).sum()))
# 3. a little more wave behind the ears (az 95-140, el 0-25): alternate yaw on the lowest third ---------------------------
n = 0
for i in range(N):
    w = bump(caz[i], 95, 140, 15) * (1 - smoothstep(5, 25, cel[i]))
    if w < 0.05: continue
    sgn = 1 if hash_noise(saz[i] * 2.1 + C.card_root[i][2] * 450, seed=29) > 0 else -1
    yaw_card(co, C, i, sgn * math.radians(5) * w, tpow=2.5); n += 1
log.append('behind-ear waves: %d cards yawed +-5 deg on the tip third' % n)
# 4. strands just left of the part: let them fall slightly forward onto the forehead (film: loose layered front) ----------
n = 0
for i in range(N):
    R = C.card_root[i]
    if not (-35 < saz[i] < -8 and 20 < cel[i] < 50): continue
    T, _ = card_tip_root(co, C, i)
    if T[2] > R[2] - 0.03: continue
    bend_toward(co, C, i, T + np.array((0, -0.05, -0.02)), math.radians(5), tpow=1.5); n += 1
log.append('front-left strands: %d hanging cards tipped 5 deg forward' % n)
co, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
log.append('head collision (smooth): %d vertex moves' % pushed)
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_C%s.npz' % SUF), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': 'C', 'mirrored': MIRROR, 'log': log}))
print('\n'.join(log)); d = np.linalg.norm(co - B['hair_co'], axis=1); print('displacement vs B: mean %.4f max %.4f' % (d.mean(), d.max()))
