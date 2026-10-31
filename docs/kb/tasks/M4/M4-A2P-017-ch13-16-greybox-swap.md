---
id: M4-A2P-017
title: "Swap the Ch13–16 and Hollowmere greyboxes onto env-art-b's kits (the Ch10–12 swap is M3-ENV-736)"
role: cinematics
status: doing
owner_session: "act1-chapters"
depends_on: [M4-C13-02, M4-C14-02]
reviewer: environment
milestone: M4
request-from: lead
---
## Goal
The same job as M3-ENV-736 for Ch13–Ch16 and `ch17/hollowmere`: remove the greybox blocks as env-art-b's dressing lands, keep the marks and triggers the flow reads, and keep the walkable tests green.

## Acceptance criteria
- [ ] Zero greybox blocks in the six zones; walkable and thread tests green; audit zero greybox items.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §0: no chapter is called playable on greybox.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters, 2026-10-31:** already met in every zone but the Choir. Each Ch10–Ch16 zone and Hollowmere
  instances env-art-b's `ZoneKitDressing`, whose `greybox` row is `{"hide_all": true}` (the greybox meshes hide,
  and their collision stays under the kit). The Act II placeholder audit (`tools/placeholder_audit.py --act 2`,
  with the runtime scan) lists no greybox item in this lane. **The Drowned Choir** has no dressing yet: it waits
  on env-art-b after M4-A2P-106's relayout. Its walk and thread tests are green.

## Review log
