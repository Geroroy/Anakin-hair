# Claude Code task — Variant 7: match the *Ahsoka* "World Between Worlds" Anakin frames

## Context
Repository `geroroy/anakin-hair`, folder `anakin_rots_project/`. Read `README.md` and `reports/MODIFICATION_LOG.md`
first (especially the variant 4 and variant 6 iteration notes: what worked, what mangled cards). The pipeline is NumPy
stage scripts (`scripts/stage_*.py`, toolkit `scripts/deform.py`) plus `scripts/apply_stage.py` (Blender 4.2: applies
positions, regenerates scalp normals, saves `working/<stage>.blend`, renders `renders/<stage>/`).

- **Input asset:** `input/hair_anakin_01_mesh.fbx` (the Battlefront II hair-card mesh, 463 cards, 11,662 triangles).
- **Starting geometry:** `output/variant_3_saved_latest/positions_En.npz` (= `working/positions_En.npz`), the
  un-mirrored chain An → Bn → Cn → D → En. Do **not** start from G (variant 6): G exposes the ears and tucks the
  sideburns, which is the opposite of this target. You may copy code from `stage_G_sculpt.py` §3 (front wave),
  §5 (grouped waves) and §6 (back layering) and re-tune it.
- **Target photos** (all the same hairstyle, Hayden Christensen in *Ahsoka* ep. 5, 2023):
  - `references/ref_target_ahsoka_front_portrait.jpg` — front, eye-level, sharpest view of the part, fringe and ends.
  - `references/ref_target_ahsoka_smile_3q.jpg` — front / slight three-quarter, best view of the crown and waves.
  - `references/ref_target_ahsoka_dark_3q.png` — three-quarter from his right, best view of the side volume and ear cover.
  - `references/ref_target_ahsoka_wide_full.png` — full body, shows the overall silhouette and back length at the collar.
  - `references/ref_coruscant_promo_portrait_tall.png` — Episode III promo for colour only (not a shape target).
- New stage letter **H**: write `scripts/stage_H_ahsoka.py` (SRC=En, OUTN=H), render with `apply_stage.py -- H`,
  export with `export_final.py -- H output/variant_7_ahsoka`, then `qa_geometry.py -- H <fbx>`,
  `final_renders.py -- H skip-original`, `build_comparison.py H final_D output/variant_7_ahsoka/comparison`.

## Hard rules (unchanged from the project)
- **Do NOT mirror.** In every target frame the part is on his right (viewer-left in a front view), the same side as the
  game asset. No side swap.
- Keep all 463 cards, 11,662 triangles, vertex order, faces, UVs, skin weights and `hair_cap` untouched. Only vertex
  positions move, via per-card operations about each root (`scale_about_root`, `bend_toward`, `yaw_card`) and
  `resolve_head_collision_smooth` with clearance `min(original distance, 4 mm)`. No per-vertex pushes.
- Every scale step is clamped to **0.80–1.35 × the ORIGINAL card length** (`L0` / `clamp_k` as in `stage_G_sculpt.py`).
  Roots never move.
- Eye-zone guard: no vertex below z 1.715 in front of the eyes (y < −0.105, |x| < 0.05).
- Do not overwrite variants 1–6. Textures are never repainted.

## What the target shows (and how En differs)
Coordinates are on `HEAD_REF`: brow z ≈ 1.715, ear box |x| 0.078–0.099 / y −0.049…−0.019 / z 1.651–1.712,
jaw z ≈ 1.59–1.61, chin z ≈ 1.57, upper neck z ≈ 1.55, collar z ≈ 1.53.

| Feature | Target (Ahsoka frames) | Current (En) | Change to make |
|---|---|---|---|
| Overall | Big, soft, **voluminous wavy mane**: a rounded mass that is widest at cheekbone–jaw level, ends curling outward and under. Reads as thick curls, not strands | Flatter, closer to the skull, strand-like ends hanging straight to mid-neck | Lift the whole side/back mass off the skull, lengthen a little, add strong grouped waves and outward end curls |
| Part | On his right, ~2.5–3 cm right of centre, soft (not a clean line), visible from the hairline to the crown | Part in the same place, cleaner | Keep; let 2–3 cards cross it softly |
| Front, his left of the part | One **thick wave** sweeps from the part across the forehead to his left temple. Lowest point on the outer third of his left brow (z ≈ 1.715), then the wave turns outward and down past the temple and over the ear. The centre of the forehead is open (widow's peak visible) | The fringe hangs lower and flatter, crossing toward his left eye | Reuse G §3: cut the sweep cards to brow height, guide them to his left temple (0.085, −0.075, 1.705), turn them back; add 15–25 mm of lift on their mid-length so the wave bulges out |
| Front, his right of the part | A thick lock swoops down over his right temple **in front of the ear**, ending at cheekbone / eye level but outside the eye (tip z ≈ 1.68–1.70, |x| ≥ 0.07, y ≈ −0.09). His right forehead beside the part is open to the hairline | Short hanging cards at the right temple | Lengthen the right-temple cards (k ≤ 1.25) and curve them 10–15° down and forward along the temple; keep them outside the eye zone |
| Ears | **Both ears fully hidden** in all four frames | Upper half to two-thirds covered | Keep En's forward ear drape, then push the ear-zone tips 15–25 mm forward and 10 mm down so the cards cover the ear box completely; lengthen cards rooted above the ears up to 1.20× |
| Top / crown | **Tall and airy**: the hair stands 25–30 mm off the scalp at the top-sides, with one broad lifted wave from the part going back to the crown; no flat spot, no sleek cap | Moderate height, sleek on top | Lift cards with elevation > 35° by 6–12° away from the scalp on their mid-length (tpow 1.5); keep tips within 35 mm of the skin so there is no spike |
| Side volume | Widest at cheekbone–jaw level: the outer silhouette sits **38–45 mm** off the skin at z 1.60–1.64 on both sides (his left slightly fuller), tapering to 20–25 mm at the temples | ~25 mm at the jaw | Lift mid-length of side cards 10–18° off the skull (tpow 1.3), more on his left |
| Length | Sides end at the **chin / just below the jaw** (tip z ≈ 1.56–1.58); the back hangs to the **collar / nape** (tip z ≈ 1.53–1.55), slightly longer than the sides | Sides to mid-neck (z ≈ 1.55), back ragged shelf | Shorten the side cards that fall below 1.56; lengthen back cards toward 1.54 (k ≤ 1.15), layered, no blunt shelf |
| Ends | Thick **outward-and-under curls** in clumps of 4–6 cards at jaw and collar level, alternating left/right | Thin downward wisps | Lowest 35 % of every hanging card: bend outward 10–18° then turn the last 15 % back toward the neck (tpow 3), grouped by lobe |
| Waves | Strong S-waves along the whole length, two bends per card, lobes of 4–6 cards moving together | Mostly straight | Grouped yaw ±12–15° at 35–50 % and ∓10° at 70–85 % of the card length (use a per-lobe seed so neighbours stay together) |
| Sideburns | Present, soft, blending into the side mass in front of the ear (no gap at the ear) | Present | Keep, blend them 8–10° outward with the side mass |
| Colour | Medium golden-brown, warm highlights (blue-lit in three frames) | Darker chestnut texture | **Do not repaint the textures.** Optionally lighten the preview material only (base-colour multiply ~1.2) for comparison renders; note it in the report |

## Iteration loop (3–5 rounds)
1. Apply one region at a time in this order: **ears/sideburns → length → front wave and right-temple lock → side and
   top volume → end curls → waves → back layering → guards**. Render with `apply_stage.py -- H` after each.
2. Write `scripts/compare_ahsoka.py` (adapt `scripts/compare_promo.py`): crop each target photo around the head and put
   it beside `H_front`, `H_three_quarter`, `H_right`, `H_left`. Pair the front portrait with `H_front`, the smile frame
   with `H_three_quarter`, the dark three-quarter with `H_right`. Save `renders/H/H_vs_ahsoka.jpg` and **look at it**.
3. Name the single largest remaining difference (volume, length, ear cover, wave size, end curl), fix it, re-render.
4. Watch for the failures recorded in the modification log: cards crossing the eyes, yaws > 15° splaying locks into
   spikes, cards crumpling at the ears, the cap showing through on the lifted top, a blunt shelf at the back.

## Deliverables
- `output/variant_7_ahsoka/` — `anakin_rots_hair_final.fbx`, `.blend`, `comparison/` (incl. `H_vs_ahsoka.jpg`).
- Update `reports/MODIFICATION_LOG.md` (stage H table + "Variant 7 iteration notes") and `reports/FINAL_QA.md`
  (variant 7 section with the same checks as variants 4 and 6: triangle count, UV/weights hash, signed-distance
  percentiles, eye-zone violations, ear-box coverage, length cap).
- Commit and push to the working branch.
- Final message: what matches the frames, what the existing cards cannot express (thick curl masses, colour), and the QA
  numbers.
