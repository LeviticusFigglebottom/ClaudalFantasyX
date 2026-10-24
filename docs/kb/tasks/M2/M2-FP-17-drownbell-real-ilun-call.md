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

- **Done (m2-slice, 2026-10-24), for review by lead.** The sim's `ch03_drownbell` loadout retires `call_ilun` (`retire_skills`). Policies call Ilun into the flood with Floodtide on, and his Floodnet clears it, so `TUT_DROWNBELL_FLOOD` still tells the truth. The live game keeps `call_ilun` (now `requires_field: flood`) as a fallback until M2-UI-05's Call command; ADR 0026 has a note.
- The bell answers a lone water-absorber: a new AI condition `foes_all_absorb` makes the flood phase pick Hood Slam (battle_ctb.md, "The real call").
- The new `flood_call` policy wins 38.7% (cap 95%, at or under smart's 89.0%) with no timeouts, so the Drownbell's p90 turn cap is now 70. Tuning: Ilun's gauge rate 150 → 220, Floodtide power 14 → 13.
- `sim.py --check` passes every band; see the balance_report.md tuning log.

## Review log
