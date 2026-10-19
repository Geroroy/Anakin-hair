#!/usr/bin/env bash
# Executable reconstruction workflow (Linux; Blender 4.2 at $BLENDER; system python3 with numpy, pillow, scipy).
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/opt/blender/blender-4.2.23-linux-x64/blender}
export MIRROR=${MIRROR:-0}          # 0 = keep the game's part side (final deliverable); 1 = film part side (variant)
SUF=$([ "$MIRROR" = "1" ] && echo "" || echo "n")
$BLENDER -b -P scripts/01_inspect_original.py          # import + inspect -> working/00_original_import.blend
$BLENDER -b -P scripts/02_render_original.py           # materials, head alignment, baseline renders
$BLENDER -b -P scripts/03_card_table_and_rerender.py   # card table -> reports/card_table_original.json
$BLENDER -b -P scripts/05_fix_head_normals.py          # consistent head winding (collision reference)
$BLENDER -b -P scripts/04_export_npz.py                # -> working/geometry_original.npz
python3 scripts/stage_A_silhouette.py && $BLENDER -b -P scripts/apply_stage.py -- A$SUF
python3 scripts/stage_B_locks.py      && $BLENDER -b -P scripts/apply_stage.py -- B$SUF
python3 scripts/stage_C_fine.py       && $BLENDER -b -P scripts/apply_stage.py -- C$SUF
SRC=C$SUF OUTN=D python3 scripts/stage_D_film_push.py && $BLENDER -b -P scripts/apply_stage.py -- D
python3 scripts/export_textures.py
$BLENDER -b -P scripts/export_final.py -- D            # -> output/anakin_rots_hair_final.fbx / .blend
$BLENDER -b -P scripts/qa_geometry.py -- D             # -> reports/qa_geometry_D.json (incl. FBX round trip)
$BLENDER -b -P scripts/final_renders.py -- D           # -> renders/final_D/
python3 scripts/build_comparison.py D                  # -> output/comparison/
