---
id: M4-CRB-002
title: "The Mangrove Drowner at the Act I bar: its own clip per skill, the risen stance's clips, planted roots, anchors and snag-root parts"
role: character
status: review
owner_session: "creatures-b"
depends_on: [M3-CRE-622, M3-CRB-015]
reviewer: combat
milestone: M4
request-from: ""
---
## Goal
ADR 0041 §3 and ADR 0205 (Act II starts for creatures-b): bring the Ch10 boss to the Act I bosses' move-pass bar
(M3-CRB-013) from its design sheet, [mangrove_drowner.md](../../plan/act2/bosses/mangrove_drowner.md), and its art sheet,
[act2/mangrove_drowner.md](../../art/creatures/act2/mangrove_drowner.md).

## Acceptance criteria
- [x] Audited from the battle camera in `ossa_fen_roots` and up close; anything unfinished or off-sheet fixed within
      the 18k budget (the snag roots' motes and their torn state were missing).
- [x] Clips: `intro` (1.5-3.5 s), `ready`, `idle_b`, one clip per skill on the sheet with a wind-up of at least 0.45 s,
      `hit`/`hit_b`, `snag_break`, `phase_change` into `uprooted`, that phase's stance versions through its `clips` map,
      and `ko_risen`. Every clip starts and ends on its phase's idle first frame; nothing goes under the water; planted
      roots stay planted (IK at every frame).
- [x] Unweighted anchors `vfx_wound`, `vfx_core`, `vfx_phase`.
- [x] creatures.json: `contact` for every striking clip, the phase `clips` map, `vfx_anchors`. No `clip_by_skill` (the
      skills are combat's, not in skills.json yet): the clip map for combat is in the design sheet's move list and the
      art sheet's "As built".
- [x] tests/unit/test_creature_bosses_act2.gd (`test_mangrove_drowner_*`).
- [x] Art sheet "As built" and budget; design sheet marks what is built; PROVENANCE row for `mote_snag.tres`.

## Notes
- For combat (M4-A2P-010): paste the clip map, `break_parts` and the boss seat from the art sheet's "As built" when the
  skills and the enemy row land.

## Review log
