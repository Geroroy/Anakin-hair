"""Side-by-side of the Ahsoka target frames and the stage renders. Run: python3 scripts/compare_ahsoka.py <stage>"""
import sys, os
from PIL import Image, ImageDraw
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); stage = sys.argv[1]; H = 900
REF = os.path.join(PROJ, 'references'); RD = os.path.join(PROJ, 'renders', stage)
def ref(name, box):
    im = Image.open(os.path.join(REF, name)).convert('RGB').crop(box); return im.resize((int(im.size[0] * H / im.size[1]), H), Image.LANCZOS)
def rnd(view):
    im = Image.open(os.path.join(RD, '%s_%s.png' % (stage, view))).convert('RGB').crop((230, 90, 794, 700)); return im.resize((int(564 * H / 610), H), Image.LANCZOS)
pairs = [(ref('ref_target_ahsoka_front_portrait.jpg', (70, 0, 730, 800)), 'TARGET front portrait', rnd('front'), stage + ' front'),
         (ref('ref_target_ahsoka_smile_3q.jpg', (300, 0, 790, 480)), 'TARGET smile', rnd('three_quarter'), stage + ' three_quarter'),
         (ref('ref_target_ahsoka_dark_3q.png', (160, 60, 530, 480)), 'TARGET dark 3/4 (his right)', rnd('right'), stage + ' right'),
         (ref('ref_target_ahsoka_wide_full.png', (255, 0, 425, 150)), 'TARGET wide', rnd('left'), stage + ' left')]
tiles = [t for p in pairs for t in ((p[0], p[1]), (p[2], p[3]))]
W = sum(t.size[0] for t, _ in tiles); s = Image.new('RGB', (W, H + 24), 'black'); d = ImageDraw.Draw(s); x = 0
for t, lab in tiles: s.paste(t, (x, 24)); d.text((x + 6, 4), lab, fill='yellow'); x += t.size[0]
out = os.path.join(RD, stage + '_vs_ahsoka.jpg'); s.save(out, quality=90)
s2 = Image.new('RGB', (tiles[0][0].size[0] + tiles[1][0].size[0], H)); s2.paste(tiles[0][0], (0, 0)); s2.paste(tiles[1][0], (tiles[0][0].size[0], 0))
s2.save(os.path.join(RD, stage + '_vs_ahsoka_front.jpg'), quality=90)
print(out)
