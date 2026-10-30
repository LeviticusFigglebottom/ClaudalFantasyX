---
id: M4-A2P-1403
title: "Ch4 derelict: the hero slides round the hold hatch's 0.42 m coaming instead of catching on its corner (cloud-qa)"
role: environment
status: review
owner_session: "claude/env-art"
depends_on: []
reviewer: qa
milestone: M4
request-from: lead
---
## Goal
cloud-qa (via the Lead, 10-30): walking straight at the corner of the derelict's bottle-hermit hold hatch, the hero
catches on its 0.42 m lip.

## Acceptance criteria
- [x] The hatch's collider has chamfered corners, so the capsule slides round.
- [x] A probe shows it: walking along -x at the corner (lateral offsets 0.0 and 0.1 m), the old square stops the
      hero after 0.5 m, and the octagon lets him slide on 4.35 m. Walking into the flat face still stops him.

## Notes
`tools/act1/ch04_ferry_dressing.py` `derelict_hatch()` replaces the one `DerelictHatch` box with an octagon: a cross of
two boxes, plus four boxes turned 45 degrees whose outer faces are the 0.25 m chamfers. Nothing else names the
block. Only the collider changes (brightwater_ferry_collision.json); the mesh is unchanged.

## Review log
