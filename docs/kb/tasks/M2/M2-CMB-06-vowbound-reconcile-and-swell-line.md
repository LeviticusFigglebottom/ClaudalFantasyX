---
id: M2-CMB-06
title: Reconcile the two M2-CMB-05 implementations; a Vowbound masher line with the heroes' Swell on
role: combat
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
reviewer: lead
depends_on: [M2-CMB-05]
milestone: M2
request-from: "lead"
---
## Goal
Review-sweep-Q on M2-CMB-05. **M2-CMB-05 was implemented twice.** The integration branch has it (merged at 3e59f8d). `claude/m2-slice` also did it, together with M2-FP-17, in d396f57, d8c71d1 and da6588c, from a merge base (a514c06) that predates the integration copy. The two read A1 differently:
- **Integration (canonical, accepted by sweep-Q):** an absorb fills the gauge from the **rolled** absorb (`hit["absorbed"]`, before the max-HP cap). Ilun keeps HP scale 100% and rate 150.
- **m2-slice:** the gauge fills from the HP actually restored (`absi(amount)`, damaging skills only). That fills nothing at full HP, so the track lowered Ilun's HP scale to 60% and raised his rate to 220 to compensate.

Merging m2-slice will conflict in battle_engine.gd, battle_vowbound.gd, boss_mechanics.gd, the sim policies, targets.json, balance_targets.md, formulas.md, vowbound.json and test_battle_vowbound.gd.

## Acceptance criteria
- [x] One implementation after the merge. Keep the integration engine: A1 as the rolled absorb, `BattleEngine._turn_ticks`, and `_check_outcome`'s defeat after a recall. Keep what only m2-slice has: `bound_flag` and its validator, `requires_field`, the enemy-AI answer to a lone absorber, `sim_policy_flood_call.gd` and the FP-17 suite.
- [x] Re-derive Ilun's `scale_pct.hp` and `swell.rate` **on the merged rules**. HP 60% and rate 220 were tuned for the HP-restored reading. Record the choice in formulas.md § Vowbound and in a balance_report.md tuning-log entry.
- [x] **The Swell-on Vowbound line (sweep-Q design verdict).** Keep `sandbox_reef_vowbound` (heroes' Swell `off`, naive_swell 0–40%) as the line that isolates the Vowbound's own lift. Add a second suite, `sandbox_reef_vowbound_good`, with the heroes' Swell at `good` and a naive_swell ceiling of **50%** (it measured 46.2%). Add the tuning-log entry that accepts the measured rate. Change targets.json and balance_targets.md together.
- [x] Re-measure both lines after the merge. The binding per-encounter check stays on the Drownbell (M2-FP-17), with the heroes' Swell at `good`.
- [x] `sim.py --check` passes. Run `--filter=battle`, `vowbound` and `formulas`, and keep the battle and progression coverage.

## Notes
- **Why a Swell-on band is needed.** Hero Swell can't be turned off in play, and the masher who finds the Vowbound row is, by this project's definition, `naive_swell`, who also unleashes the heroes' gauges. A line measured only with Swell off watches a state the player can't reach, so a change to how hero Swell and the Vowbound interact (for example, a technique that feeds Ilun's gauge) would pass it unseen. The sandbox is pre-Ilun content, so neither line is a player experience. Both are engine regression ceilings, which is why the Swell-on one is set just above today's number and doesn't have to come down to 40%.

## Done (m2-slice, 2026-10-24), for review by lead
- **One implementation:** the merge at 7fa4400 took the integration engine whole (A1 as the rolled absorb, `_turn_ticks`, the recall-then-defeat check).
- **Three of the "keep what only m2-slice has" items were deliberately not kept, after the Lead's later notes and measurement:**
  - **`bound_flag`:** M2-UI-05 shipped its own `bound_flag` and validator (batch 3), so that one is used.
  - **`requires_field`:** the integration branch's Swell-finisher exemption already lets Floodnet be used anywhere, and `call_ilun`, the only user, is now removed.
  - **The enemy-AI answer to a lone absorber:** under the rolled-absorb A1 the flood doesn't stall (0 timeouts in 1000 `flood_call` fights), and the rule dropped role_answer to 62.7% and smart's p90 to 72. It's recorded in battle_ctb.md, "The real call".
- `sim_policy_flood_call.gd` and the FP-17 suite are kept.
- **Ilun's HP scale and rate** were re-derived on the merged rules: 100% and 150 hold every line, so they stay (formulas.md § Vowbound, plus the tuning log).
- **New suite `sandbox_reef_vowbound_good`:** the heroes' Swell at `good`, naive_swell [0, 50], measured **46.2%**, accepted in the tuning log. targets.json, balance_targets.md and `tools/tests/test_balance_naive_swell.py` changed together.
- **Re-measured at 1000 seeds:** Swell-off line 38.9% (≤ 40), Swell-on 46.2% (≤ 50), Drownbell role_answer 71.0%, smart 85.3% (p90 60), flood_call 38.8%. `sim --check` rc 0.

## Review log
