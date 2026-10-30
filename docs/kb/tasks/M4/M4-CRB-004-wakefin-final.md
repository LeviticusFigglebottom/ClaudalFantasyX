---
id: M4-CRB-004
title: "The Wakefin at the final bar: breach root, anchors, a clip per skill, the close circle, staged off the barge"
role: character
status: review
owner_session: creatures-b
depends_on: [M3-CRE-626, M3-CRE-635]
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
The Wakefin (Ch15 boss, docs/kb/plan/act2/bosses/wakefin.md) at the Act I final-quality bar (ADR 0041 §3), under
ADR 0204: one whole animal, no deck adds, no fin target or part, `sound_dive` evasive with a clear telegraph, never
untargetable; darkness never hides what the timeline shows.

## Acceptance criteria
- [x] Audit at battle distance and up close on the bridal barge at night; fixes in budget (11,128 triangles of 14k).
- [x] Clips: `intro` (3.0 s), `ready`, `idle_b`, a clip per proposed skill (`attack`/Fin Cut, `dive`/Sound Dive,
      `rise_strike`, `wake_wash`, `bill_strike_close`) with wind-ups ≥ 0.45 s, `hit`/`hit_b`, the `close_circle`
      phase (`phase_close`, `idle_close`, every stance variant through the phase `clips` map), `ko`. Every clip starts
      and ends on its phase's idle first frame; nothing passes through the barge (tools/tests/test_wakefin.py).
- [x] Anchor bones `vfx_wound`, `vfx_core`, `vfx_phase` (unweighted).
- [x] creatures.json `contact` for every striking clip and the phase `clips` map; no `clip_by_skill` (the skills are
      combat's). The clip map for combat is in the design sheet and the art sheet's "As built".
- [x] tests/unit/test_creature_bosses_act2.gd (`test_wakefin_*`); the Wakefin case in test_creature_actor.gd updated
      for the new bones.
- [x] Art sheet "As built" and budget, design sheet marked built. No new material, so no new PROVENANCE row.

## Notes
- **For combat (reviewer):** add the enemy row and skills, then `clip_by_skill`
  `{"fin_cut": "attack", "sound_dive": "dive", "wakefin_rise": "rise_strike", "wake_wash": "wake_wash",
  "bill_strike": "bill_strike_close"}` and the enemy's `close_circle` phase at 50%.
- **For battle-presentation (M4-A2P-062):** the clips are staged at (−5.0, −0.6, −6.5), `yaw_deg` 90 (build_wakefin
  `STAGE_POS`/`STAGE_YAW`). The arena's `BossAnchor` (−10, −0.6, −1.5) is outside the battle camera's frame and puts
  the bill into the bow, and bosses are seated today on enemy slot 0, on the deck. Seat it at the staging (or move the
  anchor), with `travel: none` for its strikes. The wake, the rise's ring of sea-glow and the seam brightening are
  VFX and rendering. A held "dived" idle while the evasion lasts is not built (the `dive` clip ends surfaced, per the
  clip rule); ask if presentation wants one.
- Self-rendered and viewed: `creature_wakefin`, `creature_wakefin_body`, and every clip at five beats on the barge at
  night from the battle camera and a close camera. Baselines not written.

## Review log
