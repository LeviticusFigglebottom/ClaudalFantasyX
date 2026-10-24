---
id: M2-FP-17
title: The Drownbell with the real Vowbound call (replace call_ilun; band the call-into-the-flood policy)
role: combat
status: todo
owner_session: ""
reviewer: lead
depends_on: [M2-CMB-05, M2-FP-06]
milestone: M2
request-from: "lead"
---
## Goal
ADR 0027 is accepted (review-sweep-P). The m2-slice track's `call_ilun` stand-in (ADR 0024/0026) should become the real call: `engine.summon(&"ilun")`, with `ch03_ilun_bound` → `known`. Review-sweep-P found that, under the M2-CMB-04 data, a called Ilun stalls the flood phase: both sides absorb water. ADR 0027's amendments A1 and A2 (M2-CMB-05) fix the rules. This task checks the real fight.

## Acceptance criteria
- [ ] The Drownbell uses the real call. `call_ilun` is retired, or kept only as a flagged fallback; ADR 0024/0026 is noted superseded where it applies.
- [ ] `TUT_DROWNBELL_FLOOD` ("Call on Ilun") still tells the truth: calling Ilun into the flood leads to Floodnet clearing it.
- [ ] Bands re-run for the Drownbell, including a new policy that **calls Ilun when the flood rises and stays out until he falls or the bell dies**. Its win rate must not exceed the encounter's `smart` band, and it must not stall: battles end within the sim's turn cap.
- [ ] The bell's AI is checked against a lone water-absorbing foe. If the flood phase only heals Ilun, give its AI a rule that answers him (for example, Hood Slam when every foe absorbs the flood). Record the choice in battle_ctb.md.
- [ ] `sim.py --check` passes. Tests.

## Notes
- Filed on the integration branch. The m2-slice track owns the Drownbell, and its task ids run to M2-FP-16, so this is FP-17.

## Review log
