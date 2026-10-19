"""Iteration A (v2) — primary silhouette using per-card operations that preserve each card's wave shape.
Output: working/positions_A.npz   (run apply_stage.py -- A afterwards)
"""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.environ.get('MIRROR', '1') == '1'; SUF = '' if MIRROR else 'n'   # MIRROR=0 builds the un-mirrored variant (stages A n/B n/C n)
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz'))
hair = G['hair_co'].copy(); cap = G['cap_co'].copy(); capn = G['cap_cnrm'].copy()
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
log = []
# 1. mirror --------------------------------------------------------------------------------------------
if MIRROR:
    hair[:, 0] *= -1; cap[:, 0] *= -1; capn[:, 0] *= -1
    log.append('mirror X (hair + cap); facial L/R vertex groups swapped on apply')
else:
    log.append('NO mirror (variant n)')
rows = build_cards(hair, G['hair_faces'], G['hair_uv'])
C = Cards(hair, rows, uv_v=G['hair_uv'][:, 1])
co = hair.copy()
caz = np.abs(C.card_az); saz = C.card_az; cel = C.card_el; N = len(rows)
s_orig, _, _ = head.signed(hair)
EAR = {+1: np.array((-0.096, -0.035, 1.69)), -1: np.array((0.088, -0.035, 1.69))}   # +az side = his right = -x
# 2. length ------------------------------------------------------------------------------------------------
noise = hash_noise(saz * 2.7 + C.card_root[:, 2] * 300, seed=5)
k = 1 + 0.06 * noise
k *= 1 - 0.07 * bump(caz, 60, 125, 20) * (1 - smoothstep(10, 30, cel))     # sides to the jaw line
k *= 1 - 0.05 * bump(caz, 120, 150, 15) * (1 - smoothstep(0, 20, cel))     # back-sides: soft V taper
k *= 1 + 0.03 * bump(caz, 160, 181, 15) * (1 - smoothstep(0, 20, cel))     # centre back longest
k *= 1 - 0.10 * bump(caz, -1, 35, 15) * smoothstep(5, 20, cel) * (1 - smoothstep(50, 60, cel))   # fringe to brow
co = C.scale_about_root(co, k)
log.append('per-card length scale: range %.2f..%.2f (noise ±6%%, sides -7%%, back-sides -5%%, back +3%%, fringe -10%%)' % (k.min(), k.max()))
# 3. side / back volume: bend over-extended lower cards toward the head ---------------------------------------
n_bend = 0
for i in range(N):
    if not (caz[i] > 50 and cel[i] < 25): continue
    T, R = card_tip_root(co, C, i)
    s, q, n = head.signed(T[None]); s = s[0]
    allowed = 0.028 if caz[i] < 130 else 0.036                # film: hair hugs the jaw at the sides, fuller at the back
    if s > allowed:
        L = np.linalg.norm(T - R); excess = s - allowed
        ang = min(math.atan2(excess, L) * 0.9, math.radians(25))
        bend_toward(co, C, i, q[0], ang, tpow=1.2); n_bend += 1
log.append('volume: %d lower side/back cards bent toward the head (tip clearance > 22/28 mm), max 25 deg' % n_bend)
# 4. ear coverage: drape the cards rooted behind/above the ear forward over the back of the ear (no yaw) ------------
n_ear = 0
for i in range(N):
    sgn = 1 if saz[i] > 0 else -1
    w = bump(caz[i], 98, 128, 12) * smoothstep(8, 20, cel[i]) * (1 - smoothstep(38, 48, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    target = T + np.array((0, -0.06, -0.02))                  # forward (toward the face) and a little down
    ang = math.radians(10 if sgn > 0 else 7) * w              # his right side fuller/forward than his left
    bend_toward(co, C, i, target, ang, tpow=1.5); n_ear += 1
log.append('ear coverage: %d cards rooted behind/above the ears draped forward 7-10 deg (tpow 1.5)' % n_ear)
# 5. crown: small tilt toward the scalp ------------------------------------------------------------------------
n_cr = 0
for i in range(N):
    if cel[i] < 45: continue
    T, R = card_tip_root(co, C, i); s, q, n = head.signed(T[None])
    if s[0] > 0.030:
        bend_toward(co, C, i, q[0], math.radians(6) * smoothstep(45, 60, cel[i]), tpow=1.5); n_cr += 1
log.append('crown: %d cards tilted up to 6 deg toward the scalp' % n_cr)
# 6. fringe: no yaw (the mirrored original lock already falls over his right brow as in the film); shortened in step 2
# 7. collisions (never closer to the skin than the shipped asset; 4 mm where it was further) ---------------------
clear = np.minimum(s_orig, 0.004)
co, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
log.append('head collision: %d vertex pushes' % pushed)
hair_n = scalp_normals(co, cap, capn)
meta = {'stage': 'A', 'mirrored': MIRROR, 'log': log}
np.savez(os.path.join(PROJ, 'working', 'positions_A%s.npz' % SUF), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps(meta))
print('\n'.join(log)); d = np.linalg.norm(co - hair, axis=1); print('displacement vs mirrored original: mean %.4f max %.4f m' % (d.mean(), d.max()))
