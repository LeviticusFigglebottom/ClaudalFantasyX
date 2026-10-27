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
- [ ] With hero-integration's real heroes on this branch: check each hero's stand_in `radius` matches its footprint,
      and view a melee freeze-frame per hero.

## Review log
