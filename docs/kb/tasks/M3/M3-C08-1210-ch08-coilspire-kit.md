---
id: M3-C08-1210
title: Ch8 greybox to final, ch08/coilspire stood upright on env-art's Coilspire kit (the path, the hall, four tiers, the crown, the gallery)
role: cinematics
status: doing
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-ENV-10, M3-C08-02, M3-C08-1202]
milestone: M3
request-from: ""
---
## Goal
The greybox laid the spire's tiers out flat; the kit stands them up (cs_common.plan()). Swap Ch8's Coilspire to the
kit without changing the trial's rules (CoilspireTrial, ch08_field.json).

## Acceptance criteria
- [x] `tools/act1/ch08_coilspire_dressing.py`: Corrow's world frame (the kit preview's); the dressing (ground, path,
      scrub, shell, flues, tiers, hut, beacon, the flue-keys with their wheels spinning with the trial's Key blocks,
      the tier braziers on the Flame blocks with their lights, Corrow's wall as the backdrop) and the collision
      (trimesh on the shell, tiers, ground and hut; ramp chains over the five flights and the path; Gate_t1-t4 across
      flights 1-4; the path's verges; the landings' well guards). The story points moved once (`--relayout`).
- [x] The trial's 14 keys on the kit's flue-keys (its 10 angles plus four free angles on their landings).
- [x] `test_ch08_thread` and the Coilspire tests pass; `tools/tests/test_act1_kit_collision.py` checks the chains,
      the gates and the keys.
- [ ] Shots `ch08_coilspire_path`, `ch08_coilspire_hall` rendered on the PC, viewed, approved.

## Notes
- The interior grade (`coilspire_int_environment.tres`, LUT copied) isn't switched yet: the zone has one Environment.
  A trigger at the door could swap it (a Ch06Zone `lights` row by flag doesn't fit: it's by place, not story).
- ZoneKitDressing gained `spin_with` (a piece turns about its Z with its block's Y turn).

## Review log
