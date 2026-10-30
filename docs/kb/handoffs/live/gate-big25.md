# Gate big25 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ efe7fb10 (Merge lead/gate-big24).
Lead rule from 15:49: a single red that takes more than 15 min to classify is routed, and GATE-FAST-DONE is posted.

## Pinned heads (merged --no-ff, in order)
- claude/hero-integration @ a4b2a60c
- claude/characters @ c23db4d4
- claude/act1-chapters @ d997ad24
- claude/env-art @ d5b7db31
- claude/m2-slice @ c933590d
- claude/env-art-b @ 96bef177
- claude/creatures @ 7096ae41
- claude/creatures-b @ 7cfbb2e9
- claude/battle-presentation @ c3d06333
- claude/ui @ 41b44fee
- claude/audio @ ee01d114
- claude/act2-plan @ c83b5419

## Resolutions
- act1-chapters: `M4-A2P-0401` `owner_session`: theirs (the owner now writes `act1-chapters`).
- ui: `objectives.json`: theirs. ui's file came from merging big23 and is byte-identical to act2-plan's
  restored rows (M4-A2P-114, act2-plan @ ccab7aac).
- audio: `tools/tests/test_cutscene_sfx_files.py`: the comments differed, the code is the same; the owner (audio) wins.
- act2-plan: `tests/integration/qa_known.json` `unraised`: theirs (the objectives' owner). It includes ui's
  ch14_started and ch14_declared_heretics keys, plus the flags of the restored beat-level rows.
- **Task id clash:** M4-A2P-114 was claimed by act2-plan (Act II beats in the flows, 14:38) and by env-art-b (Lowlight
  arena wall blocks the battle camera, 15:03). env-art-b's is renumbered **M4-A2P-116** (file renamed, plus a gate note).
  env-art-b's live log still says 114.

## Build checks
validate_data 0/0 · taskboard --check clean · gdlint and gdformat clean (1053 files) · no conflict markers · no new duplicate
PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ ca5d12c6

## Fast gate
- Selected: 33 test files.
- Lane A (mine): 17; lane B (GATE-HELPER): 16, in `gate-big25-lanes-b.txt` @ 829b09a6.
