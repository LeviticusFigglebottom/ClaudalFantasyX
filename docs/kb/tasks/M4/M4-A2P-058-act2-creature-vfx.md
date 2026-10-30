---
id: M4-A2P-058
title: "Act II creatures' own VFX: snagged motes, lamps, snow, wake and the regulars' skills"
role: character
status: doing
owner_session: "creatures-b (the four bosses' part; the regulars' part stays with creatures)"
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

## Review log
- 2026-10-30, creatures-b: claimed **the four bosses' part** (ADR 0205): the Drowner's snagged motes and drag, the
  Engine's lamps and KO lift, the Ram's breath and snow (**no ice**: ADR 0015, M4-A2P-059 — the title's "ice" is
  void), the Wakefin's wake and sea-glow, as each creature scene's own ambient effects (game/creatures/<id>/).
  Battle-skill VFX stay battle-presentation's (effects.json). **The regulars' skills (archer's jet, urchin's rime,
  moth's ...) are the creatures track's** (act2_tracks.md's per-id ownership); creatures-b leaves them.
