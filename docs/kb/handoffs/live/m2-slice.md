# Live log: m2-slice environment

Feature track for the M2 vertical slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`, started from `claude/first-playable` 67984ce. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Now
- **Done, in review:** M2-FP-10 dialogue key light (`CutsceneKeyLight`; docs/kb/tech/cutscenes.md "Key light"). Needs the PC GPU check of Cutscene A.
- **In progress:** nothing.
- **Un-pushed state:** none.
- **Integration merge:** not yet. The Lead is merging `claude/first-playable` into the integration branch; once that's in, merge the integration branch into this one before the next code item. The FP-10 task file was taken verbatim from the integration branch, so it should merge cleanly.

## Exact next step
Item 2 of the queue: the Drownbell follow-ups (M2-FP-06). Read its task file and Review log, then the boss feel (telegraphs, HUD, defeat/retry), keeping `tools/balance/sim.py --check` green.

## Queue
1. ~~M2-FP-10 dialogue key light~~ (review)
2. Drownbell follow-ups (M2-FP-06)
3. M2-FP-05 and M1-ARC-15 follow-ups; M1-UI-10 if nobody has it
4. Haluna at vertical-slice quality
5. Shell Shrine temple trial
6. First Vowbound; Cutscene A/B facial animation

## Setup notes
- `fetch_godot.py` doesn't put Godot on PATH: `ln -s /root/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`).
- `pip install -r tools/requirements.txt` for gdlint/gdformat.

## History
- 2026-10-23: setup; claimed and finished M2-FP-10. Gates: gdlint/gdformat, `--filter=cutscene` (26), `--filter=key_light` (8), `--filter=haluna` (8), validate_data, taskboard --check. No game/battle or progression code touched (no coverage step), no skills or encounters (no sim), no screenshot covers cutscenes (no shots).
