# Modification Log — ROTS Anakin hair reconstruction

All geometry edits are scripted and reproducible: `scripts/stage_A_silhouette.py` → `stage_B_locks.py` →
`stage_C_fine.py` → `stage_D_film_push.py` (NumPy, operate on `working/geometry_original.npz`) and
`scripts/apply_stage.py` (Blender, applies the positions, regenerates scalp-transferred normals, saves
`working/<stage>.blend`, renders `renders/<stage>/`).

**Two deliverables** (both in `output/`):
* `output/variant_1_game_part_side/` (= `output/anakin_rots_hair_final.*`): stage D of the **un-mirrored** chain
  (An → Bn → Cn → D). Part on Anakin's right as the game shipped; film-style restyle.
* `output/variant_2_coruscant_frame/`: stage En of the **un-mirrored** chain (An → Bn → Cn → D → En), built after the
  user supplied a Coruscant front frame (`references/ref_coruscant_front_user.jpg`) and asked for a copy that matches
  it. Per the user's decision the mesh is **not mirrored** and the part stays on the game's side (his right), so the
  frame's styling is applied with the sides swapped: wide front wave sweeping across the forehead to his *left* temple,
  the part side pushed back over the ear, chin-length sides curling outward, flat crown. (A mirrored build, stage E,
  was made first and discarded at the user's request; `working/E.blend` is the only trace.)

* `output/variant_3_saved_latest/`: frozen copy of the latest reconstruction (= variant 2 geometry, stage En) kept at
  the user's request as the starting point for variant 4.
* `output/variant_4_promo_photo/`: stage F (`stage_F_promo.py`, SRC=En), built to match the promo front photo
  `references/ref_target_promo_front.jpg`: compact rounded jaw-length bob, grouped outward-up flip curls, full sides,
  open forehead with one soft lock at his right temple, soft S-waves. No mirror (the photo's part is on his right,
  same as the game asset).

* `output/variant_5_saved_promo/`: frozen copy of variant 4 (stage F) with `positions_F.npz`, saved at the user's
  request as a fixed starting point for later work.

* `output/variant_6_sculpt/`: stage G (`stage_G_sculpt.py`, SRC=En = variant 3), built to match the head sculpt
  `references/ref_target_sculpt_front.jpg`: part on his right, one broad front wave to his left brow/temple turning
  back, right forehead open, ears exposed (sideburns tucked), long S-wave locks behind the ears to chin level, widest
  at the jaw, sleek top. No mirror.

**Variant 1 = stage D of the un-mirrored variant** (`MIRROR=0`: stages An → Bn → Cn → D). The mirrored
variant (stages A → B → C, part on Anakin's left as in the film) was built first; the user reviewed the evidence
(`reports/part_side_evidence.jpg`, `reports/variants_original_vs_unmirrored_vs_mirrored.jpg`) and chose to keep the
game's original part side, and asked for a stronger push toward the film look (stage D). `working/C.blend` keeps the
mirrored variant for reference; it is not exported.
Only vertex *positions* and *normals* change; vertex order, topology, UVs and skin weights are never touched.
Every operation is a per-card transform about the card's root (uniform scale, bend about an axis through the root with
angle ∝ tᵖ, yaw about the vertical through the root) or a smoothed per-card collision push, so each card keeps its
authored wave shape and its texture mapping.

| Stage | File | Operation | Parameters / affected cards |
|---|---|---|---|
| 00 | `01_inspect_original.py`, `02_render_original.py`, `03_card_table_and_rerender.py` | Import, inspect, classify 463 cards into regions, baseline renders | — |
| 00 | `05_fix_head_normals.py` | **Head reference only**: recalculated face winding/normals of the user's head re-export (its exported vertex normals were inconsistent — scalp normals averaged z = 0.08) | head mesh is never exported |
| A | `stage_A_silhouette.py` §1 | Mirror X (`MIRROR=1` only; **not used in the final**) | mirrored variant only |
| A | §2 | Per-card length scale about the root | ±6 % noise everywhere; sides −7 %; back-sides −5 %; centre back +3 %; fringe −10 % (range 0.84–1.08) |
| A | §3 | Bend lower side/back cards toward the head when the tip is further than 28 mm (sides) / 36 mm (back) from the skin | 111 cards, ≤ 25°, t^1.2 |
| A | §4 | Drape cards rooted behind/above the ears forward | 21 cards, 7° (his left) – 10° (his right), t^1.5 |
| A | §5 | Crown cards tilted toward the scalp when tip > 30 mm off the skin | 40 cards, ≤ 6°, t^1.5 |
| A | §7 | Smoothed collision: no vertex closer to the skin than in the shipped asset, 4 mm elsewhere | 1 654 vertex moves |
| B | `stage_B_locks.py` §1 | Layered hem: lowest 40 % of back/nape cards flicked outward (60 %) or tucked (40 %) | 84 cards, 6–16°, t^2.5 |
| B | §2 | Jaw-level S-waves: alternating yaw ±7° (t²) + outward tip flick 5–11° (t³) | 141 cards |
| B | §3 | Asymmetry: his left side swept back ≤ 6°, his right side forward ≤ 4° and +2 % length | 105 cards |
| C | `stage_C_fine.py` §1 | Ear coverage: cards rooted above the ears lengthened so tips reach the lobe level, draped 7–9° forward | 31 cards, scale ≤ 1.28 |
| C | §2 | Back hem layers: low-frequency ±7 % length modulation (3–4 adjacent cards per layer) | 93 cards |
| C | §3 | Behind-ear waves: ±5° yaw on the tip third | 141 cards |
| C | §4 | Loose strands left of the part tipped 5° forward onto the forehead | 14 cards |
| D | `stage_D_film_push.py` §1 | Front sweep: hanging front cards bent 6–16° back (centre/part side only) and yawed 8° along the sweep (towards his left) → forehead/hairline exposed as in the Utapau/Palpatine frames | 42 cards |
| D | §2 | Face-framing S-waves: grouped yaw ±11° (lobes of 3–4 cards) + tip flick 3–9° | 151 cards |
| D | §3 | Fuller behind the ears: lower halves lifted 5–12° off the skull | 29 cards |
| D | §4 | Ear coverage: cards above the ears lengthened (≤ ×1.35) to lobe level and draped 12° forward | 38 cards |
| D | §5 | Temple locks tipped 6° forward/down around the ears | 66 cards |
| En (variant 2 only) | `stage_E_variant2.py` §1 | Sides lengthened up to +12 % (jaw/chin length as in the frame) | 187 cards |
| En | §2 | Front wave on the sweep side yawed 22° across the forehead toward the temple, lifted to brow level | 35 cards |
| En | §2b | Front, part side: hanging cards pushed back/up 10–26° and yawed 12° toward the ear | 17 cards |
| En | §3 | Part side swept back 6°, ends flicked outward 8–16° | 107 cards |
| En | §3b | Part-side volume over the ear: lower halves lifted 5–11° | 38 cards |
| En | §4 | Sweep-side ends curled outward 10–18° | 94 cards |
| En | §5 | Crown flattened: tips tilted up to 8° toward the scalp | 32 cards |
| F (variant 4) | `stage_F_promo.py` §1–2 | Side/back cards hanging below the jaw line shortened to z = 1.600 | 87 cards, k ≥ 0.80 of original |
| F | §4a | Compact silhouette: tips > 34 mm off the skin bent toward it (≤ 22°) | 162 cards |
| F | §4b | Side volume: 8–14° lift off the skull; ear-zone tips ~20 mm forward; ear cards lengthened toward the lobe and draped forward | 78 + 78 + 69 cards |
| F | §3 | Flip curls: lowest 30 % bent outward+up 6–12° in lobes of 3–4 cards (t³) | 231 cards |
| F | §7 | Soft S-waves: grouped yaw ±4° on the lower part (t²) | 266 cards |
| F | §5 | Open forehead: hanging/crossing front cards on his left swept back 15–25°; the near-horizontal sweep cards beside the part bent 22° back over the top | 32 + 17 cards |
| F | §5b | His left side splayed tips pulled back down along the face | 59 cards |
| F | §5d | Soft lock at his right temple: cards already falling down the temple lengthened to brow height and curved 10° down the temple | 17 cards |
| F | §6 | Crown: stray tips 4–8° toward the scalp | 4 cards |
| F | guard | Eye-zone enforcement (no vertex below z 1.715 in front of the face) + smoothed collision | 0 violations |
| G (variant 6) | `stage_G_sculpt.py` §1 | Ears exposed: cards above/in front of the ears restored to original length and bent 15–25° backward; cards crossing the measured ear volume swept back | 34 + 80 cards |
| G | §2 | Sides/back lengthened toward z = 1.57 (chin / upper neck), back to 1.56 | 225 cards, k ≤ 1.15 |
| G | §3 | Front wave: sweep-side cards cut to brow height, guided to his left temple (0.085, −0.075, 1.705) and turned back; hanging cards on his right forehead swept back 18° | 23 + 9 cards |
| G | §3b | Sideburns (rooted in front of the ears, below the temple): shortened to 0.80 and tucked back 14° | 84 cards |
| G | §4 | Silhouette: temples ≤ 18 mm from the skin, jaw level ≥ 25 mm (+6 mm on his left), lower tips > 36 mm bent in; ends flared 4–8° (t³) | 135 + 130 + 214 cards |
| G | §5 | Waves: grouped yaw ±8° (t^1.8) in lobes of 3–4 cards | 266 cards |
| G | §6 | Back layers ±6 % low-frequency modulation | 71 cards |
| G | §7 | Top sleek: tips > 17 mm off the scalp (el > 38°) tilted 5–10° toward it | 45 cards |
| G | guard | Eye-zone enforcement + smoothed collision | 1 bend step, 0 violations |
| H (variant 7) | `stage_H_ahsoka.py` §1 | Ears hidden: cards above/around the ears lengthened (≤ ×1.25) to below the ear and swung 14–26° so they hang over / in front of the ear 2–3 cm off the skin; then an iterative pass pulls the three nearest cards over every ear sample point still visible to a front or side ray (< 3 card triangles crossed) | 76 cards + 162 / 159 bend steps |
| H | §1b | Sideburns kept, lengthened to the jaw in front of the ear (tip z ≤ 1.618), 1–2° outward, turned over the ear front | 88 cards |
| H | §2 | Length: sides to the chin (tip z 1.572), back to the collar (1.542), ±6 mm layering, k 0.85–1.15 | 250 cards |
| H | §3 | Front wave: sweep-side cards cut to brow height, mid-length bulged 13° off the forehead (airy wave), guided 14° to his left temple (0.088, −0.078, 1.703) and tips turned 12° back over the ear; his-left temple cards hanging forward of the eye line turned back 8° | 24 + 3 cards |
| H | §3b | Right temple lock: cards already falling down his right temple lengthened (≤ ×1.25) to tip z ≈ 1.69 and curved 13° down the temple in front of the ear | 14 cards |
| H | §4 | Top: mid-length lifted 5° (×0.7–1.3) off the scalp for cards < 28 mm from it; stray tips > 26 mm tilted back | 82 cards |
| H | §4b | Side volume: temples (above the ear cover) held at 23 ± 6 mm; cheek/jaw level pushed out to 42 mm (+4 mm on his left), tips > 52 mm bent in | 131 cards |
| H | §5 | Ends: lowest ~35 % curled outward 10–14° in lobes (t³), last ~15 % turned back under (t⁷) | 237 cards |
| H | §6 | Waves: grouped yaw ±11° (t^1.8) with a −9° counter yaw on the lower part (t⁴), lobes of 4–6 cards | 290 cards |
| H | §7 | Back layers ±5 % low-frequency modulation | 78 cards |
| H | guards | Final ear pass; ear-cover tips > 32 mm off the skin folded in (66); top tips > 24 mm tilted to the scalp (17); eye-zone enforcement (0 steps); smoothed collision (855 vertex moves) | — |
| Hr (variant 7c) | `stage_Hr_right_ends_rots.py` region | Only his RIGHT side ends (the region the user circled on the variant 7 front view): hanging cards az +45…+135°, el < 22°, tip z < 1.635 — 61 cards; every other card asserted bit-identical to H | 61 cards / 1419 vertices |
| Hr | §1 | Length: tips below z 1.590 shortened to the jaw–chin line (1.590 ± 8 mm by lobe, k ≥ 0.80) | 28 cards |
| Hr | §2 | Rounded bob: mid-length (t ≈ 0.55) lifted so it sits ~36 mm off the cheek (≤ 12°, t^0.8); tips kept within 42 mm | 19 cards |
| Hr | §3 | Ends: soft outward C-curve 20° (×0.85–1.0 by lobe, t²) then 10° out-and-under (t⁵), tips pointing out and slightly back toward the neck as in the Episode III portrait | 61 cards |
| Hr | §4 | Clumping: cards yawed up to 6° toward their lobe centre so lobes read as thick wavy clumps | 61 cards |
| Hr | guards | Tips within 42 mm of the skin, nothing below z 1.57, smoothed collision restricted to the region (27 vertex moves) | — |
| J (variant 8) | `stage_J_narrow_sides.py` region | Only the side masses on BOTH sides (the two boxes the user drew on the variant 7c front view): hanging cards with \|az\| 40…140°, el < 40° — 211 cards; every other card asserted bit-identical to Hr | 211 cards / 4685 vertices |
| J | §1 | Narrower sides after the Episode III portrait: four passes bending each card toward its closest skin point until the mid-length (t ≈ 0.6) sits ≤ 24 mm and the tip ≤ 26 mm off the skin (temples 20 mm), ≤ 14° per pass; smoothed collision restricted to the region (354 vertex moves) | 418 bend steps |
| D-shading | `common.py` materials, `export_textures.py` | **Shading/texture**: no texture repaint; NS maps restored to 128-centred encoding; preview material: alpha clip 0.35, NS B → roughness; scalp-transferred normals regenerated from the deformed cap (validated to render identically to the shipped normals) | — |
| E | `final_renders.py` | Gameplay-readability renders (1080p third-person perspective, head ≈ 45 px), strong side light, Mustafar light | — |

Net displacement of `HairPlanes_M` vs the original (un-mirrored chain): stage A mean 3.0 mm / max 3.0 cm, B +1.0 mm, C +0.9 mm / max 3.3 cm, D +2.8 mm / max 6.2 cm (the lengthened ear cards and the swept front). `hair_cap`: **unchanged** in the final.

## Things tried and rejected (visible in the iteration history)
* **Mirroring the asset** to put the part on his left (as in every film frame): rejected by the user for both variants. Neither deliverable is mirrored.
* **Per-vertex radial "slimming" field** (first stage A attempt): crushed cards into flat vertical strips at the back —
  replaced by per-card bends toward the skin.
* **Yawing temple cards 35° over the ears** and a **fringe yaw**: produced splayed, spiky locks at the temples and a lock
  swinging away from the face. Replaced by small forward drapes + lengthening; the fringe keeps the (mirrored) original
  lock over his right brow, shortened 10 % so it ends at the brow instead of the eye as in the film.
* **Per-vertex collision pushes** crumpled cards at the ear; replaced by the per-card smoothed push.
* **Nearest-vertex signed distance** against the head: the user's head export had inconsistent normals → garbage
  distances and runaway pushes; replaced by consistent winding + triangle-accurate closest point.

## Variant 4 iteration notes (4 rounds, `renders/F/F_vs_promo_big.jpg`)
1. Round 1: jaw length and open forehead achieved, but ±10° waves and 10–24° flips blew his left side out
   horizontally. 2. Round 2: waves halved; the "temple lock" step caught the game's crossing fringe and dropped it
   over his left eye. 3. Round 3: lock restricted to cards already falling down his right temple, eye-zone guard
   added. 4. Round 4: the near-horizontal sweep cards beside the part were bent back over the top, opening the
   forehead corner as in the photo. Not achievable with the existing cards: the photo's thick, smooth curl masses
   (the sides stay strand-like) and its lighter golden colour (textures untouched, preview material unchanged).

## Variant 6 iteration notes (5 rounds, `renders/G/G_vs_sculpt.jpg`)
1. The first "ear box" was far larger than the ear (the original asset hit it 172 times); its enforcement loop
   mangled cards. Replaced by the ear volume measured on HEAD_REF (right ear y −0.049…−0.019, z 1.651…1.712) and
   an explicit undo of variant 3's forward ear drape. The shipped asset itself has 33 sideburn cards rooted inside
   that volume, so the metric is informational only.
2. The crossing front lock drooped to the cheek; cut to brow height, guided to the temple and turned back.
3. Sideburn cards (absent on the sculpt) shortened and tucked; sides narrowed (jaw fullness 25 mm, flare 4–8°).
4. Top sleeked (17 mm threshold). Not achievable with the cards: the sculpt's carved, continuous locks read as
   strand groups; the lower ends stay wispier than the sculpt's solid mass.

## Variant 7 iteration notes (5 rounds, `renders/H/H_vs_ahsoka.jpg`)
1. Round 1 (from En): fringe still a flat dark lock across the forehead, top spiky, both ears visible. The first ear
   metric (any vertex within 12 mm) read 100 % while the render showed the ears: replaced by ray casts from the
   ear's front and outer faces counting crossed card triangles.
2. Round 2: front wave bulged 13° off the forehead and turned back at the temple (reads as the airy wave of the
   frames); top lift halved; sideburns lengthened to the jaw. His right ear still read through a gap behind the
   sideburn.
3. Round 3: ear-cover loop (nearest cards over still-visible ear points) — 0.83 coverage, no visible gain: the cards
   it picked were rooted beside the ear and only rotated in place.
4. Round 4: candidates restricted to cards rooted above the ear point, 10° steps, and the temple-tightening /
   eye-line steps no longer touch ear-cover cards. Ears hidden in all six views; three his-left cards flew out to
   6 cm off the cheek.
5. Round 5: ear-cover tips > 32 mm folded back in, sideburn outward blend removed (closes the temple gap), top
   silhouette pass. Kept as variant 7. Not achievable with the cards: the frames' thick continuous curls (the
   mass stays strand-like, wispy at the ends), the ear lobe row of the metric (sideburn tips are alpha-faded
   there) and the warm golden colour (textures untouched).

## Variant 7c iteration notes (3 rounds, `renders/Hr/Hr_right_ends_before_after.jpg`)
Target: `references/ref_target_rots_portrait_front.jpg` (Episode III promo portrait), his right jaw only; base variant 7.
1. Round 1 (fullness 32 mm, C-curve 15°, clump 4°): wisps to the neck gone, ends at the jaw–chin line, mild outward
   flick — close to the photo's silhouette but thin.
2. Round 2 (36 mm, 20°, 6°): a little rounder and more clumped. **Chosen by the user** after reviewing round 3.
3. Round 3 (44 mm, 26°, clump 8°, region widened to el < 28°, tips ≤ 50 mm): rounder and thicker; the user judged it
   too much and asked for round 2, which is what variant 7c ships.
An earlier attempt at the same region against the *Ahsoka* frames (flip curls rolling outward and up, three rounds)
was reviewed and rejected by the user: with these cards the upward hook reads as a splayed wing of strands.

## Variant 8 iteration notes (1 round, `renders/J/J_sides_before_after.jpg`)
Target: `references/ref_target_rots_portrait_front_b.jpg` (Episode III promo portrait), both side masses; base variant 7c.
One round (tip 26 mm / mid 24 mm / temples 20 mm) was confirmed by the user as is. Measured at z 1.58–1.66: the 90th
percentile hair-to-skin distance went from 47 / 48 mm (his right / left) to 45 / 39 mm and the outline beyond the head
from 44 / 53 mm to 44 / 31 mm; on his right the outline is held by the variant 7c end curls, which were kept. The
ray-cast ear cover is unchanged on his right (0.83 front / 0.96 side) and drops to 0.5 on the side rays of his left ear
(the ear still reads as hidden in the left view).

## Known remaining gaps vs. the film
* Ears are covered on roughly the upper half to two thirds (stage D); Full coverage needs new cards
  (the asset has none in front of the ears), which was ruled out to keep the triangle count and topology intact.
* Back layering is suggested by length modulation and tip flicks; the film's rear curls are looser than what the
  existing straight-hanging cards can express without re-authoring the card texture mapping.
