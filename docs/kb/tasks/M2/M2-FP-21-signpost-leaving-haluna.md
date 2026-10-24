---
id: M2-FP-21
title: Signpost the causeway head as the end of Haluna's day (a point of no return for B04 and the barks)
role: cinematics
status: review
owner_session: "m2-slice subagent (FP-20/21)"
depends_on: []
milestone: M2
request-from: cinematics
---
## Goal
Found in the m2-slice playthrough pass (2026-10-24). The causeway head plays B05 and hands off to the Shell Shrine at once. Haluna returns only at night (B11), when Osu (B04, optional, `ch02_heard_pila`, paid off in B09 and Ch20), the day barks and the lintel-gull look are gone. Nothing tells the player that walking north ends the day, so a player who meant to come back loses B04's payoff without knowing it.

## Acceptance criteria
- [ ] Before B05 starts, the player can tell this is a departure: a held beat with a choice ("Go now" / "Not yet", where "Not yet" steps Rhen back off the trigger), or a line in B05 itself plus a visible threshold. Design chooses; Narrative writes any line (pillar 1: sincere, no meta "point of no return" wording).
- [ ] If there's a choice, "Not yet" returns control with nothing lost, and the trigger fires again on the next approach.
- [ ] Tests, and PLAYTEST.md (step 7 already warns testers in words).

## Notes
- **What:** a choice. `ch02_low_tide.dlg` (B05) now opens with Asha: "Once we cross, we won't be back before dark. Is there anyone you want to see first?" The options are **Go now.** and **Not yet.**
  - **Not yet:** Asha says "Then go and see them. The tide will hold a while yet.", then `<<event departure_declined>>` (newly declared in `game/data/dialogue/events.json`, no args) and `<<stop>>`.
  - **Go now:** continues into the original four B05 lines.
  - Nothing says "point of no return"; the cost is put in Asha's words (pillar 1).
- **Flow:** `HalunaStory._end()` checks `sequencer.events` for `haluna.ending_decline_event` after B05. If it is there, Rhen is placed at `haluna.ending_decline_spawn` (`Spawns/CausewayHead`, about 4 m short of the box), `busy` clears, and nothing is handed off. The causeway trigger is not `once`, so the next walk-in asks again. Otherwise the hand-off runs as before. Both new keys are in `first_playable.json` "haluna" and its doc.
- **Tests:** `tests/integration/test_haluna_causeway_head.gd` covers:
  - "Not yet": no hand-off, control returns, Rhen is off the trigger at the spawn, the trigger stays armed, and walking in again asks again.
  - "Go now": hands off to the Shell Shrine.
  - The dialogue data: B05 asks before it starts, the choice has two options, and the decline event is reported.
  - The existing tests (`test_low_tide_plays_before_cutscene_b`, `test_fp_thread`) take option 0, "Go now".
- **PLAYTEST.md step 7** describes the choice and the unsaved bark.
- **Gates (2026-10-24):** `gdlint game tests` clean; `gdformat -l 120 --check game tests` 356 unchanged; `validate_data` 0 errors, 0 warnings; `dlgc --check` 0 errors, 0 warnings; `taskboard --check` OK. Godot: `--filter=haluna` 39 run, 0 failed; `--filter=fp_` 22 run, 0 failed (`test_fp_thread` takes "Go now" by default, `auto_choice = 0`); full suite 1442 run, 0 failed. Skipped: coverage (nothing in game/battle or game/progression), tools unittest (no tools/ change), screenshots (only an invisible Area3D and dialogue changed; no shot renders them), Blender.
- **Reviewer:** Design for the choice; Narrative for the lines (SPEC §12.3).

## Review log
