# Gate big43 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 6980e847 (Merge lead/gate-big42).

## Pinned heads
- claude/characters @ b48c6325: row 56 skirt polish, WIP (a5698164: the reduced hem swing eased in over starts and out over stops; b48c6325: in the
  locomotion clips the staff keeps clear of the full swing's cloth). The only head with new commits; no other branch moved since big42.
- A watcher is on claude/characters for the polish's MERGE-READY. It is merged between test runs, then a fresh import and a re-gate.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1107 files) · test_gdignore_imports OK · no conflict
markers · no new duplicate PROVENANCE rows.

GATE-BUILT @ a6c072dc

## Fast gate
- Selected: 1 test files (plus test_hero_stage, to re-check big42's routed red).
