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
- Lead list (16:09), checked against the build: battle-presentation's aa227a57, 7c3307df, ef997f3d, 4c4a3dd3, 6f3608a7
  (head c3d06333), act2-plan's 86262eb9, creatures' conduit crawler and kingfisher (7096ae41), ui's controls line
  (db67f48b) and env-art are all in. Newer heads merged during the gate: audio @ c7f22ea1 (an integration merge; only
  the comment-only test_cutscene_sfx_files.py conflict again, owner's wording; tools test OK), env-art @ 526f1a8a (log),
  act2-plan @ 85e9e554 (M4-A2P-114 setters, docs). None touches game/, assets/ or tests/, so the running lanes stand.

## Fast-gate results
- Import check clean · boot 0 ERROR lines · log check 0.
- Lane A (mine, 17 files, @ 829b09a6 content): 16 green.
  - **test_aspect_layouts** 18/1: `battle read_panel at (1920, 1440)` (4:3), text 100% and 130%: a Label at x −41 / −63
    leaves the screen. Red on big24's tree too (= integration efe7fb10), so it predates this batch; big25 changes
    nothing in the Read panel. Routed: **ui** (owner of game/ui/battle/read_panel.gd; big24 brought eb1d1299, a foe's
    broken parts on the Read), with battle-presentation's aa227a57 (rank overlap and safe area) as a co-suspect.
- Lane B (GATE-HELPER, 16 files @ 829b09a6, arrived 16:30): 15 green.
  - **test_causeway_route** 5/1 ("at least 2 fights (206 m walk)"), as in big24. Routed: **act1-chapters**.
- Not in this batch's selection, and still open from big24: test_qa_field_camera (FieldShore.settle vs Lowlight's
  Sanctum). Routed: integration-qa FAST-TRACK.
- Tools suite (-j 2): 207 units, only the known reds (test_palette_check, test_screenshots, test_villagers).

GATE-FAST-DONE @ cc62ef20 (merge-approved under the standing rule: no batch-caused red). Routed: ui
(test_aspect_layouts, the 4:3 Read panel); act1-chapters (test_causeway_route); integration-qa FAST-TRACK (test_qa_field_camera,
from big24); known: test_palette_check, test_screenshots, test_villagers.
