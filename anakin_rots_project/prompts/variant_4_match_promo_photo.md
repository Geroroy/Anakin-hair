# Claude Code task — Variant 4: match the promo photo, starting from the latest reconstruction

## Context
Repository: `geroroy/anakin-hair`, project folder `anakin_rots_project/`. Read `README.md` and
`reports/MODIFICATION_LOG.md` first. The pipeline is NumPy stage scripts (`scripts/stage_*.py`, toolkit in
`scripts/deform.py`) plus `scripts/apply_stage.py` (Blender 4.2, applies positions, regenerates scalp normals,
saves `working/<stage>.blend`, renders `renders/<stage>/`).

- **Starting geometry:** `output/variant_3_saved_latest/positions_En.npz` (identical to `working/positions_En.npz`).
  This is the un-mirrored chain An → Bn → Cn → D → En. Its front render is
  `output/variant_3_saved_latest/user_screenshot_front.png`.
- **Target photo:** `references/ref_target_promo_front.jpg` (front view, slightly low camera).
- Write a new stage script `scripts/stage_F_promo.py` (SRC=En, OUTN=F), render with `apply_stage.py -- F`,
  then export to `output/variant_4_promo_photo/` with `export_final.py -- F output/variant_4_promo_photo`,
  run `qa_geometry.py`, `final_renders.py -- F skip-original`, `build_comparison.py F final_D output/variant_4_promo_photo/comparison`.

## Hard rules (unchanged from the project)
- **Do NOT mirror.** The part stays on Anakin's right (viewer-left in a front view), which is also where it is in
  the target photo, so no side swap is needed.
- Keep all 463 cards, 11,662 triangles, vertex order, faces, UVs, skin weights and `hair_cap` untouched.
  Only vertex positions move, via per-card operations about each root (`scale_about_root`, `bend_toward`,
  `yaw_card`) and `resolve_head_collision_smooth` with clearance `min(original distance, 4 mm)`.
- Cumulative card length must stay within 0.80–1.35 × the ORIGINAL card length (`L0` cap as in
  `stage_D_film_push.py`). Roots never move.
- Do not overwrite variants 1–3.

## What the target photo shows (and how the current render differs)
| Feature | Target photo | Current render (En) | Change to make |
|---|---|---|---|
| Overall silhouette | Rounded "bob" mass, widest at temples/cheekbones, tapering to the jaw | Taller, narrower top; straggly ends flaring out below the jaw to the neck | Compact the mass into a rounded bob |
| Length at the sides | Ends at the **jaw line / chin** (z ≈ 1.59–1.61 on `HEAD_REF`) | Ends hang to mid-neck (z ≈ 1.55) | Shorten side and back-side cards 10–20 % toward jaw length |
| Ends | Thick **outward-and-up flip curls** at jaw level on both sides, grouped in 3–4 card clumps | Thin, separated, downward-pointing wisps | Strong tip flick outward + upward on the lowest 30 % (tpow 3), grouped by lobe |
| Side volume | Full, wavy, bulging over and in front of the ears; ears fully hidden | Thinner, ears partly visible | Lift mid-length of side cards 8–14° off the skull; push ear-zone tips 15–25 mm forward |
| Front | Forehead mostly **open**; hair swept back and outward from a part on his right; one soft lock curves down at his right temple (viewer-left) to the brow; on his left the hair arcs back over the temple | Heavy lock across the brow on viewer-right; forehead half covered | Lift/sweep the hanging front cards on his left (viewer-right) back 15–25°; keep one lock at his right temple ending at brow height (z ≈ 1.72) |
| Crown | Moderate, rounded volume, no flat spot, no spikes | Slightly peaked with loose strands | Tilt stray crown tips toward the scalp 4–8°; smooth the outline |
| Back | Same bob length as the sides, tips flipping outward at the collar | Long ragged shelf | Shorten back cards 10–15 %, add outward flip |
| Waves | Soft S-waves along the whole length | Mostly straight cards | Alternating grouped yaw ±10° at 40–70 % of card length |
| Colour | Lighter golden/ash brown with sun-lightened ends | Darker chestnut | **Do not repaint the textures**; note it in the report. Optionally lighten the preview material only (base-colour multiply ~1.25) for comparison renders |

## Iteration loop (repeat until the front, three-quarter and both side views read as the photo)
1. Apply one region at a time (sides → ends → front → crown → back), render `apply_stage.py -- F`.
2. Build a side-by-side of the target photo next to `renders/F/F_front.png` and `F_three_quarter.png`
   (adapt `scripts/compare_user_frame.py`) and **look at it**.
3. Name the largest remaining difference, fix it, re-render. Expect 3–5 rounds.
4. Watch for: cards crossing the eyes (no vertex below z 1.715 in front of the face, y < −0.105),
   bald patches, cap showing through, cards crumpling at the ears.

## Deliverables
- `output/variant_4_promo_photo/` — FBX, blend, `comparison/` (incl. target-vs-render sheet).
- Update `reports/MODIFICATION_LOG.md` (stage F table), `reports/FINAL_QA.md` (variant 4 section with the same
  checks as variant 2), commit and push to the working branch.
- Final message: what matches the photo, what does not (straight-card limits, texture colour), and QA numbers.
