---
id: M2-CMB-08
title: The slice party can Read (SPEC §6.1); the bestiary fills in the slice
role: combat
status: doing
owner_session: worktree-agent-aa4303cb02313a538
reviewer: lead
depends_on: [M1-CMB-03]
milestone: M2
request-from: "lead"
---
## Goal
Only Ysolde knows `read`, and she is not in the vertical slice (Rhen, Asha, Toma). So the slice never shows the Read panel or fills a bestiary page from a Read.

## Acceptance criteria
- [ ] One slice hero has Read, decided from the design docs and put in data.
- [ ] Tests: the slice party Reads each tideline foe (crab, eel, harrier) and the bestiary logs it.
- [ ] `sim.py --check` still passes.

## Review log
