---
id: M1-CMB-08
title: Wire the shrine HP/MP carry-over into live battles; economy.md cleanups
role: combat
status: doing
owner_session: "worktree-agent-af6af1b46e0ce25af"
depends_on: [M1-ARC-06]
milestone: M1
request-from: "architect"
---
## Goal
ARC-06 asked Combat to wire party HP/MP carry-over; until then a shrine heal restores nothing in play.

## Acceptance criteria
- [ ] Live battles start from the party's carried HP/MP (and write it back at the end); the ARC-06 event is consumed
- [ ] Decide and document what a KO'd member does at battle start
- [ ] economy.md: Ember Pot price 220; remove the stale 'fold into formulas.md' paragraph (~:72)
- [ ] formulas.md:58 'can't launder' wording fixed; the balance test reads the ceiling from targets.json
- [ ] Tests; game/battle coverage does not drop

## Notes
See the review-sweep-F entries in the source tasks' Review logs for file:line.

## Review log
