"""Photo | base front | stage front, plus left/right views side by side. Run: python3 scripts/compare_sides.py J [base=Hr]"""
import sys, os
from PIL import Image, ImageDraw
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); stage = sys.argv[1]; base = sys.argv[2] if len(sys.argv) > 2 else 'Hr'
H = 820
def rnd(stg, view):
    im = Image.open(os.path.join(PROJ, 'renders', stg, '%s_%s.png' % (stg, view))).convert('RGB').crop((150, 80, 874, 900)); return im.resize((int(724 * H / 820), H), Image.LANCZOS)
ref = Image.open(os.path.join(PROJ, 'references', 'ref_target_rots_portrait_front_b.jpg')).convert('RGB'); ref = ref.resize((int(ref.size[0] * H / ref.size[1]), H), Image.LANCZOS)
tiles = [(ref, 'REFERENCE Episode III portrait'), (rnd(base, 'front'), 'variant 7c (%s) front' % base), (rnd(stage, 'front'), '%s front' % stage),
         (rnd(base, 'right'), '%s right' % base), (rnd(stage, 'right'), '%s right' % stage), (rnd(base, 'left'), '%s left' % base), (rnd(stage, 'left'), '%s left' % stage)]
W = sum(t.size[0] for t, _ in tiles); s = Image.new('RGB', (W, H + 24), 'black'); d = ImageDraw.Draw(s); x = 0
for t, lab in tiles: s.paste(t, (x, 24)); d.text((x + 6, 4), lab, fill='yellow'); x += t.size[0]
out = os.path.join(PROJ, 'renders', stage, '%s_sides_before_after.jpg' % stage); s.save(out, quality=90); print(out)
s2 = Image.new('RGB', (tiles[0][0].size[0] + 2 * tiles[1][0].size[0], H + 24), 'black'); d = ImageDraw.Draw(s2); x = 0
for t, lab in tiles[:3]: s2.paste(t, (x, 24)); d.text((x + 6, 4), lab, fill='yellow'); x += t.size[0]
s2.save(os.path.join(PROJ, 'renders', stage, '%s_sides_front.jpg' % stage), quality=90)
