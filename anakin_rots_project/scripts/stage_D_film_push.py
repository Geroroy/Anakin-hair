"""Iteration D — stronger push toward the Episode III look (user-approved, un-mirrored variant).
Starts from positions_Cn.npz. 1) front sweep back/sideways to expose the hairline (Utapau / Palpatine frames),
2) larger grouped S-waves around the face, 3) fuller volume behind the ears, 4) more ear coverage,
5) temple locks brought forward/down around the ears."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('SRC', 'Cn'); OUTN = os.environ.get('OUTN', 'D')
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); P = np.load(os.path.join(PROJ, 'working', 'positions_%s.npz' % SRC))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = P['hair_co'].copy(); cap = P['cap_co']; capn = P['cap_nrm']; mirrored = bool(json.loads(str(P['meta']))['mirrored'])
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
L0 = np.array([r['length'] for r in build_cards(G['hair_co'], G['hair_faces'], G['hair_uv'])])   # original card lengths
MAX_STRETCH = 1.35   # cumulative cap vs the ORIGINAL card length (user-approved)
caz = np.abs(C.card_az); saz = C.card_az; cel = C.card_el; N = len(rows); log = []
hm = G['hair_co'].copy()
if mirrored: hm[:, 0] *= -1
s_orig, _, _ = head.signed(hm); clear = np.minimum(s_orig, 0.004)
rng = np.random.default_rng(41)
# the part is on his right (az>0) in the un-mirrored asset: the sweep runs from the part towards his LEFT (+x)
sweep_dir = np.array((+1.0, 0, 0)) if not mirrored else np.array((-1.0, 0, 0))
# 1. front sweep: hanging front cards lifted back/up and swung along the sweep direction ------------------------------
n = 0
for i in range(N):
    w = bump(caz[i], -1, 42, 12) * smoothstep(8, 22, cel[i]) * (1 - smoothstep(50, 60, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > 1.735: continue                        # already above the hairline
    drop = np.clip((1.735 - T[2]) / 0.05, 0, 1)      # how far it hangs below the hairline (0..1)
    ang = math.radians(6 + 10 * drop) * w
    if (saz[i] * sweep_dir[0]) < -22:   # cards already on the sweep side (his left for sweep +x): no lift, yaw only
        pass
    else:
        bend_toward(co, C, i, T + np.array((0, 0.08, 0.02)) + sweep_dir * 0.04, ang, tpow=1.4)   # mostly back, a little up
    yaw_card(co, C, i, math.radians(8) * w * (1 if sweep_dir[0] > 0 else -1), tpow=1.4)
    n += 1
log.append('front sweep: %d hanging front cards bent 6-16 deg back and yawed 8 deg along the sweep (tpow 1.4)' % n)
# 2. larger grouped S-waves around the face (|az| 40-110, el < 30): lobes of 3-4 cards share a direction ---------------
n = 0
for i in range(N):
    w = bump(caz[i], 40, 110, 15) * (1 - smoothstep(10, 30, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > R[2] - 0.02: continue
    lobe = math.sin(saz[i] / 9.0 + R[2] * 60.0)      # smooth sign pattern -> grouped waves
    yaw_card(co, C, i, math.radians(11) * lobe * w, tpow=2.0)
    s, q, nrm = head.signed(T[None])
    bend_toward(co, C, i, T + nrm[0] * 0.06, math.radians(3 + 6 * (0.5 + 0.5 * lobe)) * w, tpow=3.0); n += 1
log.append('face-framing S-waves: %d side cards, grouped yaw +-11 deg + tip flick 3-9 deg' % n)
# 3. fuller behind the ears (|az| 95-145, el -10..32): lift cards away from the skull on the lower half ------------------
n = 0
for i in range(N):
    w = bump(caz[i], 95, 145, 15) * bump(cel[i], -10, 32, 10)
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i); s, q, nrm = head.signed(T[None])
    if s[0] > 0.034: continue
    bend_toward(co, C, i, T + nrm[0] * 0.06, math.radians(5 + 7 * rng.random()) * w, tpow=2.0); n += 1
log.append('behind-ear volume: %d cards lifted 5-12 deg off the skull' % n)
# 4. ear coverage: longer and further forward ------------------------------------------------------------------------------
n = 0; k = np.ones(N)
for i in range(N):
    if not (60 < caz[i] < 125 and 15 < cel[i] < 55): continue
    T, R = card_tip_root(co, C, i)
    if T[2] >= R[2] - 0.02: continue
    k[i] = float(np.clip((R[2] - 1.645) / max(R[2] - T[2], 1e-3), 1.0, 1.35))
    k[i] = float(min(k[i], max(1.0, MAX_STRETCH * L0[i] / max(C.card_len[i], 1e-6)))); n += 1
co = C.scale_about_root(co, k)
for i in range(N):
    if k[i] == 1.0: continue
    T, R = card_tip_root(co, C, i)
    bend_toward(co, C, i, T + np.array((0, -0.07, -0.03)), math.radians(12), tpow=1.5)
log.append('ear coverage: %d cards above the ears lengthened (<=x1.35) to the lobe level and draped 12 deg forward' % n)
# 5. temple locks (|az| 45-80, el 30-55) brought a little forward/down around the ears ---------------------------------------
n = 0
for i in range(N):
    w = bump(caz[i], 45, 80, 12) * bump(cel[i], 30, 55, 8)
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    bend_toward(co, C, i, T + np.array((0, -0.05, -0.05)), math.radians(6) * w, tpow=1.5); n += 1
log.append('temples: %d cards tipped 6 deg forward/down' % n)
co, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
log.append('head collision (smooth): %d vertex moves' % pushed)
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_%s.npz' % OUTN), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': OUTN, 'mirrored': mirrored, 'log': log}))
print('\n'.join(log)); d = np.linalg.norm(co - P['hair_co'], axis=1); print('displacement vs %s: mean %.4f max %.4f' % (SRC, d.mean(), d.max()))
