"""NumPy hair-card deformation toolkit (no bpy). Works on the arrays exported by 04_export_npz.py.
Every operation keeps vertex order, topology and UVs untouched: only positions change.
"""
import numpy as np, json, math
try:
    from scipy.spatial import cKDTree
except Exception:
    class cKDTree:   # brute-force fallback (head has ~4k verts, fine)
        def __init__(self, co): self.co = co
        def query(self, p):
            p = np.atleast_2d(p); idx = np.empty(len(p), int); dist = np.empty(len(p))
            for s in range(0, len(p), 2048):
                d = ((p[s:s+2048, None, :] - self.co[None, :, :]) ** 2).sum(-1)
                idx[s:s+2048] = d.argmin(1); dist[s:s+2048] = np.sqrt(d.min(1))
            return dist, idx

FRONT = np.array((0., -1., 0.)); UP = np.array((0., 0., 1.)); RIGHT = np.cross(FRONT, UP)   # (-1,0,0)
CENTER = np.array((0., -0.03, 1.69))

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

def bump(x, lo, hi, soft):
    """1 inside [lo,hi], smooth falloff of width `soft` outside."""
    return smoothstep(lo - soft, lo, x) * (1 - smoothstep(hi, hi + soft, x))

def ang_bump(az, c, half, soft):
    d = (az - c + 180) % 360 - 180
    return bump(np.abs(d), -1, half, soft)

class Head:
    """Approximate signed distance to the head surface using nearest head vertex + its normal."""
    def __init__(self, co, nrm):
        self.co = co; self.nrm = nrm; self.tree = cKDTree(co)
    def nearest(self, p):
        d, i = self.tree.query(p); return self.co[i], self.nrm[i], d
    def signed(self, p):
        q, n, d = self.nearest(p); return np.einsum('ij,ij->i', p - q, n), q, n

class Cards:
    def __init__(self, co, rows, uv_v=None):
        self.co0 = co.copy(); self.rows = rows
        self.n = len(co)
        self.card_of = np.full(self.n, -1); self.t = np.zeros(self.n)
        self.root = np.zeros((self.n, 3)); self.cid = np.zeros(self.n, int)
        self.az = np.zeros(self.n); self.el = np.zeros(self.n)
        for r in rows:
            idx = np.array(r['verts']); self.card_of[idx] = r['id']
            v = uv_v[idx] if uv_v is not None else None
            if v is not None and (r['v1'] - r['v0']) > 1e-6:
                self.t[idx] = (r['v1'] - v) / (r['v1'] - r['v0'])
            else:
                # fall back: distance from root along card direction
                d = np.array(r['dir']); self.t[idx] = np.clip(((co[idx] - np.array(r['root'])) @ d) / max(r['length'], 1e-6), 0, 1)
            self.root[idx] = r['root']; self.az[idx] = r['az']; self.el[idx] = r['el']
        self.card_az = np.array([r['az'] for r in rows]); self.card_el = np.array([r['el'] for r in rows])
        self.card_root = np.array([r['root'] for r in rows]); self.card_len = np.array([r['length'] for r in rows])
        self.card_idx = [np.array(r['verts']) for r in rows]

    # ---- helpers -------------------------------------------------------------------------------------
    def card_weight(self, fn):
        """fn(az, el, root) -> per-card weight; returns per-vertex weights."""
        w = fn(self.card_az, self.card_el, self.card_root)
        out = np.zeros(self.n)
        for i, idx in enumerate(self.card_idx): out[idx] = w[i]
        return out

    def scale_about_root(self, co, k_card):
        """k_card: per-card scale factor (1 = unchanged). Uniform scale of the card about its root."""
        out = co.copy()
        for i, idx in enumerate(self.card_idx):
            if abs(k_card[i] - 1) < 1e-6: continue
            R = co[idx][self.t[idx].argmin()]  # current root vertex (roots never move → use current)
            out[idx] = R + (co[idx] - R) * k_card[i]
        return out

    def rotate_about_root(self, co, axis_card, angle_card, tpow=1.0):
        """Rotate each card's vertices about an axis through its root; angle grows with t**tpow (0 at root)."""
        out = co.copy()
        for i, idx in enumerate(self.card_idx):
            a = angle_card[i]
            if abs(a) < 1e-6: continue
            ax = axis_card[i] / (np.linalg.norm(axis_card[i]) + 1e-12)
            R = co[idx][self.t[idx].argmin()]
            p = co[idx] - R; th = a * (self.t[idx] ** tpow)
            c, s = np.cos(th)[:, None], np.sin(th)[:, None]
            out[idx] = R + p * c + np.cross(ax, p) * s + ax * (p @ ax)[:, None] * (1 - c)
        return out

    def displace(self, co, vec_per_vertex, w_per_vertex):
        return co + vec_per_vertex * w_per_vertex[:, None]

def card_frames(co, cards):
    """Per card: current root, tip, direction (root->tip) and the width axis of the card."""
    roots, tips, dirs, widths = [], [], [], []
    for idx in cards.card_idx:
        t = cards.t[idx]; p = co[idx]
        r = p[t <= t.min() + 1e-6].mean(0); tp = p[t >= t.max() - 1e-6].mean(0)
        d = tp - r; L = np.linalg.norm(d) + 1e-9; d = d / L
        # width axis: principal direction of the root row, orthogonal to d
        rr = p[t <= t.min() + 1e-6]
        if len(rr) >= 2:
            w = rr[-1] - rr[0]
        else:
            w = np.cross(d, UP)
        w = w - d * (w @ d); w = w / (np.linalg.norm(w) + 1e-9)
        roots.append(r); tips.append(tp); dirs.append(d); widths.append(w)
    return np.array(roots), np.array(tips), np.array(dirs), np.array(widths)

def radial_from_center(p, center=CENTER):
    v = p - center; v[:, 2] *= 0.6   # ellipsoidal head approximation
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)

def resolve_head_collision(co, head, clearance, w=None, iters=2):
    """Push vertices that are inside the head (or closer than `clearance`) outward along the head normal.
    `clearance` may be a per-vertex array: use np.minimum(original_signed_distance, 0.004) so that intersections the
    shipped asset already had (the cap/head overlap) are tolerated, but no vertex moves closer to the skin than it was."""
    out = co.copy(); pushed = 0
    for _ in range(iters):
        s, q, n = head.signed(out)
        bad = s < clearance
        if w is not None: bad &= (w > 0)
        if not bad.any(): break
        cl = clearance[bad] if np.ndim(clearance) else clearance
        out[bad] += n[bad] * (cl - s[bad])[:, None]; pushed += bad.sum()
    return out, pushed

def taper_variation(seed, n, amp):
    rng = np.random.default_rng(seed); return 1 + amp * (rng.random(n) * 2 - 1)

def hash_noise(x, seed=0):
    """Deterministic smooth-ish per-card noise in [-1,1] from a scalar (e.g. azimuth)."""
    return np.sin(x * 0.173 + seed * 1.7) * 0.6 + np.sin(x * 0.051 + seed * 0.3) * 0.4

# ---------------------------------------------------------------------------------------------------
def build_cards(co, faces, uv, center=CENTER, front=FRONT):
    """NumPy re-implementation of cards.card_table (islands from faces, root = max v, tip = min v)."""
    n = len(co); parent = np.arange(n)
    def f(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for tri in faces:
        for x, y in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])):
            ra, rb = f(x), f(y)
            if ra != rb: parent[ra] = rb
    roots = np.array([f(i) for i in range(n)])
    groups = {}
    for i, r in enumerate(roots): groups.setdefault(r, []).append(i)
    right = np.cross(front, UP)
    rows = []
    for ci, comp in enumerate(sorted(groups.values(), key=lambda c: c[0])):
        idx = np.array(comp); c = co[idx]; u = uv[idx]
        vmax, vmin = u[:, 1].max(), u[:, 1].min()
        root = c[u[:, 1] >= vmax - 1e-4].mean(0); tip = c[u[:, 1] <= vmin + 1e-4].mean(0)
        d = tip - root; L = float(np.linalg.norm(d))
        rel = root - center
        az = math.degrees(math.atan2(rel @ right, rel @ front)); el = math.degrees(math.atan2(rel[2], np.linalg.norm(rel[:2])))
        rows.append({'id': ci, 'verts': comp, 'n': len(comp), 'root': root.tolist(), 'tip': tip.tolist(), 'length': L,
                     'dir': (d / max(L, 1e-9)).tolist(), 'az': az, 'el': el, 'u0': float(u[:, 0].min()), 'u1': float(u[:, 0].max()),
                     'v0': float(vmin), 'v1': float(vmax)})
    return rows

def scalp_normals(co, cap_co, cap_nrm):
    """Scalp-transferred normals: nearest deformed-cap vertex normal (the technique used by the original asset)."""
    t = cKDTree(cap_co); d, i = t.query(co); return cap_nrm[i]

def vertex_normals(co, faces):
    n = np.zeros_like(co)
    a, b, c = co[faces[:, 0]], co[faces[:, 1]], co[faces[:, 2]]
    fn = np.cross(b - a, c - a)
    for k in range(3): np.add.at(n, faces[:, k], fn)
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)

# ---------------------------------------------------------------------------------------------------
def bend_toward(co, cards, i, target, angle, tpow=1.0, max_angle=None):
    """Bend card i so that its tip moves toward `target` (a point): rotation about an axis through the root,
    axis = dir x (target-root); angle grows with t**tpow so the root row stays fixed."""
    idx = cards.card_idx[i]; p = co[idx]; t = cards.t[idx]
    R = p[t <= t.min() + 1e-6].mean(0); T = p[t >= t.max() - 1e-6].mean(0)
    d = T - R; L = np.linalg.norm(d)
    if L < 1e-6: return
    d /= L; u = np.asarray(target, float) - R; nu = np.linalg.norm(u)
    if nu < 1e-6: return
    u /= nu
    ax = np.cross(d, u); na = np.linalg.norm(ax)
    if na < 1e-6: return
    ax /= na
    full = math.acos(np.clip(d @ u, -1, 1))          # angle needed to point exactly at the target
    a = min(angle, full) if angle >= 0 else max(angle, -full)
    if max_angle is not None: a = float(np.clip(a, -max_angle, max_angle))
    q = p - R; th = a * (t ** tpow)
    c, s = np.cos(th)[:, None], np.sin(th)[:, None]
    co[idx] = R + q * c + np.cross(ax, q) * s + ax * (q @ ax)[:, None] * (1 - c)

def yaw_card(co, cards, i, angle, tpow=1.0):
    """Rotate card i about the vertical axis through its root (tip swings horizontally)."""
    idx = cards.card_idx[i]; p = co[idx]; t = cards.t[idx]
    R = p[t <= t.min() + 1e-6].mean(0); q = p - R; th = angle * (t ** tpow)
    c, s = np.cos(th), np.sin(th)
    x, y = q[:, 0], q[:, 1]
    co[idx] = R + np.stack([x * c - y * s, x * s + y * c, q[:, 2]], 1)

def card_tip_root(co, cards, i):
    idx = cards.card_idx[i]; p = co[idx]; t = cards.t[idx]
    return p[t >= t.max() - 1e-6].mean(0), p[t <= t.min() + 1e-6].mean(0)

# ---------------------------------------------------------------------------------------------------
def resolve_head_collision_smooth(co, cards, head, clearance, iters=3, window=0.12):
    """Like resolve_head_collision but the push amount is dilated along each card (max over neighbours within
    `window` in t) so a card that touches the head/ear lifts as a smooth sheet instead of crumpling per vertex."""
    out = co.copy(); total = 0
    for _ in range(iters):
        s, q, n = head.signed(out)
        need = np.maximum(0, clearance - s)          # required outward push per vertex
        if need.max() <= 1e-6: break
        push = np.zeros(len(out))
        for idx in cards.card_idx:
            nd = need[idx]
            if nd.max() <= 1e-6: continue
            t = cards.t[idx]
            # dilated max along the card
            fall = np.clip(1 - np.abs(t[:, None] - t[None, :]) / window, 0, 1)   # linear falloff along the card
            push[idx] = (nd[None, :] * fall).max(1) * smoothstep(0.0, 0.1, t)     # roots stay put
        moved = push > 1e-6
        out[moved] += n[moved] * push[moved][:, None]; total += moved.sum()
    return out, total

# ---------------------------------------------------------------------------------------------------
class HeadMesh:
    """Triangle-accurate closest point + signed distance (sign from the face normal of the closest triangle,
    falling back to the angle-weighted vertex normal near edges/vertices). Requires consistent winding."""
    def __init__(self, co, faces, vnrm, fnrm=None, k=10):
        self.co = co; self.faces = faces; self.vn = vnrm; self.k = k
        if fnrm is None:
            fnrm = np.cross(co[faces[:, 1]] - co[faces[:, 0]], co[faces[:, 2]] - co[faces[:, 0]]); fnrm /= np.linalg.norm(fnrm, axis=1, keepdims=True) + 1e-12
        self.fn = fnrm
        self.tree = cKDTree(co)
        inc = [[] for _ in range(len(co))]
        for fi, f in enumerate(faces):
            for v in f: inc[v].append(fi)
        self.inc = inc
    @staticmethod
    def _closest_on_tris(p, a, b, c):
        # Ericson, Real-Time Collision Detection, closest point on triangle (vectorised over triangles)
        ab = b - a; ac = c - a; ap = p - a
        d1 = (ab * ap).sum(1); d2 = (ac * ap).sum(1)
        out = np.empty_like(a); done = np.zeros(len(a), bool)
        m = (d1 <= 0) & (d2 <= 0); out[m] = a[m]; done |= m
        bp = p - b; d3 = (ab * bp).sum(1); d4 = (ac * bp).sum(1)
        m = (~done) & (d3 >= 0) & (d4 <= d3); out[m] = b[m]; done |= m
        vc = d1 * d4 - d3 * d2
        m = (~done) & (vc <= 0) & (d1 >= 0) & (d3 <= 0)
        v = np.where((d1 - d3) != 0, d1 / np.where((d1 - d3) != 0, d1 - d3, 1), 0); out[m] = (a + ab * v[:, None])[m]; done |= m
        cp = p - c; d5 = (ab * cp).sum(1); d6 = (ac * cp).sum(1)
        m = (~done) & (d6 >= 0) & (d5 <= d6); out[m] = c[m]; done |= m
        vb = d5 * d2 - d1 * d6
        m = (~done) & (vb <= 0) & (d2 >= 0) & (d6 <= 0)
        w = np.where((d2 - d6) != 0, d2 / np.where((d2 - d6) != 0, d2 - d6, 1), 0); out[m] = (a + ac * w[:, None])[m]; done |= m
        va = d3 * d6 - d5 * d4
        m = (~done) & (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)
        den = (d4 - d3) + (d5 - d6); w = np.where(den != 0, (d4 - d3) / np.where(den != 0, den, 1), 0); out[m] = (b + (c - b) * w[:, None])[m]; done |= m
        den = va + vb + vc; den = np.where(den != 0, den, 1); v = vb / den; w = vc / den
        m = ~done; out[m] = (a + ab * v[:, None] + ac * w[:, None])[m]
        return out
    def signed(self, p):
        p = np.atleast_2d(p); n = len(p)
        d, kn = self.tree.query(p, k=self.k)
        res_q = np.zeros((n, 3)); res_n = np.zeros((n, 3)); res_s = np.zeros(n)
        for i in range(n):
            cand = sorted({f for v in kn[i] for f in self.inc[v]})
            F = self.faces[cand]; a, b, c = self.co[F[:, 0]], self.co[F[:, 1]], self.co[F[:, 2]]
            q = self._closest_on_tris(p[i][None].repeat(len(F), 0), a, b, c)
            dd = np.linalg.norm(q - p[i], axis=1); j = dd.argmin()
            nf = self.fn[cand[j]]; vec = p[i] - q[j]
            # near a vertex/edge the face normal can mis-sign; blend with the nearest vertex normal
            nv = self.vn[kn[i][0]]; nn = nf + nv; nn /= np.linalg.norm(nn) + 1e-12
            sgn = 1.0 if (vec @ nn) >= 0 else -1.0
            res_q[i] = q[j]; res_n[i] = nf if (nf @ nn) > 0 else nn; res_s[i] = sgn * dd[j]
        return res_s, res_q, res_n
