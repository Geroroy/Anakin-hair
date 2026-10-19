import sys, os
from PIL import Image, ImageDraw
rd, stage = sys.argv[1], sys.argv[2]
names = ['front', 'left', 'right', 'back', 'three_quarter', 'elevated']
sheet = Image.new('RGB', (640 * 3, 640 * 2)); dr = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    p = os.path.join(rd, '%s_%s.png' % (stage, n))
    if not os.path.exists(p): continue
    im = Image.open(p).convert('RGB').resize((640, 640)); sheet.paste(im, ((i % 3) * 640, (i // 3) * 640)); dr.text(((i % 3) * 640 + 8, (i // 3) * 640 + 8), n, fill='yellow')
sheet.save(os.path.join(rd, '%s_sheet.jpg' % stage), quality=88)
