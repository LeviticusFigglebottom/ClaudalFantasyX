---
id: M3-C04-06
title: Ch4 creatures in battle (sail_leech, bottle_hermit, spar_wraith) and combat rulings on the derelict's bands
role: combat
status: todo
owner_session: ""
depends_on: [M3-C04-02]
milestone: M3
request-from: cinematics
---
## Goal
M3-C04-02 added the derelict's foes to the battle tables with stand-in shapes. Two parts:

**Creatures (with character art).** The models exist on `claude/creatures` (`assets/creatures/{sail_leech,bottle_hermit,spar_wraith}`, docs/kb/art/creatures/act1/). Seat them on the battle stage, with the Spar-Wraith's two phase models (the rigging as its body in phase 1, dropped to the deck and sheathed in water in phase 2), and the bottle-hermit's glass reading as a plain oil-lamp glass, never a bound housing (act1_ch04.md §9 Creatures, keep-all answer 3). Ysolde's first-cast fan-arc in this fight is character art's.

**Rulings (balance_targets.md "Ch4").**
1. **The leeches' `role_answer` is report only.** Rhen answers them and is already on the field, so the policy plays like the masher. Keep that, or give the leech something only its answer meets?
2. **The Spar-Wraith's `smart` ceiling is lifted to 100%** (with a mean-turns floor of 30). Asha's Mend out-heals any damage that `role_answer` survives. Keep the exception, or add a mechanic that taxes healing?
3. **The sim plays every opening as normal** (BattleSim never sets `engine.opening`), so the scripted leech ambush is measured without it. Simulate openings?
4. **"Fragile once they've struck"** (the leech) and **"reflects fire"** (the hermit) have no engine rule: the leech is evasive, and the glass is immune to fire. Rule whether either needs a mechanic.
5. **Battle barks** (§5: Ysolde's first cast, Toma's "On my shield") are spoken before the fight, because the engine has no in-battle barks.
6. **Phase prompts show on every attempt**, not once by a seen-flag (as Ch1's).

## Acceptance criteria
- [ ] The three creatures stand on the battle stage in place of the stand-ins.
- [ ] Each ruling is recorded in balance_targets.md, with the bands and `targets.json` changed to match, and `sim.py --check` passes.

## Notes

## Notes (creatures)
- 2026-10-27, creatures: the creatures part is in place. sail_leech, bottle_hermit and spar_wraith have enemies.json `model` rows and stand on the battle stage. The Spar-Wraith's phase models are in creatures.json `phases`. The rulings are Combat's.

## Review log
