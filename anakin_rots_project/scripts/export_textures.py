"""Texture deliverables. No repainting: resample the as-uploaded copies to power-of-two sizes and restore the NS maps
to the conventional 128-centred (linear) encoding that the uploaded copies lost through an sRGB transform."""
import numpy as np, os
from PIL import Image
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(PROJ, 'input'); OUT = os.path.join(PROJ, 'output', 'textures'); os.makedirs(OUT, exist_ok=True)
def srgb_to_linear(a):
    a = a / 255.0; return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
jobs = [('T_Heads_Anakin_01_HairPlanes_CA', (1024, 512), False), ('T_Heads_Anakin_01_HairPlanes_NS', (1024, 512), True),
        ('T_Heads_Anakin_01_HairCap_CA', (2048, 2048), False), ('T_Heads_Anakin_01_HairCap_NS', (2048, 2048), True)]
for name, size, is_ns in jobs:
    im = Image.open(os.path.join(IN, name + '_asUploaded.png')).convert('RGBA')
    if im.size != size: im = im.resize(size, Image.LANCZOS)
    im.save(os.path.join(OUT, name + '.png'))
    if is_ns:
        a = np.asarray(im).astype(np.float64)
        lin = srgb_to_linear(a[..., :3])                       # undo the sRGB encoding -> 0.5-centred normal XY, B = gloss
        x = lin[..., 0] * 2 - 1; y = lin[..., 1] * 2 - 1
        # re-normalise XY where lossy compression pushed |xy| slightly above 1
        r = np.sqrt(x * x + y * y); f = np.where(r > 0.999, 0.999 / np.maximum(r, 1e-6), 1.0); x *= f; y *= f
        out = np.zeros_like(a); out[..., 0] = (x * 0.5 + 0.5) * 255; out[..., 1] = (y * 0.5 + 0.5) * 255
        out[..., 2] = lin[..., 2] * 255; out[..., 3] = 255
        Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, name + '_linear128.png'))
        # also a conventional 3-channel tangent normal (Z reconstructed) for DCC preview / sanity
        z = np.sqrt(np.clip(1 - x * x - y * y, 0, 1)); nm = np.stack([x, y, z], -1) * 0.5 + 0.5
        Image.fromarray(np.clip(nm * 255 + 0.5, 0, 255).astype(np.uint8), 'RGB').save(os.path.join(OUT, name + '_previewXYZ.png'))
        print(name, 'linear128 R/G means:', out[..., 0].mean().round(1), out[..., 1].mean().round(1))
print('written', sorted(os.listdir(OUT)))
