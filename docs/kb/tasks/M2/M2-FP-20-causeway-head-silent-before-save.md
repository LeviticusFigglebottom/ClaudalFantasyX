---
id: M2-FP-20
title: The causeway head says nothing before the first save (a gated trigger with no feedback)
role: cinematics
status: review
owner_session: "m2-slice subagent (FP-20/21)"
depends_on: []
milestone: M2
request-from: cinematics
---
## Goal
Found in the m2-slice playthrough pass (2026-10-24). The causeway-head trigger (`Triggers/CausewayHead` in `game/levels/ch02/haluna/haluna.tscn`) needs `ch02_saved_once`. Before the player has saved, walking into it does nothing at all. With no feedback, a tester who skipped the shrine reads it as a dead end or a bug (pillar 4: the player always knows what an action costs).

## Acceptance criteria
- [ ] Walking into the causeway head before the first save plays a short overheard bark from Toma or Asha that points to the shrine. It plays once per arrival, in-engine, without stopping Rhen, using the same overheard path as B03's fragments. Narrative writes the line.
- [ ] After the save, the trigger works as now.
- [ ] Test on the real zone.

## Notes
- **What:** `Triggers/CausewayHeadUnsaved` in `haluna.tscn`, on the same transform and box as `Triggers/CausewayHead`. It is a touch trigger with `requires_flag = ch02_met_asha`, `blocked_by_flag = ch02_saved_once` and payload `{"dialogue": "ch02_bark_causeway_unsaved", "overheard": true}`, so it plays on B03's overheard path: Rhen is not stopped and the lines advance by themselves.
- **Line** (`game/data/dialogue/ch02/ch02_bark_causeway_unsaved.dlg`; Narrative should review): Toma: "Hold, Rhen. No one walks the causeway without resting at the town shrine first." Asha: "It only takes a moment. Sit at the little shrine in town, then we'll go."
- **`once` semantics:** the trigger is not `once`. FieldController fires a touch trigger once per entry into the box, so the bark plays on every walk-in until the first save, never over itself (HalunaStory skips it while the overhear sequencer is busy). After the save it is blocked and the causeway head plays B05 as before. Documented in `game/levels/ch02/haluna/README.md` and `docs/kb/tech/first_playable_flow.md`.
- **Tests:** `tests/integration/test_haluna_causeway_head.gd` covers the trigger's data, walking in before the save (the bark plays, Rhen keeps input, nothing is busy, no hand-off, it plays again on the next walk-in), and walking in after the save (silent, and B05 runs).
- **Gates (2026-10-24):** `gdlint game tests` clean; `gdformat -l 120 --check game tests` 356 unchanged; `validate_data` 0 errors, 0 warnings; `dlgc --check` 0 errors, 0 warnings; `taskboard --check` OK. Godot: `--filter=haluna` 39 run, 0 failed; `--filter=fp_` 22 run, 0 failed (`test_fp_thread` takes "Go now" by default, `auto_choice = 0`); full suite 1442 run, 0 failed. Skipped: coverage (nothing in game/battle or game/progression), tools unittest (no tools/ change), screenshots (only an invisible Area3D and dialogue changed; no shot renders them), Blender.
- **Reviewer:** Narrative for the line; Systems/Tech for the trigger (SPEC §12.3).

## Review log
