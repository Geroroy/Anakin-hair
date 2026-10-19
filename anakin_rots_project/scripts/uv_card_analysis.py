"""Analyse hair-card islands of HairPlanes_M directly from the FBX: UV column usage, root/tip direction, sizes."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fbx_dump import read_fbx, find
from collections import Counter, defaultdict
v, nodes = read_fbx(sys.argv[1])
objs = find(nodes, 'Objects')[0][2]
geo = [o for o in objs if o[0] == 'Geometry' and o[1][1].startswith('HairPlanes_M')][0]
ch = {c[0]: c for c in geo[2]}
V = np.array(ch['Vertices'][1][0]).reshape(-1, 3)
idx = np.array(ch['PolygonVertexIndex'][1][0])
uvn = [c for c in geo[2] if c[0] == 'LayerElementUV'][0]
UV = np.array([cc for cc in uvn[2] if cc[0] == 'UV'][0][1][0]).reshape(-1, 2)
tris = idx.reshape(-1, 3).copy(); tris[:, 2] = -tris[:, 2] - 1
print('verts', len(V), 'tris', len(tris), 'uv per vertex', len(UV))
# union-find islands
parent = list(range(len(V)))
def f(a):
    while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
    return a
for a, b, c in tris:
    for x, y in ((a, b), (b, c), (a, c)):
        ra, rb = f(x), f(y)
        if ra != rb: parent[ra] = rb
isl = defaultdict(list)
for i in range(len(V)): isl[f(i)].append(i)
islands = list(isl.values())
print('islands', len(islands))
cols = Counter(); rows = Counter(); widths = Counter(); heights = []
info = []
for comp in islands:
    uv = UV[comp]; co = V[comp]
    umin, umax = uv.min(0), uv.max(0)
    # root = highest V (top of atlas), tip = lowest V in FBX convention (v=1 top) -> check against world Z
    top = co[uv[:, 1] >= umax[1] - 1e-3]; bot = co[uv[:, 1] <= umin[1] + 1e-3]
    cols[round(umin[0] * 16) / 16] += 1
    widths[round((umax[0] - umin[0]) * 32) / 32] += 1
    heights.append(umax[1] - umin[1])
    length = np.linalg.norm(top.mean(0) - bot.mean(0))
    info.append((len(comp), umin.round(3).tolist(), umax.round(3).tolist(), round(length, 4), round(top.mean(0)[1] - bot.mean(0)[1], 4)))
print('UV column starts (u rounded to 1/16):', sorted(cols.items()))
print('UV widths (rounded 1/32):', sorted(widths.items()))
print('UV height range', min(heights), max(heights), 'mean', np.mean(heights))
L = np.array([i[3] for i in info]); dz = np.array([i[4] for i in info])
print('card length (root->tip, m): min %.3f max %.3f mean %.3f' % (L.min(), L.max(), L.mean()))
print('root minus tip height (Y in FBX = up): min %.3f max %.3f mean %.3f ; fraction with root above tip %.2f' % (dz.min(), dz.max(), dz.mean(), (dz > 0).mean()))
print('vertex-count histogram', sorted(Counter(i[0] for i in info).items()))
print('UV v min overall', UV[:, 1].min(), 'max', UV[:, 1].max(), 'u min', UV[:, 0].min(), 'max', UV[:, 0].max())
# cap
geo = [o for o in objs if o[0] == 'Geometry' and o[1][1].startswith('hair_cap')][0]
uvn = [c for c in geo[2] if c[0] == 'LayerElementUV'][0]
UVc = np.array([cc for cc in uvn[2] if cc[0] == 'UV'][0][1][0]).reshape(-1, 2)
print('cap UV range u', UVc[:, 0].min(), UVc[:, 0].max(), 'v', UVc[:, 1].min(), UVc[:, 1].max())
