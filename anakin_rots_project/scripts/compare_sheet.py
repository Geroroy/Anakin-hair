"""Side-by-side: film reference crops vs original render vs stage render for matching views."""
import sys, os
from PIL import Image, ImageDraw
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stage = sys.argv[1]
pairs = [('ref_palpatine_right_profile', 'right'), ('ref_palpatine_right_3q', 'right'), ('ref_front_dark', 'front'), ('ref_mustafar_3q_front', 'front'), ('ref_utapau_rear_left_3q', 'three_quarter'), ('ref_premiere_2005_top_front', 'elevated')]
H = 420; rows = []
for ref, view in pairs:
    r = Image.open(os.path.join(PROJ, 'references', ref + '.png')).convert('RGB'); r = r.resize((int(r.size[0] * H / r.size[1]), H))
    o = Image.open(os.path.join(PROJ, 'renders', '00_original', 'orig_%s.png' % view)).convert('RGB').resize((H, H))
    s = Image.open(os.path.join(PROJ, 'renders', stage, '%s_%s.png' % (stage, view))).convert('RGB').resize((H, H))
    rows.append((ref, view, r, o, s))
W = max(r.size[0] for _, _, r, _, _ in rows) + 2 * H
sheet = Image.new('RGB', (W, H * len(rows)), 'black'); d = ImageDraw.Draw(sheet)
for i, (ref, view, r, o, s) in enumerate(rows):
    y = i * H; sheet.paste(r, (0, y)); sheet.paste(o, (r.size[0], y)); sheet.paste(s, (r.size[0] + H, y))
    d.text((4, y + 4), ref, fill='yellow'); d.text((r.size[0] + 4, y + 4), 'ORIGINAL ' + view, fill='yellow'); d.text((r.size[0] + H + 4, y + 4), stage + ' ' + view, fill='yellow')
out = os.path.join(PROJ, 'renders', stage, '%s_vs_reference.jpg' % stage); sheet.save(out, quality=88); print(out, sheet.size)
