# Gate big33 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 8889542f (Merge lead/gate-big32). Act III (M5-A3P) work rides the batches from
here on (ADR 0207).

## Pinned heads (merged --no-ff, in order; the Lead's priority first)
- claude/act1-chapters @ c2616407
- claude/m2-slice @ 97c591c3
- claude/hero-integration @ 7fbb97a9
- claude/env-art @ deff0d41
- claude/env-art-b @ 1281c188
- claude/act2-plan @ fee86431
- claude/ui @ d6d05a6d
- claude/creatures @ f2c0e49b
- claude/audio @ 14f59173
- claude/characters @ 425abec3
- claude/creatures-b @ 8dfdbaa9
- claude/battle-presentation @ 78b0a1bb
- claude/creatures @ b05a9294

The Lead's list is in: act1-chapters 7a37c3d5 (the Ch6/Ch8 Act I objectives FAST-TRACK), slice-polish's 97c591c3 on
claude/m2-slice (M4-A2P-070: Haluna's beach actor posed a frame after the swap, part of the Haluna add-frame split),
integration-qa's newest (the --ready-profile probe), and every other new head.

## Resolutions
- ownership.md: three new Act III claim rows (env-art's Ch20 memory rooms and Undertow kit; env-art-b's Ch17 Hollowmere
  dry-dock; creatures-b's Act III bosses and Vowbound), kept by the marker strip. There are no duplicate paths, and the
  table is intact.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1072 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ c2f4ec9f

## Fast gate
- Selected: 55 test files (plus test_qa_capsules for the routed red).
- Lane A (mine): 28; lane B (GATE-HELPER): 27, in `gate-big33-lanes-b.txt` @ 1067c447.
