---
id: M1-ARC-14
title: Lattice: a save naming another board is frozen, not rewritten
role: architect
status: todo
owner_session: ""
depends_on: [M1-ARC-13]
milestone: M1
request-from: "qa"
---
## Goal
From the review-sweep-J entries (file:line references there).

## Acceptance criteria
- [ ] A save whose Lattice board differs from the loaded one is frozen (no rewrite of the board field; positions kept) (lattice_progress.gd ~:305, ~:337-341)
- [ ] battle_stage.gd ~:38 and debug_readouts.gd ~:212 load the board the save names, or refuse
- [ ] The start node is not added to activated when a saved position is lost (~:362)
- [ ] Tests

## Review log
