"""Variant 2 — match the user's Coruscant front frame (references/ref_coruscant_front_user.jpg):
part on his left, a wide front wave sweeping across the forehead to his right temple and down past the cheek,
his left side swept back over the ear, both ears covered, chin-length sides curling outward, flat crown.
Side-aware: on the mirrored chain the sweep side is his right; on the un-mirrored chain (final, user decision) the
part stays on his right and the same styling is applied with the sides swapped (sweep toward his left)."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('SRC', 'D2'); OUTN = os.environ.get('OUTN', 'E')
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); P = np.load(os.path.join(PROJ, 'working', 'positions_%s.npz' % SRC))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = P['hair_co'].copy(); cap = P['cap_co']; capn = P['cap_nrm']; mirrored = bool(json.loads(str(P['meta']))['mirrored'])
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
L0 = np.array([r['length'] for r in build_cards(G['hair_co'], G['hair_faces'], G['hair_uv'])]); MAX_STRETCH = 1.35
caz = np.abs(C.card_az); saz = C.card_az; cel = C.card_el; N = len(rows); log = []
hm = G['hair_co'].copy()
if mirrored: hm[:, 0] *= -1
s_orig, _, _ = head.signed(hm); clear = np.minimum(s_orig, 0.004)
rng = np.random.default_rng(77)
SW = -1.0 if mirrored else +1.0            # x direction of the front sweep (toward the side opposite the part)
az_sw = saz * (1.0 if mirrored else -1.0)  # >0 on the sweep side, <0 on the part side
def cap_scale(i, k):
    return float(min(k, max(1.0, MAX_STRETCH * L0[i] / max(C.card_len[i], 1e-6))))
# 1. chin-length sides: lengthen side cards (the frame's sides reach the jaw/chin) ---------------------------------------
k = np.ones(N); n = 0
for i in range(N):
    w = bump(caz[i], 45, 135, 15) * (1 - smoothstep(10, 30, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > R[2] - 0.02: continue
    k[i] = cap_scale(i, 1 + 0.12 * w); n += 1
co = C.scale_about_root(co, k)
log.append('sides lengthened up to +12%% (%d cards) -> jaw/chin length' % n)
# 2. front wave: cards right of the part (his right, az 0..45) swept ACROSS the forehead to the right temple at brow
#    level (yaw 22 deg toward his right + lift so the lowest point is the brow, not the eye) ---------------------------
n = 0
for i in range(N):
    w = bump(az_sw[i], 0, 45, 12) * smoothstep(8, 22, cel[i]) * (1 - smoothstep(50, 60, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > R[2] - 0.02: continue
    best = None
    for a in (math.radians(22), -math.radians(22)):
        tmp = co.copy(); yaw_card(tmp, C, i, a, tpow=1.3); T2, _ = card_tip_root(tmp, C, i)
        if best is None or T2[0] * SW > best[0]: best = (T2[0] * SW, a)
    yaw_card(co, C, i, best[1] * w, tpow=1.3)
    T, R = card_tip_root(co, C, i)
    if T[2] < 1.70:                                   # hanging below the brow: lift the tip sideways/up along the sweep
        lift = np.clip((1.70 - T[2]) / 0.05, 0, 1)
        bend_toward(co, C, i, T + np.array((SW * 0.05, 0.0, 0.05)), math.radians(6 + 14 * lift) * w, tpow=1.4)
    n += 1
log.append('front wave: %d cards on the sweep side yawed 22 deg across the forehead toward the temple, lifted to brow level' % n)
# 2b. front LEFT of the part (his left, az -45..-5): pushed back from the forehead over the ear (frame shows no lock there)
n = 0
for i in range(N):
    w = bump(-az_sw[i], 5, 45, 10) * smoothstep(8, 22, cel[i]) * (1 - smoothstep(50, 60, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > 1.735: continue
    drop = np.clip((1.735 - T[2]) / 0.06, 0, 1)
    bend_toward(co, C, i, T + np.array((-SW * 0.03, 0.08, 0.04)), math.radians(10 + 16 * drop) * w, tpow=1.4)   # back, up, toward the part-side ear
    best = None
    for a in (math.radians(12), -math.radians(12)):
        tmp = co.copy(); yaw_card(tmp, C, i, a, tpow=1.4); T2, _ = card_tip_root(tmp, C, i)
        if best is None or T2[0] * (-SW) > best[0]: best = (T2[0] * (-SW), a)       # tip toward the part-side ear
    yaw_card(co, C, i, best[1] * w, tpow=1.4); n += 1
log.append('front, part side: %d hanging cards pushed back/up 10-26 deg and yawed 12 deg toward the ear' % n)
# 3. his left side (az<0): swept back over the ear; lower part flicks outward at the jaw -----------------------------------
n = 0
for i in range(N):
    w = bump(-az_sw[i], 40, 120, 15) * (1 - smoothstep(20, 40, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > R[2] - 0.02: continue
    v = (T - R)[:2]; a1 = math.atan2(v[1], v[0]); back = math.atan2(1, 0); da = (back - a1 + math.pi) % (2 * math.pi) - math.pi
    yaw_card(co, C, i, float(np.clip(da, -1, 1)) * math.radians(6) * w, tpow=1.3)
    s, q, nrm = head.signed(T[None])
    bend_toward(co, C, i, T + nrm[0] * 0.06, math.radians(8 + 8 * rng.random()) * w, tpow=3.0); n += 1
log.append('part side: %d cards swept back 6 deg, ends flicked outward 8-16 deg' % n)
# 3b. volume over his left ear (frame: the left side bulges over the ear) ---------------------------------------------
n = 0
for i in range(N):
    w = bump(-az_sw[i], 60, 120, 15) * bump(cel[i], -5, 32, 10)
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i); s_, q, nrm = head.signed(T[None])
    if s_[0] > 0.036: continue
    bend_toward(co, C, i, T + nrm[0] * 0.06, math.radians(5 + 6 * rng.random()) * w, tpow=2.0); n += 1
log.append('part-side volume: %d cards lifted 5-11 deg off the skull over the ear' % n)
# 4. his right side lower ends: outward curl at the jaw (the big wave's ends flip out in the frame) ------------------------
n = 0
for i in range(N):
    w = bump(az_sw[i], 40, 120, 15) * (1 - smoothstep(15, 35, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] > R[2] - 0.02: continue
    s, q, nrm = head.signed(T[None])
    bend_toward(co, C, i, T + nrm[0] * 0.06 + np.array((0, -0.02, 0)), math.radians(10 + 8 * rng.random()) * w, tpow=3.0); n += 1
log.append('sweep side: %d cards, ends curled outward 10-18 deg' % n)
# 5. flat crown: tips of crown cards pulled toward the scalp -------------------------------------------------------------
n = 0
for i in range(N):
    if cel[i] < 42: continue
    T, R = card_tip_root(co, C, i); s, q, nrm = head.signed(T[None])
    if s[0] > 0.026:
        bend_toward(co, C, i, q[0], math.radians(8) * smoothstep(42, 60, cel[i]), tpow=1.5); n += 1
log.append('crown flattened: %d cards tilted up to 8 deg toward the scalp' % n)
co, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
log.append('head collision (smooth): %d vertex moves' % pushed)
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_%s.npz' % OUTN), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': OUTN, 'mirrored': mirrored, 'log': log}))
print('\n'.join(log)); d = np.linalg.norm(co - P['hair_co'], axis=1); print('displacement vs %s: mean %.4f max %.4f' % (SRC, d.mean(), d.max()))
