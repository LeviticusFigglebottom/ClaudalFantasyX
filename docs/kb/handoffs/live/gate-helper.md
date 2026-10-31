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
- big29 @ 43af4e0c (HEAD checked): lanes B 22 files, 19:30-19:32 UTC (2 min). 21 green, 1 red:
  test_cutscene_face_per_actor (1 failed: Sefir's shipped face poses, game/data/cutscene/sefir_face_poses.json, drifted
  from the character source in `sad` and `tender`). Result: gate-big29-lanes-b-result.md.
- big30 @ f2b6b633 (HEAD checked): lanes B 52 files, 20:33-20:50 UTC (17 min). **All 52 green.**
  Result: gate-big30-lanes-b-result.md.
- big31 @ 6a695535 (HEAD checked): lanes B 21 files, 21:10-21:13 UTC (3 min). **All 21 green.**
  Result: gate-big31-lanes-b-result.md.
- big32 @ 7f6211b3 (HEAD checked): lanes B 3 files, 21:49-21:52 UTC (3 min). 2 green, 1 red:
  test_qa_capsules (1 failed: abiding_first, abiding_guard and court_stillguard fight as primitive stand-ins, with no actor
  scene in battle_sandbox or creatures). Result: gate-big32-lanes-b-result.md.
- big33 @ 1067c447 (HEAD checked): lanes B 27 files, 22:32-22:48 UTC (16 min). 26 green, 1 red:
  test_debug_overlay (1 failed: game/core/scene_router.gd names SceneSwapProbe, a class under game/core/debug/, which the
  release build strips). Result: gate-big33-lanes-b-result.md.
- big34 @ ec0a766c (HEAD checked): lanes B 5 files, 23:11-23:23 UTC (12 min). **All 5 green.**
  Result: gate-big34-lanes-b-result.md.
- big35 @ f91030ac (HEAD checked): lanes B 70 files, 00:12-00:38 UTC (26 min). 69 green, 1 red:
  test_battle_act2_ability_vfx (1 failed: 15 Act II foe skills of abiding_first, abiding_guard, court_stillguard, flat_engine,
  malcor_venn and storm_crawler have no effect of their own; the list is in the result). Result: gate-big35-lanes-b-result.md.
- big36 @ df7ed3f9 (HEAD checked): lanes B 57 files, 01:06-01:35 UTC (29 min). 56 green, 1 red:
  test_qa_dock_edges (1 failed, 14 lines: in hollowmere.tscn the hero walks off the dock from HullDeck, Cabin, EngineBay and
  Berths and stands 0.7-1.0 m deep in the water, x 76-90, y -2). Result: gate-big36-lanes-b-result.md.
- big37 @ b76e6c32 (HEAD checked): lanes B 22 files, 02:16-02:23 UTC (7 min). **All 22 green.**
  Result: gate-big37-lanes-b-result.md.
- big38 @ bdfd9311: the lanes B list held 0 test files (d2dcb965d); nothing to run, empty result pushed.
- big39 @ 4793c37e (HEAD checked): lanes B 4 files, 03:52-03:54 UTC (2 min). **All 4 green.**
  Result: gate-big39-lanes-b-result.md.
- big40 @ 9c120402 (HEAD checked): lanes B 21 files, 05:02-05:07 UTC (5 min). 20 green, 1 red:
  test_battle_party_kits (1 failed: hesper_oan's wardens_go_home and cage_chains on cage_orin, cage_halde, cage_isse and
  cage_cael stage as a melee run at one hero, which this reach test does not expect). Result: gate-big40-lanes-b-result.md.
- big41 @ 4eb49fff (HEAD checked): lanes B 5 files, 05:50-06:00 UTC (10 min). **All 5 green.**
  Result: gate-big41-lanes-b-result.md.
- big42 @ 64e308db (HEAD checked): lanes B 6 files, 06:51-06:53 UTC (2 min). **All 6 green.**
  Result: gate-big42-lanes-b-result.md.
- big43 @ 43f4c49b: the lanes B list held 0 test files; nothing to run, empty result pushed.
- big44 @ 2e9f94b8 (HEAD checked): lanes B 1 file, 08:07 UTC (<1 min). **Green.** Result: gate-big44-lanes-b-result.md.
- big45 @ 3fc847a9: the lanes B list held 0 test files; nothing to run, empty result pushed.
