# Gate big44 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ a86c366f (Merge lead/gate-big43).

## Pinned heads
- claude/characters @ 137b6597: row 56 polish (cloud pass 6): the underskirt drawn in under the outer skirt, so no notch shows through its folds.
  The only head with new commits since big43.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1107 files) · test_gdignore_imports OK · no conflict
markers · no new duplicate PROVENANCE rows.

GATE-BUILT @ 06588c8d

## Fast gate
- Selected: 3 test files (plus test_hero_stage for big42's routed red).
- Lane A (mine): 2; lane B (GATE-HELPER): 1, in `gate-big44-lanes-b.txt` @ 2e9f94b8.
