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
- LEAD-ANSWERED (01:41):
  1. Ch17 flow: **act1-chapters' version stands** (9a42a42a, 4a6418b5; it owns `game/levels/ch1x`). act2-plan's a2bc108d stays out;
     act2-plan merges integration and rebases its Ch18 work (36c65c41) onto act1-chapters' Ch17.
  2. The .res conversion: **characters' own rebuild stands** (abf7391b). creatures-b's a0ba7200 stays out; creatures-b drops or
     reverts it and files the .res idea as a request task to characters. The rest of creatures-b's head (the Act III bosses)
     joins a batch once it's rebased.

## Late merge: characters @ 8b7fce9c
- After the pass-7 re-gate: characters' newest, with **row 56** (37f63713, Asha's skirt WIP: the neighbour lag 40 → 60°) and
  8b7fce9c (Sefir rebuilt, row 54; Fenn's and Sabe's head maps, row 55). Clean. The batch's tools-suite **test_hero_locomotion**
  red (locomotion.json not matching its generator) was characters' own WIP at b99cf56c, and its later commits regenerate the
  file: now OK. Re-import plus test_field_motor 9/0 and test_hero_field_gait 13/0.

## Fast-gate results
- Import check clean · boot 0 ERROR lines · log check 0 throughout. **`Parameter "t" is null`: not seen** in any log.
- Lane A (mine, 57 files): all green. The pass-7 re-gate (38 files, fresh import): all green.
- Lane B (GATE-HELPER, 57 files @ df7ed3f9, arrived 01:36): 56 green.
  - **test_qa_dock_edges** 1/1: Hollowmere's HullDeck, Cabin, EngineBay and Berths spawns let the hero stand 0.7–1.0 m deep in the
    water (around x 76–90). Red on claude/act1-chapters alone (env-art-b green; probed). Routed: **act1-chapters** (its Ch17 Hollowmere
    layout or spawns vs FieldShore). On the final tree after the characters merge the file ran 0 tests; that wasn't investigated.
- Tools suite (217 units, plus the fast ones re-run on the final tree):
  - **test_rig_integrity Asha** (after characters' row 56): `prop through_garment`, the staff shaft crosses the skirt at run@6. That is
    characters' skirt WIP. Routed: **characters**.
  - Routed as before: test_act1_audio_audit and test_battle_vfx_coverage (act1-chapters); test_cutscene_sfx_files, test_villagers
    and test_hero_clips (the Act III scripts, act2-plan). Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ a66748c3 (merge-approved: no batch-caused red; act2-plan and creatures-b held out per the Lead).
In: PC pass 7 (integration-qa rows 74/68; characters rows 46/54/55/56; slice-polish rows 18/75; env-art rows 59/76/77/83;
env-art-b rows 62/82/84; battle-presentation row 61) and creatures' CrowdFar threading. Routed: act1-chapters (test_qa_dock_edges,
plus its earlier reds), characters (test_rig_integrity Asha), act2-plan (Act III cues and clips; Ch17 rebase), creatures-b (drop
a0ba7200, rebase).
