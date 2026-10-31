# Gate big35 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 9317c6b6 (Merge lead/gate-big34).

## Pinned heads (merged --no-ff, in order; the Lead's priority first)
- claude/act1-chapters @ 782ff863
- claude/hero-integration @ 6555ccf4
- claude/env-art @ 6f0aee74
- claude/env-art-b @ b3e7c493
- claude/ui @ fa75e3ed
- claude/creatures @ b97186e3
- claude/audio @ 1c14fa74
- claude/characters @ f0ce0f53
- claude/battle-presentation @ 94ee0995

- act1-chapters @ 782ff863 carries the 23:05 FAST-TRACK: d74da756 (a touch beat entered while a scene plays is kept and plays
  when the scene ends), f46ec395 (Ch9's landing trigger and its marker on the strand), and Ch8's interior headless.
- integration-qa's cross-zone prewarm (the Drownbell, 8.2 s on the PC) isn't posted yet. A watcher is on
  claude/hero-integration; it is merged between test runs, followed by a fresh import and a re-gate.

## Resolutions
- Every merge was clean. On flags.tres, merge_union used what the two real merge bases agree on; no flag was dropped or
  duplicated (one line gained a trailing comma before the appended rows).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1083 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ a22bb284

## Fast gate
- Selected: 140 test files.
- Lane A (mine): 70; lane B (GATE-HELPER): 70, in `gate-big35-lanes-b.txt` @ f91030ac.

## Mid-batch (the Lead, 00:26): ReturnPark, the human's last playtest item
- **claude/hero-integration @ 74c732fc**: eea6c24e, row 74, a fight builds its cross-zone return scene while it runs
  (ReturnPark, ADR 0209). The Drownbell → Haluna field-in goes from 3.39 s to 1.05 s headless. Clean; checks clean (validate_data
  0/0, taskboard, gdlint, gdformat 1085).
- To avoid testing a half-imported tree (big24's lesson), lane A was stopped at 50 of its 70 files (50 done, all green but the
  routed test_qa_capsules), then the merge, then a fresh import. The re-gate is 33 files: lane A's 20 unrun ones, the
  merge's selection, and every scene_router, return_park, battle_return, field_battle, battle_request and resident test,
  plus a fresh tools suite. Every log is scanned for the engine's `Parameter "t" is null` (1 in 5 parked runs logged it,
  per the Lead); if it appears it is routed to integration-qa and doesn't hold the batch.
