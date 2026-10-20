"""Before/after crops of his right-side ends (the circled region): photo | variant 7 (H) | stage <arg>.
Run: python3 scripts/compare_right_ends.py Hr [base] [reference.jpg]"""
import sys, os
from PIL import Image, ImageDraw
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); stage = sys.argv[1]; base = sys.argv[2] if len(sys.argv) > 2 else 'H'
refname = sys.argv[3] if len(sys.argv) > 3 else 'ref_target_rots_portrait_front.jpg'
S = 560
def crop(stg, view, box):
    im = Image.open(os.path.join(PROJ, 'renders', stg, '%s_%s.png' % (stg, view))).convert('RGB').crop(box); return im.resize((S, S), Image.LANCZOS)
ref = Image.open(os.path.join(PROJ, 'references', refname)).convert('RGB').crop((110, 270, 450, 610)).resize((S, S), Image.LANCZOS)
boxes = {'front': (120, 400, 540, 820), 'three_quarter': (120, 400, 540, 820), 'right': (260, 360, 740, 840)}
rows = []
for view, box in boxes.items(): rows.append([(crop(base, view, box), 'variant 7 (%s) %s' % (base, view)), (crop(stage, view, box), '%s %s' % (stage, view))])
W = S * 3; H = (S + 24) * len(rows); sheet = Image.new('RGB', (W, H), 'black'); d = ImageDraw.Draw(sheet)
for r, row in enumerate(rows):
    y = r * (S + 24) + 24
    if r == 0: sheet.paste(ref, (0, y)); d.text((6, y - 20), 'REFERENCE Episode III portrait, his right jaw', fill='yellow')
    for c, (im, lab) in enumerate(row): sheet.paste(im, ((c + 1) * S, y)); d.text(((c + 1) * S + 6, y - 20), lab, fill='yellow')
out = os.path.join(PROJ, 'renders', stage, '%s_right_ends_before_after.jpg' % stage); sheet.save(out, quality=90); print(out)
a = Image.open(os.path.join(PROJ, 'renders', base, '%s_front.png' % base)).convert('RGB'); b = Image.open(os.path.join(PROJ, 'renders', stage, '%s_front.png' % stage)).convert('RGB')
s2 = Image.new('RGB', (2048, 1024)); s2.paste(a, (0, 0)); s2.paste(b, (1024, 0)); d = ImageDraw.Draw(s2); d.text((8, 8), 'variant 7 (%s)' % base, fill='yellow'); d.text((1032, 8), stage, fill='yellow')
s2.save(os.path.join(PROJ, 'renders', stage, '%s_vs_%s_front.jpg' % (stage, base)), quality=90)
