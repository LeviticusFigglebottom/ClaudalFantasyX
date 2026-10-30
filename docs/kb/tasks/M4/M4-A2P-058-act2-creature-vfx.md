---
id: M4-A2P-058
title: "Act II creatures' own VFX: snagged motes, lamps, snow, wake and the regulars' skills"
role: character
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
The VFX each build left out by its sheet: the Drowner's snagged motes and drag, the Engine's lamps and KO lift, the Ram's breath, snow and ice, the Wakefin's wake and sea-glow, and the regulars' skills (the archer's jet, the urchin's rime, the moth's unravel). Hand the battle-side entries to battle-presentation (M4-A2P-060).

## Acceptance criteria
- [ ] Effects data-driven; viewed in the creature stages.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). act2_plan §3: every enemy needs its battle VFX.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30, the creatures track: **the regulars' part is specified** in [docs/kb/art/creatures/act2/skill_vfx.md](../../art/creatures/act2/skill_vfx.md): an entry per skill (tannin_jet, root_drag, leech_bite, glide_lash, rime_spine, unravel, scree_slide, skate_sting) in the Act I generator's vocabulary, for M4-A2P-060 to generate into effects.json (rendering's file, not edited here). The bosses' effects (the Drowner, the Engine, the Ram, the Wakefin) are creatures-b's and remain open.

## Review log
