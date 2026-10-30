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
- Lane A (mine): 60; lane B (GATE-HELPER): 60, in `gate-big26-lanes-b.txt` @ e8ae9b74.

## Fast-gate results
- Import check clean · boot 0 ERROR lines · log check 0.
- Lane A (mine, 60 files): 58 green. Previously routed reds now green: **test_qa_field_camera** (integration-qa's 314559cf,
  the Sanctum fix) and **test_causeway_route** (act1-chapters).
  - **test_aspect_layouts** 18/1 (the 4:3 battle Read panel): unchanged from big25 and predates it. Still routed: **ui**.
  - **test_objective_tracker** 9/1, batch-caused (green on big25's tree): ui's merge ce9c0d6d (big24 into claude/ui) had
    rolled the test back to ui's zone-level rows along with objectives.json; git took the test silently while the
    conflicted data stayed ours. **Fixed** (a2ba0922): the integration test restored, 9/0.
- Lane B (GATE-HELPER, 60 files @ e8ae9b74, arrived 17:26): all green.
- Tools suite (-j 2): beyond the known test_palette_check, test_screenshots and test_villagers, two merge reds, both **fixed**:
  - test_gdignore_imports: characters' jog captures tracked `.import` sidecars (b344b974), and creatures-b's 00cb761f put
    docs/kb/qa/characters under .gdignore. The six sidecars were removed (ed646902); OK.
  - test_ch11_lowlight_dressing: env-art-b moved the south pier in the shared `lowlight.py` (M4-A2P-116) without
    re-running env-art's Ch11 dressing. Regenerated with tools/act2/ch11_lowlight_dressing.py (519680f5; only
    lowlight_dressing.json changes); OK. Re-ran the Lowlight Godot tests on it: hero_field_snaps, objective_tracker,
    pseudo_loc_screens, ch11_thread, ch11_walkable and qa_field_camera all green.
- For the owners: ui, keep your branch's objectives.json and test_objective_tracker.gd at the integration version
  (act2-plan's rows). env-art-b, after a shared-kit edit, run the generators that read it.

GATE-FAST-DONE @ 519680f5 (merge-approved: the batch-caused reds are fixed). Routed: ui (test_aspect_layouts);
known: test_palette_check, test_screenshots, test_villagers.
