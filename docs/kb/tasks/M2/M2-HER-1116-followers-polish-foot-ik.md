---
id: M2-HER-1116
title: "Followers' polish and foot IK: face the speaker, stairs and slopes, feet on uneven ground"
role: combat
status: review
owner_session: "hero-integration (session_01PzF7Jc4XVQdTWcaYUyCjPB)"
reviewer: character
depends_on: [M2-HER-1101, M2-HER-1102]
milestone: M2
request-from: lead
---
## Goal
The standing queue's item 6: the party should behave like people around Rhen, and their feet should meet the ground.

## Acceptance criteria
- [x] **Face the speaker:** when Rhen talks to someone (FieldController.interacted), every follower standing still
      turns to face the speaker. The turn is eased by its body (≤400 deg/s, head leading) and holds until Rhen walks
      on. Data: hero_motion.json `field.followers.face_release_mps`. Test: test_hero_followers (it turns, no snap,
      then faces its walk again).
- [x] **Stairs and slopes:** a follower takes a floor only within `step_m` (0.45) of Rhen's trail height, and its
      feet ease toward it at `vertical_mps` (4.0). This fixes Asha dropping 2 m through the Brightwater Ferry's pier
      edge (M2-HER-1110). Tests: test_hero_field_snaps, test_hero_followers.
- [x] **Foot IK** (`HeroFootIK`, game/hero_motion/hero_foot_ik.gd; data game/data/hero_motion/foot_ik.json): a ray
      under each foot, the foot moved by the floor's height relative to the root plane (eased at 1.5 m/s, at most
      0.3 m), the hips dropped for the lower foot, and a two-bone solve on thigh and shin in the knee's plane, with
      the foot keeping its orientation. On every field and cutscene hero body (HeroMotion.add_foot_ik). On flat ground
      it touches nothing, so flat-ground shots can't change. Tests: test_hero_foot_ik (flat is untouched; a step lifts
      one foot; lower ground drops the hips; legs keep their length; a step edge eases).
- [ ] GPU cost on the PC: 2 rays and 2 two-bone solves per body per frame, only when the floor isn't flat (Lead/PC
      to measure in the Haluna slope run).
- [ ] Shots viewed: field shots on slopes or steps (render request in the live log).

## Notes
- Battle bodies get no foot IK (the arenas are flat). Villagers (creatures' FieldNpc) can opt in with one line,
  `HeroMotion.add_foot_ik(actor)`, after FieldNpc adds its micro-motion. That's for creatures to take; offered in
  the fold-into-characters handoff.

## Review log
