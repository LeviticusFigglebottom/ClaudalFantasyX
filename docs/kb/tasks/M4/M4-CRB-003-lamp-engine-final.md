---
id: M4-CRB-003
title: "The Lamp Engine at final quality: audit, the full move pass from the battle camera, anchors, contacts"
role: character
status: review
owner_session: "creatures-b"
depends_on: [M3-CRE-623, M3-CRB-015]
reviewer: combat
milestone: M4
---
## Goal
ADR 0205 starts Act II for creatures-b. Bring the Lamp Engine (the Ch11 boss, docs/kb/plan/act2/bosses/lamp_engine.md,
ADR 0204) to the Act I final-quality bar (ADR 0041 §3; M3-CRB-013's move pass): nothing a player sees reads unfinished,
from the battle camera or up close. The conduit crawlers are the creatures track's, not this task's.

## Acceptance criteria
- [x] Audited from the battle camera in `lowlight_engine_hall` and up close; primitive or off-sheet parts fixed within
  the 20k budget (18,680 triangles).
- [x] Clips per the design sheet: `intro` (2.8 s), `ready`, one clip per skill (wind-up ≥ 0.45 s before contact),
  `hit`/`hit_b`, `phase_change` into `opened` with its stance and phase versions through the `clips` map, `ko`. Every
  clip starts and ends on its phase's idle first frame; nothing under the floor; planted feet don't slide.
- [x] Unweighted anchors `vfx_wound`, `vfx_core`, `vfx_phase`.
- [x] creatures.json: `contact` for every striking clip, the phase `clips` map, `vfx_anchors`. No `clip_by_skill`
  (the skills aren't in skills.json yet); the ready-to-paste table is in both sheets.
- [x] tests/unit/test_creature_bosses_act2.gd (`test_lamp_engine_...`): the clip set, intro length, anchors, wind-ups,
  the open stance mapping.
- [x] Art sheet "As built" (budget, clips, the combat clip map); design sheet marks what is built.

## Notes
- No gold mote-light from the engine: the lamps and core stay `glimmer_bound`. The opened burst (`vfx_phase`) and the
  KO lift (`vfx_core`) are battle-presentation's VFX.
- The stand-in yaw went from 90° to 55°. Side-on, the near arm cut across the core.
- The ring break parts are not built. `break_parts` is keyed by skill id, so it waits for M4-A2P-022, and the broken
  lamp meshes need a budget call (see the art sheet).
- With no `lamp_engine` enemy row, the arena preview (`battle_arena_lowlight_engine_hall`) still draws a capsule.
  That is combat's row.

## Review log
