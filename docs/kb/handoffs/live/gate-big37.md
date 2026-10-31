# Gate big37 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 1983de0a (Merge lead/gate-big36).
(Gate tooling moved to a new local working folder this batch; nothing in the repo changed because of it.)

## Pinned heads (merged --no-ff, in order)
- claude/characters @ b2ec6cf3
- claude/audio @ f376c6fc
- claude/creatures-b @ d7b6fff8
- claude/m2-slice @ 64f0ed5b
- claude/act1-chapters @ 4f6da2dd
- claude/ui @ e081f95c
- claude/act1-chapters @ eb4536e3

- characters @ b2ec6cf3: Asha's library (the jog counter-turn) and **row 56 settled**. b2ec6cf3 reverts the skirt lag to 40,
  because 60 let the staff cross skirt_13 (big36's rig_integrity Asha red). Rows 54 and 55 (Sefir's front, Fenn).
- audio @ f376c6fc: 5537dc6e, UiAudio never connects a signal twice (the `used` reconnect hardened), and the Act III cutscene sounds.
- **creatures-b @ d7b6fff8 (rebased per the Lead):** c8f7af0b reverts a0ba7200 (no .res conversion of characters' clips), and
  9b585ee0 offers it to characters as M4-A2P-1981; plus the Act III bosses. The only conflict was ownership.md.
- act1-chapters @ eb4536e3: M5-A3P-1007, Ch19 at Iskarra (the plaza, the hitch, the Lamp Spire).

## Held out
- **claude/act2-plan @ cffc73e1**: not yet rebased onto act1-chapters' Ch17 (the Lead's 01:41 answer). It still holds
  a2bc108d and conflicts in 12 files (M5-A3P-1001's task file, flags.tres, chapters.json, ch17.json, ch17_zone.gd,
  hollowmere_layout.json and others). Its newer Act III work (Ch21 and the Ending, M5-A3P-1015) waits behind that. act2-plan:
  merge integration, take act1-chapters' Ch17 files, then put Ch18 to Ch21 on top.

## Resolutions
- ui's tests/integration/test_memory_replay.gd (M5-A3P-1710): a 123-column doc comment rewrapped to 120 (gdlint; the same line
  is on claude/ui).
- creatures-b's ownership.md rows: kept by the marker strip; no duplicate paths.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1094 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ 8c1ab2d3

## Fast gate
- Selected: 44 test files.
- Lane A (mine): 22; lane B (GATE-HELPER): 22, in `gate-big37-lanes-b.txt` @ b76e6c32.

## Mid-batch (the Lead, 02:41): row 85, the 59 GB shutdown log on the human's PC
Merged after both lanes were green (lane A 22/22, lane B 22/22 @ b76e6c32, arrived 02:24):
- claude/hero-integration @ 8cb73872: **row 85**, the off-tree resident zone and the parked return are freed as the tree quits
  (clean shutdown).
- claude/creatures @ 5a0a0df8: **f6c23ed1, M3-CRE-707 (row 85)**: override materials free after their meshes (the storm figure).
- claude/characters @ aa4fa100 (≥ fd9b4879): the jog counter-turn and Asha's skirt; M3-CHR-1000 in review.
All clean; checks clean (validate_data 0/0 · taskboard · dlgc · gdlint · gdformat 1096). Re-gate on a fresh import: the 19 files these
merges touch plus every resident, return_park, scene_router and storm test. Each log's size and the boot run's quit (ERROR and leak lines)
are recorded.

## Fast-gate results
- Lane A (mine, 22 files) and lane B (GATE-HELPER, 22 files @ b76e6c32): all green. Import and boot clean; log check 0;
  **`Parameter "t" is null`: not seen.**
- Row-85 re-gate (19 files, fresh import): 18 green. The boot run's quit has 0 ERROR lines and a 2.4 KB log; the largest test log is
  271 KB (no runaway log). It carries one "ObjectDB instances leaked at exit" warning, which was already in this batch's first boot log.
  - **test_clean_shutdown** 1/1 (integration-qa's new row-85 test): the probe's child Godot never starts. The test launches
    `OS.get_executable_path()`, which on the cloud's fetched Godot (tools/dev/fetch_godot.py's sysroot) is the loader,
    `ld-linux-x86-64.so.2: unrecognized option '--headless'`, so the exit time reads as garbage (1.79e9 s). The same holds on
    claude/hero-integration alone: an environment assumption in the test, not the fix. Routed: **integration-qa** (launch
    through the godot wrapper, or skip when the executable is a loader). The real check is the PC's shutdown.
- Tools suite (221 units; the new ones re-run on the final tree). Each new red traces to one branch's own merge:
  - test_status_names: memories.csv `MEMORY_CH04_SHELL_IS_SET` uses the old "Shell" status name (ADR 0202: Tide Ward), from **ui**.
  - test_freed_cast_lint: a new hit at `game/audio/prop_audio.gd:77`, from **audio**.
  - test_ch08_flow and test_act1_flow_audit: ch08's arrive row names an undeclared objective flag, and the ch05/ch07/ch08 arrive rows
    can't run, from **act1-chapters**.
  - test_creatures: the new Act III bosses old_shoal and the_cage have clips under the floor (up to 0.37 m), from **creatures-b**.
  - test_rig_integrity Asha: **characters** (as before). Still routed: test_act1_audio_audit and test_battle_vfx_coverage
    (act1-chapters); test_cutscene_sfx_files, test_villagers and test_hero_clips (act2-plan, Act III). Known: test_palette_check,
    test_screenshots.

GATE-FAST-DONE @ 6ffaf223 (merge-approved: no batch-caused red). In: **row 85** (integration-qa 8cb73872, creatures
f6c23ed1), characters' jog counter-turn and skirt, audio's UiAudio hardening, creatures-b rebased, act1-chapters' Ch19. Held out:
act2-plan (not yet rebased on act1-chapters' Ch17). Routed: integration-qa (test_clean_shutdown), ui (test_status_names), audio
(test_freed_cast_lint), act1-chapters (test_ch08_flow, test_act1_flow_audit, plus earlier), creatures-b (test_creatures), characters
(rig Asha, test_hero_clips), act2-plan (Act III cues and clips).
