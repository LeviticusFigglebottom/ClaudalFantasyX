# Gate big31 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 7c4c6de1 (Merge lead/gate-big30).

## Pinned heads (merged --no-ff, in order)
- claude/creatures @ 100f767f
- claude/hero-integration @ cbbbc34b
- claude/env-art @ 07f876e9
- claude/act1-chapters @ f243dec2
- claude/env-art-b @ 9a85e089
- claude/act2-plan @ 00314a8d
- claude/audio @ 1ad6cfc9
- claude/characters @ 418bc13f
- claude/m2-slice @ 4d5c9ed0
- claude/creatures-b @ c095cfec
- claude/battle-presentation @ b417e390
- claude/env-art @ 82c7033c

creatures' M3-HER-1168 (the threaded villager build: the Drownbell/Haluna reveal) isn't posted yet; per the Lead it goes
in the moment it posts, even mid-batch. A watcher is on claude/creatures. If it lands while lanes run, it is merged
between runs, followed by a fresh import and a re-gate of its tests. creatures' 2be4ee1f (the test_villager_routines fix)
is in.

## Resolutions
- act2-plan: compiled ch11_drowned_galleries.json and ch11_nhoa.json (generated) regenerated with tools/dlgc.py from the
  cleanly merged .dlg sources.
- battle-presentation: `tools/vfx/readability_sheet.gd.uid`: theirs. big30's gate had committed an import-written uid for
  the owner's script; the owner's own uid wins.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1063 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ 3a1ad626

## Fast gate
- Selected: 43 test files (plus test_villager_routines and test_qa_capsules, to re-check routed reds).
- Lane A (mine): 22; lane B (GATE-HELPER): 21, in `gate-big31-lanes-b.txt` @ 6a695535.
