import sys, os
from PIL import Image, ImageDraw
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); stage = sys.argv[1]; H = 900
ref = Image.open(os.path.join(PROJ, 'references', 'ref_target_promo_front.jpg')).convert('RGB').crop((150, 60, 590, 520)); ref = ref.resize((int(ref.size[0] * H / ref.size[1]), H))
tiles = [(ref, 'TARGET promo photo')]
for v in ('front', 'three_quarter', 'right', 'left'):
    im = Image.open(os.path.join(PROJ, 'renders', stage, '%s_%s.png' % (stage, v))).convert('RGB').crop((230, 100, 794, 690)); tiles.append((im.resize((int(564 * H / 590), H), Image.LANCZOS), stage + ' ' + v))
W = sum(t.size[0] for t, _ in tiles); s = Image.new('RGB', (W, H + 24), 'black'); d = ImageDraw.Draw(s); x = 0
for t, lab in tiles: s.paste(t, (x, 24)); d.text((x + 6, 4), lab, fill='yellow'); x += t.size[0]
out = os.path.join(PROJ, 'renders', stage, stage + '_vs_promo.jpg'); s.save(out, quality=90); print(out)
