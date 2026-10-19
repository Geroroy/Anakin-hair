# Claude Code task — Variant 6: match the head sculpt (references/ref_target_sculpt_front.jpg)

Repository geroroy/anakin-hair, folder anakin_rots_project/. Read README.md and reports/MODIFICATION_LOG.md first.

Start from output/variant_3_saved_latest/positions_En.npz (un-mirrored chain An→Bn→Cn→D→En; same as working/positions_En.npz).
Target: references/ref_target_sculpt_front.jpg (a front view of a head sculpt). Write scripts/stage_G_sculpt.py (SRC=En,
OUTN=G) using scripts/deform.py, render with apply_stage.py -- G, and export to output/variant_6_sculpt/.

Hard rules: do NOT mirror (the sculpt's part is on his right, same as the game asset). Keep all 463 cards, 11,662 tris,
faces, UVs, weights and hair_cap untouched. Only per-card moves about the root (scale_about_root, bend_toward, yaw_card)
plus resolve_head_collision_smooth with clearance min(original distance, 4 mm). Every scale step is clamped to
0.80–1.35x the ORIGINAL card length. Roots never move. Do not overwrite variants 1–5.

Make it match the sculpt:
1. Part: on his right, about 3 cm right of centre, clean and visible from the front, running back to the crown.
2. Front wave: one broad wave from the part across the forehead to his LEFT temple. Its lowest point sits on his left
   brow (z≈1.715) at the outer third of the eyebrow, then it turns back and down past the temple. His right forehead,
   beside the part, stays open to the hairline. No vertex below z 1.715 in front of the eyes (y<−0.105, |x|<0.05).
3. Crown and top: smooth, moderate height, strands flowing in parallel bands from the part. Tilt stray tips 4–8°
   toward the scalp. No spikes, no flat spot.
4. EARS EXPOSED: both ears fully visible from the front. Cards rooted above and in front of the ears go back over the
   top of the ear and fall behind it. Undo the forward drape that En applied (bend those tips 15–25° backward, toward +y).
5. Sides: hair falls behind the ears in long S-waves, clearly separated into 4–6 locks per side. Ends sit BELOW the jaw,
   at chin to upper-neck level (tip z≈1.56–1.58). Lengthen side and back-side cards 8–15% to get there (within the cap).
6. Side silhouette: narrow at the temples above the ears, widening below the ears to its widest at jaw level, ends
   flaring slightly outward (6–10° tip flick, tpow 3). His left side is fuller than his right.
7. Waves: grouped yaw ±8° in lobes of 3–4 cards along the lower 60%, so neighbouring cards move together as locks.
8. Back: same length as the sides or slightly longer, layered, no blunt shelf.
9. Colour: textures untouched. The sculpt has no colour, so judge shape only.

Loop: work one region at a time (front wave → ears → sides → crown → back). After each, render and put the sculpt
beside G_front, G_three_quarter, G_left and G_right (adapt scripts/compare_promo.py; crop the sculpt around the head).
Name the biggest shape difference, fix it, and repeat 3–5 rounds. Then run qa_geometry.py -- G <fbx>,
final_renders.py -- G skip-original and build_comparison.py G final_D output/variant_6_sculpt/comparison. Update
MODIFICATION_LOG.md and FINAL_QA.md, commit and push. Report what matches, what doesn't, and the QA numbers.
