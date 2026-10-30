# Gate big32 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 25ed4702 (Merge lead/gate-big31).

## Pinned heads (merged --no-ff, in order)
- claude/m2-slice @ ff317f99
- claude/hero-integration @ 12789126
- claude/act2-plan @ 7934f45c
- claude/creatures @ 143daa28
- claude/characters @ 39ef46eb
- claude/creatures-b @ 488de2fd
- claude/battle-presentation @ 178b3a8c
- claude/hero-integration @ c125d631

The Lead's priority items aren't posted yet: slice-polish's Haluna add-to-tree split (the last of the human's black-screen
report; slice-polish's commits arrive on claude/m2-slice) and act1-chapters' Ch6/Ch8 objective rows (act1-chapters has
no new commits). A watcher is on both. Either one is merged between test runs, followed by a fresh import and a re-gate.

## Resolutions
- None needed: every merge was clean.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1064 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ d8fa3da2

## Fast gate
- Selected: 7 test files (plus test_qa_capsules for the routed red).
