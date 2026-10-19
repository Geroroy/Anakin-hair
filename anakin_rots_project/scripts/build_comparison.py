"""Assemble output/comparison/ from renders/final_C (final + original rendered with the identical rig)."""
import os, shutil
from PIL import Image, ImageDraw
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'D'
R = os.path.join(PROJ, 'renders', 'final_' + STAGE); O = os.path.join(PROJ, 'output', 'comparison'); os.makedirs(O, exist_ok=True)
for v in ('front', 'left', 'right', 'back', 'three_quarter'):
    shutil.copy(os.path.join(R, 'final_neutral_%s.png' % v), os.path.join(O, '%s.png' % v))
shutil.copy(os.path.join(R, 'final_neutral_elevated.png'), os.path.join(O, 'elevated_third_person.png'))
# gameplay distance: the 1080p frame plus a 4x crop of the head so the reader can see what 45 px of hair looks like
g = Image.open(os.path.join(R, 'final_gameplay_1080p.png')).convert('RGB'); g.save(os.path.join(O, 'gameplay_distance.png'))
# find the head: brightest non-background region near the centre -> just crop the centre
cx, cy = g.size[0] // 2, g.size[1] // 2
crop = g.crop((cx - 120, cy - 150, cx + 120, cy + 90)).resize((960, 960), Image.NEAREST)
go = Image.open(os.path.join(R, 'original_gameplay_1080p.png')).convert('RGB').crop((cx - 120, cy - 150, cx + 120, cy + 90)).resize((960, 960), Image.NEAREST)
s = Image.new('RGB', (1920, 960)); s.paste(go, (0, 0)); s.paste(crop, (960, 0)); d = ImageDraw.Draw(s)
d.text((8, 8), 'ORIGINAL @ gameplay size (4x nearest zoom)', fill='yellow'); d.text((968, 8), 'FINAL @ gameplay size (4x nearest zoom)', fill='yellow')
s.save(os.path.join(O, 'gameplay_distance_zoom.png'))
# original vs final grid
views = ['front', 'left', 'right', 'back', 'three_quarter', 'elevated']; T = 512
sheet = Image.new('RGB', (T * len(views), T * 2 + 24), 'black'); d = ImageDraw.Draw(sheet)
for i, v in enumerate(views):
    for row, lab in enumerate(('original', 'final')):
        im = Image.open(os.path.join(R, '%s_neutral_%s.png' % (lab, v))).convert('RGB').resize((T, T)); sheet.paste(im, (i * T, 24 + row * T))
    d.text((i * T + 8, 4), v, fill='yellow')
d.text((8, 30), 'ORIGINAL (BF2 2017)', fill='yellow'); d.text((8, 30 + T), 'FINAL (ROTS reconstruction)', fill='yellow')
sheet.save(os.path.join(O, 'original_vs_final.png'))
# lighting sheet
tiles = []
for lab in ('original', 'final'):
    for n in ('side_front', 'side_right', 'side_three_quarter', 'mustafar_front', 'mustafar_three_quarter', 'mustafar_elevated'):
        tiles.append((lab + '_' + n, Image.open(os.path.join(R, '%s_%s.png' % (lab, n))).convert('RGB').resize((T, T))))
sheet = Image.new('RGB', (T * 6, T * 2), 'black'); d = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(tiles): sheet.paste(im, ((i % 6) * T, (i // 6) * T)); d.text(((i % 6) * T + 8, (i // 6) * T + 8), n, fill='yellow')
sheet.save(os.path.join(O, 'lighting_side_and_mustafar.png'))
print(sorted(os.listdir(O)))
