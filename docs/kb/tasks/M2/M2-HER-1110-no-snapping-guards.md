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
- [ ] Field: the leader and followers through walk, run, stop and turn-around on the slice and Act I zones.
- [ ] Cutscenes: hero actors through the slice cutscenes (prologue, Haluna beach) and the Act I greybox ones.
- [ ] Everything the guards find is fixed (or requested from the owner).

## Notes
### 2026-10-25: battle
All 26 battle clip changes × 3 heroes pass. Largest steps: Toma idle -> attack 0.219 m/frame (the strike clip's own
fastest frame is 0.175; allowed 0.377), Rhen idle -> attack 0.185 (own 0.105). The strike clips start on the idle pose,
so even a cut into one barely moves (guard checked against a zero-blend idle -> victory cut instead, which it flags).
A first, naive criterion (the clips' own motion only) flagged every change into victory: victory and idle are near
static, so any blend between them has to move the arms. That's a gesture, not a pop; the gap share fixes it.

## Review log
