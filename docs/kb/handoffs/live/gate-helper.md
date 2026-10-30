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
- **CORRECTION 17:05 UTC: big25's result above is INVALID.** My checkout of 829b09a6 failed (the import's
  .uid and .import files blocked it) and the script went on at big24's 797b02cc. big26's run hit the same fault and was not
  pushed. Fixed (the run now resets my own scratch worktree, aborts on a failed checkout and checks HEAD); rerunning
  big26 @ e8ae9b74 now, then big25 @ 829b09a6.
- big26 @ e8ae9b74 (rerun, HEAD checked): lanes B 60 files, 16:57-17:10 UTC (13 min). **All 60 green.**
  test_footsteps_jog, test_input_parity_pad_walk and test_qa_dock_edges now run (they were the 0-run files at the wrong
  sha). Result: gate-big26-lanes-b-result.md.
- big25 @ 829b09a6 (rerun, HEAD checked; replaces the invalid result): lanes B 16 files, 17:10-17:26 UTC.
  **All 16 green**, so test_causeway_route's red earlier was big24's code, not big25's.
- big27 @ 66ae0cc2 (HEAD checked): lanes B 27 files, 17:56-18:08 UTC (12 min). **All 27 green.**
  Result: gate-big27-lanes-b-result.md.
- big28 @ e4a5e089 (HEAD checked): lanes B 50 files, 18:51-19:12 UTC (21 min). **All 50 green.**
  Result: gate-big28-lanes-b-result.md.
