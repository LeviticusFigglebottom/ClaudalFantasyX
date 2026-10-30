# Gate big28 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 9572c412 (Merge lead/gate-big27).

## Pinned heads (merged --no-ff, in order; the Lead's priority first)
- claude/hero-integration @ 799b6633
- claude/ui @ fc6d2d1c
- claude/act1-chapters @ 75c8c06a
- claude/act2-plan @ 1cb0e1f6
- claude/env-art @ 8321aebf
- claude/env-art-b @ b31a5152
- claude/audio @ 90992bc6
- claude/creatures @ ba244513
- claude/characters @ e8157319
- claude/m2-slice @ b710cfa9
- claude/creatures-b @ 5e3492af
- claude/battle-presentation @ e72820da
- claude/creatures @ dbc3628a
- claude/env-art @ 35081a52

The Lead's list is all in: integration-qa 799b6633 (row 74: every fight, scripted ones too, keeps the field resident;
the last piece of the human's post-battle black-screen report), ui 07386b3d (first-time tip fixes), act1-chapters'
newest (the Act I story fixes M4-A2P-116/117), act2-plan's newest (tip and tutorial text), env-art 922cd122 (the
Underway caustics; its newer head 35081a52 adds an in-progress log line only), env-art-b, audio and creatures' newest.
slice-polish has no new commits (its M4-A2P-115 fixes aren't pushed yet).

## Resolutions
- None needed: every merge was clean (ownership.md and append-only files through merge_union).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1058 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ e94beb97

## Fast gate
- Selected: 100 test files.
- Lane A (mine): 50; lane B (GATE-HELPER): 50, in `gate-big28-lanes-b.txt` @ e4a5e089.
- Lead (18:45): battle-presentation @ 5aa9f169 (064c9e46 crawler and Vowbound effects, bdc5ef22 Act II boss intros) and creatures-b @ ≥ 6973ffc0 (the Lamp Engine lineup fix): both already in (pinned heads e72820da and 5e3492af).
