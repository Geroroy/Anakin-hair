# Claude Code task — Variant 8: narrower sides (both sides) after the Episode III portrait

## Context
Repository `geroroy/anakin-hair`, folder `anakin_rots_project/`. Read `README.md`, `reports/MODIFICATION_LOG.md` and
`prompts/variant_7c_right_ends_rots.md` first.

- **Base:** variant 7c = `working/positions_Hr.npz` (stage Hr, un-mirrored). Everything outside the region stays
  **bit-identical**: assert zero displacement for every card that is not in the region.
- **Region (the two boxes the user drew on the variant 7c front view: the side masses on BOTH sides, from the
  temples down to the ends):** hanging cards with |azimuth| 40…140°, elevation < 40°.
- **Reference:** `references/ref_target_rots_portrait_front_b.jpg` (Episode III promo portrait, front). The side hair
  hugs the cheeks: the mass sits ~20–30 mm off the skin from the temples to the jaw and the outline is only
  ~25–35 mm outside the face. Variant 7c there: 45–52 mm off the skin at jaw level, outline 60–70 mm outside the head.
- New stage name **J**: `scripts/stage_J_narrow_sides.py` (SRC=Hr, OUTN=J), render with `apply_stage.py -- J`,
  sheets with `scripts/compare_sides.py J`.

## Hard rules (unchanged)
No mirror. All 463 cards, 11,662 triangles, vertex order, faces, UVs, skin weights and `hair_cap` untouched; only
per-card `bend_toward` about the root on the region's cards (no scaling); roots never move;
`resolve_head_collision_smooth` with clearance `min(original distance, 4 mm)` restricted to the region's cards; textures
untouched; variants 1–7c not overwritten (new output folder `output/variant_8_narrow_sides/`).

## What to do in the region
1. For every region card, up to four passes: if the mid-length point (t ≈ 0.6) is further than the target from the
   skin, bend the card toward the closest skin point (≤ 14° per pass, t^0.9); then the same for the tip (t^1.3).
   Targets: tip 26 mm, mid-length 24 mm, temples (el > 24°) 20 mm.
2. Keep the ear cover, the front wave, the top and the back untouched (they are outside the region).
3. Report the side width beyond the head outline at z 1.58–1.66 and the ray-cast ear coverage before and after.

## Loop and hand-off
Render, build `renders/J/J_sides_before_after.jpg` (photo | 7c | J front, then right and left views) and **stop and show
the user for confirmation**. Only after approval: export to `output/variant_8_narrow_sides/`, QA, final renders,
comparison, report updates, commit and push.
