# Live log: m2-slice environment

Feature track for the M2 vertical slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`, started from `claude/first-playable` 67984ce. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Now
- **Done, in review:** M2-FP-10 dialogue key light (`CutsceneKeyLight`; docs/kb/tech/cutscenes.md "Key light"). Needs the PC GPU check of Cutscene A.
- **Done, in review:** M1-UI-10, the Graphics settings page (title → Settings). **`boot_title` baseline re-approved** for the new row; no other shot drifts.
- **Done, in review:** M2-FP-11, the Drownbell at slice quality (`BattleBossStatus` read-out, toll chip text, retry test). Reviewer ui, because of the one-line `timeline_chip.gd` change.
- **In progress:** nothing.
- **Un-pushed state:** none.
- **Integration merge:** not yet. The Lead is merging `claude/first-playable` into the integration branch; once that's in, merge the integration branch into this one before the next code item. The FP-10 task file was taken verbatim from the integration branch, so it should merge cleanly.

## For the Lead (send_message to the Lead is refused: elevated_session_untrusted_device, so this file is the report)
- **M2-FP-11 is review-ready** (see its task file). Also: **c818bc8 and ef563ee carry a test leak** (a key-light test didn't free its zone, failing 7 field/Haluna/save tests in a full run). The FP-11 push fixes it, so merge the branch head, never c818bc8 alone.
- **M2-FP-10 is review-ready at c818bc8.** Please ask the PC GPU session to check Cutscene A (H05/H06): nose and mouth-corner shadows with the key on, the key's cost (a second shadowed directional light shares the directional atlas), and whether Haluna's `face_key_shadow_normal_bias` 3.0 on the zone sun can return to 1.0 (RND-20 S1).

## Exact next step
Queue item 4: Haluna at vertical-slice quality (beats B02–B07 and B11 in docs/kb/story/beats/vertical_slice.md: zone dressing, encounters, NPC beats, camera rails, the save-shrine flow). File task files first; check the integration branch for id collisions.

## Queue
1. ~~M2-FP-10 dialogue key light~~ (review)
2. ~~Drownbell follow-ups (M2-FP-06)~~ → M2-FP-11 (review)
3. ~~M2-FP-05 and M1-ARC-15 follow-ups; M1-UI-10~~: FP-05 and ARC-15 had no open review items (their known gaps are documented). M1-UI-10 is done (review).
4. Haluna at vertical-slice quality
5. Shell Shrine temple trial
6. First Vowbound; Cutscene A/B facial animation

## Setup notes
- `fetch_godot.py` doesn't put Godot on PATH: `ln -s /root/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`).
- `pip install -r tools/requirements.txt` for gdlint/gdformat.

## History
- 2026-10-24: M1-UI-10 done. Gates: gdlint and gdformat; the full Godot suite, 1263 green; tools unittest 448 OK; validate_data and taskboard --check clean; `HYMN_SHOTS=boot_title` captured and re-approved after a side-by-side view. No coverage step (no battle or progression code since the last run).
- 2026-10-24: M2-FP-11 done. Gates: gdlint and gdformat over game and tests; the full Godot suite under coverage (1257 tests; battle 99.95%, progression 96.52%, within baseline); `sim.py --check` passes every band; validate_data and taskboard --check are clean. I checked two lavapipe renders by eye; no manifest shot covers a boss fight.
- 2026-10-23: setup; claimed and finished M2-FP-10. Gates: gdlint/gdformat, `--filter=cutscene` (26), `--filter=key_light` (8), `--filter=haluna` (8), validate_data, taskboard --check. No game/battle or progression code touched (no coverage step), no skills or encounters (no sim), no screenshot covers cutscenes (no shots).
