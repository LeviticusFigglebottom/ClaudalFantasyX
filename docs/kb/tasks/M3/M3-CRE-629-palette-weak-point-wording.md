---
id: M3-CRE-629
title: "Request: align palette.json spawn_wound usage_limit with ADR 0150 (one weak-point colour for every foe)"
role: lead
status: todo
owner_session: ""
reviewer: character
depends_on: []
milestone: M3
request-from: creatures
---
## Goal
(Routed to the Lead: docs/kb/art/** is the art-direction stream's, which has no task-board role.)
palette.json says `spawn_wound` is never a non-Undertow creature's weak point. The creature README and every
shipped non-spawn creature use it as their (small, closed) weak point. ADR 0150 (proposed) keeps one weak-point
colour for every foe (pillar 4) and keeps the wound *language* (open seams, motes) for spawn.

## Acceptance criteria
- [ ] Accept or amend ADR 0150 (docs/kb/decisions/0150-one-weak-point-colour-for-every-foe.md)
- [ ] Reword `swatches.spawn_wound.usage_limit` in docs/kb/art/palette.json as the ADR proposes (or as amended)
- [ ] color_script.md, if it repeats the old limit

## Review log
