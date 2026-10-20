"""Variant 8 — narrower sides (both sides, the two boxes the user drew on the variant 7c front view), after
references/ref_target_rots_portrait_front_b.jpg: the side mass hugs the cheeks, ~25-30 mm off the skin at jaw level.
Base: stage Hr (variant 7c). Region: hanging cards with |azimuth| 40-140 deg, elevation < 40 deg (the side masses from
the temples down); every other card is asserted bit-identical to Hr. Only bends toward the skin (no scaling), roots fixed."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('SRC', 'Hr'); OUTN = os.environ.get('OUTN', 'J')
def env(k, d): return float(os.environ.get(k, d))
WANT_TIP = env('WANT_TIP', 0.026); WANT_MID = env('WANT_MID', 0.024); WANT_TEMPLE = env('WANT_TEMPLE', 0.020)
AZ0, AZ1, EL1 = 40.0, 140.0, 40.0
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); P = np.load(os.path.join(PROJ, 'working', 'positions_%s.npz' % SRC))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = P['hair_co'].copy(); co_src = P['hair_co'].copy(); cap = P['cap_co']; capn = P['cap_nrm']; assert not bool(json.loads(str(P['meta']))['mirrored'])
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
L0 = np.array([r['length'] for r in build_cards(G['hair_co'], G['hair_faces'], G['hair_uv'])])
caz = np.abs(C.card_az); cel = C.card_el; N = len(rows); log = []
s_orig, _, _ = head.signed(G['hair_co']); clear = np.minimum(s_orig, 0.004)
FACES = G['hair_faces']
def tr(i): return card_tip_root(co, C, i)
def ray_hits(co, origins, d):
    a, b, c = co[FACES[:, 0]], co[FACES[:, 1]], co[FACES[:, 2]]
    e1 = b - a; e2 = c - a; pv = np.cross(d, e2); det = (e1 * pv).sum(1); ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0); hits = []
    for o in origins:
        tv = o - a; u = (tv * pv).sum(1) * inv; qv = np.cross(tv, e1); v = (d * qv).sum(1) * inv; t = (e2 * qv).sum(1) * inv
        hits.append(int((ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0.002)).sum()))
    return np.array(hits)
EAR_Y = (-0.049, -0.019); EAR_Z = (1.646, 1.714)
def ear_coverage(co, min_hits=3):
    out = {}
    for sgn, name in ((-1, 'his_right'), (+1, 'his_left')):
        pts = [(y, z) for y in np.linspace(*EAR_Y, 4) for z in np.linspace(*EAR_Z, 6)]
        front = ray_hits(co, np.array([(sgn * 0.088, EAR_Y[0], z) for y, z in pts]), np.array((0., -1., 0.)))
        side = ray_hits(co, np.array([(sgn * 0.100, y, z) for y, z in pts]), np.array((sgn * 1., 0., 0.)))
        out[name] = (round(float((front >= min_hits).mean()), 2), round(float((side >= min_hits).mean()), 2))
    return out
def width_profile(co):
    out = {}
    for sgn, name in ((-1, 'his_right'), (+1, 'his_left')):
        b = (co[:, 2] > 1.58) & (co[:, 2] < 1.66) & (np.sign(co[:, 0]) == sgn); hb = (G['head_co'][:, 2] > 1.58) & (G['head_co'][:, 2] < 1.66) & (np.sign(G['head_co'][:, 0]) == sgn)
        out[name] = round(float((np.abs(co[b, 0]).max() - np.abs(G['head_co'][hb, 0]).max()) * 1000))
    return out
log.append('start: ear coverage (front, side) %s; side width beyond the head at z 1.58-1.66 (mm) %s' % (ear_coverage(co), width_profile(co)))
# region ---------------------------------------------------------------------------------------------------------------
region = [i for i in range(N) if AZ0 < caz[i] < AZ1 and cel[i] < EL1 and tr(i)[0][2] < tr(i)[1][2] - 0.02]
region_v = np.zeros(len(co), bool)
for i in region: region_v[C.card_idx[i]] = True
log.append('region: %d cards (both sides, |az| %.0f-%.0f, el < %.0f, hanging), %d vertices' % (len(region), AZ0, AZ1, EL1, region_v.sum()))
# narrow: bring the mid-length and the tip toward the skin ---------------------------------------------------------------
n = 0
for it in range(4):
    for i in region:
        idx = C.card_idx[i]; T, R = tr(i); L = max(np.linalg.norm(T - R), 1e-3)
        want_t = WANT_TEMPLE if cel[i] > 24 else WANT_TIP; want_m = WANT_TEMPLE if cel[i] > 24 else WANT_MID
        mid = co[idx][np.argmin(np.abs(C.t[idx] - 0.6))]; sm, qm, nm = head.signed(mid[None])
        if sm[0] > want_m + 0.003:
            bend_toward(co, C, i, qm[0], min(math.radians(14), math.atan2(sm[0] - want_m, 0.6 * L)), tpow=0.9); n += 1
        T, R = tr(i); s, q, nrm = head.signed(T[None])
        if s[0] > want_t + 0.003:
            bend_toward(co, C, i, q[0], min(math.radians(14), math.atan2(s[0] - want_t, L)), tpow=1.3); n += 1
log.append('narrow: %d bend steps (tips toward %.0f mm, mid-length toward %.0f mm, temples %.0f mm; <= 14 deg per step, 4 passes)' % (n, WANT_TIP * 1e3, WANT_MID * 1e3, WANT_TEMPLE * 1e3))
# collision for the region's cards only ----------------------------------------------------------------------------------
co2, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
moved = region_v & (np.abs(co2 - co).max(1) > 0); co[moved] = co2[moved]
log.append('head collision (smooth, region only): %d vertex moves' % int(moved.sum()))
d = np.linalg.norm(co - co_src, axis=1)
assert d[~region_v].max() == 0.0, 'a card outside the region moved'
viol = int(((co[:, 2] < 1.715) & (co[:, 1] < -0.105) & (np.abs(co[:, 0]) < 0.05)).sum())
rows1 = build_cards(co, G['hair_faces'], G['hair_uv']); ratio = np.array([r['length'] for r in rows1]) / np.maximum(L0, 1e-6)
sT = np.array([head.signed(tr(i)[0][None])[0][0] for i in region]) * 1000
log.append('final: ear coverage %s; side width beyond the head (mm) %s; region tip-to-skin median %.0f max %.0f mm; outside the region 0 vertices moved; region displacement mean %.1f max %.1f mm; eye-zone violations %d; length ratio %.2f-%.2f'
           % (ear_coverage(co), width_profile(co), np.median(sT), sT.max(), d[region_v].mean() * 1000, d.max() * 1000, viol, ratio.min(), ratio.max()))
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_%s.npz' % OUTN), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': OUTN, 'mirrored': False, 'src': SRC, 'region_cards': [int(i) for i in region], 'log': log}))
print('\n'.join(log))
