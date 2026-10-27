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
- [ ] With hero-integration's real heroes on this branch: check each hero's stand_in `radius` matches its footprint,
      and view a melee freeze-frame per hero.

## Review log
