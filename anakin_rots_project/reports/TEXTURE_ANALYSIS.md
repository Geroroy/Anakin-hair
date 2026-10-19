# Texture Analysis — Anakin hair (Battlefront II 2017)

## 1. What was actually supplied

| Requested file | Received as | Size received | Mode | Notes |
|---|---|---|---|---|
| `T_Heads_Anakin_01_HairPlanes_CA.png` | `2.webp` → `input/T_Heads_Anakin_01_HairPlanes_CA_asUploaded.png` | 1024 × 512 | RGBA | 8 strand strips (3 dense, 5 wispy) on transparent background |
| `T_Heads_Anakin_01_HairPlanes_NS.png` | `3.webp` → `input/T_Heads_Anakin_01_HairPlanes_NS_asUploaded.png` | 1024 × 512 | RGBA (A ≈ 255) | greenish-yellow packed map |
| `T_Heads_Anakin_01_HairCap_CA.png` | `4.webp` → `input/T_Heads_Anakin_01_HairCap_CA_asUploaded.png` | 1500 × 1500 | RGBA | scalp colour, large oval + thin strip islands |
| `T_Heads_Anakin_01_HairCap_NS.png` | `1.webp` → `input/T_Heads_Anakin_01_HairCap_NS_asUploaded.png` | 2000 × 2000 | RGBA (A ≈ 255) | yellow packed map |

**Important caveat.** The four textures reached this session as WebP conversions made by the upload pipeline, with an
embedded ICC profile, and resized to non-power-of-two sizes (1500 and 2000 px). The original Frosty exports are almost
certainly 2048 × 2048 (cap) and 2048 × 1024 or 1024 × 512 (planes) PNG/DDS. Consequences:

* Lossy compression noise exists in all channels (e.g. 254/255 alpha speckle in the NS maps).
* The two HairCap textures no longer share a resolution; they were resampled to 2048 × 2048 when re-exported (see §5).
* Exact channel values cannot be trusted to ±2/255; the *semantics* below are nonetheless unambiguous.

## 2. Numerical inspection (per channel, 0–255)

```
HairPlanes_CA : R mean 30.6  G 22.8  B 17.6  A mean 42.5 ; alpha==0 68.8 %, alpha==255 2.9 %, 256 distinct alpha values
HairPlanes_NS : R 139–224 (mean 186.1, std 13.8)  G 156–213 (mean 187.2, std 2.6)  B 100–213 (mean 145.2)  A 254/255
HairCap_CA    : R 0–101 (mean 35.5) G 0–78 B 0–68 ; A: 49 % == 255, 35 % == 0, 15 % partial (soft hairline edge)
HairCap_NS    : R 159–207 (mean 187.0, std 2.7) G 157–214 (mean 187.3, std 4.2) B 0–181 ; corners = (187,188,0)
```

RGB channels of both `_CA` maps are highly correlated (r ≈ 0.97–0.99) → they are a single albedo colour, not packed data.
Both `_NS` maps have R and G **centred on 187, not 128**. 187/255 = 0.733 = sRGB-encode(0.5). This proves the
uploaded copies were gamma-encoded (linear → sRGB) somewhere between Frosty and this session. After linearising
(sRGB → linear) the R/G means become 0.497–0.501, i.e. a textbook 0.5-centred tangent-space normal map.

## 3. Channel semantics (verified, not assumed)

### `_CA` = Colour + Alpha
* RGB: sRGB albedo. In-strand mean (82, 57, 41); 10th–90th percentile (57,36,23)–(112,83,63) → chestnut / dark warm brown,
  matching the film's medium-dark brown with warm highlights. Cap albedo mean (57, 38, 28) — darker than the strands, as
  expected for a scalp base layer seen through gaps.
* A: coverage mask. Planes alpha is a continuous 0–255 gradient (soft strand edges, 256 distinct values) → the game uses
  alpha test + possibly alpha-to-coverage; the pipeline here uses a 0.35 clip which keeps the strand silhouettes clean.
  Cap alpha is binary inside the scalp with a 15 % soft-edge band = the feathered hairline on the forehead and neck.
* Root-to-tip gradient on the planes (mean luminance per 64-px band, top→bottom): 51, 56, 65, 71, 66, 60, 57 → roots
  are darkest, the mid-length is brightest, tips darken again. Roots are at the **top (v = 1)** of the atlas.
* Alpha coverage per 128-px column (left→right): 0.39, 0.45, 0.31, 0.21, 0.13, 0.07, 0.06, 0.07 → columns 0–2 are
  dense structural locks, 3–4 medium clumps, 5–7 wispy breakup strands.

### `_NS` = Normal (XY) + Specular/gloss (B)
* R = normal X, G = normal Y (both 0.5-centred after linearisation; |xy| never exceeds 0.56, so Z can be reconstructed
  with `z = sqrt(1 − x² − y²)`; the in-game shader does the same — Frostbite stores 2-channel normals).
* R varies strongly across strands horizontally (mean |∂R/∂u| = 3.1 vs |∂R/∂v| = 0.7) and G is nearly flat (std 2.6):
  exactly what cylindrical vertical strands produce. Y-flip is **not** needed for Blender (the sign of the tiny G
  variation is consistent with OpenGL/+Y-up convention in the test render; if Frostbite expects DirectX −Y it is a
  shader-side convention, and the textures are left untouched here).
* B is a 0–1 mask, not Z: on the cap it is 0 outside the scalp and correlates r = 0.97 with cap alpha; on the planes it
  correlates with strand luminance (r = 0.27) and alpha (r = 0.20). It behaves like a **specular / gloss mask**
  (brighter where the strand is lit). In the Blender material it drives roughness (0.85 → 0.5).
* A ≈ 1 everywhere: unused (or a dropped fourth packed channel such as AO/ID that the exporter did not write).

## 4. How the Blender preview material uses them

`scripts/common.py::hair_material()` — Image(CA, sRGB) → Base Colour, alpha > clip → Alpha; Image(NS, loaded with the
sRGB transform so Blender linearises 187 → 0.5) → separate → x = 2R−1, y = 2G−1, z = sqrt(1−x²−y²) → Normal Map
(tangent, strength 0.6); B → roughness. Dithered (hashed) blend, no backface culling (cards are single-sided quads seen
from both sides in game).

## 5. Modifications made to textures

* **No texture content was repainted or recoloured.** The chestnut colour, gradients, strand density and alpha edges of
  the originals are correct for the film look, and the hair-card UVs are preserved so the cards keep sampling the same
  atlas columns.
* `output/textures/` contains the four maps as lossless PNG at power-of-two sizes (cap 2048², planes 1024 × 512) with
  the NS maps **un-gamma'd back to the 128-centred linear encoding** (`T_*_NS_linear128.png`) so a DDS/texture import
  into Frosty receives conventional data, plus the as-uploaded copies for reference. See `scripts/export_textures.py`.
  If the user still has the original Frosty PNG/DDS exports, those should be used in preference to anything in
  `output/textures/` — they are lossless and the exact game resolution.

## 6. Shader dependencies that cannot be reproduced here

* Frostbite hair shader parameters (anisotropic highlight shift/width, alpha-to-coverage settings, two-sided lighting,
  strand-tint multipliers) live in the game's `ShaderGraph`/`MaterialInstance` EBX assets, which were not supplied.
* Whether the NS alpha / missing fourth channel carries an ID/AO/root mask in the shipped DDS is unknowable from the PNGs.
* The game's normal convention (DirectX −Y vs OpenGL +Y) and any 2-channel BC5 reconstruction happen in the shader.
