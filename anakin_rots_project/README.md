# anakin_rots_project — Episode III Anakin hair reconstruction for Battlefront II (2017)

Reconstruction of Hayden Christensen's *Revenge of the Sith* hairstyle from the original Battlefront II hair-card asset
(`hair_anakin_01_mesh.fbx`, Frosty export) by re-laying the existing cards only: no new geometry, same 11 662 triangles,
same UVs, same skin weights.

```
input/        original FBX + head reference + the four textures as uploaded (never modified)
references/   cropped Episode III frames used as the visual target (+ reference sheets)
scripts/      the whole pipeline (see scripts/run_all.sh)
working/      incremental .blend files per iteration, NumPy geometry/positions per stage
renders/      per-iteration renders, comparison sheets, final QA renders
output/       anakin_rots_hair_final.fbx / .blend, textures/, comparison/
reports/      ASSET_ANALYSIS, TEXTURE_ANALYSIS, MODIFICATION_LOG, GAME_COMPATIBILITY, FINAL_QA (+ raw dumps/JSON)
```

Run everything: `scripts/run_all.sh` (needs Blender 4.2.x, python3 with numpy/pillow/scipy; headless Eevee needs Mesa EGL).
