# GATE lead/gate-big19 @ 5993e490: screenshot results, FINAL (247 of 254 shots, 09:06 UTC 10-30)

Fast gate (ADR 0205): only the 254 shots big19 can affect (the tracks' SELF-RENDERED / MERGE-READY / RENDER-REQUEST
ids since big17, plus every shot whose scene, or the scenes, resources and data it loads, changed). Lavapipe, one
process per shot, two parallel captures. The list is `shots.txt`. Non-blocking: big19 merged at GATE-FAST-DONE.

- `compare.txt`: every compared shot's status and linear-light RMSE.
- `out/<id>.png`: the capture of every non-PASS shot, plus the PENDING ones.
- `sheets/new_NN.jpg`: shots with no baseline or PENDING their first one, 6 to a sheet.
- `sheets/drift_NN.jpg`: BASE | OUT | DIFF for the drifts over their limit, 3 to a sheet, largest RMSE first.
- The gate never writes or approves baselines.

So far: compared 247; FAIL 176 (73 drift, 115 new/pending); PASS 71

FINAL: both captures done (18382 s and 19608 s of wall time, paused while big20's and big21's blocking tests ran).
7 shots have no capture: their Godot process hung past 900 s or aborted. See `godot_failures.txt`:
slice_beach_h05_asha, slice_beach_h06_toma, slice_beach_standing, slice_dock_night_yes and slice_neme_table hung;
battle_boss_intro_reach aborted (exit 134); villager_hobb_face exited 1. The slice shots' hangs match m2-slice's
`hold_line` red (test_slice_shots).
