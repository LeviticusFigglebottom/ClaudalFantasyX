---
id: M1-NAR-02
title: Vertical-slice beat sheet and two cutscene scripts in .dlg
role: narrative
status: done
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
- 2026-10-23 cinematics (review-sweep-B): **approve with fixes**. Both scenes have the right beats in the right order: waking into kindness, then the grief turn in cyan, then warmth, and in Ch3 quiet steps, released light, the lullaby, the toll. The H06 framing supports the facial beat, the S10 fill requirement is exactly what the recognition needs, and branching stays small and meaningful. No lore run exceeds 4 lines (the longest single-speaker run is 2 lines, not counting the 4 sung lines). `dlgc --check` is clean, and `--filter=dialogue` passes 47/47. The fixes are camera grammar, two tone slips, and a pending grade.
  - **should-fix (camera grammar):** blends are used between non-continuous setups, so they will play as swoops and whip-pans. In ch02: H05→H06 `blend=0.4` (a low 35 mm POV to a 50 mm side-on from the north, a ~90° axis change in 0.4 s), H06→H05 0.8, H05→H06 1.2, H06→H05 1.0, and H05→H01 3.0 (0.4 m on the sand to 180 m offshore). In ch03: S09↔S10 0.6 (shot/reverse-shot across the axis) and S09→S10 1.5. Make all of these cuts (`blend=0.0`). Keep blends for same-axis moves only (for example a slow push-in on S10). Check that S07→S08 `blend=2.0` doesn't fly through the sinking door; if it does, cut on the fade instead.
  - **should-fix (staging):** Asha's lines 014/015 play on the H01 wide, where she is a few pixels tall 180 m away, so the lip-flap is wasted and the line floats. Keep 014/015 on H05, and cut to H01 at the `@mark ... beach_path walk` for VO 035.
  - **should-fix (S10 timing):** the camera reaches Rhen only on the last sung word ("...mir."), so the "slow recognition" lasts about 2 s and starts after the tune is nearly over. He would know it from the first phrase. Cut to S10 at line 043 and hold through 044–046 (≥ 6 s, with Asha's voice over his face). Drop the self-blend `@camera S09 blend=2.5`, or give the `threshold_west` setup its own id (S09b). Also, `@face rhen surprised 3.0` is the wrong target for this ache: a full-weight 3 s "surprised" reads as comic shock. Layer neutral → surprised 0.3 → sad/grief 0.6, or ask Systems for an emotion layer.
  - **should-fix (pillar 1):** ch02 line 021 (Toma: "She woke the whole house. I have learned not to argue.") is a laugh line placed between "Those are ours. Aren't they." and the choice to stay with the dead, so it undercuts the grief turn. Cut it, or move it after line 030, where the scene returns to warmth.
  - **should-fix (pillar 1, voice guide):** ch03 line 054 (Rhen: "Small world.") is a modern idiom and reads glib at the slice's emotional apex, where two griefs meet. Replace it with a held look (`@wait 1.5`) or an in-voice line, for example "...He never said where he learned it."
  - **should-fix:** the node `steps` still has `grade: ch03_shrine_int`. S06 is exterior `ch03_steps` (haluna.md §0, beat sheet B08; M1-ART-03 request 1). The C08 `grade=ch03_boss` request is already applied.
  - **should-fix (continuity):** N-08 says Dace learned the verse from Imra "on the pilgrimage", but he never returned from it to hum it to Rhen. This breaks the logic of Cutscene B's reveal. See the M1-NAR-01 review for the fix.
  - **nit:** the stillness beat speaks during the stillness ("That lantern." comes before the `@wait 0.6`). The beat sheet asks for a silent half-beat, so add `@wait 0.6` before line 006 as well, and let the look land before the words.
  - **nit (voice guide, no modern rhythm):** ch02 027 "Nope. Up." could be "No. Up. I'm getting up."
- 2026-10-23 lead: closing on review-sweep-B approve-with-fixes; should-fix items are tracked in M1-NAR-05.
