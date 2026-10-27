---
id: M3-BPR-402
title: "Melee spacing: heroes and creatures never interpenetrate"
role: combat
status: review
owner_session: battle-presentation (session_014EcW9e5tEmjDi5S2HmCECd)
depends_on: [M2-BPR-01]
milestone: M3
request-from: lead
reviewer: lead
---
## Goal
With the real hero rigs (claude/hero-integration), approach and return paths, facing and spacing must read: no two
fighters overlap at contact.

## Acceptance criteria
- [x] A melee run stops by both bodies' radii + clearance (lunge included), against every body in its path.
- [x] Test: hero on creature and creature on hero, sampled across the sequence, no overlap.
- [x] A body beside the path turns the run (melee_approach) instead of stopping it short: Rhen used to strike the
      air 2.9 m from the reef crab in battle_choreo_hit.
- [x] Shots viewed and re-approved: battle_choreo_melee, battle_choreo_hit (with 401: battle_choreo_ko, battle_choreo_toll).
- [x] With the real heroes (big9, characters' `*_battle.tscn`), checked headlessly on 2026-10-27:
      - every contract clip is present except the optional `revive`;
      - contact markers on attack 0.33 s, cast 0.8, item 0.47, finisher 0.87, read 0.6;
      - footprints Rhen 0.45 m, Asha 0.41, Toma 0.56. The spacing uses these, and the stand-in `radius` (0.32,
        0.28, 0.42) applies only to a primitive.
- [ ] View a melee freeze-frame per hero: in the PC render request at 25dcea24 (battle_choreo_*).

## Review log
