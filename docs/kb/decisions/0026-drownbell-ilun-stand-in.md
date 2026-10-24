# 0026 — The Drownbell's Ilun call is a first-playable stand-in for Vowbound

- **Status:** accepted
- **Date:** 2026-10-23
- **Roles affected:** Combat, UI, Narrative, Lead (first playable)
- **Author role:** Combat (M2-FP-06, first-playable stream)

## Context
SPEC §6.3: when a Vowbound is summoned it **replaces the whole party on the field**, with its own HP, abilities and Swell, and a full cinematic on first use. vertical_slice.md §5 makes the Drownbell's phase 2 the slice's one Vowbound moment: the spawn-polyps heal the bell faster than the party can kill them, and summoning Ilun clears the water field with *Floodnet*. M2-FP-06 has to ship the Drownbell for the first playable now, and the Vowbound system (party replacement, summon HP and Swell, summon cinematics) does not exist yet. Building it is well beyond this task.

## Options
1. Build the Vowbound system first, then the boss. Correct, but it blocks the first-playable thread on a system with its own design, art and cinematic work.
2. Ship phase 2 without Ilun (for example, the party just out-damages the polyps). This loses the phase's lesson and contradicts the story beat.
3. A stand-in: an ordinary Asha skill, *Call Ilun*, that only exists once `ch03_ilun_bound` is set and does what Floodnet does to the fight (ends the water field and the polyps bound to it), built on generic, data-driven engine rules (`requires_flag`, `clears_field`, fields, field-bound combatants) that the real summon can reuse.

## Decision
Option 3. `call_ilun` (skills.json) is a 12 MP, rank-4 magical hit on all foes with `requires_flag: ch03_ilun_bound` and `clears_field: flood`. Party members only know a flag-locked skill when the flag is in `BattleEngine.story_flags`, which the battle scene fills from `Game.get_flag` before `setup()` (the engine stays headless). The skill is refused at no cost while no field is up. Ilun does not replace the party and has no HP, Swell or cinematic. The balancing simulator's `role_answer` and `smart` policies call it as soon as the field is up (`sim_policies.json` `clear_field_skill`). Details: battle_ctb.md "The Drownbell (M2-FP-06)".

## Consequences
- The slice's phase 2 plays as written (the water feeds it; call on Ilun) and is balanced against it (balance_report.md).
- When the Vowbound system lands, replace `call_ilun` with the real summon command and keep the field rule as Floodnet's effect. The bands must then be re-run, since a summon that takes the hits changes phase 2's damage race.
- The full first-use cinematic (C10) and the "the party steps off the field" read are missing from the first playable. Playtest notes should not judge the Vowbound feel from this stand-in.
- `requires_flag`, fields and field-bound combatants are general tools; other story-gated skills can use them.
- 2026-10-24 (Lead, at merge): renumbered from 0024 to 0026, because 0024 was already taken on the integration branch by 0024-asha-hair-shading-values.

## Superseded in the simulator (M2-FP-17, m2-slice, 2026-10-24)
The Drownbell's bands are now measured with the real Vowbound call (ADR 0027): the sim's `ch03_drownbell` loadout retires `call_ilun`, and the policies call Ilun into the flood. The live game keeps `call_ilun` as the fallback until M2-UI-05 gives the player the Call command. Then it is removed from Asha and this ADR is fully superseded.

## Fully superseded (M2-FP-17, m2-slice, 2026-10-24)
M2-UI-05's Call row landed (batch 3), so `call_ilun` is removed: from Asha's kit, from skills.json with its loc key, and from the simulator (`clear_field_skill`). Ilun is bound by vowbound.json's `bound_flag` (`ch03_ilun_bound`), and his finisher, Floodnet, clears the flood (ADR 0027 A2). This ADR now records history only.
