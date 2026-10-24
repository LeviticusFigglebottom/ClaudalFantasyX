---
id: M2-FP-17
title: The Drownbell with the real Vowbound call (replace call_ilun; band the call-into-the-flood policy)
role: combat
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
reviewer: lead
depends_on: [M2-CMB-05, M2-FP-06]
milestone: M2
request-from: "lead"
---
## Goal
ADR 0027 is accepted (review-sweep-P). The m2-slice track's `call_ilun` stand-in (ADR 0024/0026) should become the real call: `engine.summon(&"ilun")`, with `ch03_ilun_bound` → `known`. Review-sweep-P found that, under the M2-CMB-04 data, a called Ilun stalls the flood phase: both sides absorb water. ADR 0027's amendments A1 and A2 (M2-CMB-05) fix the rules. This task checks the real fight.

## Acceptance criteria
- [x] The Drownbell uses the real call. `call_ilun` is retired, or kept only as a flagged fallback; ADR 0024/0026 is noted superseded where it applies.
- [x] `TUT_DROWNBELL_FLOOD` ("Call on Ilun") still tells the truth: calling Ilun into the flood leads to Floodnet clearing it.
- [x] Bands re-run for the Drownbell, including a new policy that **calls Ilun when the flood rises and stays out until he falls or the bell dies**. Its win rate must not exceed the encounter's `smart` band, and it must not stall: battles end within the sim's turn cap.
- [x] The bell's AI is checked against a lone water-absorbing foe. If the flood phase only heals Ilun, give its AI a rule that answers him (for example, Hood Slam when every foe absorbs the flood). Record the choice in battle_ctb.md.
- [x] `sim.py --check` passes. Tests.

## Notes
- Filed on the integration branch. The m2-slice track owns the Drownbell, and its task ids run to M2-FP-16, so this is FP-17.

- **Done (m2-slice, 2026-10-24), for review by lead. Rebased on the canonical M2-CMB-05 (the integration branch's 3e59f8d):** the m2-slice branch's own CMB-05 (gauge from the HP restored, Ilun at 60% HP, rate 220, `requires_field`, `bound_flag`, Floodtide 13) was dropped in the merge. Only the FP-17 wiring remains:
  - **The suite plays the real call:** `ch03_drownbell` binds Ilun (`"vowbound": ["ilun"]`) and retires the stand-in (`"retire_skills": ["call_ilun"]`, `BattleSim.retire_skills`). The live game keeps `call_ilun` until M2-UI-05; ADR 0026 has the note.
  - **The new policy `flood_call`:** it calls Ilun when the flood rises and keeps him out (`call_vowbound: field_up`, a third rule beside `at_once` and `on_field`). Band [0, 95], the smart ceiling.
  - **Bands at 1000 seeds, unchanged:** role_answer 71.0%, smart 85.3% (p90 60), flood_call 38.8%, no timeouts.
  - **The bell's AI:** under canonical A1 the flood does not stall on a lone Ilun, so no answer rule is needed. I tried one and dropped it, because it lowered every band (battle_ctb.md, "The real call").
  - **`TUT_DROWNBELL_FLOOD`** ("Call on Ilun") still tells the truth.
  - **Tests:** `tests/unit/test_sim_flood_call.gd` (3). In `test_drownbell_battle.gd`, the 200-seed guard allows the sampling spread near the band edges, and "without Ilun" also drops the loadout's Vowbound.

## Review log

## Lead note (2026-10-24)
M2-CMB-05 is **merged** on the integration branch (3e59f8d): absorb fills the gauge (A1, read as the rolled absorb), Floodnet is non-elemental and clears the flood (A2), and the call runs the caller's end-of-turn ticks (A3). The sim has the call rule (`call_vowbound` in sim_policies.json) and a `sandbox_reef_vowbound` suite. The exact steps for this task are in handoff `2026-10-24-combat-13.md` § "What m2-slice needs for M2-FP-17". Start from the scratch results there: role_answer 72.0%, smart 87.0% (p90 60, at the ceiling).

## Lead note 2 (2026-10-24): M2-UI-05 is in the same merge batch
- **Don't wire the bind flag again.** Every live battle already binds Ilun from `ch03_ilun_bound`, through `bound_flag` in vowbound.json. M2-UI-05 adds Asha's "Call Ilun" row (R3; greyed with a reason when refused) and Ilun's own menu (Attack, Floodnet, Skills, Dismiss).
- **Remove the `call_ilun` stand-in:** from Asha's kit, skills.json with its loc key, and `clear_field_skill` in sim_policies.json. Until then, Asha in the Drownbell has both the real Call row and the stand-in under Skills.
- **Take the integration branch's CMB-05 mechanics** (the rolled absorb, HP 100%, rate 150). See review-sweep-Q and M2-CMB-06. Then re-band the Drownbell.
- **Optional:** a Drownbell shot can bind Ilun with `"vowbound": ["ilun"]` in its fixture.
