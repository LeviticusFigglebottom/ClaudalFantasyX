# Gate big26 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 4b198810 (Merge lead/gate-big25).

## Pinned heads (merged --no-ff; the Lead's priority first)
- claude/env-art @ 3da64040 (incl. bc790ea8, Oruvel hull vs deck: the human's playtest follow-up)
- claude/hero-integration @ 9e81e0c3 (integration-qa: b335f032 run speed vs the jog; 314559cf the big24 FAST-TRACK,
  FieldShore's catch leaves a hero under a surface alone, which fixes Lowlight's Sanctum / test_qa_field_camera)
- claude/act1-chapters @ 3586d500 (incl. d19b47b9)
- claude/act2-plan @ 339f298a (incl. f5f0be21)
- claude/creatures @ 6ee7b51e (incl. 517c2270, d7509e52)
- claude/ui @ ce2e3f3e (Act II portraits)
- claude/env-art-b @ 69346fde
- claude/characters @ fef2636e (the villager limits / shoulder fix, MERGE-READY)
- claude/creatures-b @ da2cddf8
- claude/battle-presentation @ 55e54edd
- claude/audio @ 25ab33be
- m2-slice: no new commits.

## Resolutions
- ui: `objectives.json` and `qa_known.json`: ours. ui has no commits of its own on either file; its side came from a merge
  on its branch that dropped act2-plan's restored beat-level rows (M4-A2P-114) and their unraised entries. The
  integration base (the owner's content) stands.
- env-art-b: M4-A2P-116 (renamed by the big25 gate from env-art-b's 114): kept id 116; took env-art-b's status (review),
  owner and Review-log line, with the gate note after it.

## Build checks
validate_data 0/0 · taskboard --check clean · gdlint and gdformat clean (1055 files) · no conflict markers · no new duplicate
PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ d40e4864

## Fast gate
- Selected: 120 test files (the diff's, plus test_qa_field_camera, test_causeway_route and test_aspect_layouts to
  re-check the routed reds).
