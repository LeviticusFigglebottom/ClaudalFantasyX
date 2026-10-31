# big30 capture (SHOTS track, cloud lavapipe)

- Source: `claude/new-session-mj8c3c` @ 7c4c6de1 (Merge lead/gate-big30), covering big23–big30. HYMN_SKIP_BLENDER=1, LFS pulled, clean import.
- Selection (609 of 758): shots whose scene's res:// path closure touches a file changed in 19e7f01c..7c4c6de1 (audio and docs
  excluded), or that were added or edited in shots.json, plus every shot without a baseline at 7c4c6de1.
  Not selected (149): shots with a baseline and no changed file in their closure. They are expected to match big22's PASS/DRIFT state.
- Renderer and compare: as in big22 (Forward+ on llvmpipe, `compare.py` linear RMSE, baselines read-only). 3 workers,
  HYMN_SHOT_TIMEOUT=1500, and each worker has its own Xvfb display (`:200+k`) to avoid the wrapper's display race.
- `out/<id>.png` for every captured shot; `compare.txt`; `sheets/` (BASE | OUT, 8 per sheet, every non-PASS shot).

## Failed to capture (timeout at 1500 s with 3 workers)
ch10_causeway_r03, ch10_tide_f02, ch10_tide_t04, ch10_outside_r07: new pending_baseline ch10 cutscene shots
(slice_cutscene_shot.tscn, settle 480–900 frames). Their sibling ch10_edge_o02 captured in 1457 s, so these are slow rather than
hung; the log shows only a `CutsceneSequencer(ch10_causeway): no actor 'owa' on the stage` warning. They are re-run in the
next capture with a solo worker and a longer limit.
