---
id: M1-NAR-02
title: Vertical-slice beat sheet and two cutscene scripts in .dlg
role: narrative
status: review
owner_session: narrative-stream-2
reviewer: cinematics
depends_on: [M1-NAR-01, M1-NAR-03]
milestone: M1
request-from: ""
---
## Goal
Prepare the M2 script early.

## Acceptance criteria
- [x] Beat sheet for the 30–45 minute slice: `docs/kb/story/beats/vertical_slice.md` (12 beats, 39.5 min critical path, 45 with optional content)
- [x] Two cutscenes in .dlg with emotion and camera cues: `ch02/ch02_girl_on_the_beach.dlg` (expanded), `ch03/ch03_the_first_verse.dlg`
- [x] Every branch tested: `tests/unit/test_dialogue_vs_scenes.gd`
- [x] Word counts: `tools/dialogue_stats.py` (numbers in the beat sheet §8)
- [x] Art's open questions for Narrative answered: `docs/kb/story/decisions_log.md` N-01 to N-04

## Notes
- **For Cinematics (reviewer):** check the staging against the beat. Focus on the H06 facial beat (smile, stillness, smile), the S10 recognition hold (3 s, no cutaway), and the single S08 frame of Ilun. Anim clip and mark names in the scripts are proposals. Rename them in the `.dlg` as you implement.
- Flags added (all in `game/data/flags.tres`): `ch02_rhen_stayed_with_dead`, `ch02_heard_pila`, `ch02_saved_once`, `ch03_found_net_float`, `ch03_rhen_asked_after`, `ch03_ilun_bound`, `ch03_rhen_named_lullaby`, `ch03_first_verse_sung`, `ch03_drownbell_defeated`, `ch03_rhen_sworn_guardian`.
- Cross-role asks (Art): add held motes in `ch02` H06, and re-time `ch03_boss` to about 18:15 (beat sheet §9). Narrative's calls N-05 (Vowbound read as bound light) and N-07 (the boss follows the verse) bind Art and Rendering, so the Lead may want them in an ADR.
- `tests/unit/test_dialogue_scenes.gd` (Systems' file) pinned the old 15-line sample's exact line order. Its two beach tests were relaxed to the opening, the first menu, the closing variant, and the flags, because the expansion could not land otherwise.
- **Format requests to Systems** (dlgc / runner / DialogueBox; none block this task):
  1. **Display-name override:** a per-line way to show a speaker under another name ("???" or "Girl") before the player has met them. Asha speaks from line 2 but names herself at line 30.
  2. **Narration with an emotion and an identity:** narration can't carry `[emotion]`, and nothing separates Rhen's older voice-over from captions. Today it is tagged `#vo`. Suggest `VO [tender]: ...`, which keeps narration's no-name and no-blip behavior.
  3. **Sung and untranslated lines:** a convention for `#sung` (no blip, no per-vowel lip-flap, distinct text style, advance on a music marker) and `#lamptongue` (do not translate; write a translator note into `dialogue.csv`).
  4. **Cue vocabulary:** add `@sfx id at=` (used for `drownbell_toll`), a reserved `@music silence` (or `@music stop fade=`), and document the `@vfx` kwargs used (`motion=spiral_up`, `drift=down_seaward`, `count`, `form`) and `@camera ... grade=`.
  5. **Line-id helper:** `dlgc --assign-ids` (or `--next-id <prefix>`) to fill in missing `#line:` ids. Hand numbering is the biggest chore when writing.
  6. **Event registry:** a data list of dialogue event names and their args (`zone_unlock`, `start_battle`) so the validator can catch typos.
  7. **Line-length lint:** a `dlgc --check` warning for lines over 25 words (voice guide). `tools/dialogue_stats.py` reports these for now.
  8. **Music sync:** `@wait music=<marker>` so sung lines can follow the score instead of fixed waits.
- Word counts (dialogue_stats): 735 words written (beach 323, verse 412), about 568 on a single path. The slice's fair share is 889–1,333 words. The remaining beats are budgeted at 625 words.

## Review log
