# Gate big36 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 6df68f05 (Merge lead/gate-big35).

## Pinned heads (merged --no-ff, in order; the Lead's PC pass-7 priority first)
- claude/hero-integration @ 56410bdf
- claude/characters @ b99cf56c
- claude/m2-slice @ bbee8146
- claude/env-art @ 015bae26
- claude/env-art-b @ 3ebdff07
- claude/act1-chapters @ 196b6246
- claude/ui @ e35d3650
- claude/creatures @ b868b21d
- claude/creatures @ 87d6824a

PC pass 7, as merged: integration-qa 1d2a9476 (rows 74/68: prewarm the parked return during the fight, one family of loads
at a time, ADR 0209 amendment) and a5212956 (row 74: big meshes' occlusion triangles on the zone's worker thread);
characters b99cf56c (WIP: the jog's torso counter-turn and steady head; Sefir's front) and bdc06684 (row 46); creatures'
16fbcf8d (M5-A3P-1809, CrowdFar off the main thread: worst frame 5.3 s down to 48 ms); and the m2-slice (slice-polish), env-art,
env-art-b, act1-chapters, ui and creatures heads. battle-presentation and audio had no new commits.

## Held out (cross-owner conflicts; LEAD-ASK)
- **claude/act2-plan @ 3bbbab74**: **M5-A3P-1001 (Ch17 at Hollowmere, staging and flow) was built twice.**
  act1-chapters (ours, 9a42a42a and 4a6418b5; the task file says `doing`, owner act1-chapters, which owns `game/levels/ch1[0-9]/**`)
  and act2-plan (theirs, a2bc108d, "supplementing act1-chapters, the Lead 2026-10-30 23:26"; the task file says `review`). Its Ch18
  critical path (36c65c41, M5-A3P-1004) sits on top. Eleven files conflict: chapters.json, ch17.json and test_ch17_thread.gd
  (add/add), ch17_zone.gd, hollowmere_layout.json, qa_known.json, chapter_flow_check.py, tools/act2/ch10_greybox.py, and
  tools/act1/ch15_16_greybox.py (deleted on one side). Picking one implementation is the owners' call, not the gate's.
  LEAD-ASK: whose Ch17 flow stands? The other side then rebases its Ch18 work on it and merges integration into its branch.
- **claude/creatures-b @ 30ec17e9**: a0ba7200 (M4-A2P-1980) converts **characters'** Asha and Rhen clip
  libraries to compressed binary .res (hero_clips.py, the stage scenes, scene_loads.json and the import rule changed). It
  conflicts (modify/delete) with characters' own rebuild of the .tres (abf7391b, M3-CHR-1000), so either side breaks the other.
  LEAD-ASK: characters to take the .res conversion into its own pipeline (or say no), then creatures-b drops or rebases
  a0ba7200. Its Act III boss work (M5-A3P-1851..1853) waits behind that.

## Resolutions
- Everything else merged clean.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1089 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ 7d5693ac

## Fast gate
- Selected: 114 test files.
- Lane A (mine): 57; lane B (GATE-HELPER): 57, in `gate-big36-lanes-b.txt` @ df7ed3f9.

## Mid-batch (the Lead, 01:21), merged after lane A finished
- integration-qa's rows 74/68 (1d2a9476, the prewarm during the fight and one family of loads at a time) were already in.
  - claude/env-art @ e119e6a8
  - claude/env-art-b @ b1c10bc4
  - claude/battle-presentation @ 617d91f0
  - claude/m2-slice @ ff50ec33
  These carry env-art 7769d2ad (pass-7 rows 59, 76, 77, 83), env-art-b's rows 62, 82, 84, battle-presentation **34bb40ca** (row 61:
  the Reach's rest frame looks up its arm) and slice-polish's **row 18** (4edda074 and ff50ec33: C07 frames the harrier; its
  aim_node comes from the causeway generator), plus row 75's dive rim (dd808caa, not yet viewed). All clean; checks clean.
- Re-gate: a fresh import plus the 38 files these merges touch, with the `Parameter "t" is null` scan.
