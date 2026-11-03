# Handoff: env-art, 2026-11-03 (session 1)

Branch `claude/env-art`. Integration `claude/undertow-lead-handoff-ze8rrn` @ e2411fb0, fast-forwarded in.
Lead: session_018aiGwGLGkxsnMnu8VfCu1m.

## Done
- PC rows 24, 47 and 77: the fixes (8f0b0188, 6c08bd85) postdate the PC's big38 check. Re-verified on this head
  by self-render (walk stills for DockShore, brightwater_landing_f01/f06, oruvel_o17_pen_split).
- Row 86, my part: Lowlight's floor patch. A kit bug (the bay's rubble on a zero-width range); the rubble now lies on
  the sun's pool (fa34e5f6, 1881f2b5).
- Row 90: probed on lavapipe. There are no compiles and no spike after the fade, so it needs a GPU re-measure with
  the screen on (PC-QUEUE).
- FAST-TRACK 4 (Ch1): the `oruvel_raft_storm` arena with the real UndertowStorm, and `ArenaCameraReach`
  (M3-ENV-1340, 52bf4c11).
- M3-ENV-1222 set to review (both halves were already built).
- Act II (ADR 0205 §4): M4-A2P-115 (Quellan at eye height: the road walls' unbounded crag mesa, the road notch,
  flagged yards, house footings) and M4-A2P-1501 (Ch11 drift, and no flicker: all of Ch11's light is bound), both
  to review, MERGE-READY @ ad228e53.

## In progress
- Nothing un-pushed.

## Exact next step
1. If the Lead routes the repoint back to env-art: set `"arena": "oruvel_raft_storm"` on `ch01_scuttlers` and
   `ch01_hullgnaw` in game/data/battle/encounters.json, and update tests/unit/test_battle_arena.gd lines 15–16.
2. Otherwise, Act II, in my lane (Ch10–Ch12): M4-A2P-040/041/042 are `doing` and STALE on the board. Re-walk Ossa
   Fen, Reedhollow, Lowlight, the Sunken Vey, Keth Pass, Quellan and Cloudloom at eye height (as for M4-A2P-115:
   `walk_render.tscn`, four views per spawn), fix what reads unfinished, then move each to review. Act III stays
   paused (ADR 0205 §4).

## Known issues
- `arena_scenes.py` with no `--arena` rewrites env-art-b's wrapped arenas. Always pass `--arena`.
- The arena's Undertow can't stand nearer than ~14 km: the raft would be under its canopy.
- `test_every_glb_import_runs_its_category_script` is red on integration for cinematics' and characters' imports
  (LEAD-ASK in the live log).

## Files touched
assets_src/environments/kits/haluna/{lowlight_zones.py,arena_scenes.py}, assets/environments/kits/haluna/lowlight_hall.glb,
assets/environments/arenas/oruvel_raft_storm/, game/world/arenas/{arena_camera_reach.gd,battle_arena_root.gd},
game/levels/_tests/battle_arenas/preview_oruvel_raft_storm.tscn, tests/screenshots/shots.json,
tests/unit/test_battle_arenas.gd, tools/tests/{test_arenas.py,test_ch11_lowlight_dressing.py}, tools/act1/walkthrough.py,
assets/PROVENANCE.md, docs/kb/tech/battle_arenas.md, docs/kb/tasks/M3/M3-ENV-{1222,1340}*.md,
docs/kb/handoffs/live/env-art.md.
