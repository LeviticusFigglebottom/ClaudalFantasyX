# Gate-helper live log

The cloud gate-helper session (`session_01UPFyE8yvVQq7sK9XruLDxk`) runs the second half (lanes B) of each batch's
filtered Godot test files, beside the gate session (`session_01UPFyEAXofxWazWNnRTzFGJ`), per ADR 0205. It only runs
and reports; it never edits game or test files.

## How it works
- Polls the newest `origin/lead/gate-bigN` every 3 min for `docs/kb/handoffs/live/gate-bigN-lanes-b.txt`
  (line 1 `# sha <sha>`, then one res:// test file per line).
- Checks out exactly that sha (LFS pulled, re-imported), runs each file with
  `godot --headless --path . res://tests/run_tests.tscn -- --filter=<file stem>` in 3 lanes, 1800 s per file, a fresh
  XDG_DATA_HOME per file.
- Note: the runner's filter is a substring match, so a stem that prefixes another file's name runs both.
- Pushes `docs/kb/handoffs/live/gate-bigN-lanes-b-result.md` to `lead/gate-helper`.

## Log
- 2026-10-30 13:45 UTC: set up (Godot 4.6.3, import done at big23's head, 197 LFS objects pulled). Polling from
  big23 on.
- big24 @ 797b02cc: lanes B 35 files, 14:18-14:32 UTC (14 min, import included). 33 green, 2 red:
  test_causeway_route (1 failed: fewer than 2 fights on the 206 m walk after the harrier) and test_resident_loads
  (1 failed: haluna.tscn's resident list lacks the shopkeeper, smith and innkeeper actors; rerun
  tools/loading/scene_loads.gd). Result: gate-big24-lanes-b-result.md.
- big25 @ 829b09a6: lanes B 16 files, 16:13-16:28 UTC (15 min, import included). 15 green, 1 red:
  test_causeway_route (1 failed, the same as big24's: fewer than 2 fights on the 206 m walk after the harrier).
  Result: gate-big25-lanes-b-result.md.
