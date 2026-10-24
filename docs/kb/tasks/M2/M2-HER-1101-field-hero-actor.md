---
id: M2-HER-1101
title: "Field hero actor: the player's capsule becomes Rhen, with a locomotion blend, eased turning and ground alignment"
role: architect
status: doing
owner_session: "hero-integration (claude/hero-integration)"
reviewer: character
depends_on: []
milestone: M2
request-from: lead
---
## Goal
The human's playtest: walking around in the field, the heroes are still capsules. The player becomes the real Rhen
model in every slice zone (Haluna, the Saltgrass Causeway, the Shell Shrine, the tideline / First Verse) and moves
naturally: no snapping turns, no instant start or stop.

## Acceptance criteria
- [ ] `HeroFieldActor` (game/hero_motion/) shows a hero model on a FieldController and hides its capsule stand-in;
      one hook line (`HeroFieldActor.attach(self)` in FieldController._ready, like FieldHud) covers every zone, the
      greybox zones included, with no zone scene edits.
- [ ] An AnimationTree locomotion BlendSpace1D (idle / walk / run by ground speed) with a playback scale so the feet
      plant (clip speeds measured from the clips, in game/data/hero_motion/hero_motion.json).
- [ ] The visible body turns toward its travel at a data-driven max turn rate, eased in and out, never snapping
      (HeroLocomotion). When still it turns to its node's facing (so cutscene `_face` calls on the player ease too).
- [ ] Foot-plant-friendly start and stop: the gait speed is filtered, and the field acceleration and deceleration are
      tuned so the body visibly accelerates (field_movement.json, coordinated with m2-slice).
- [ ] Ground alignment: feet on the floor (the controller's origin is its feet), teleports and zone loads snap.
- [ ] Tests: turn-rate cap and no snapping frame to frame, blend weights by speed, the hook hides the stand-in, the
      clips exist on the model. Shots: field_hero_rhen_* (viewed).

## Notes
- ADR 0190. Core maths: game/hero_motion/hero_locomotion.gd (tests/unit/test_hero_locomotion.gd).
- m2-slice owns the zone flow and scenes; this adds no zone edits. Its live log is told.

## Review log
