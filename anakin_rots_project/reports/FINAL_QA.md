# FINAL QA — `output/anakin_rots_hair_final.fbx` / `.blend` (stage D, un-mirrored)

Source of numbers: `reports/qa_geometry_D.json` (Blender 4.2.23), `scripts/qa_geometry.py`, NumPy checks in this file.

## 1. Geometry integrity
| Check | HairPlanes_M | hair_cap |
|---|---|---|
| Vertices / triangles | 9519 / 10432 (orig 9 519 / 10 432) | 704 / 1230 (orig 704 / 1 230) |
| Non-finite coordinates | 0 | 0 |
| Degenerate (zero-area) triangles | 0 | 0 |
| Exactly coincident vertex positions | 3 (orig 203 — collapsed wisp ends in the shipped asset; fewer now because they moved apart) | 9 (orig 9, unchanged) |
| Faces identical to original (vertex sets) | True | True |
| UV values identical to original | max diff 0.0 | max diff 0.0 |
| UV non-finite | 0 | 0 |
| Vertex groups | 15 (same names as original) | 4 |
| Unweighted vertices / weight sums | 0 / 1.000–1.000 | 0 / 1.000–1.000 |
| Custom normals | yes (scalp-transferred, regenerated) | yes (original) |
| Object transforms | identity under the imported armature frame; exported FBX nodes carry no scale (UnitScaleFactor 100 = metres, as the Frosty file) | same |
| Textures | none embedded (as the original); preview materials only in the .blend | |

## 2. Head fit (against `HEAD_REF`, triangle-accurate signed distance, mm)
| Metric | Original | Final |
|---|---|---|
| Hair vertex to skin, 1st / 5th / 50th percentile | -1.2 / 3.6 / 20.6 | -0.7 / 4.0 / 20.8 |
| Vertices inside the skin | 1.7 % | 1.3 % |
| Vertices pushed deeper than the shipped asset by > 1 mm | — | 2 |
| hair_cap moved | — | 0.0 mm (unchanged) |
No bald patches, floating roots or forehead intersections were observed in the six neutral views, the side-light and
Mustafar views, or the gameplay-distance view (`output/comparison/`). Roots are never moved by any operation.

## 3. Card deformation budget
* Card length ratio final / original: min 0.84, 5th pct 0.88, median 0.96, 95th pct 1.35, max 1.37
  (cap 1.35 vs the original; 1 card marginally above because of a post-scale bend).
* Vertex displacement vs original: mean 4.7 mm, 95th pct 16.5 mm, max 66.6 mm.
* Triangle count unchanged: 11 662.

## 4. Export round trip (fresh scene import of the final FBX)
* Objects: ['HairPlanes_M', 'Reference', 'hair_anakin_01_mesh_lod0', 'hair_cap']
* Armature `Reference`: 247 bones, `Head` present: True
* HairPlanes_M: 9519 verts / 10432 faces, max position difference vs the stage mesh 2.2e-08 m, 15 vertex groups, custom normals True, armature modifier ['Reference']
* hair_cap: 704 verts / 1230 faces, max position difference 2.2e-08 m, 4 vertex groups
* FBX header (`scripts/fbx_dump.py`): version 7400, UpAxis Y, FrontAxis +Z, UnitScaleFactor 100 — same conventions and
  the same vertex value ranges as the Frosty export (hair X −0.12…0.13, Y 1.55…1.84, Z −0.09…0.15 in FBX axes).

## 5. Visual QA (renders in `output/comparison/` and `renders/final_D/`)
* `original_vs_final.png` — six matched orthographic views. Final: part on his right as shipped (user decision),
  forehead/hairline exposed with the front swept to his left, jaw-length wavy sides framing the face, ears ~half
  covered, layered/tapered hem instead of the blunt shelf, flatter crown.
* `final_vs_film_references.jpg` — the same views next to the Episode III crops.
* `lighting_side_and_mustafar.png` — strong single side light and warm Mustafar-style light: no black/inverted cards,
  no card edges catching light as lines, no floating locks.
* `gameplay_distance.png` / `gameplay_distance_zoom.png` — 1080p third-person framing (head ≈ 45 px): the silhouette
  reads as a shorter, wavier cut; no visual noise or obvious card edges at that size.
* `elevated_third_person.png` — crown/part readability from the typical camera height.

## 6. Not verified (environment limits)
* Frosty Editor import and an in-game runtime test (Windows + game files required). See GAME_COMPATIBILITY.md §Frosty.
* The original textures at their shipped resolution (only lossy, resized uploads were available).
* LOD1+ (the export contained LOD0 only).


---
# Variant 2 — `output/variant_2_coruscant_frame/` (stage En, un-mirrored chain)
Built to match the user-supplied Coruscant front frame with the part kept on the game's side (user decision; the mesh
is **not** mirrored, so the frame's styling is applied with the sides swapped). Same checks (`reports/qa_geometry_En.json`):

| Check | HairPlanes_M | hair_cap |
|---|---|---|
| Vertices / triangles | 9519 / 10432 | 704 / 1230 |
| Non-finite / degenerate tris / unweighted verts | 0 / 0 / 0 | 0 / 0 / 0 |
| Faces identical (vertex sets) / UVs identical | True / max diff 0.0 | True / max diff 0.0 |
| Mirror / winding / vertex-group names | none / original / original | none; cap positions unchanged (0.0e+00 m) |
| Round trip (fresh import of the FBX) | 9519 verts, max position diff 2.2e-08 m, 15 groups | 704 verts, 4 groups |
| Skeleton in FBX / units | `Reference`, 247 bones / UnitScaleFactor 100, Y-up, +Z front | |

* Hair-to-skin signed distance (mm) 1st/5th/50th pct: original -1.2 / 3.6 / 20.6 → variant 2 -0.5 / 4.2 / 22.8; vertices pushed deeper than the shipped clearance by > 1 mm: 2.
* Card length ratio vs original: min 0.85, median 1.01, 95th pct 1.35, max 1.37 (cap 1.35).
* Vertex displacement vs original: mean 6.5 mm, 95th pct 25.5 mm, max 74.9 mm.
* Visual: `comparison/En_vs_user_frame_big.jpg` (the supplied frame, the frame flipped to the game's part side, and the
  front / three-quarter renders), `comparison/original_vs_final.png`, `lighting_side_and_mustafar.png`,
  `gameplay_distance_zoom.png`.
* Matches the (flipped) frame: forehead exposed on the part side, wide front wave across the forehead to the opposite
  temple and down the cheek, part side pushed back over the ear, both ears covered, chin-length sides with
  outward-curling ends, flat crown. Does not match: the part is on the opposite side from the photo by the user's
  decision, and the frame's wave is one smooth thick lock whereas here it is a group of straight-hanging cards.


---
# Variant 4 — `output/variant_4_promo_photo/` (stage F, un-mirrored, from variant 3 / stage En)
Built to match `references/ref_target_promo_front.jpg`. Checks from `reports/qa_geometry_F.json`:

| Check | HairPlanes_M | hair_cap |
|---|---|---|
| Vertices / triangles | 9519 / 10432 | 704 / 1230 |
| Non-finite / degenerate tris / unweighted verts | 0 / 0 / 0 | 0 / 0 / 0 |
| Faces identical (vertex sets) / UVs identical | True / max diff 0.0 | True / max diff 0.0 |
| Mirror / winding / group names | none / original / original | none; cap positions unchanged (0.0e+00 m) |
| Round trip (fresh import of the FBX) | 9519 verts, max position diff 2.2e-08 m, 15 groups | 704 verts, 4 groups |
| Skeleton in FBX / units | `Reference`, 247 bones / UnitScaleFactor 100, Y-up, +Z front | |

* Side/back tip height (|az| > 45°, el < 30°): median 1.625 m, 10th pct 1.579 (target jaw line 1.59–1.61; chin 1.576).
* Hair-to-skin signed distance (mm) 1st/5th/50th pct: original -1.2 / 3.6 / 20.6 → variant 4 -0.5 / 4.2 / 23.7; vertices pushed deeper than the shipped clearance by > 1 mm: 12.
* Card length ratio vs original: min 0.80, median 0.99, 95th pct 1.35, max 1.38 (cap 0.80–1.35 applied to the scale steps; the max above the cap comes from post-scale bends changing the root-to-tip chord).
* Eye zone: 0 cards with vertices below z 1.715 in front of the face.
* Vertex displacement vs original: mean 10.4 mm, 95th pct 39.8 mm, max 107.5 mm.
* Visual: `comparison/F_vs_promo_big.jpg` (photo beside front and three-quarter), `comparison/F_vs_promo.jpg`
  (all four views), `original_vs_final.png`, `lighting_side_and_mustafar.png`, `gameplay_distance_zoom.png`.
* Matches the photo: part side, open forehead with the sweep over the top, soft lock down his right temple,
  rounded jaw-length bob, outward-flipped ends, ears mostly hidden, moderate rounded crown.
  Does not match: the photo's thick smooth curl masses (the sides remain strand-like card groups), its lighter
  golden colour (textures and preview material untouched), and the ears are hidden rather than fully covered in
  profile.


---
# Variant 6 — `output/variant_6_sculpt/` (stage G, un-mirrored, from variant 3 / stage En)
Built to match `references/ref_target_sculpt_front.jpg` (head sculpt). Checks from `reports/qa_geometry_G.json`:

| Check | HairPlanes_M | hair_cap |
|---|---|---|
| Vertices / triangles | 9519 / 10432 | 704 / 1230 |
| Non-finite / degenerate tris / unweighted verts | 0 / 0 / 0 | 0 / 0 / 0 |
| Faces identical (vertex sets) / UVs identical | True / max diff 0.0 | True / max diff 0.0 |
| Mirror / winding / group names | none / original / original | none; cap positions unchanged (0.0e+00 m) |
| Round trip (fresh import of the FBX) | 9519 verts, max position diff 2.2e-08 m, 15 groups | 704 verts, 4 groups |
| Skeleton in FBX / units | `Reference`, 247 bones / UnitScaleFactor 100, Y-up, +Z front | |

* Side/back tip height (|az| > 45°, el < 30°): median 1.626 m, 10th pct 1.566 (target chin / upper neck 1.56–1.58; chin 1.576).
* Hair-to-skin signed distance (mm) 1st/5th/50th pct: original -1.2 / 3.6 / 20.6 → variant 6 -0.5 / 4.0 / 19.0; vertices pushed deeper than the shipped clearance by > 1 mm: 12.
* Card length ratio vs original: min 0.78, median 1.01, 95th pct 1.24, max 1.35 (scale steps clamped 0.80–1.35; the small excursions come from bends changing the root-to-tip chord).
* Eye zone: 0 cards with vertices below z 1.715 in front of the eyes.
* Vertex displacement vs original: mean 9.2 mm, 95th pct 33.4 mm, max 83.3 mm.
* Visual: `comparison/G_vs_sculpt.jpg` (sculpt beside front, three-quarter, left, right), `comparison/G_vs_sculpt_front.jpg`,
  `original_vs_final.png`, `lighting_side_and_mustafar.png`, `gameplay_distance_zoom.png`.
* Matches the sculpt: part on his right; one broad wave from the part across the forehead to his left brow/temple that
  turns back; his right forehead open; sideburns gone and his right ear exposed; long S-wave locks behind the ears to
  chin level; widest at the jaw; sleeker top. Does not match: the sculpt's carved continuous locks (the sides stay
  strand groups, wispier at the ends); his left ear is partly covered by the returning wave rather than fully clear.

# Variant 7 — `output/variant_7_ahsoka/` (stage H, un-mirrored, from variant 3 / stage En)
Built to match the four *Ahsoka* "World Between Worlds" frames (`references/ref_target_ahsoka_*`). Checks from
`reports/qa_geometry_H.json`:

| Check | HairPlanes_M | hair_cap |
|---|---|---|
| Vertices / triangles | 9519 / 10432 | 704 / 1230 |
| Non-finite / degenerate tris / unweighted verts | 0 / 0 / 0 | 0 / 0 / 0 |
| Faces identical (vertex sets) / UVs identical | True / max diff 0.0 | True / max diff 0.0 |
| Mirror / winding / group names | none / original / original | none; cap positions unchanged (0.0e+00 m vs En) |
| Round trip (fresh import of the FBX) | 9519 verts, max position diff 2.2e-08 m, 15 groups, custom normals | 704 verts, 4 groups |
| Skeleton in FBX / units | `Reference`, 247 bones / UnitScaleFactor 100, Y-up, +Z front | |

* Side/back tip height (|az| > 45°, el < 30°): median 1.614 m, 10th pct 1.569 (target sides at the chin 1.56–1.58, back at the collar 1.53–1.55).
* Side fullness at z 1.60–1.64 (hair outer |x| minus head outer |x|): his right 64 mm, his left 72 mm (target 38–45 mm at the skin-normal; the chord measurement includes the outward-curled ends). Hair top 30 mm above the skull (target 25–30 mm).
* Ear cover (ray casts from the ear's front and outer faces, ≥ 3 card triangles crossed): his right front 0.83 / side 0.92, his left front 1.00 / side 0.71 — the misses are the ear-lobe row (z 1.646) and the upper-back corner behind the ear; both ears are hidden in all six neutral renders.
* Hair-to-skin signed distance (mm) 1st/5th/50th pct: original −1.2 / 3.6 / 20.6 → variant 7 −0.5 / 4.3 / 23.4; vertices pushed deeper than the shipped clearance by > 1 mm: 31.
* Card length ratio vs original: min 0.80, median 1.14, 95th pct 1.35, max 1.35 (scale steps clamped 0.80–1.35).
* Eye zone: 0 cards with vertices below z 1.715 in front of the eyes.
* Vertex displacement vs original: mean 10.8 mm, 95th pct 37.8 mm, max 118 mm (vs En: mean 7.5 mm, max 92 mm — the cards swung over the ears).
* Visual: `comparison/H_vs_ahsoka.jpg` (each target frame beside the matching render: front, three-quarter, right, left),
  `comparison/H_vs_ahsoka_front.jpg`, `original_vs_final.png`, `lighting_side_and_mustafar.png`, `gameplay_distance_zoom.png`.
* Matches the frames: part on his right; one thick airy wave from the part to his left brow/temple that turns back over
  the ear; a lock down his right temple in front of the ear; both ears hidden; taller top; wide wavy side mass widest
  at cheek/jaw level with outward-and-under curled ends; sides at the chin, back at the collar; grouped S-waves.
  Does not match: the frames' thick continuous curl masses (the sides stay strand-like card groups, wispy at the
  ends); a small skin gap at his right temple above the sideburn; the warm golden colour (textures and preview
  material untouched).
