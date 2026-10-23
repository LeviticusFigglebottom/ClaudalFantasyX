---
id: M1-ARC-11
title: Save and camera fixes from review-sweep-F
role: architect
status: todo
owner_session: ""
depends_on: [M1-ARC-10]
milestone: M1
request-from: "qa"
---
## Goal
Review-sweep-F findings on ARC-06/07/08/10 and PRG-03.

## Acceptance criteria
- [ ] MUST: a leftover .tmp is never 'recoverable' over a slot from a newer build or a newer version (save_system.gd ~:190); test with v99
- [ ] v2 (and every older) migration runs after, or is guarded by, shape validation; malformed old inventories read as corrupt (save_system.gd ~:368-371)
- [ ] A camera director reparented mid-cutscene drops its scripted shot (or the hold) so the autosave hold cannot leak
- [ ] Continue with a location missing from locations.json warns and never records a test location as the new save location (world_return.gd ~:80-102)
- [ ] An equipment piece cannot be worn by two heroes or by the wrong hero; load rejects it
- [ ] Second set-aside does not overwrite an existing .recovered file; same-second saves stay recoverable
- [ ] ADR 0018 amendment wording matches what Continue picks
- [ ] Tests for each

## Notes
See the review-sweep-F entries in the source tasks' Review logs for file:line.

## Review log
