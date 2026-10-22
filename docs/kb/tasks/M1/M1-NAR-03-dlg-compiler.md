---
id: M1-NAR-03
title: dlgc.py compiler and runtime DialogueRunner
role: architect
status: review
owner_session: architect-stream-1
reviewer: narrative
depends_on: []
milestone: M1
request-from: "narrative"
---
## Goal
ADR 0004 implementation.

## Acceptance criteria
- [x] tools/dlgc.py → compiled JSON + loc CSV, with tests
- [x] game/narrative/dialogue_runner.gd: flags, choices, cue events
- [x] Typewriter text box with per-speaker blip (UI)

## Notes
- Syntax reference and "how to add a scene": `docs/kb/tech/dialogue_format.md`.
- Compiler: `tools/dlgc.py` (`--check` for CI); tests `tools/tests/test_dlgc.py`. The validator runs the check, so stale outputs fail `validate_data.py`.
- Emotion tags now live in `game/data/dialogue/emotions.json`; speakers (name_key, blip_pitch, portrait_id) in `speakers.json`; text-box defaults in `text_box.json`.
- Runtime: `DialogueRunner`, `DialogueStep`, `DialogueOption`, `DialogueFlagAccess` / `GameFlagAccess`, `DialogueSpeakers` in `game/narrative/`; `DialogueBox` + `DialogueTextSettings` in `game/ui/dialogue/`.
- Sample scene: `game/data/dialogue/ch02/ch02_girl_on_the_beach.dlg` (15 lines). Test fixture: `game/data/dialogue/test/test_dialogue_fixture.dlg` (only for tests; its strings ship in dialogue.csv with a `DLG_TEST_` prefix).
- Decisions inside the ADR's scope: one compiled JSON per `.dlg`, first node title = file name, jumps are file-local; options support a trailing `<<if>>`; added `<<stop>>`.
- Follow-ups for other roles: add `res://game/data/loc/dialogue.en.translation` to `project.godot` `locale/translations` (Lead; DialogueBox registers it at runtime until then). Options UI, portraits, and a theme are UI's. Lip-flap from `mouth_flap` is Cinematics'.
- Reviewer (narrative): please check the sample scene against voice_guide.md and the act outline beat.

## Review log
