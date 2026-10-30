# Live log: SHOTS track (post-merge screenshot capture while the PC is offline)

Branch per batch: `lead/shots-bigN`. Output: `docs/kb/qa/gate-runs/bigN/` (`out/<id>.png`, `compare.txt`, `sheets/`).
Capture: `tools/screenshots/capture.sh --shots <id> --out ...` per shot (lavapipe, Forward+, `--fixed-fps 60`), 3 workers,
HYMN_SKIP_BLENDER=1, unique TMPDIR/XDG_DATA_HOME per worker. Baselines are never written. Compare uses
`tools/screenshots/compare.py`'s RMSE (linear light) against `tests/screenshots/baselines/`, read-only.
Contact sheets: BASE | OUT, 8 rows per sheet, for every non-PASS shot.

## big22 (claude/new-session-mj8c3c @ 19e7f01c)
- 13:38 UTC: import clean after `git lfs pull` (the checkout had LFS pointers: 193 Ogg decode errors before). Full manifest: 687 shots, 3 workers.
