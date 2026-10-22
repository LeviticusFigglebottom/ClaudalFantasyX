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
- 2026-10-22 narrative (narrative-stream-2): **approve, with fixes applied by Narrative.**
  - *The sample against the beat (act_outline Ch2, Cutscene A):* it hits the beat in order. She smiles first, the spear comes in, Rhen's first words are a joke, she laughs, goes still at the lantern, and smiles again. The facial beat is cued (`@wait 0.6` between `neutral` and `soft_smile`), and the lantern branch pays off in the closing line. Nothing in it breaks pillar 1, and nothing runs past four lines of exposition.
  - *Against voice_guide.md:* Rhen's lines (004, 010, the run-on in 012) and Asha's (002, 005, 011) are on voice. Two fixes: Toma's 003 ended on an orphaned "I would rather not". That phrase works in the guide's sample after "Step back... slowly", but not after "hands open", so it now sets up Rhen's "small conversation" joke instead. His `[cold]` became `[determined]`, because cold is Ysolde's register; Toma is courteous even with a spear out.
  - *Against the cue contract:* the camera ids (`haluna_shallows_dawn`, `spear_insert`, `lantern_insert`) were invented. They are now haluna.md shot ids (H05, H06, H01). The scene left the letterbox on, so it now ends `@letterbox off`. Narration is tagged `#vo`.
  - *Ergonomics for writers:* good. It reads like a screenplay, the indentation rules are learnable in one sitting, and errors are `file:line:` and specific. Writing 110 lines across two scenes, I hit no compiler surprises. The real friction is listed as requests to Systems in M1-NAR-02's notes. The biggest are hand-numbered `#line:` ids, no display-name override for a speaker the player hasn't met, no emotion or identity on narration, and no `#sung`/do-not-translate convention.
  - The scene is now the full Cutscene A (M1-NAR-02). Its two pinned-sequence tests in `tests/unit/test_dialogue_scenes.gd` were relaxed to the opening, the menu, and the flags. Every branch is covered in `tests/unit/test_dialogue_vs_scenes.gd`.
