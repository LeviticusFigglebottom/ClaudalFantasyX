---
id: M2-CMB-05
title: Vowbound fixes from ADR 0027's acceptance (absorb fills the gauge, Floodnet clears the flood, the call's turn end, sim call rule)
role: combat
status: doing
owner_session: "worktree-agent-a7aa8de557501f0a5"
reviewer: lead
depends_on: [M2-CMB-04]
milestone: M2
request-from: "lead"
---
## Goal
Review-sweep-P (Design) accepted ADR 0027 with amendments A1–A3. A called Ilun was immortal and harmless in the Drownbell's flood phase: the bell and its polyps absorb water, Ilun absorbs water, and his gauge filled only from HP he lost. The call also skipped the caller's end of turn. This task implements the amendments and gives the simulator a call rule, so the Vowbound line can become a real band.

## Acceptance criteria
- [ ] **A1:** an `absorb` hit on the Vowbound fills its gauge. Use `Formulas.swell_gain` on the HP restored, at its row's `swell.rate`, in `BattleVowbound._on_action_resolved`. Update formulas.md § Vowbound, battle_ctb.md § Vowbound (rule 3) and the tests together.
- [ ] **A2:** Floodnet is `element: none` and carries `clears_field: flood` (skills.json). The field is cleared through the same path as the `call_ilun` stand-in. Add a test that Floodnet clears an active flood field.
- [ ] **A3:** the call runs the caller's end of turn at the moment of the call: Poison and Regen, the status countdown, Doom, `turns_taken` and `turn_ended`. Only the caller's `next_time` waits for the return, at the `call_rank` delay. Add tests: a Poisoned caller ticks once per call, and a Doomed caller counts down once per call.
- [ ] battle_ctb.md and ADR wording: "once-a-battle rescue" becomes "one HP pool per battle" (a dismissed Vowbound can be called again as it left).
- [ ] The simulator gets a call rule for `naive_swell`/masher, `role_answer` and `smart` (the Drownbell's `clear_field_skill` is the model). balance_targets.md gets a Vowbound masher line: ≤ 40% on the sandbox with no gear, a masher calling at once (the provisional ceiling in ADR 0027's Acceptance). `sim.py --check` passes.
- [ ] Gates: `--filter=battle`, `vowbound` and `formulas` green; coverage holds (battle and progression).

## Notes
- The test name `test_the_call_replaces_the_party_and_takes_the_turn_at_no_cost` will read wrong after A3. Rename it.
- With A1 and A2, check that Ilun can't loop Floodnet against the bell's `undertow_surge` after the flood clears; M2-FP-17 bands it on the real fight.

## Review log
