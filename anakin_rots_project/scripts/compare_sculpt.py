import sys, os
from PIL import Image, ImageDraw
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); stage = sys.argv[1]; H = 1000
ref = Image.open(os.path.join(PROJ, 'references', 'ref_target_sculpt_front.jpg')).convert('RGB').crop((110, 20, 620, 640)); ref = ref.resize((int(ref.size[0] * H / ref.size[1]), H))
tiles = [(ref, 'TARGET sculpt')]
for v in ('front', 'three_quarter', 'left', 'right'):
    im = Image.open(os.path.join(PROJ, 'renders', stage, '%s_%s.png' % (stage, v))).convert('RGB').crop((230, 90, 794, 700)); tiles.append((im.resize((int(564 * H / 610), H), Image.LANCZOS), stage + ' ' + v))
W = sum(t.size[0] for t, _ in tiles); s = Image.new('RGB', (W, H + 24), 'black'); d = ImageDraw.Draw(s); x = 0
for t, lab in tiles: s.paste(t, (x, 24)); d.text((x + 6, 4), lab, fill='yellow'); x += t.size[0]
out = os.path.join(PROJ, 'renders', stage, stage + '_vs_sculpt.jpg'); s.save(out, quality=90)
s2 = Image.new('RGB', (tiles[0][0].size[0] + tiles[1][0].size[0], H)); s2.paste(tiles[0][0], (0, 0)); s2.paste(tiles[1][0], (tiles[0][0].size[0], 0)); s2.save(os.path.join(PROJ, 'renders', stage, stage + '_vs_sculpt_front.jpg'), quality=90)
print(out)
