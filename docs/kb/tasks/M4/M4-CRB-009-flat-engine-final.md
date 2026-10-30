---
id: M4-CRB-009
title: "The flat-engine at final quality: audit, the move pass with its break and broken stance, anchors, contacts"
role: character
status: review
owner_session: "creatures-b"
depends_on: [M3-CRE-637]
reviewer: combat
milestone: M4
---
## Goal
ADR 0205 starts Act II for creatures-b. Bring the flat-engine (the Ch14 boss part on Warden Malcor Venn's pursuit barge,
docs/kb/plan/act2/bosses/malcor_venn.md, ADR 0204) to the Act I final-quality bar (ADR 0041 §3; M3-CRB-013's move pass).
Venn himself is the characters track's.

## Acceptance criteria
- [x] Audited from the battle camera on `bridal_barge_night` (7 m beyond the enemy line, on the water) and up close.
  Fixed: the stand-in yaw (90° → 20°, so the window faces the camera), a brass ring on the lid, brass seam faces.
  Still 7,620 triangles (≤ 8k).
- [x] The broken state reads as broken at battle distance: the only light out, the stack over, the drum split 14°,
  the paddles slewed, two jammed up.
- [x] Clips: `idle`, `idle_b`, `intro` (2.6 s), `ready`, `cast` (flat_pulse: wind-up 0–0.7 s, contact 0.8), `attack`
  (its copy), `hit`/`hit_b`, `ko` (the stop), `break` (phase clip, crack at 0.6), `idle_broken`,
  `hit_broken`/`hit_b_broken`, and `ko_broken`. Each starts from its stance's idle first frame. Nothing goes under the
  water.
- [x] Unweighted anchors `vfx_wound`, `vfx_core`, `vfx_phase`.
- [x] creatures.json: `contact`, `loop`, `vfx_anchors`, and the `broken` phase (`hide`/`show` swaps the lights on the
  break's first frame). No `clip_by_skill` or `break_parts` (the skills aren't in skills.json). The ready-to-paste
  block is in both sheets.
- [x] Tests: `test_flat_engine_...` in tests/unit/test_creature_bosses_act2.gd. The existing actor test
  (test_creature_actor.gd) now checks the split on `break` instead of `ko`, with the anchor bones in the rig list.
- [x] Both sheets updated, the portrait re-baked, Blender build verified byte-identical.

## Notes
- The broken stance is a pose of the rig, not a baked mesh. Both meshes share one rest geometry, so the swap only
  changes the lights and every broken clip poses the broken mesh correctly.
- Combat: Liss's lent break (M4-A2P-023) should call `enter_phase(&"broken")`. `break_parts` alone, without the phase,
  would show a dark window on an unsplit, running drum.
- There is no Ch14 lagoon arena yet; placement on the pursuit barge's `BossAnchor` is battle-presentation's.

## Review log
