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
