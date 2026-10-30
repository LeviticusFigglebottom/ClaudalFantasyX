# big22 full-manifest capture (SHOTS track, cloud lavapipe)

- Source: `claude/new-session-mj8c3c` @ 19e7f01c (Merge lead/gate-big22), HYMN_SKIP_BLENDER=1, after `git lfs pull` and a clean import.
- Renderer: Godot 4.6.3-stable (debian4.6.3+ds-2), Vulkan Forward+ on llvmpipe (LLVM 22.1.8, 256 bits), the same as the baselines.
  Unchanged shots match their baselines at RMSE 0.00000, so parity holds.
- Capture: `tools/screenshots/capture.sh --shots <id> --out <worker dir>`, one process per shot, as in `tools/ci_local.sh`.
  Pass 1 ran 3 workers with the 600 s guard; the rest ran 2 workers with HYMN_SHOT_TIMEOUT=1500.
- Compare: `tools/screenshots/compare.py`'s linear-light RMSE against `tests/screenshots/baselines/` at that sha (read-only;
  no baseline was written). `compare.txt` lists PASS / DRIFT (rmse, limit) / NO-BASELINE for every id. NO-BASELINE ids marked
  `(pending_baseline)` are flagged as such in shots.json.
- `sheets/sheet_NNN.png`: BASE | OUT, 8 rows per sheet, for every non-PASS shot in manifest order (NO-BASELINE rows show a purple placeholder).
- `out/<id>.png`: the capture for every one of the 687 shots.

## Pass-1 timeouts (600 s), all re-captured cleanly with a 1500 s limit
These are slow scenes, not hangs. Raise HYMN_SHOT_TIMEOUT for full-manifest runs.
- npc_haluna_dock
- npc_haluna_chapel
- npc_haluna_market
- npc_haluna_lane
- slice_beach_h05_asha
- slice_beach_h06_toma
- slice_prologue_vigil_line
- slice_verse_steps
- slice_verse_threshold
- slice_beach_standing
- slice_verse_c08
- slice_verse_recognition
- slice_dock_night_yes
- ch01_oruvel_storm
- slice_neme_table
- ch01_scale_hull
- ch01_bell_room
- ch01_hullgnaw_rises
- ch01_drop
- ch01_net_pen

Re-capture times:
- npc_haluna_dock rc=0 png 771s
- npc_haluna_market rc=0 png 795s
- npc_haluna_chapel rc=0 png 578s
- npc_haluna_lane rc=0 png 646s
- slice_beach_h05_asha rc=0 png 815s
- slice_prologue_vigil_line rc=0 png 767s
- slice_beach_standing rc=0 png 1074s
- slice_beach_h06_toma rc=0 png 1040s
- slice_verse_steps rc=0 png 570s
- slice_verse_threshold rc=0 png 565s
- slice_verse_recognition rc=0 png 463s
- slice_verse_c08 rc=0 png 628s
- slice_dock_night_yes rc=0 png 1075s
- slice_neme_table rc=0 png 1069s
- ch01_oruvel_storm rc=0 png 490s
- ch01_drop rc=0 png 667s
- ch01_bell_room rc=0 png 587s
- ch01_scale_hull rc=0 png 615s
- ch01_net_pen rc=0 png 661s
- ch01_hullgnaw_rises rc=0 png 654s
