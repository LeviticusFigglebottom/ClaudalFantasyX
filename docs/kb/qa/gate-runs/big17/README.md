# GATE lead/gate-big17 @ 1a986abf: screenshot results, PARTIAL (372 of 612 shots, 00:45 UTC 10-30)

**PARTIAL.** The capture is still running in the cloud gate session (lavapipe, one process per shot). This commit has
the first 372 shots so the Lead can start viewing; GATE-DONE replaces it with the full set and the final README.

- `compare.txt`: every compared shot's status and linear-light RMSE (only the 372 captured so far).
- `out/<id>.png`: the capture of every non-PASS shot, plus the PENDING ones (189).
- `sheets/new_NN.jpg`: the 45 shots with no baseline (43) or PENDING their first one (2), 6 to a sheet.
- `sheets/drift_NN.jpg`: BASE | OUT | DIFF for the 144 drifts over their limit, 3 to a sheet, largest RMSE first.
- The gate never writes or approves baselines.

So far: 372 compared, 187 FAIL (43 no baseline + 144 drift), 185 PASS (2 of them PENDING).
Spotted while checking the sheets (not a verdict): `drownbell_flood` OUT shows no party in the water, where the
baseline has them.
