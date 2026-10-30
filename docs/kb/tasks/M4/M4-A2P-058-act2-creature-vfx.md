---
id: M4-A2P-058
title: "Act II creatures' own VFX: snagged motes, lamps, snow, wake and the regulars' skills"
role: character
status: review
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
- 2026-10-30, the creatures track: **the regulars' part is specified** in [docs/kb/art/creatures/act2/skill_vfx.md](../../art/creatures/act2/skill_vfx.md): an entry per skill (tannin_jet, root_drag, leech_bite, glide_lash, rime_spine, unravel, scree_slide, skate_sting) in the Act I generator's vocabulary, for M4-A2P-060 to generate into effects.json (rendering's file, not edited here). The bosses' effects (the Drowner, the Engine, the Ram, the Wakefin) are creatures-b's and remain open.

## Review log
- 2026-10-30, creatures-b: claimed **the four bosses' part** (ADR 0205): the Drowner's snagged motes and drag, the
  Engine's lamps and KO lift, the Ram's breath and snow (**no ice**: ADR 0015, M4-A2P-059 — the title's "ice" is
  void), the Wakefin's wake and sea-glow, as each creature scene's own ambient effects (game/creatures/<id>/).
  Battle-skill VFX stay battle-presentation's (effects.json). **The regulars' skills (archer's jet, urchin's rime,
  moth's ...) are the creatures track's** (act2_tracks.md's per-id ownership); creatures-b leaves them.
- 2026-10-30, creatures-b: **the four bosses' part built, to review (combat).** CreatureAmbientVfx
  (`game/creatures/ambient_vfx/creature_ambient_vfx.gd`, an `AmbientVfx` child of each boss's battle scene) reads the
  actor (clip, clip time, KO, phase, node visibility) and builds every effect from
  `game/data/creatures/creature_vfx.json`: the Drowner's snagged-mote drift and halos, their upward lift (on a break
  part's hide and on the KO) and the drag's churn; the Engine's steady lamp and core halos and core light (no flicker:
  colour script rule 2), going dark with its lamp glass on the KO as twelve motes lift out of the core; the Ram's
  breath, snow and drips on hits and the fleece shake, and shed `glimmer_held` motes (soft puffs only, no ice); the
  Wakefin's sea-glow wake held level on the water line. Each art sheet's "Own VFX" says what and why;
  tests/unit/test_creature_vfx_act2.gd; prewarm entries for the four materials. Viewed on lavapipe in the bosses'
  arenas (battle camera and close). **For battle-presentation:** the Drowner's `break_parts` lift fires on its own
  when combat keys the snag cradles; the arena previews still seat capsules for these four (no enemies.json
  `model` yet), so `battle_arena_*` shots do not show these effects; the `creature_*` shots change (the halos, the
  drift, the wake) and need new baselines.
