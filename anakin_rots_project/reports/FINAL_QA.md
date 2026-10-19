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
# Variant 2 — `output/variant_2_coruscant_frame/` (stage E, mirrored chain)
Built to match the user-supplied Coruscant front frame. Same checks (`reports/qa_geometry_E.json`):

| Check | HairPlanes_M | hair_cap |
|---|---|---|
| Vertices / triangles | 9519 / 10432 | 704 / 1230 |
| Non-finite / degenerate tris / unweighted verts | 0 / 0 / 0 | 0 / 0 / 0 |
| Faces identical (vertex sets) / UVs identical | True / max diff 0.0 | True / max diff 0.0 |
| Mirror | X mirrored, winding reversed, `FACIAL_LOD1_L_*`↔`_R_*` swapped (verified in the group list) | X mirrored |
| Round trip (fresh import of the FBX) | 9519 verts, max position diff 2.2e-08 m, 15 groups | 704 verts, 4 groups |
| Skeleton in FBX | `Reference`, 247 bones | |

* Hair-to-skin signed distance (mm) 1st/5th/50th pct: mirrored original -5.3 / -0.0 / 22.4 → variant 2 -4.2 / 1.5 / 23.8; vertices pushed deeper than the shipped clearance by > 1 mm: 4.
* Card length ratio vs original: min 0.84, median 1.01, 95th pct 1.35, max 1.36 (cap 1.35).
* Vertex displacement vs the mirrored original: mean 6.4 mm, 95th pct 25.4 mm, max 64.7 mm.
* Visual: `comparison/E_vs_user_frame_big.jpg` (the supplied frame next to the front and three-quarter renders),
  `comparison/original_vs_final.png`, `lighting_side_and_mustafar.png`, `gameplay_distance_zoom.png`.
* Matches the frame: part on his left, wide front wave across the forehead to his right temple and down the cheek,
  his left side pushed back over the ear, both ears covered, chin-length sides with outward-curling ends, flat crown.
  Does not match: the frame's wave is one smooth thick lock; here it is a group of straight-hanging cards, so it reads
  as a looser, stragglier lock at close range (fine at gameplay distance).
