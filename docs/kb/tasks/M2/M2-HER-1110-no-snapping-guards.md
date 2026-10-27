---
id: M2-HER-1110
title: "No-snapping audit: automated guards for transform snaps and clip pops across field, cutscenes and battle"
role: combat
status: doing
owner_session: "hero-integration (session_01PzF7Jc4XVQdTWcaYUyCjPB)"
reviewer: qa
depends_on: [M2-HER-1101, M2-HER-1103, M2-HER-1104]
milestone: M2
request-from: lead
---
## Goal
The human's #1 playtest complaint was rigid, snapping motion. Make "no snapping" a test, not an impression: sample hero
(and villager) motion and fail on per-frame jumps.

## Acceptance criteria
- [x] `HeroMotionGuard` (game/hero_motion/hero_motion_guard.gd; limits in game/data/hero_motion/motion_guard.json):
      transform snaps (speed, yaw rate, deliberate cuts reported apart) and clip-change pops (every bone, against
      the clips' own motion plus the pose gap spread over the blend), plus zero cross-fades.
- [x] Battle: every clip change the battle makes, on the real Rhen, Asha and Toma (tests/unit/test_hero_battle_pops.gd).
- [x] Field: the leader and followers through walk, run, stop and turn-around on the slice and Act I zones
      (tests/unit/test_hero_field_snaps.gd, 13 walkable zones; first_verse has no field player).
- [ ] Cutscenes: hero actors through the slice cutscenes (prologue, Haluna beach) and the Act I greybox ones.
- [ ] Everything the guards find is fixed (or requested from the owner).

## Notes
### 2026-10-25: battle
All 26 battle clip changes × 3 heroes pass. Largest steps: Toma idle -> attack 0.219 m/frame (the strike clip's own
fastest frame is 0.175; allowed 0.377), Rhen idle -> attack 0.185 (own 0.105). The strike clips start on the idle pose,
so even a cut into one barely moves (guard checked against a zero-blend idle -> victory cut instead, which it flags).
A first, naive criterion (the clips' own motion only) flagged every change into victory: victory and idle are near
static, so any blend between them has to move the arms. That's a gesture, not a pop; the gap share fixes it.

### 2026-10-27: field
- **Found and fixed:** on the Brightwater Ferry, Asha dropped 2 m in one frame and popped back over two frames. Her
  floor ray fell through a gap at the pier's edge that Rhen's capsule spans. HeroFieldParty now takes a floor only
  within `step_m` (0.45) of the height Rhen walked at that trail point, else his height, and eases the feet toward it
  at `vertical_mps` (4.0), so a stair or a slope no longer pops either.
- Every other zone: peaks at the 3.6 m/s run and the 400 deg/s turn cap. Followers catching up reach 5.4 m/s (their
  data cap; inside the guard's 6.0). Rhen peaks at 5.85 m/s on Pemakar and 5.49 on Ashcrown: slope or step
  push-ups from the CharacterBody, under the limit. Worth a look in play (FieldController is m2-slice's).

## Review log
