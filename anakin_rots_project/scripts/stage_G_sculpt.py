"""Variant 6 — match references/ref_target_sculpt_front.jpg (head sculpt, front view) from stage En.
Part on his right (as the asset), broad front wave to his left brow/temple, right forehead open, EARS EXPOSED,
long S-wave locks behind the ears to chin/upper-neck level, widest at the jaw, his left side fuller, smooth crown.
No mirror, roots fixed, scale steps clamped to 0.80-1.35x the original length."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('SRC', 'En'); OUTN = os.environ.get('OUTN', 'G')
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); P = np.load(os.path.join(PROJ, 'working', 'positions_%s.npz' % SRC))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = P['hair_co'].copy(); cap = P['cap_co']; capn = P['cap_nrm']; assert not bool(json.loads(str(P['meta']))['mirrored'])
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
L0 = np.array([r['length'] for r in build_cards(G['hair_co'], G['hair_faces'], G['hair_uv'])])
caz = np.abs(C.card_az); saz = C.card_az; cel = C.card_el; N = len(rows); log = []
s_orig, _, _ = head.signed(G['hair_co']); clear = np.minimum(s_orig, 0.004)
rng = np.random.default_rng(123)
EAR = {+1: np.array((-0.095, -0.035, 1.69)), -1: np.array((0.088, -0.035, 1.69))}   # +az = his right (x<0)
def tr(i): return card_tip_root(co, C, i)
def hanging(T, R): return T[2] < R[2] - 0.02
def clamp_k(i, k):
    L = max(float(np.linalg.norm(np.subtract(*tr(i)))), 1e-6); return float(np.clip(k, 0.80 * L0[i] / L, 1.35 * L0[i] / L))
def in_ear_box(p, sgn):
    # the ear as measured on HEAD_REF (right ear: |x| 0.078-0.099, y -0.049..-0.019, z 1.651..1.712) plus 4 mm margin
    return (np.abs(p[:, 0]) > 0.076) & (np.abs(p[:, 0]) < 0.106) & (np.abs(np.sign(p[:, 0]) + sgn) < 0.5) & (p[:, 1] > -0.053) & (p[:, 1] < -0.015) & (p[:, 2] > 1.647) & (p[:, 2] < 1.716)
# 1. EARS EXPOSED: (a) undo the forward ear drape of stage En: cards rooted above/in front of the ears whose tips sit
#    forward of the ear are bent backward (toward +y) 15-25 deg; (b) anything still crossing the ear itself is swept back
n = 0
for i in range(N):
    if not (55 < caz[i] < 128 and 10 < cel[i] < 52): continue
    T, R = tr(i)
    if not hanging(T, R): continue
    L = float(np.linalg.norm(T - R))
    if L > 1.02 * L0[i]:                                   # En lengthened these for ear coverage: restore the original length
        k1 = np.ones(N); k1[i] = clamp_k(i, L0[i] / L); co = C.scale_about_root(co, k1); T, R = tr(i)
    if T[1] > -0.01: continue
    ang = math.radians(15 + 10 * np.clip((-0.01 - T[1]) / 0.05, 0, 1))
    bend_toward(co, C, i, T + np.array((0, 0.12, -0.03)), ang, tpow=1.2); n += 1
log.append('ears: %d cards above/in front of the ears restored to original length and bent 15-25 deg backward' % n)
n = 0
for i in range(N):
    sgn = 1 if saz[i] > 0 else -1
    for it in range(5):
        p = co[C.card_idx[i]]
        if not in_ear_box(p, sgn).any(): break
        T, R = tr(i); bend_toward(co, C, i, T + np.array((0, 0.10, -0.02)), math.radians(6), tpow=1.3)
        if it == 0: n += 1
log.append('ears: %d cards crossing the ear itself swept back' % n)
# 2. length: sides/back-sides to chin-upper-neck (z ~1.57), back a little longer ------------------------------------------
k = np.ones(N); n = 0
for i in range(N):
    w = smoothstep(40, 55, caz[i]) * (1 - smoothstep(22, 34, cel[i]))
    if w < 0.05: continue
    T, R = tr(i)
    if not hanging(T, R): continue
    target = 1.570 if caz[i] < 150 else 1.560
    if T[2] <= target - 0.005: continue
    kk = (R[2] - target) / max(R[2] - T[2], 1e-3)
    k[i] = clamp_k(i, 1 + (min(kk, 1.15) - 1) * w); n += 1
co = C.scale_about_root(co, k)
log.append('length: %d side/back cards lengthened toward z=1.57 (k max %.2f)' % (n, k.max()))
# 3. front wave: the sweep-side cards form one broad wave whose lowest point sits on his left brow (outer third) and then
#    turns back past the temple; his right forehead beside the part stays open -------------------------------------------
BROW_L = np.array((0.048, -0.135, 1.717)); n = 0
for i in range(N):
    T, R = tr(i)
    sweep = (saz[i] < 2 and saz[i] > -45) or (saz[i] >= 2 and saz[i] < 38 and T[0] > 0.0)
    if not (sweep and 8 < cel[i] < 55 and hanging(T, R)): continue
    # cards reaching the forehead: lowest point to the brow, tip onward to the temple
    if T[1] < -0.06 and T[2] < 1.76:
        if T[2] < 1.705:                                             # ends below the brow: shorten so the tip sits at brow/temple height
            k1 = np.ones(N); k1[i] = clamp_k(i, (R[2] - 1.705) / max(R[2] - T[2], 1e-3)); co = C.scale_about_root(co, k1); T, R = tr(i)
        bend_toward(co, C, i, np.array((0.085, -0.075, 1.705)), math.radians(12), tpow=1.3)   # to his left temple
        T, R = tr(i); bend_toward(co, C, i, T + np.array((0.0, 0.08, 0.0)), math.radians(10), tpow=2.0); n += 1   # tip turns back
log.append('front wave: %d sweep-side cards cut to brow height, guided to his left temple and turned back' % n)
# sideburns: the sculpt has none. Cards rooted in front of the ears below the temple are shortened and tucked back
n = 0
for i in range(N):
    R0 = C.card_root[i]
    if not (38 < caz[i] < 75 and cel[i] < 30 and R0[1] < -0.035): continue
    T, R = tr(i)
    k1 = np.ones(N); k1[i] = clamp_k(i, 0.80); co = C.scale_about_root(co, k1); T, R = tr(i)
    bend_toward(co, C, i, T + np.array((0, 0.10, 0.0)), math.radians(14), tpow=1.2); n += 1
log.append('sideburns: %d cards in front of the ears shortened to 0.80 and tucked back' % n)
n = 0
for i in range(N):
    if not (5 < saz[i] < 45 and 8 < cel[i] < 55): continue
    T, R = tr(i)
    if T[0] > -0.01 or not hanging(T, R) or T[2] > 1.745 or T[1] > -0.07: continue     # hanging on his right forehead
    bend_toward(co, C, i, T + np.array((-0.03, 0.08, 0.05)), math.radians(18), tpow=1.3); n += 1
log.append('right forehead open: %d cards swept back' % n)
# 4. side silhouette: narrow at the temples, widest at the jaw, ends flare out; his left fuller ----------------------------
n = 0
for i in range(N):
    w = bump(caz[i], 50, 130, 15)
    if w < 0.05: continue
    T, R = tr(i)
    if not hanging(T, R): continue
    s, q, nrm = head.signed(T[None])
    if cel[i] > 22:                       # temple zone: keep tight (<= 22 mm)
        if s[0] > 0.018: bend_toward(co, C, i, q[0], min(math.radians(22), math.atan2(s[0] - 0.014, max(np.linalg.norm(T - R), 1e-3))) * w, tpow=1.2); n += 1
    else:                                 # below the ears: fullness (>= 30 mm), more on his left
        want = 0.025 + (0.006 if saz[i] < 0 else 0.0)
        if s[0] < want: bend_toward(co, C, i, T + nrm[0] * 0.08, min(math.radians(14), math.atan2(want - s[0], max(np.linalg.norm(T - R), 1e-3)) * 1.2) * w, tpow=1.0); n += 1
log.append('silhouette: %d cards (temples tight, jaw level full, his left fuller)' % n)
n = 0
for i in range(N):
    w = smoothstep(40, 55, caz[i]) * (1 - smoothstep(12, 28, cel[i]))
    if w < 0.05: continue
    T, R = tr(i)
    if not hanging(T, R): continue
    s, q, nrm = head.signed(T[None])
    bend_toward(co, C, i, T + nrm[0] * 0.06, math.radians(4 + 4 * rng.random()) * w, tpow=3.0); n += 1
log.append('ends: %d cards flared 4-8 deg outward (tpow 3)' % n)
n = 0
for i in range(N):
    w = smoothstep(40, 55, caz[i]) * (1 - smoothstep(25, 40, cel[i]))
    if w < 0.05: continue
    T, R = tr(i); s_, q, nrm = head.signed(T[None])
    if s_[0] > 0.036: bend_toward(co, C, i, q[0], min(math.radians(20), math.atan2(s_[0] - 0.032, max(np.linalg.norm(T - R), 1e-3))) * w, tpow=1.2); n += 1
log.append('compact: %d lower cards further than 36 mm from the skin bent in' % n)
# 5. waves: grouped yaw +-8 deg in lobes of 3-4 cards on the lower 60% ----------------------------------------------------
n = 0
for i in range(N):
    w = smoothstep(30, 45, caz[i]) * (1 - smoothstep(28, 42, cel[i]))
    if w < 0.05: continue
    T, R = tr(i)
    if not hanging(T, R): continue
    lobe = math.sin(saz[i] / 9.0 + C.card_root[i][2] * 80.0)
    yaw_card(co, C, i, math.radians(8) * lobe * w, tpow=1.8); n += 1
log.append('waves: %d cards, grouped yaw +-8 deg' % n)
# 6. back: layered, no shelf -----------------------------------------------------------------------------------------------
k2 = np.ones(N); n = 0
for i in range(N):
    w = smoothstep(130, 150, caz[i]) * (1 - smoothstep(5, 25, cel[i]))
    if w < 0.05: continue
    k2[i] = clamp_k(i, 1 + 0.06 * (math.sin(saz[i] / 12.0) * 0.5 + math.sin(C.card_root[i][2] * 110.0) * 0.5) * w); n += 1
co = C.scale_about_root(co, k2)
log.append('back layers: %d cards +-6%% low-frequency modulation' % n)
# 7. crown: stray tips toward the scalp ------------------------------------------------------------------------------------
n = 0
for i in range(N):
    if cel[i] < 38: continue
    T, R = tr(i); s, q, nrm = head.signed(T[None])
    if s[0] > 0.017: bend_toward(co, C, i, q[0], math.radians(5 + 5 * smoothstep(38, 65, cel[i])), tpow=1.4); n += 1
log.append('crown/top sleek: %d tips further than 17 mm off the scalp tilted 5-10 deg toward it' % n)
# guards -----------------------------------------------------------------------------------------------------------------
n = 0
for i in range(N):
    for it in range(5):
        p = co[C.card_idx[i]]
        if not ((p[:, 2] < 1.715) & (p[:, 1] < -0.105) & (np.abs(p[:, 0]) < 0.05)).any(): break
        T, R = tr(i); bend_toward(co, C, i, T + np.array((0, 0.04, 0.08)), math.radians(8), tpow=1.3); n += 1
log.append('eye-zone enforcement: %d bend steps' % n)
co, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
log.append('head collision (smooth): %d vertex moves' % pushed)
ear_hits = sum(1 for i in range(N) if in_ear_box(co[C.card_idx[i]], 1 if saz[i] > 0 else -1).any())
rows1 = build_cards(co, G['hair_faces'], G['hair_uv']); ratio = np.array([r['length'] for r in rows1]) / np.maximum(L0, 1e-6)
log.append('final: %d cards still in an ear box; length ratio vs original min %.2f max %.2f' % (ear_hits, ratio.min(), ratio.max()))
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_%s.npz' % OUTN), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': OUTN, 'mirrored': False, 'log': log}))
print('\n'.join(log)); d = np.linalg.norm(co - P['hair_co'], axis=1); print('displacement vs %s: mean %.4f max %.4f' % (SRC, d.mean(), d.max()))
