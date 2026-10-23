---
id: M1-CMB-08
title: Wire the shrine HP/MP carry-over into live battles; economy.md cleanups
role: combat
status: review
owner_session: "worktree-agent-af6af1b46e0ce25af"
reviewer: architect
depends_on: [M1-ARC-06]
milestone: M1
request-from: "architect"
---
## Goal
ARC-06 asked Combat to wire party HP/MP carry-over; until then a shrine heal restores nothing in play.

## Acceptance criteria
- [ ] Live battles start from the party's carried HP/MP (and write it back at the end); the ARC-06 event is consumed
- [ ] Decide and document what a KO'd member does at battle start
- [ ] economy.md: Ember Pot price 220; remove the stale 'fold into formulas.md' paragraph (~:72)
- [ ] formulas.md:58 'can't launder' wording fixed; the balance test reads the ceiling from targets.json
- [ ] Tests; game/battle coverage does not drop

## Notes
See the review-sweep-F entries in the source tasks' Review logs for file:line.

- 2026-10-23 worktree-agent-af6af1b46e0ce25af (combat): ready for review (architect).
  - **In and out.** New `game/battle/scene/battle_vitals.gd` (`BattleVitals`, scene glue; no engine-core edit, battle_engine.gd untouched at 996 lines). For live battles (`persist_progress` on, no fixture) `BattleController._build_engine` calls `BattleVitals.setup`, which composes `progress.apply_to` then `Game.vitals_modifier()` (run last). `_show_result` calls `BattleVitals.send_back`, which emits `EventBus.battle_party_returned` after a **victory or escape**. `Game.record_party` consumes it. A **defeat writes nothing**: it is a game over (back to the last save), and the sandbox's Retry replays the same start. Capture fixtures and tests (`persist_progress` off) never read or write vitals, so no baseline moves. battle_controller.gd goes from 994 to 995 lines.
  - **KO'd at battle start (decided; battle_ctb.md "Carried vitals").** Fallen (0 HP or stone) active members trade places with the first unused living reserve member, before `begin()`, so it costs no time. With no living reserve left, the fallen member keeps its slot at 0 HP (revive or swap it later). If nobody in the party stands (only after a victory where the last foe and the last active member fell together), the active members get up with 1 HP and their stone breaks, so a fight never opens already lost. The re-lineup re-runs `engine.setup` (deterministic, rolls nothing).
  - **Docs.** economy.md: Ember Pot has its own row at 220 (not in a slice shop; Pemakar), and the stale "please fold into formulas.md" request is replaced with a pointer to formulas.md § Items. formulas.md § Time: the swap/delay-count reason is reworded as the review asked (the swap-in inherits the slot's delayed `next_time`). This is wording only, so formulas.gd and test_formulas.gd are unchanged. architecture.md "Requests for Combat" has a done note.
  - **Balance test.** test_sandbox_battle.gd reads the smart ease ceiling from `tools/balance/targets.json` (`mean_turns_min`) rather than a constant, and a new test checks that every `mean_turns_min` key is a banded policy (the review's misspelt-key nit).
  - **Tests.** `tests/unit/test_battle_vitals.gd` (14): the lineup rule (no change, first living reserve, stone counts as fallen and each reserve is used once, no reserve left, nobody standing gets 1 HP and the battle opens with no outcome), setup with and without carry, send_back only after victory or escape (and Game records it), and the live controller (carried HP, MP and Poison; a carried KO swapped out before the first turn; victory write-back, then Retry starting from it, then a shrine heal clearing it; defeat recording nothing and Retry replaying the same start; tests and fixtures ignoring vitals).
  - **Not done:** live battles still build no `EquipmentEffects` (that was true before this task). When they do, put `fx.modifier()` between the Lattice and the vitals in `BattleVitals.setup`.

## Review log
