---
id: M3-CRE-629
title: "Request: align palette.json spawn_wound usage_limit with ADR 0150 (one weak-point colour for every foe)"
role: lead
status: done
owner_session: "creatures (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY), for the Lead"
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
- [x] Accept or amend ADR 0150 (accepted by the Lead as proposed: ADR 0151) (docs/kb/decisions/0150-one-weak-point-colour-for-every-foe.md)
- [x] Reword `swatches.spawn_wound.usage_limit` in docs/kb/art/palette.json as the ADR proposes (or as amended)
- [x] color_script.md, if it repeats the old limit (it does not)

## Review log
- 2026-10-27, the Lead: approved as proposed; creatures amended palette.json and wrote ADR 0151.
