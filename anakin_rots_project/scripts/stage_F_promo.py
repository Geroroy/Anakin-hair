"""Variant 4 — match references/ref_target_promo_front.jpg (promo front photo) starting from stage En.
Compact rounded bob: jaw-length sides/back, outward-up flip curls grouped in clumps, full sides hiding the ears,
open forehead with one soft lock at his right temple, rounded crown, soft S-waves. No mirror, roots fixed,
cumulative card length within 0.80-1.35x the original."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('SRC', 'En'); OUTN = os.environ.get('OUTN', 'F')
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); P = np.load(os.path.join(PROJ, 'working', 'positions_%s.npz' % SRC))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = P['hair_co'].copy(); cap = P['cap_co']; capn = P['cap_nrm']; mirrored = bool(json.loads(str(P['meta']))['mirrored'])
assert not mirrored
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
L0 = np.array([r['length'] for r in build_cards(G['hair_co'], G['hair_faces'], G['hair_uv'])])
caz = np.abs(C.card_az); saz = C.card_az; cel = C.card_el; N = len(rows); log = []
s_orig, _, _ = head.signed(G['hair_co']); clear = np.minimum(s_orig, 0.004)
rng = np.random.default_rng(99)
JAW_Z = float(os.environ.get('JAW_Z', 1.600)); BROW_Z = 1.72
def cur_len(i):
    T, R = card_tip_root(co, C, i); return float(np.linalg.norm(T - R))
def clamp_k(i, k):   # cumulative 0.80..1.35 of the ORIGINAL length
    L = max(cur_len(i), 1e-6); return float(np.clip(k, 0.80 * L0[i] / L, 1.35 * L0[i] / L))
hanging = lambda T, R: T[2] < R[2] - 0.02
# 1+2. jaw-length sides and back: cards whose tips hang below the jaw line are shortened to it -------------------------
k = np.ones(N); n = 0
for i in range(N):
    w = smoothstep(35, 50, caz[i]) * (1 - smoothstep(20, 32, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if not hanging(T, R) or T[2] >= JAW_Z: continue
    kk = (R[2] - JAW_Z) / max(R[2] - T[2], 1e-3)
    k[i] = clamp_k(i, 1 - (1 - kk) * w); n += 1
co = C.scale_about_root(co, k)
log.append('jaw length: %d side/back cards shortened to z=%.3f (k min %.2f)' % (n, JAW_Z, k.min()))
# 4a. compact the silhouette: tips further than 34 mm from the skin bent toward it ---------------------------------------
n = 0
for i in range(N):
    w = smoothstep(35, 50, caz[i]) * (1 - smoothstep(25, 40, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i); s, q, nrm = head.signed(T[None])
    if s[0] <= 0.034: continue
    L = np.linalg.norm(T - R); ang = min(math.atan2(s[0] - 0.030, L) * 0.9, math.radians(22))
    bend_toward(co, C, i, q[0], ang * w, tpow=1.2); n += 1
log.append('compact: %d cards with tips > 34 mm off the skin bent toward it (<= 22 deg)' % n)
# 4b. side volume: mid-length lift 8-14 deg off the skull, ears hidden (ear-zone tips 15-25 mm forward) -------------------
n = 0
for i in range(N):
    w = bump(caz[i], 50, 130, 15) * bump(cel[i], -5, 40, 10)
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i); s, q, nrm = head.signed(T[None])
    if s[0] > 0.030: continue
    bend_toward(co, C, i, T + nrm[0] * 0.08, math.radians(8 + 6 * rng.random()) * w, tpow=1.0); n += 1
log.append('side volume: %d cards lifted 8-14 deg off the skull' % n)
n = 0
for i in range(N):
    w = bump(caz[i], 62, 122, 12) * bump(cel[i], 12, 50, 8)
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if not hanging(T, R): continue
    L = max(np.linalg.norm(T - R), 1e-3); ang = min(0.020 / L, math.radians(25))
    bend_toward(co, C, i, T + np.array((0, -0.08, -0.01)), ang * w, tpow=1.5); n += 1
log.append('ears: %d cards above the ears, tips pushed ~20 mm forward' % n)
# 3. ends: outward-and-up flip curls at jaw level, grouped in clumps of 3-4 cards ------------------------------------------
n = 0
for i in range(N):
    w = smoothstep(35, 50, caz[i]) * (1 - smoothstep(15, 30, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if not hanging(T, R): continue
    lobe = 0.5 + 0.5 * math.sin(saz[i] / 8.0 + C.card_root[i][2] * 90.0)       # clumps of ~3-4 adjacent cards
    s, q, nrm = head.signed(T[None])
    bend_toward(co, C, i, T + nrm[0] * 0.06 + np.array((0, 0, 0.05)), math.radians(6 + 6 * lobe) * w, tpow=3.0); n += 1
log.append('flip curls: %d cards, lowest 30%% bent outward+up 6-12 deg in lobes' % n)
# 7. soft S-waves: alternating grouped yaw +-10 deg on the lower 60% ---------------------------------------------------------
n = 0
for i in range(N):
    w = smoothstep(25, 40, caz[i]) * (1 - smoothstep(25, 40, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if not hanging(T, R): continue
    lobe = math.sin(saz[i] / 11.0 + C.card_root[i][2] * 70.0)
    yaw_card(co, C, i, math.radians(4) * lobe * w, tpow=2.0); n += 1
log.append('S-waves: %d cards yawed +-4 deg (grouped) on the lower part' % n)
# 5. front: open forehead. his left (az<0) hanging front cards swept back 15-25 deg; his right temple lock kept at brow --------
n = 0
for i in range(N):
    T, R = card_tip_root(co, C, i)
    crossing = (saz[i] > -5) and (saz[i] < 45) and (T[0] > 0.0) and cel[i] > 8 and cel[i] < 60
    w = max(bump(-saz[i], 5, 45, 10), 1.0 if crossing else 0.0) * smoothstep(8, 20, cel[i]) * (1 - smoothstep(50, 60, cel[i]))
    if w < 0.05: continue
    if T[2] > 1.745: continue
    drop = np.clip((1.745 - T[2]) / 0.05, 0, 1)
    bend_toward(co, C, i, T + np.array((0.03, 0.08, 0.05)), math.radians(15 + 10 * drop) * w, tpow=1.3); n += 1
log.append('front, his left: %d cards swept back 15-25 deg (forehead opened)' % n)
n = 0
for i in range(N):
    w = bump(saz[i], 5, 45, 10) * smoothstep(8, 20, cel[i]) * (1 - smoothstep(50, 60, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if T[2] >= BROW_Z: continue
    kk = (R[2] - BROW_Z) / max(R[2] - T[2], 1e-3)
    k1 = np.ones(N); k1[i] = clamp_k(i, 1 - (1 - kk) * w); co = C.scale_about_root(co, k1)
    T, R = card_tip_root(co, C, i)
    bend_toward(co, C, i, T + np.array((-0.05, 0.0, 0.0)), math.radians(8) * w, tpow=1.5); n += 1    # drape to his right temple
log.append('front, his right temple lock: %d cards shortened to brow height and draped 8 deg to the temple' % n)
# 5b. his left side (sweep side) falls DOWN along the face, not outward: pull splayed tips toward a point below the root
n = 0
for i in range(N):
    w = bump(-saz[i], 15, 85, 12) * (1 - smoothstep(30, 45, cel[i]))
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if not hanging(T, R): continue
    s, q, nrm = head.signed(T[None])
    if s[0] < 0.028: continue
    bend_toward(co, C, i, np.array((R[0], R[1], R[2] - 0.2)), math.radians(min(22, 60 * (s[0] - 0.028))) * w, tpow=1.0); n += 1
log.append('his left side: %d splayed cards pulled back down along the face' % n)
# 5c. ears hidden: cards rooted above/behind the ears lengthened (<= cap) toward the lobe and draped forward/down
n = 0; k2 = np.ones(N)
for i in range(N):
    w = bump(caz[i], 60, 125, 12) * bump(cel[i], 12, 50, 8)
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if not hanging(T, R) or T[2] < 1.64: continue
    k2[i] = clamp_k(i, 1 + ((R[2] - 1.64) / max(R[2] - T[2], 1e-3) - 1) * w); n += 1
co = C.scale_about_root(co, k2)
for i in range(N):
    if k2[i] == 1.0: continue
    T, R = card_tip_root(co, C, i)
    bend_toward(co, C, i, T + np.array((0, -0.06, -0.03)), math.radians(10), tpow=1.5)
log.append('ears: %d cards lengthened toward the lobe (k max %.2f) and draped forward' % (n, k2.max()))
# 5d. his right temple lock: front-right cards lengthened to the brow and curved down the temple
n = 0; k3 = np.ones(N)
for i in range(N):
    w = bump(saz[i], 12, 45, 8) * bump(cel[i], 18, 45, 8)
    if w < 0.05: continue
    T, R = card_tip_root(co, C, i)
    if not hanging(T, R) or T[2] < BROW_Z or T[0] > -0.035: continue     # only cards already falling down his right temple
    k3[i] = clamp_k(i, 1 + ((R[2] - BROW_Z) / max(R[2] - T[2], 1e-3) - 1) * w); n += 1
co = C.scale_about_root(co, k3)
for i in range(N):
    if k3[i] == 1.0: continue
    T, R = card_tip_root(co, C, i)
    bend_toward(co, C, i, T + np.array((-0.03, -0.01, -0.08)), math.radians(10), tpow=1.5)
log.append('right temple lock: %d cards lengthened to the brow (k max %.2f) and curved down the temple' % (n, k3.max()))
# 5e. the near-horizontal sweep cards beside the part that lie diagonally across the forehead: swept back over the top
n = 0
for i in range(N):
    if not (5 < saz[i] < 35 and 33 < cel[i] < 52): continue
    T, R = card_tip_root(co, C, i)
    if T[0] < 0.03 or T[1] > -0.06: continue
    bend_toward(co, C, i, T + np.array((0, 0.10, 0.06)), math.radians(22), tpow=1.0); n += 1
log.append('crossing sweep cards: %d bent 22 deg back over the top (forehead corner opened)' % n)
# 6. crown: stray tips toward the scalp ----------------------------------------------------------------------------------
n = 0
for i in range(N):
    if cel[i] < 45: continue
    T, R = card_tip_root(co, C, i); s, q, nrm = head.signed(T[None])
    if s[0] > 0.026:
        bend_toward(co, C, i, q[0], math.radians(4 + 4 * smoothstep(45, 65, cel[i])), tpow=1.5); n += 1
log.append('crown: %d stray tips tilted 4-8 deg toward the scalp' % n)
# eye-zone enforcement: any card with vertices below z 1.715 in front of the face is bent up/back until clear
n = 0
for i in range(N):
    for it in range(5):
        p = co[C.card_idx[i]]
        if not ((p[:, 2] < 1.715) & (p[:, 1] < -0.105) & (np.abs(p[:, 0]) < 0.06)).any(): break
        T, R = card_tip_root(co, C, i); bend_toward(co, C, i, T + np.array((0, 0.04, 0.08)), math.radians(8), tpow=1.3); n += 1
log.append('eye-zone enforcement: %d bend steps' % n)
co, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
log.append('head collision (smooth): %d vertex moves' % pushed)
# eye-zone check
bad = 0
for i in range(N):
    p = co[C.card_idx[i]]
    if ((p[:, 2] < 1.715) & (p[:, 1] < -0.105) & (np.abs(p[:, 0]) < 0.06)).any(): bad += 1
log.append('eye-zone check: %d cards with vertices below z 1.715 in front of the face (|x|<6 cm)' % bad)
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_%s.npz' % OUTN), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': OUTN, 'mirrored': False, 'log': log}))
rows1 = build_cards(co, G['hair_faces'], G['hair_uv']); ratio = np.array([r['length'] for r in rows1]) / np.maximum(L0, 1e-6)
log.append('length ratio vs original: min %.2f max %.2f' % (ratio.min(), ratio.max()))
print('\n'.join(log)); d = np.linalg.norm(co - P['hair_co'], axis=1); print('displacement vs %s: mean %.4f max %.4f' % (SRC, d.mean(), d.max()))
