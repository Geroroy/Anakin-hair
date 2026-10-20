"""Variant 7c — his RIGHT side ends only (the region the user circled on the variant 7 front view), re-laid as in the
Episode III promo portrait: jaw/chin length, rounded bob silhouette, soft outward C-curve at the ends in thick clumps.
Base: stage H (variant 7). Region: hanging cards with azimuth +45..+135 deg (his right, x<0), elevation < 22 deg,
tip z < 1.635. Every other card is asserted bit-identical to H. No mirror, roots fixed, scale clamped 0.80-1.35x."""
import numpy as np, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deform import *
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('SRC', 'H'); OUTN = os.environ.get('OUTN', 'Hr')
def env(k, d): return float(os.environ.get(k, d))
TIP_Z = env('TIP_Z', 1.590); FULL = env('FULL', 0.036); CURVE = env('CURVE', 20.0); UNDER = env('UNDER', 10.0); CLUMP = env('CLUMP', 6.0); TIPCAP = env('TIPCAP', 0.042)
AZ0, AZ1, EL1, TIPZ0 = 45.0, 135.0, 22.0, 1.635
G = np.load(os.path.join(PROJ, 'working', 'geometry_original.npz')); P = np.load(os.path.join(PROJ, 'working', 'positions_%s.npz' % SRC))
head = HeadMesh(G['head_co'], G['head_faces'], G['head_nrm'], G['head_fnrm'])
co = P['hair_co'].copy(); co_src = P['hair_co'].copy(); cap = P['cap_co']; capn = P['cap_nrm']; assert not bool(json.loads(str(P['meta']))['mirrored'])
rows = build_cards(co, G['hair_faces'], G['hair_uv']); C = Cards(co, rows, uv_v=G['hair_uv'][:, 1])
L0 = np.array([r['length'] for r in build_cards(G['hair_co'], G['hair_faces'], G['hair_uv'])])
saz = C.card_az; cel = C.card_el; N = len(rows); log = []
s_orig, _, _ = head.signed(G['hair_co']); clear = np.minimum(s_orig, 0.004)
UP = np.array((0., 0., 1.))
def tr(i): return card_tip_root(co, C, i)
def clamp_k(i, k):
    L = max(float(np.linalg.norm(np.subtract(*tr(i)))), 1e-6); return float(np.clip(k, 0.80 * L0[i] / L, 1.35 * L0[i] / L))
def scale_one(i, k):
    global co
    k1 = np.ones(N); k1[i] = clamp_k(i, k); co = C.scale_about_root(co, k1)
def lobe(i, period=6.5, seed=2.0): return math.sin(saz[i] / period + C.card_root[i][2] * 80.0 + seed)
def horiz_out(T):
    s, q, nrm = head.signed(T[None]); o = nrm[0] - UP * (nrm[0] @ UP); return s[0], q[0], o / (np.linalg.norm(o) + 1e-9)
# region ---------------------------------------------------------------------------------------------------------------
region = []
for i in range(N):
    T, R = tr(i)
    if AZ0 < saz[i] < AZ1 and cel[i] < EL1 and T[2] < TIPZ0 and T[2] < R[2] - 0.02: region.append(i)
region_v = np.zeros(len(co), bool)
for i in region: region_v[C.card_idx[i]] = True
log.append('region: %d cards (his right, az %.0f-%.0f, el < %.0f, tip z < %.3f), %d vertices' % (len(region), AZ0, AZ1, EL1, TIPZ0, region_v.sum()))
# 1. length: jaw-chin line, layered ------------------------------------------------------------------------------------
n = 0
for i in region:
    T, R = tr(i); target = TIP_Z + 0.008 * lobe(i, 9.0, 1.0)
    if T[2] < target - 0.004:
        scale_one(i, (R[2] - target) / max(R[2] - T[2], 1e-3)); n += 1
log.append('length: %d cards shortened to the jaw-chin line (tip z %.3f +- 8 mm, k >= 0.80)' % (n, TIP_Z))
# 2. rounded bob silhouette: mid-length off the cheek, tips not too far ------------------------------------------------
n = 0
for i in region:
    T, R = tr(i); s, q, out = horiz_out(T); L = max(np.linalg.norm(T - R), 1e-3)
    mid = co[C.card_idx[i]][np.argmin(np.abs(C.t[C.card_idx[i]] - 0.55))]
    sm, qm, nm = head.signed(mid[None])
    if sm[0] < FULL - 0.004: bend_toward(co, C, i, T + out * 0.10, min(math.radians(12), math.atan2(FULL - sm[0], 0.55 * L)), tpow=0.8); n += 1
    T, R = tr(i); s, q, out = horiz_out(T)
    if s > TIPCAP: bend_toward(co, C, i, q, math.atan2(s - TIPCAP + 0.006, L), tpow=1.5)
log.append('silhouette: %d cards lifted so the mid-length sits ~%.0f mm off the cheek; tips kept within %.0f mm' % (n, FULL * 1e3, TIPCAP * 1e3))
# 3. soft outward C-curve at the ends, grouped in lobes; last part turns out-and-under ---------------------------------
n = 0
for i in region:
    T, R = tr(i); s, q, out = horiz_out(T)
    amp = CURVE * (0.85 + 0.15 * lobe(i))
    bend_toward(co, C, i, T + out * 0.10, math.radians(amp), tpow=2.0)                                 # lowest ~40 %: outward
    T, R = tr(i); s, q, out = horiz_out(T)
    bend_toward(co, C, i, T + out * 0.06 - UP * 0.04 + np.array((0, 0.03, 0)), math.radians(UNDER * (amp / CURVE)), tpow=5.0)   # last ~20 %: out, slightly under and back
    n += 1
log.append('ends: %d cards, outward C-curve %.0f deg (x0.85-1.0, t^2) + %.0f deg out-and-under (t^5)' % (n, CURVE, UNDER))
# 4. clumping: yaw the cards of a lobe toward the lobe centre ------------------------------------------------------------
n = 0
for i in region:
    # lobe phase: derivative sign tells which side of the lobe centre the card sits on
    ph = saz[i] / 6.5 + C.card_root[i][2] * 80.0 + 2.0
    toward = -math.cos(ph)                                     # >0: yaw toward +az (his right/back), <0: toward the front
    yaw_card(co, C, i, math.radians(CLUMP) * toward, tpow=1.5); n += 1
log.append('clumping: %d cards yawed up to %.0f deg toward their lobe centre' % (n, CLUMP))
# guards ---------------------------------------------------------------------------------------------------------------
n = 0
for i in region:
    for it in range(4):
        T, R = tr(i); s, q, out = horiz_out(T); L = max(np.linalg.norm(T - R), 1e-3)
        if s <= TIPCAP: break
        bend_toward(co, C, i, q, math.atan2(s - TIPCAP + 0.006, L), tpow=1.5); n += 1
    T, R = tr(i)
    if T[2] < 1.570: scale_one(i, (R[2] - 1.572) / max(R[2] - T[2], 1e-3))
log.append('guards: %d bend steps (tips within %.0f mm of the skin; nothing below z 1.57)' % (n, TIPCAP * 1e3))
co2, pushed = resolve_head_collision_smooth(co, C, head, clearance=clear, iters=3)
moved = region_v & (np.abs(co2 - co).max(1) > 0); co[moved] = co2[moved]
log.append('head collision (smooth, region only): %d vertex moves' % int(moved.sum()))
d = np.linalg.norm(co - co_src, axis=1)
assert d[~region_v].max() == 0.0, 'a card outside the region moved'
rows1 = build_cards(co, G['hair_faces'], G['hair_uv']); ratio = np.array([r['length'] for r in rows1]) / np.maximum(L0, 1e-6)
tips = np.array([tr(i)[0] for i in region]); sT = np.array([horiz_out(t)[0] for t in tips]) * 1000
log.append('final: outside the region 0 vertices moved; region displacement mean %.1f mm max %.1f mm; tip z %.3f-%.3f; tip-to-skin %.0f-%.0f mm; length ratio vs original %.2f-%.2f'
           % (d[region_v].mean() * 1000, d.max() * 1000, tips[:, 2].min(), tips[:, 2].max(), sT.min(), sT.max(), ratio.min(), ratio.max()))
hair_n = scalp_normals(co, cap, capn)
np.savez(os.path.join(PROJ, 'working', 'positions_%s.npz' % OUTN), hair_co=co, hair_nrm=hair_n, cap_co=cap, cap_nrm=capn, meta=json.dumps({'stage': OUTN, 'mirrored': False, 'src': SRC, 'region_cards': [int(i) for i in region], 'log': log}))
print('\n'.join(log))
