# Claude Code task — Variant 7c: his RIGHT side ends (the circled region) as in the Episode III portrait

## Context
Repository `geroroy/anakin-hair`, folder `anakin_rots_project/`. Read `README.md`, `reports/MODIFICATION_LOG.md` and
`prompts/variant_7_match_ahsoka_frames.md` first.

- **Base:** variant 7 = `working/positions_H.npz` (stage H, un-mirrored). Everything outside the region stays
  **bit-identical**: assert zero displacement for every card that is not in the region.
- **Region (circled by the user on `output/variant_7_ahsoka/comparison/original_vs_final.png`, front view, lower left of
  the image = his RIGHT side):** the hanging ends on his right from ear level down — cards with azimuth +45…+135°
  (his right, +az = x < 0), elevation < 22°, tip z < 1.635 on `HEAD_REF`. Only those cards move, mostly their lower half.
- **Reference:** `references/ref_target_rots_portrait_front.jpg`, viewer-left at the jaw (Episode III promo portrait).
  There the side hair is a **rounded, layered bob**: the mass stays close and full down the cheek, then at jaw / chin
  level the ends turn **outward in a soft C-curve** (thick wavy clumps, 2–4 cm across, flipping out and slightly under),
  and the length stops at the **jaw–chin line** (tip z ≈ 1.585–1.605), never hanging to the neck. Current variant 7
  there: thin wisps hanging straight down to upper-neck level (tip z down to 1.56) with an outward-and-under flick.
- New stage name **Hr**: `scripts/stage_Hr_right_ends_rots.py` (SRC=H, OUTN=Hr), render with `apply_stage.py -- Hr`,
  crops with `scripts/compare_right_ends.py Hr`.

## Hard rules (unchanged)
No mirror. All 463 cards, 11,662 triangles, vertex order, faces, UVs, skin weights and `hair_cap` untouched; only
per-card moves about the root on the region's cards (`scale_about_root` clamped to 0.80–1.35 × the original length,
`bend_toward`, `yaw_card`); roots never move; `resolve_head_collision_smooth` with clearance `min(original distance,
4 mm)` restricted to the region's cards; textures untouched; variants 1–7 not overwritten (new output folder).

## What to do in the region
1. **Length:** every card whose tip hangs below z 1.590 is shortened so the tip sits at 1.590 ± 8 mm (layered by lobe,
   k ≥ 0.80); cards ending above 1.60 are left.
2. **Rounded bob silhouette:** mid-length (t ≈ 0.4–0.7) lifted so the mass sits 28–36 mm off the cheek, tips no further
   than 42 mm from the skin.
3. **Soft outward C-curve at the ends:** lowest ~40 % bent outward along the horizontal skin normal 12–18° (t²), grouped
   in lobes of 4–6 cards (same sign, similar amount); the last ~20 % turns a further 8–10° outward-and-under (t⁵) so the
   tip points out and slightly back toward the neck, as in the photo — not up.
4. **Clumping:** within each lobe, yaw the cards 3–5° toward the lobe centre so they overlap and read as one thick wavy
   clump rather than separate strands.
5. Guards: tip-to-skin 18–42 mm; no card crosses its neighbour lobe; nothing below z 1.57.

## Loop and hand-off
Render, crop front / three-quarter / right around the region beside the same crops of variant 7 and the photo
(`scripts/compare_right_ends.py Hr`). 2–3 rounds. Then **stop and show the user the before/after crops for review**. Only
after approval: export to `output/variant_7c_right_ends_rots/`, QA, final renders, comparison, report updates, commit and
push.
