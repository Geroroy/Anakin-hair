"""Iteration B — major hair locks: layered hem at the back/nape, S-wave side locks at the jaw, fuller locks behind
the ears, natural asymmetry (his right side fuller/forward, his left side swept back). Starts from positions_A.npz."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.environ.get('MIRROR', '1') == '1'; SUF = '' if MIRROR else 'n'   # MIRROR=0 builds the un-mirrored variant (stages A n/B n/C n)
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); A = np.load(os.path.join(PROJ, 'working', 'positions_A%s.npz' % SUF))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = A['hair_co'].copy(); cap = A['cap_co']; capn = A['cap_nrm']
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
caz = np.abs(C.card_az); saz = C.card_az; cel = C.card_el; N = len(rows); log = []
hair_mirr = G['hair_co'].copy()
if MIRROR: hair_mirr[:, 0] *= -1
s_orig, _, _ = head.signed(hair_mirr); clear = np.minimum(s_orig, 0.004)
rng = np.random.default_rng(11)
# 1. layered hem: flick the lowest part of back / nape / back-side cards in or out --------------------------------
n = 0
for i in range(N):
    w = smoothstep(110, 135, caz[i]) * (1 - smoothstep(5, 20, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > R[2] - 0.02: continue
    s, q, nrm = head.signed(T[None])
    out_pt = T + nrm[0] * 0.05                                     # outward from the neck/skull
    sign = 1 if hash_noise(saz[i] * 4.0 + R[2] * 500, seed=7) > -0.2 else -1   # ~60 % flick out, 40 % tuck in
    ang = math.radians(6 + 10 * rng.random()) * w
    bend_toward(co, C, i, out_pt if sign > 0 else q[0], ang * sign if sign > 0 else ang, tpow=2.5); n += 1
log.append('hem: %d back/nape cards: tips flicked outward (60%%) or tucked (40%%) by 6-16 deg on the lowest 40%% of the card' % n)
# 2. side S-waves at the jaw: alternate lateral yaw + outward flick on the lowest part ---------------------------------
n = 0
for i in range(N):
    w = bump(caz[i], 55, 120, 20) * (1 - smoothstep(0, 18, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > R[2] - 0.02: continue
    sgn = 1 if hash_noise(saz[i] * 3.3 + R[2] * 700, seed=13) > 0 else -1
    yaw_card(co, C, i, sgn * math.radians(7) * w, tpow=2.0)
    s, q, nrm = head.signed(T[None])
    bend_toward(co, C, i, T + nrm[0] * 0.05, math.radians(5 + 6 * rng.random()) * w, tpow=3.0); n += 1
log.append('side S-waves: %d jaw-level side cards yawed +-7 deg (alternating) and tip-flicked 5-11 deg outward' % n)
# 3. asymmetry: his left side (az<0) tucked/swept back a little, his right side (az>0) slightly fuller forward --------
n = 0
for i in range(N):
    w = bump(caz[i], 60, 125, 20) * smoothstep(5, 25, cel[i]) * (1 - smoothstep(45, 55, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if saz[i] < 0:   # his left: yaw tips backward (toward +y) by up to 6 deg
        v = (T - R)[:2]; a1 = math.atan2(v[1], v[0]); back = math.atan2(1, 0); da = (back - a1 + math.pi) % (2 * math.pi) - math.pi
        yaw_card(co, C, i, float(np.clip(da, -1, 1)) * math.radians(6) * w, tpow=1.3)
    else:            # his right: 4 deg forward + 2 % longer
        v = (T - R)[:2]; a1 = math.atan2(v[1], v[0]); fwd = math.atan2(-1, 0); da = (fwd - a1 + math.pi) % (2 * math.pi) - math.pi
        yaw_card(co, C, i, float(np.clip(da, -1, 1)) * math.radians(4) * w, tpow=1.3)
    n += 1
k = np.ones(N); k[(saz > 0) & (caz > 60) & (caz < 125)] *= 1.02
co = C.scale_about_root(co, k)
log.append('asymmetry: %d side cards; his left swept back (<=6 deg), his right forward (<=4 deg) and 2%% longer' % n)
# 4. collisions + normals -----------------------------------------------------------------------------------------------
co, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
log.append('head collision (smooth, per card): %d vertex moves' % pushed)
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_B%s.npz' % SUF), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': 'B', 'mirrored': MIRROR, 'log': log}))
print('\n'.join(log)); d = np.linalg.norm(co - A['hair_co'], axis=1); print('displacement vs A: mean %.4f max %.4f' % (d.mean(), d.max()))
