# Game Compatibility — Battlefront II (2017) / Frostbite / Frosty

## What is preserved (verified in `reports/qa_geometry_C.json`)
| Property | Original | Final | Status |
|---|---|---|---|
| Mesh objects | `hair_cap`, `HairPlanes_M` under `hair_anakin_01_mesh_lod0`, skeleton `Reference` | identical names / hierarchy | ✔ |
| Vertex count | 704 + 9 519 | 704 + 9 519 | ✔ unchanged |
| Triangle count | 1 230 + 10 432 = **11 662** | **11 662** | ✔ unchanged (no cards added/removed, no subdivision) |
| Topology (faces) | — | identical, same winding | ✔ |
| UV map `UVChannel0` | ByVertice | identical values | ✔ atlas layout untouched |
| Skin weights | 19 clusters, Head/HeadRoll/Neck/Neck1 + FACIAL_LOD1_* | identical values and group names | ✔ |
| Transforms | identity on meshes | identity | ✔ |
| Units/axes | FBX UnitScaleFactor 100 (metres), Y-up, +Z front | exported FBX UnitScaleFactor 100, Y-up, +Z front, no node scaling, vertex ranges identical | ✔ (verified with `fbx_dump.py`) |
| Custom normals | scalp-transferred | regenerated with the same technique from the deformed cap | ✔ |
| Tangents | present | re-exported (`use_tspace`) | ✔ |
| Materials | none in Frosty export | none required; Blender preview materials exist only in the .blend | ✔ |

## What changed and why it matters for the game
1. **Variant 1: no mirror.** Keeps the game's handedness (part on Anakin's right).
   **Variant 2 (`output/variant_2_coruscant_frame/`) is mirrored in X** to match the supplied frame: face winding is
   reversed so normals still point outward, the facial `FACIAL_LOD1_L_*`/`_R_*` vertex groups are swapped (the
   centreline bones Head/HeadRoll/Neck/Neck1 need no change), and `hair_cap` is mirrored too. *Risk:* the tangent
   handedness of the unchanged UVs is mirrored relative to the geometry, so the NS map's X detail flips; on
   cylindrical strands this is visually negligible but it is the first thing to check in-game under side light.
2. **Vertex positions** of `HairPlanes_M` moved (cumulative mean ≈ 8 mm, max ≈ 6 cm for the lengthened ear cards);
   `hair_cap` is **byte-identical in position** to the original. No vertex was moved closer to the skin than it was in
   the shipped asset.
3. **Card lengths** changed by −16 % … +35 % via uniform scaling about each root; the texture is compressed/stretched
   along the strand by the same ratio (the UVs are unchanged). The 35 % stretch applies only to the 38 cards above the
   ears (user-approved trade-off for ear coverage); everything else stays within ±16 %.
4. **Skin clusters:** Blender writes one cluster per bone per mesh (494 clusters, most empty) where Frosty wrote 19.
   Weights and bone names are identical; Frosty's importer should ignore empty clusters, but if it rejects the file,
   re-export with `use_armature_deform_only=True` after deleting the non-deforming bones from the armature.

## What could NOT be verified here
* **Frosty import / runtime test was not possible** — Frosty Editor is a Windows application needing the game files;
  neither is available in this Linux container. The FBX imports cleanly into a fresh Blender scene (round-trip QA) but
  that is *not* proof of a valid Frostbite mesh asset.
* The original export is **LOD0 only**. The game asset has further LODs; replacing only LOD0 leaves LOD1+ with the old
  (un-mirrored) silhouette → visible pop at distance. Either export/replace the other LODs with the same script
  (the pipeline is deterministic: re-run `stage_*` on an exported LOD1/LOD2 FBX) or set the LOD distances.
* Frostbite's `MeshSet` requires bounding boxes, section/LOD metadata, and the vertex layout (position, normal,
  tangent, UV, skin indices/weights as packed types) that Frosty rebuilds on import — the FBX only carries the inputs.
* Vertex colour / extra UV channels: the Frosty export had none, so none are produced; if the shipped mesh has them,
  Frosty's importer must regenerate them.

## Frosty integration steps (to validate on a Windows machine with the game)
1. Open Frosty Editor 1.0.6.x with the Battlefront II profile; browse to `Characters/.../hair_anakin_01_mesh` (the EBX
   `MeshAsset` whose export produced `hair_anakin_01_mesh.fbx`).
2. Use **Import** on the mesh asset and select `output/anakin_rots_hair_final.fbx`. Frosty's mesh importer requires:
   the same object names (`hair_cap`, `HairPlanes_M`), the same section count per LOD, and a skeleton it can match.
   If the importer asks for a skeleton, point it at the skeleton exported alongside the original (the same `Reference`
   hierarchy is in this FBX). If the importer rejects the extra `EMPTY` root, re-export without it
   (`object_types={'ARMATURE','MESH'}` in `scripts/export_final.py`).
3. Keep the original textures (`T_Heads_Anakin_01_HairPlanes_CA/NS`, `HairCap_CA/NS`) — no texture replacement is
   required. If you do replace them, import `output/textures/*_linear128.png` for the NS maps, not the as-uploaded ones.
4. Build a mod with the modified mesh and launch with Frosty Mod Manager. Check in the character selection/collection
   viewer: (a) hair sits on the head (no cap poking through, no floating roots), (b) the part is on Anakin's left,
   (c) no stretched or black cards (tangent handedness), (d) LOD transitions.
5. If LOD pop is visible, export LOD1/LOD2 from Frosty, run `python3 scripts/stage_A_silhouette.py` etc. on them
   (the scripts take any Frosty hair FBX with the same naming) and import those too.
