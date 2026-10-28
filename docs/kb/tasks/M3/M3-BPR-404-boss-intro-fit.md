---
id: M3-BPR-404
title: "Boss intros: fit the camera to the boss model's bounds (Hullgnaw framed too close)"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-BPR-02]
milestone: M3
request-from: lead
reviewer: lead
---
## Goal
The human's playtest: the Hullgnaw boss intro is framed too close. The intro shots (camera.shots `boss`,
`boss_tall`, `boss_skyward`) used fixed offsets tuned on primitive stand-ins, and the real creature models are
much bigger. FAST-TRACK playtest fix.

## Design
- BattleBossIntro keeps each shot's angle and fov but moves the camera along its line of sight, so a sphere around
  the boss's visible meshes (its world AABB in camera-parent space) fits the narrower field of view at
  `boss_intro.fit.margin`, clamped to `min_m`..`max_m`, aimed `look_drop` of the radius below the centre.
- The bounds' top and bottom must pass the safe frame, and the feet must clear the title card's top edge by
  `card_clear_px`. A first pass with only the widening let the Inquisitor's small capsule (pinned at min_m) and the
  Matron's base sink behind the card.
- The search aims lower first (`drop_step` to `drop_max`, which lifts the boss), then widens (× `widen_step` to
  `widen_max`); the closest pose that holds wins. With none clearing the card it takes the closest that passes the
  safe frame; with none at all, the default camera (as before).
- A row may set `fit_margin` or `fit: false` (the old offsets). No row needs either today.
- Data: `game/data/battle/choreo.json` `boss_intro.fit`. Code: `game/battle/scene/battle_boss_intro.gd`
  (`_bounds`, `_fit`, `_fit_search`, `_clears_card`). Tests: `tests/unit/test_battle_boss_intro.gd`.

## Acceptance criteria
- [x] Every boss intro still frames its boss inside the safe frame (test_each_row_frames_its_boss).
- [x] The distance follows the model size and keeps the shot's angle and fov; a row's fit_margin overrides the
      margin; every boss's feet clear the title card (new tests).
- [x] All six battle_boss_intro_* shots captured and viewed; the boss reads whole above the card.
- [x] PC render gpu/render-battle-presentation-25dcea2 viewed (2026-10-27). hullgnaw, matron, drownbell and wraith
      were re-approved at 89ffba3c; inquisitor and hermit pass unchanged.
- [x] **big11 regression** (the Lead's view): the real Toma stood huge at the right edge of the Drownbell's intro,
      over the timeline.
  - The fit now also needs the party clear: every party member wholly off screen, or inside the HUD-safe frame and at
    most `fit.party_max_h` (0.3) of the screen tall.
  - The search orbits the shot about the boss (`fit.yaw_steps_deg`, its own angle first) to find such a frame.
  - Test `test_no_party_member_crowds_a_boss_intro` covers every boss intro with its full party. Without the orbit,
    only the Drownbell fails it, so the other five keep their frames.
- [x] PC render of all six (FAST-TRACK) viewed: drownbell, matron, wraith at 7aa31b6f; hullgnaw after the 0.36 fix (cloud render 60cbb21). The Lead merges.

## Moved shots
All six, re-approved after viewing (captured on the integration branch + 404 only):
- battle_boss_intro_hullgnaw (rmse 0.253): whole serpent and ribs above the card; the old shot showed a leg and a jaw.
- battle_boss_intro_matron (0.109) and battle_boss_intro_drownbell (0.104): their bases now clear the card.
- battle_boss_intro_inquisitor (0.053): his capsule whole above the card, a little closer.
- battle_boss_intro_hermit (0.039) and battle_boss_intro_wraith (0.039): small reframes.

## Review log
