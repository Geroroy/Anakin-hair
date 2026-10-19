"""User's Coruscant frame next to the original and a stage's front / three-quarter renders."""
import sys, os
from PIL import Image, ImageDraw
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); stage = sys.argv[1]
H = 640
ref = Image.open(os.path.join(PROJ, 'references', 'ref_coruscant_front_user_head.png')).convert('RGB'); ref = ref.resize((int(ref.size[0] * H / ref.size[1]), H))
tiles = [(ref, 'USER FRAME (Coruscant)'), (ref.transpose(Image.FLIP_LEFT_RIGHT), 'USER FRAME flipped (part on the game side)')]
for lab, p in (('ORIGINAL front', os.path.join(PROJ, 'renders', '00_original', 'orig_front.png')), (stage + ' front', os.path.join(PROJ, 'renders', stage, stage + '_front.png')), (stage + ' three_quarter', os.path.join(PROJ, 'renders', stage, stage + '_three_quarter.png')), (stage + ' right', os.path.join(PROJ, 'renders', stage, stage + '_right.png')), (stage + ' left', os.path.join(PROJ, 'renders', stage, stage + '_left.png'))):
    tiles.append((Image.open(p).convert('RGB').resize((H, H)), lab))
W = sum(t.size[0] for t, _ in tiles); s = Image.new('RGB', (W, H + 24), 'black'); d = ImageDraw.Draw(s); x = 0
for t, lab in tiles: s.paste(t, (x, 24)); d.text((x + 6, 4), lab, fill='yellow'); x += t.size[0]
out = os.path.join(PROJ, 'renders', stage, stage + '_vs_user_frame.jpg'); s.save(out, quality=90); print(out)
