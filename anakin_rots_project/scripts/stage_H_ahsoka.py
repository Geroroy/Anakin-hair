"""Variant 7 — match the *Ahsoka* "World Between Worlds" frames (references/ref_target_ahsoka_*.{jpg,png}) from stage En (variant 3).
Part on his right (as the asset), one thick wave from the part to his left brow/temple, a lock down his right temple in
front of the ear, EARS FULLY HIDDEN, tall airy top, big wavy side mass widest at cheek/jaw level (38-45 mm off the skin),
sides to the chin, back to the collar, ends curling outward and under, strong grouped S-waves.
No mirror, roots fixed, scale steps clamped to 0.80-1.35x the original length."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('SRC', 'En'); OUTN = os.environ.get('OUTN', 'H')
# tunables (overridable from the environment for the iteration loop)
def env(k, d): return float(os.environ.get(k, d))
JAW_FULL = env('JAW_FULL', 0.042); TEMPLE_FULL = env('TEMPLE_FULL', 0.023); TOP_LIFT = env('TOP_LIFT', 5.0)
WAVE_DEG = env('WAVE_DEG', 11.0); CURL_DEG = env('CURL_DEG', 14.0); SIDE_Z = env('SIDE_Z', 1.572); BACK_Z = env('BACK_Z', 1.542)
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); P = np.load(os.path.join(PROJ, 'working', 'positions_%s.npz' % SRC))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = P['hair_co'].copy(); cap = P['cap_co']; capn = P['cap_nrm']; assert not bool(json.loads(str(P['meta']))['mirrored'])
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
L0 = np.array([r['length'] for r in build_cards(G['hair_co'], G['hair_faces'], G['hair_uv'])])
caz = np.abs(C.card_az); saz = C.card_az; cel = C.card_el; N = len(rows); log = []
s_orig, _, _ = head.signed(G['hair_co']); clear = np.minimum(s_orig, 0.004)
rng = np.random.default_rng(7)
def tr(i): return card_tip_root(co, C, i)
def hanging(T, R): return T[2] < R[2] - 0.02
def clamp_k(i, k):
    L = max(float(np.linalg.norm(np.subtract(*tr(i)))), 1e-6); return float(np.clip(k, 0.80 * L0[i] / L, 1.35 * L0[i] / L))
def scale_one(i, k):
    global co
    k1 = np.ones(N); k1[i] = clamp_k(i, k); co = C.scale_about_root(co, k1)
def lobe(i, period=7.5, seed=0.0):
    """Smooth per-card group index in [-1,1]: neighbouring cards (azimuth / root height) get the same sign."""
    return math.sin(saz[i] / period + C.card_root[i][2] * 80.0 + seed)
# ear box as measured on HEAD_REF (right ear: |x| 0.078-0.099, y -0.049..-0.019, z 1.651..1.712)
EAR_Y = (-0.049, -0.019); EAR_Z = (1.646, 1.714)
FACES = G['hair_faces']
def ray_hits(co, origins, d):
    """Number of hair triangles each ray (origin, shared direction d) crosses in front of its origin (Moller-Trumbore)."""
    a, b, c = co[FACES[:, 0]], co[FACES[:, 1]], co[FACES[:, 2]]
    e1 = b - a; e2 = c - a; pv = np.cross(d, e2); det = (e1 * pv).sum(1); ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
    hits = []
    for o in origins:
        tv = o - a; u = (tv * pv).sum(1) * inv; qv = np.cross(tv, e1); v = (d * qv).sum(1) * inv; t = (e2 * qv).sum(1) * inv
        hits.append(int((ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0.002)).sum()))
    return np.array(hits)
def ear_samples(sgn):
    return [(y, z) for y in np.linspace(*EAR_Y, 4) for z in np.linspace(*EAR_Z, 6)]
def ear_coverage(co, min_hits=3):
    """Per side: fraction of ear sample points hidden from the FRONT view (ray toward -y from the ear's front face) and
    from the SIDE view (ray outward along x from the ear's outer face); hidden = at least `min_hits` card triangles crossed."""
    out = {}
    for sgn, name in ((-1, 'his_right'), (+1, 'his_left')):      # sgn = sign of x; his right is x<0
        pts = ear_samples(sgn)
        front = ray_hits(co, np.array([(sgn * 0.088, EAR_Y[0], z) for y, z in pts]), np.array((0., -1., 0.)))
        side = ray_hits(co, np.array([(sgn * 0.100, y, z) for y, z in pts]), np.array((sgn * 1., 0., 0.)))
        out[name] = (round(float((front >= min_hits).mean()), 2), round(float((side >= min_hits).mean()), 2))
    return out
log.append('ear coverage at start (front, side): %s' % ear_coverage(co))
# 1. EARS HIDDEN: cards rooted above / behind / in front of the ears are brought down over the ear box --------------------
n = 0; EARCARDS = set()
for i in range(N):
    if not (50 < caz[i] < 130 and 6 < cel[i] < 56): continue
    T, R = tr(i)
    if not hanging(T, R): continue
    sgn = -1 if saz[i] > 0 else 1                                   # +az = his right = x<0
    if T[2] > 1.636:                                                 # tip above the bottom of the ear: lengthen (<= 1.25x)
        scale_one(i, min(1.25, (R[2] - 1.628) / max(R[2] - T[2], 1e-3))); T, R = tr(i)
    # swing the whole card so it hangs in front of / over the ear, 2-3 cm off the skin (as the side mass in the frames)
    goal = np.array((sgn * 0.108, -0.056, 1.640))
    ang = math.radians(14 + 12 * smoothstep(-0.03, 0.03, T[1] - goal[1]))   # tips sitting behind the ear move more
    bend_toward(co, C, i, goal, ang, tpow=1.0); EARCARDS.add(i); n += 1
log.append('ears: %d cards above/around the ears lengthened (<=1.25x) and swung over / in front of the ear' % n)
# sideburns: keep, lengthen to cover the front of the ear and blend 8-10 deg outward into the side mass
n = 0
for i in range(N):
    R0 = C.card_root[i]
    if not (36 < caz[i] < 76 and cel[i] < 30 and R0[1] < -0.035): continue
    T, R = tr(i)
    if T[2] > 1.625: scale_one(i, min(1.35, (R[2] - 1.618) / max(R[2] - T[2], 1e-3))); T, R = tr(i)   # down to the jaw
    s, q, nrm = head.signed(T[None])
    bend_toward(co, C, i, T + nrm[0] * 0.05, math.radians(1 + 1 * rng.random()), tpow=1.5)
    T, R = tr(i)
    if T[1] < -0.058: bend_toward(co, C, i, np.array((T[0], -0.052, T[2])), math.radians(6), tpow=1.3)   # over the ear front
    n += 1
log.append('sideburns: %d cards kept, lengthened to the jaw in front of the ear, 1-2 deg outward' % n)
# iterative cover: for every ear sample point still visible from the side or the front, pull the 3 nearest cards
# (rooted above / in front of the ear, within 6 cm) over it: bend their mid-length toward a point 10 mm outside the ear
def cover_ears(rounds=6, min_hits=3):
    global co
    n = 0
    for it in range(rounds):
        cov = ear_coverage(co, min_hits)
        if min(min(v) for v in cov.values()) >= 0.95: break
        for sgn in (-1, +1):
            pts = ear_samples(sgn)
            front = ray_hits(co, np.array([(sgn * 0.088, EAR_Y[0], z) for y, z in pts]), np.array((0., -1., 0.)))
            side = ray_hits(co, np.array([(sgn * 0.100, y, z) for y, z in pts]), np.array((sgn * 1., 0., 0.)))
            for (y, z), fh, sh in zip(pts, front, side):
                if fh >= min_hits and sh >= min_hits: continue
                goal = np.array((sgn * 0.110, y - (0.012 if fh < min_hits else 0.0), z - 0.004))
                roots = C.card_root; dist = np.linalg.norm(roots - np.array((sgn * 0.085, y, z + 0.04)), axis=1)
                cand = [i for i in np.argsort(dist)[:16] if dist[i] < 0.065 and (np.sign(roots[i][0]) == sgn) and roots[i][2] > z + 0.015 and C.card_len[i] > 0.03][:3]
                for i in cand:
                    T, R = tr(i)
                    if T[2] > z - 0.008: scale_one(i, min(1.25, (R[2] - (z - 0.012)) / max(R[2] - T[2], 1e-3)))
                    bend_toward(co, C, i, goal, math.radians(10), tpow=1.0); EARCARDS.add(i); n += 1
    return n
log.append('ears: %d extra bend steps pulling the nearest cards over still-visible ear points' % cover_ears())
log.append('ear coverage after step 1 (front, side): %s' % ear_coverage(co))
# 2. length: sides to the chin (tip z ~ SIDE_Z), back to the collar (BACK_Z), layered ---------------------------------------
k = np.ones(N); n = 0
for i in range(N):
    w = smoothstep(40, 55, caz[i]) * (1 - smoothstep(24, 36, cel[i]))
    if w < 0.05: continue
    T, R = tr(i)
    if not hanging(T, R): continue
    back = smoothstep(135, 160, caz[i]); target = SIDE_Z * (1 - back) + BACK_Z * back
    target += 0.006 * lobe(i, 10.0, 1.0)                              # layered ends, no straight shelf
    if abs(T[2] - target) < 0.004: continue
    kk = (R[2] - target) / max(R[2] - T[2], 1e-3)
    k[i] = clamp_k(i, 1 + (float(np.clip(kk, 0.85, 1.15)) - 1) * w); n += 1
co = C.scale_about_root(co, k)
log.append('   ear coverage now %s' % ear_coverage(co))
log.append('length: %d side/back cards toward chin (%.3f) / collar (%.3f) (k %.2f-%.2f)' % (n, SIDE_Z, BACK_Z, k.min(), k.max()))
# 3. front: one thick wave from the part to his left brow / temple; the centre of the forehead open ----------------------
TEMPLE_L = np.array((0.088, -0.078, 1.703)); n = 0
for i in range(N):
    T, R = tr(i)
    sweep = (saz[i] < 2 and saz[i] > -45) or (saz[i] >= 2 and saz[i] < 38 and T[0] > 0.0)
    if not (sweep and 8 < cel[i] < 55 and hanging(T, R)): continue
    if T[1] < -0.06 and T[2] < 1.76:
        if T[2] < 1.706: scale_one(i, (R[2] - 1.706) / max(R[2] - T[2], 1e-3)); T, R = tr(i)   # lowest point = brow
        s, q, nrm = head.signed(T[None])
        bend_toward(co, C, i, T + nrm[0] * 0.10, math.radians(13), tpow=0.8)                      # mid-length bulge (thick, airy wave)
        bend_toward(co, C, i, TEMPLE_L, math.radians(14), tpow=1.3)                                # to his left temple
        T, R = tr(i); bend_toward(co, C, i, T + np.array((0.0, 0.08, -0.01)), math.radians(12), tpow=2.2); n += 1   # tip turns back over the ear
log.append('front wave: %d sweep-side cards: brow height, mid bulge, guided to his left temple and turned back' % n)
n = 0
for i in range(N):
    if not (-62 < saz[i] < -28 and 6 < cel[i] < 32): continue          # his left temple / in front of the ear
    T, R = tr(i)
    if not hanging(T, R) or T[1] > -0.085 or i in EARCARDS: continue
    bend_toward(co, C, i, np.array((T[0], -0.070, T[2])), math.radians(8), tpow=1.3); n += 1   # back to the eye line
log.append('his left temple: %d cards hanging forward of the eye line turned back' % n)
# his right of the part: a thick lock swoops down the right temple in front of the ear (tip z 1.68-1.70, |x| >= 0.07)
LOCK_R = np.array((-0.090, -0.088, 1.688)); n = 0; m = 0
for i in range(N):
    if not (3 < saz[i] < 48 and 8 < cel[i] < 55): continue
    T, R = tr(i)
    if T[0] > -0.01 or not hanging(T, R) or T[2] > 1.75 or T[1] > -0.06: continue      # hanging on his right forehead/temple
    if T[0] < -0.045 or saz[i] > 22:                                                     # already at the temple: make the lock
        if T[2] > 1.70: scale_one(i, min(1.25, (R[2] - 1.695) / max(R[2] - T[2], 1e-3))); T, R = tr(i)
        bend_toward(co, C, i, LOCK_R, math.radians(13), tpow=1.0); n += 1
    else:                                                                                 # near the centre: open the forehead
        bend_toward(co, C, i, T + np.array((-0.04, 0.08, 0.05)), math.radians(18), tpow=1.3); m += 1
log.append('   ear coverage now %s' % ear_coverage(co))
log.append('right temple lock: %d cards lengthened/curved down the temple; %d centre-forehead cards swept back' % (n, m))
# 4. volume: tall airy top, side mass widest at cheek/jaw level ------------------------------------------------------------
n = 0
for i in range(N):
    if cel[i] < 35 or (caz[i] < 40 and cel[i] < 50): continue             # the fringe is handled above
    T, R = tr(i); s, q, nrm = head.signed(T[None])
    L = max(np.linalg.norm(T - R), 1e-3)
    if s[0] < 0.028:
        bend_toward(co, C, i, T + nrm[0] * 0.10, math.radians(TOP_LIFT * (0.7 + 0.6 * rng.random())) * smoothstep(35, 50, cel[i]), tpow=1.2); n += 1
    T, R = tr(i); s, q, nrm = head.signed(T[None])
    if s[0] > 0.026: bend_toward(co, C, i, q[0], min(math.radians(12), math.atan2(s[0] - 0.022, L)), tpow=2.5)   # no spikes: stray tips back toward the scalp
log.append('   ear coverage now %s' % ear_coverage(co))
log.append('top: %d cards lifted %.0f deg (x0.7-1.3) off the scalp on the mid-length; stray tips > 26 mm tilted back' % (n, TOP_LIFT))
n = 0
for i in range(N):
    w = bump(caz[i], 48, 135, 15) * (1 - smoothstep(30, 40, cel[i]))
    if w < 0.05: continue
    T, R = tr(i)
    if not hanging(T, R): continue
    s, q, nrm = head.signed(T[None]); L = max(np.linalg.norm(T - R), 1e-3)
    if cel[i] > 28 and i not in EARCARDS:                               # temple zone (above the ear cover): 20-25 mm
        want = TEMPLE_FULL
        if s[0] > want + 0.006: bend_toward(co, C, i, q[0], min(math.radians(18), math.atan2(s[0] - want, L)) * w, tpow=1.2); n += 1
        elif s[0] < want - 0.006: bend_toward(co, C, i, T + nrm[0] * 0.08, min(math.radians(12), math.atan2(want - s[0], L)) * w, tpow=1.3); n += 1
    elif cel[i] <= 16:                                                  # cheek/jaw level: 38-45 mm, his left fuller
        want = JAW_FULL + (0.004 if saz[i] < 0 else 0.0)
        if s[0] < want - 0.004: bend_toward(co, C, i, T + nrm[0] * 0.10, min(math.radians(18), math.atan2(want - s[0], L) * 1.2) * w, tpow=1.3); n += 1
        elif s[0] > want + 0.010: bend_toward(co, C, i, q[0], min(math.radians(16), math.atan2(s[0] - want - 0.006, L)) * w, tpow=1.2); n += 1
log.append('   ear coverage now %s' % ear_coverage(co))
log.append('side volume: %d cards (temples %.0f mm, cheek/jaw %.0f mm, his left +4 mm)' % (n, TEMPLE_FULL * 1e3, JAW_FULL * 1e3))
# 5. ends: thick outward-and-under curls in lobes --------------------------------------------------------------------------
n = 0
for i in range(N):
    w = smoothstep(38, 52, caz[i]) * (1 - smoothstep(14, 30, cel[i]))
    if w < 0.05: continue
    T, R = tr(i)
    if not hanging(T, R): continue
    s, q, nrm = head.signed(T[None])
    amp = CURL_DEG * (0.75 + 0.25 * lobe(i, 6.5, 2.0))                 # 10-18 deg, grouped
    bend_toward(co, C, i, T + nrm[0] * 0.08, math.radians(amp) * w, tpow=3.0)               # lowest ~35 %: outward
    T, R = tr(i); bend_toward(co, C, i, T - nrm[0] * 0.06 + np.array((0, 0, -0.02)), math.radians(0.7 * amp) * w, tpow=7.0); n += 1   # last ~15 %: under
log.append('   ear coverage now %s' % ear_coverage(co))
log.append('ends: %d cards curled outward %.0f deg (x0.75-1.0, t^3) and under (t^7)' % (n, CURL_DEG))
# 6. waves: strong grouped S-waves (two bends per card) ------------------------------------------------------------------
n = 0
for i in range(N):
    w = smoothstep(28, 45, caz[i]) * (1 - smoothstep(30, 44, cel[i]))
    if w < 0.05: continue
    T, R = tr(i)
    if not hanging(T, R): continue
    lb = lobe(i, 7.5, 0.0)
    yaw_card(co, C, i, math.radians(WAVE_DEG) * lb * w, tpow=1.8)       # first bend, mid-length
    yaw_card(co, C, i, -math.radians(0.8 * WAVE_DEG) * lb * w, tpow=4.0)   # counter bend on the lower part
    n += 1
log.append('   ear coverage now %s' % ear_coverage(co))
log.append('waves: %d cards, grouped yaw +-%.0f deg (t^1.8) with counter yaw (t^4)' % (n, WAVE_DEG))
# 7. back: layered, no shelf ---------------------------------------------------------------------------------------------
k2 = np.ones(N); n = 0
for i in range(N):
    w = smoothstep(125, 150, caz[i]) * (1 - smoothstep(5, 25, cel[i]))
    if w < 0.05: continue
    k2[i] = clamp_k(i, 1 + 0.05 * (math.sin(saz[i] / 12.0) * 0.5 + math.sin(C.card_root[i][2] * 110.0) * 0.5) * w); n += 1
co = C.scale_about_root(co, k2)
log.append('back layers: %d cards +-5%% low-frequency modulation' % n)
log.append('ears (final pass): %d extra bend steps' % cover_ears())
# ear-cover cards must still read as part of the side mass: tips further than 32 mm from the skin are folded back in
n = 0
for i in EARCARDS:
    T, R = tr(i); s_, q, nrm = head.signed(T[None]); L = max(np.linalg.norm(T - R), 1e-3)
    if s_[0] > 0.032: bend_toward(co, C, i, q[0], min(math.radians(22), math.atan2(s_[0] - 0.026, L)), tpow=1.5); n += 1
log.append('ear cards compacted: %d tips > 32 mm off the skin folded back in' % n)
n = 0
for i in range(N):
    if cel[i] < 42: continue
    T, R = tr(i); s_, q, nrm = head.signed(T[None]); L = max(np.linalg.norm(T - R), 1e-3)
    if s_[0] > 0.024: bend_toward(co, C, i, q[0], min(math.radians(12), math.atan2(s_[0] - 0.020, L)), tpow=2.0); n += 1
log.append('top silhouette: %d stray tips > 24 mm tilted back toward the scalp' % n)
# guards -----------------------------------------------------------------------------------------------------------------
n = 0
for i in range(N):
    for it in range(6):
        p = co[C.card_idx[i]]
        if not ((p[:, 2] < 1.715) & (p[:, 1] < -0.105) & (np.abs(p[:, 0]) < 0.05)).any(): break
        T, R = tr(i); bend_toward(co, C, i, T + np.array((0, 0.04, 0.08)), math.radians(8), tpow=1.3); n += 1
log.append('eye-zone enforcement: %d bend steps' % n)
co, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
log.append('head collision (smooth): %d vertex moves' % pushed)
rows1 = build_cards(co, G['hair_faces'], G['hair_uv']); ratio = np.array([r['length'] for r in rows1]) / np.maximum(L0, 1e-6)
viol = int(((co[:, 2] < 1.715) & (co[:, 1] < -0.105) & (np.abs(co[:, 0]) < 0.05)).sum())
log.append('final: ear coverage (front, side) %s; eye-zone violations %d; length ratio vs original min %.2f max %.2f' % (ear_coverage(co), viol, ratio.min(), ratio.max()))
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_%s.npz' % OUTN), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': OUTN, 'mirrored': False, 'log': log}))
print('\n'.join(log)); d = np.linalg.norm(co - P['hair_co'], axis=1); print('displacement vs %s: mean %.4f max %.4f' % (SRC, d.mean(), d.max()))
