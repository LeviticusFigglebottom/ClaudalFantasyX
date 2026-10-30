# Live log: SHOTS track (post-merge screenshot capture while the PC is offline)

Branch per batch: `lead/shots-bigN`. Output: `docs/kb/qa/gate-runs/bigN/` (`out/<id>.png`, `compare.txt`, `sheets/`).
Capture: `tools/screenshots/capture.sh --shots <id> --out ...` per shot (lavapipe, Forward+, `--fixed-fps 60`), 3 workers,
HYMN_SKIP_BLENDER=1, unique TMPDIR/XDG_DATA_HOME per worker. Baselines are never written. Compare uses
`tools/screenshots/compare.py`'s RMSE (linear light) against `tests/screenshots/baselines/`, read-only.
Contact sheets: BASE | OUT, 8 rows per sheet, for every non-PASS shot.

## big22 (claude/new-session-mj8c3c @ 19e7f01c)
- 13:38 UTC: import clean after `git lfs pull` (the checkout had LFS pointers: 193 Ogg decode errors before). Full manifest: 687 shots, 3 workers.
- 14:30 UTC: 182/687 captured: 123 PASS, 51 DRIFT, 8 NO-BASELINE, 0 failed. Drifts so far are content (villager face/hair/brow restyles, Asha clips, Haluna set, battle UI panels); unchanged shots match at RMSE 0.00000, so lavapipe parity holds. Chunks push every 20 min.
- Gotcha: after `git lfs pull` the pre-push hook failed with "Unable to verify locks"; fixed with `git config lfs.https://github.com/LeviticusFigglebottom/ClaudalFantasyX.git/info/lfs.locksverify false`.
- 17:00 UTC: 507/687: 307 PASS, 144 DRIFT, 44 NO-BASELINE, 12 timed out (600 s guard; heavy Haluna/slice cutscene scenes such as npc_haluna_*, slice_beach_h05/h06, slice_verse_*, slice_prologue_vigil_line). `slice_haluna_villagers_village` took 386 s and passed, so these look slow under 3-way contention, not deadlocked. They will be retried one at a time with HYMN_SHOT_TIMEOUT=1500 after the main pass.
- Seen: `Merge lead/gate-big24` at efe7fb10 (big23 included). big24 capture follows big22 on `lead/shots-big24`: shots whose scene's res:// closure touches a file changed in 19e7f01c..efe7fb10 (path refs, audio/docs excluded; about 400, driven by re-exported asha/fen_leech GLBs and kit changes), plus manifest-new/edited shots, plus every NO-BASELINE shot.
- 19:15 UTC: 598/687. Restarted the remainder with 2 workers and HYMN_SHOT_TIMEOUT=1500. Every pass-1 timeout re-captured cleanly (npc_haluna_* 770–800 s, slice_beach_* 815–1075 s, slice_dock_night_yes 1075 s, ch01_* 590–725 s): slow scenes, not hangs. **Suggest the 600 s per-shot guard is too low for these on lavapipe**; the gate should set HYMN_SHOT_TIMEOUT≥1500 for full-manifest runs.
- Seen: `Merge lead/gate-big26` at e605c9f4. The next capture is `lead/shots-big26`, covering 19e7f01c..e605c9f4 (big23–26): 435 path-affected shots plus every NO-BASELINE shot.
