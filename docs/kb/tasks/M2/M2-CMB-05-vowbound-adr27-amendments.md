---
id: M2-CMB-05
title: Vowbound fixes from ADR 0027's acceptance (absorb fills the gauge, Floodnet clears the flood, the call's turn end, sim call rule)
role: combat
status: done
owner_session: "worktree-agent-a7aa8de557501f0a5"
reviewer: lead
depends_on: [M2-CMB-04]
milestone: M2
request-from: "lead"
---
## Goal
Review-sweep-P (Design) accepted ADR 0027 with amendments A1–A3. A called Ilun was immortal and harmless in the Drownbell's flood phase: the bell and its polyps absorb water, Ilun absorbs water, and his gauge filled only from HP he lost. The call also skipped the caller's end of turn. This task implements the amendments and gives the simulator a call rule, so the Vowbound line can become a real band.

## Acceptance criteria
- [x] **A1:** an `absorb` hit on the Vowbound fills its gauge. Use `Formulas.swell_gain` on the HP restored, at its row's `swell.rate`, in `BattleVowbound._on_action_resolved`. Update formulas.md § Vowbound, battle_ctb.md § Vowbound (rule 3) and the tests together.
- [x] **A2:** Floodnet is `element: none` and carries `clears_field: flood` (skills.json). The field is cleared through the same path as the `call_ilun` stand-in. Add a test that Floodnet clears an active flood field.
- [x] **A3:** the call runs the caller's end of turn at the moment of the call: Poison and Regen, the status countdown, Doom, `turns_taken` and `turn_ended`. Only the caller's `next_time` waits for the return, at the `call_rank` delay. Add tests: a Poisoned caller ticks once per call, and a Doomed caller counts down once per call.
- [x] battle_ctb.md and ADR wording: "once-a-battle rescue" becomes "one HP pool per battle" (a dismissed Vowbound can be called again as it left).
- [x] The simulator gets a call rule for `naive_swell`/masher, `role_answer` and `smart` (the Drownbell's `clear_field_skill` is the model). balance_targets.md gets a Vowbound masher line: ≤ 40% on the sandbox with no gear, a masher calling at once (the provisional ceiling in ADR 0027's Acceptance). `sim.py --check` passes.
- [x] Gates: `--filter=battle`, `vowbound` and `formulas` green; coverage holds (battle and progression).

## Notes
- The test name `test_the_call_replaces_the_party_and_takes_the_turn_at_no_cost` will read wrong after A3. Rename it.
- With A1 and A2, check that Ilun can't loop Floodnet against the bell's `undertow_surge` after the flood clears; M2-FP-17 bands it on the real fight.

## Implementation notes (worktree-agent-a7aa8de557501f0a5, 2026-10-24)
- **A1:** `BattleHits` records `absorbed` (the rolled absorb, before the max-HP cap) and `BattleVowbound._on_action_resolved` fills the gauge from `max(HP lost, absorbed)`. **This reads A1 as the rolled absorb, not the HP actually restored.** Ilun is called at full HP, so the literal reading filled nothing in the flood: in a scratch Drownbell probe with the real call, role_answer and smart won 0.0% and most fights timed out. Recorded in ADR 0027's implementation note, for Design to confirm.
- **A2:** Floodnet is `element: none` with `clears_field: flood`. It clears through `BossMechanics.after_action` → `clear_field`, the stand-in's path. A Swell finisher is never refused (`no_field`) while its field is down, and it clears only a field that is up.
- **A3:** `BattleEngine._turn_ticks` (split from `_end_turn`) runs for the caller in `summon()`; `vowbound.call_changes` holds the changes. The caller's `delays_taken` resets as at a turn end. `_check_outcome` now calls a defeat when a recall hands back a party with nobody standing (A3 makes that reachable: Doom can fell the last caller at the call).
- **Sim:** a loadout's `vowbound` list binds; `sim_policies.json` `call_vowbound`: `naive_swell` `at_once` (stays out), `role_answer`/`smart` `on_field` (dismissed on the first turn after the field is gone). The finisher goes first (`SimPolicy.unleash_vowbound`). New suite `sandbox_reef_vowbound` (`kind: vowbound`, loadout `sandbox_vowbound`, heroes' Swell off): naive_swell **38.9%** against the 0–40% line. At `good` it is 46.2%; balance_targets.md flags that for a decision.
- **Floodnet against undertow_surge after the flood:** under `on_field` Ilun goes home once the flood clears, so the policy can't loop him there. An `at_once` Ilun can still drink Undertow Surge (power 5) after the flood, but naive_swell wins 1.0% on the probe. M2-FP-17 bands it.
- The renamed test is `test_the_call_replaces_the_party_and_hands_ilun_the_turn_at_once`.

## Review log
- 2026-10-24 review-sweep-Q (design): **approve-with-fixes.** All six criteria hold in the code on the integration branch. A1: `BattleHits._mark_absorbed` and `BattleVowbound._on_action_resolved` (`max(HP lost, absorbed)`). A2: Floodnet is `element: none` with `clears_field: flood`, a Swell finisher is never refused `no_field`, and `after_action` clears only a field that is up. A3: `summon()` runs `_turn_ticks(caller)`, and `_check_outcome` rules a defeat when a recall hands back a fallen party. The renamed test, the sim call rule and the `sandbox_reef_vowbound` suite are all present. `--filter=battle`: 390 run, 0 failed. I didn't re-run `sim.py --check` or coverage (CPU); the Lead's gate covers them. **Design verdict on A1: the rolled absorb is the right reading, and it is canonical.** The gauge measures what the hit gave Ilun, the same quantity the damage side measures, and the fiction is that he drinks the flood. The HP-restored reading fills nothing at full HP, so the flood stalls (0% wins, ~80% timeouts on the probe). One asymmetry is accepted: damage counts only the HP actually lost, while an absorb counts the uncapped roll. `swell_fill` caps the gauge either way. **On the Swell-on case: yes, a line is needed.** Hero Swell can't be off in play, and the masher who finds the Vowbound row is `naive_swell`, who also unleashes the heroes' gauges. A line measured only with Swell off watches a state the player can't reach. Keep the 40% Swell-off line as the Vowbound's own lift, and add a Swell-`good` ceiling at 50% (46.2% measured) with a tuning-log entry. The sandbox is pre-Ilun content, so this is a regression ceiling, not a target. Don't retune Ilun for it now. **URGENT for the Lead:** `claude/m2-slice` implemented M2-CMB-05 a second time (d396f57, d8c71d1, da6588c, with M2-FP-17), from a merge base that predates this copy. It reads A1 as HP restored and compensates with Ilun at HP 60% and rate 220. Filed **M2-CMB-06**: reconcile on merge (keep this engine and m2-slice's extras, re-derive Ilun's HP and rate), and add the Swell-on line.
