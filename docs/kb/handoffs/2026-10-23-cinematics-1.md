# Handoff — cinematics — 2026-10-23 #1

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Task: M2-FP-10 dialogue key light.

## Done
- `CutsceneKeyLight` (`game/cutscene/cutscene_key_light.gd`): on close shots (frame ≤ 1.0 m above and below the aim) the cast moves to render layer 20, the zone sun stops lighting that layer, and a short-range copy of the sun (orthogonal, 6 m, normal bias 4.5, sky light-only, no fog or GI energy) lights only the cast. Everything is restored on the next wide shot, `@camera release`, the end of the scene and an abort.
- Per-shot overrides on `CutsceneShotNode`: `key_light` AUTO/ON/OFF, `key_yaw_deg`, `key_pitch_deg`, `key_energy_scale`.
- `CutsceneStage.sun_path`/`sun()`, `cast()`, `shot_node()`. Tuning: `sequencer.json` `key_light`.
- Docs: docs/kb/tech/cutscenes.md, "Key light". Tests: `tests/unit/test_cutscene_key_light.gd` (8) and a Haluna classification check in `tests/integration/test_haluna_zone.gd`.

## In progress
- Nothing. The task is in `review` (reviewer: rendering).

## Exact next step
- The Lead asks the PC GPU session for a check of Cutscene A (H05 and H06: nose and mouth-corner shadow, the key's cost, and whether Haluna's sun bias 3.0 can return to 1.0).

## Known issues
- Casters more than 6 m from the camera don't shadow the cast during a close shot.
- The second shadowed directional light shares the directional shadow atlas with the sun during close shots (scenery only).
- No screenshot covers a cutscene, so lavapipe has no baseline for this.

## Files touched
- game/cutscene/cutscene_key_light.gd (new), cutscene_sequencer.gd, cutscene_stage.gd, cutscene_shot_node.gd
- game/data/cutscene/sequencer.json
- tests/unit/test_cutscene_key_light.gd (new), tests/integration/test_haluna_zone.gd
- docs/kb/tech/cutscenes.md, docs/kb/tasks/M2/M2-FP-10-dialogue-key-light.md
