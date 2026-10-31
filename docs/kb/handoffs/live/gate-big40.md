# Gate big40 (fast gate, ADR 0205)

Base: **lead/gate-big39 @ 700bf014** (the rebuilt big39's GATE-FAST-DONE tip; the Lead asked for big40 straight away).

## Pinned heads (merged --no-ff, in order; pass-7 art rows first)
- claude/env-art-b @ db144a6c
- claude/battle-presentation @ 519cbf4b
- claude/m2-slice @ e772aa1f
- claude/hero-integration @ abdd0a05
- claude/act1-chapters @ 5a166cf2
- claude/ui @ aa45f467
- claude/creatures-b @ 80af10c4

- env-art-b @ db144a6c: **row 81** (7e7a4d38: the Brine channel's banks sink flush with the flats).
- battle-presentation @ 519cbf4b: **row 61 signed off on big38** (0afcaf44: the Undertow's Reach lit, with a moonlight rim and key). 34bb40ca was already in.
- m2-slice @ e772aa1f: slice-polish's row 75 note (on the PC's big38 still: 34% dark, the hull reads).
- env-art: **no new commits.** The Lead's "env-art 2a0e5c12" isn't on any branch (unknown object); it goes in when pushed.
- **characters: held at b0cf4111** (in big39). Its head still carries the Act III WIP: `assets/characters/props/act3/` with no PROVENANCE
  rows, and e12c0305e parks the Wardens' entries. There are no new Act I rows past b0cf4111. It comes back once the rows exist.
- Held out: claude/act2-plan (not yet rebased onto act1-chapters' Ch17).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1106 files) · test_gdignore_imports OK · no
conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids. The characters WIP (c61187ce) didn't come in through any branch.

GATE-BUILT @ 5bf99483

## Fast gate
- Selected: 43 test files.
- Lane A (mine): 22; lane B (GATE-HELPER): 21, in `gate-big40-lanes-b.txt` @ 9c120402.
