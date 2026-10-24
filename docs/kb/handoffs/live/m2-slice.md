# Live log: m2-slice environment

Feature track for the M2 vertical slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`, started from `claude/first-playable` 67984ce. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Now
- **Done, in review:** M2-FP-10 dialogue key light (`CutsceneKeyLight`; docs/kb/tech/cutscenes.md "Key light"). Needs the PC GPU check of Cutscene A.
- **Done, in review:** M2-FP-16, the Shell Shrine trial (B07). The puzzle rules are headless and data-driven; the room is a greybox built from JSON. The thread now runs the causeway head → low tide → the trial → Cutscene B. Filed M2-ENV-03 (the shrine kit) and M2-AUD-01 (the trial audio).
- **Done, in review:** M2-FP-13, Haluna by day (B02 Neme's table after the tideline win, B03's four fragments overheard on walk-past, B05 Low tide). Filed M2-FP-14, M2-FP-15, M2-ENV-02 and M2-UI-05.
- **Done, in review:** M2-FP-11 (the integration branch's task: zone suns back to bias 1.0, FlowRouting serving waiters in turn). I took it because it lives in my scenes and pairs with FP-10. The file is taken verbatim from the integration branch, so it should merge clean, apart from my status and notes.
- **Done, in review:** M1-UI-10, the Graphics settings page (title → Settings). **`boot_title` baseline re-approved** for the new row; no other shot drifts.
- **Done, in review:** M2-FP-12, the Drownbell at slice quality (`BattleBossStatus` read-out, toll chip text, retry test). Reviewer ui, because of the one-line `timeline_chip.gd` change.
- **In progress:** nothing.
- **Un-pushed state:** none.
- **Integration merge:** not yet. The Lead is merging `claude/first-playable` into the integration branch; once that's in, merge the integration branch into this one before the next code item. The FP-10 task file was taken verbatim from the integration branch, so it should merge cleanly.

## For the Lead (send_message to the Lead is refused: elevated_session_untrusted_device, so this file is the report)
- **Trial merge of the integration branch (9a133ee) into this branch:** three add/add conflicts, all trivial. `M2-FP-09-thread-hardening.md`: take first-playable's. `M2-FP-10-dialogue-key-light.md`: take this branch's. `tests/unit/test_vegetation_plant.gd.uid`: take the integration branch's. I'm not merging until you say the first-playable merge is in.
- **Two queue items remain after Haluna** (5, the Shell Shrine trial; 6, the first Vowbound and Cutscene A/B facial animation). Please queue more when you can. New requests for other roles: M2-ENV-02 (Haluna night light, which blocks B11) and M2-UI-05 (shop and inn).
- **Task-id note:** my Drownbell task was renumbered FP-11 → **FP-12**, because the integration branch's FP-11 came first.
- **M2-FP-12 is review-ready** (see its task file). Also: **c818bc8 and ef563ee carry a test leak** (a key-light test didn't free its zone, failing 7 field/Haluna/save tests in a full run). The FP-12 push (09db8b2) fixes it, so merge the branch head, never c818bc8 alone.
- **M2-FP-10 is review-ready at c818bc8.** Please ask the PC GPU session to check Cutscene A (H05/H06): nose and mouth-corner shadows with the key on, the key's cost (a second shadowed directional light shares the directional atlas), and whether Haluna's `face_key_shadow_normal_bias` 3.0 on the zone sun can return to 1.0 (RND-20 S1).

## Exact next step
Queue item 6: the first Vowbound (Ilun as a real summon that replaces the party, superseding ADR 0024's Call Ilun stand-in; SPEC §6.3, docs/kb/story/vowbound.md §1), then Cutscene A/B facial animation. File task files first. M2-FP-14 (B04) is blocked on the wake-shell wall being out of reach (see its notes).

## Queue
1. ~~M2-FP-10 dialogue key light~~ (review)
2. ~~Drownbell follow-ups (M2-FP-06)~~ → M2-FP-12 (review)
3. ~~M2-FP-05 and M1-ARC-15 follow-ups; M1-UI-10~~: FP-05 and ARC-15 had no open review items (their known gaps are documented). M1-UI-10 is done (review).
4. Haluna at vertical-slice quality: M2-FP-13 in review; M2-FP-14 (B04) next, M2-FP-15 (B11) once M2-ENV-02 lands
5. ~~Shell Shrine temple trial~~: M2-FP-16 (review)
6. First Vowbound; Cutscene A/B facial animation

## Setup notes
- `fetch_godot.py` doesn't put Godot on PATH: `ln -s /root/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`).
- `pip install -r tools/requirements.txt` for gdlint/gdformat.

## History
- 2026-10-24: M2-FP-16 done (the Shell Shrine trial). Gates: dlgc, validate_data, lint and format, Godot shell_shrine 11, fp_ 22 and haluna 13, plus the full Godot suite (1280 green) and tools unittest (452 OK). I checked three lavapipe renders by eye.
- 2026-10-24: M2-FP-13 done. Gates: dlgc and `--check`; validate_data; lint and format; the full Godot suite, 1269 green. Filed FP-14, FP-15, ENV-02 and UI-05.
- 2026-10-24: M2-FP-11 done (bias and FlowRouting). Gates: lint and format; Godot flow_routing 4, fp_ 22, haluna 8. Renumbered the Drownbell task to FP-12.
- 2026-10-24: M1-UI-10 done. Gates: gdlint and gdformat; the full Godot suite, 1263 green; tools unittest 448 OK; validate_data and taskboard --check clean; `HYMN_SHOTS=boot_title` captured and re-approved after a side-by-side view. No coverage step (no battle or progression code since the last run).
- 2026-10-24: M2-FP-12 done. Gates: gdlint and gdformat over game and tests; the full Godot suite under coverage (1257 tests; battle 99.95%, progression 96.52%, within baseline); `sim.py --check` passes every band; validate_data and taskboard --check are clean. I checked two lavapipe renders by eye; no manifest shot covers a boss fight.
- 2026-10-23: setup; claimed and finished M2-FP-10. Gates: gdlint/gdformat, `--filter=cutscene` (26), `--filter=key_light` (8), `--filter=haluna` (8), validate_data, taskboard --check. No game/battle or progression code touched (no coverage step), no skills or encounters (no sim), no screenshot covers cutscenes (no shots).
