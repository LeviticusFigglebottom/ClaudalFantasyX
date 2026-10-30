---
id: M4-A2P-100
title: "placeholder_audit.py --act 2 (report only), and the Act II inventory file"
role: qa
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: lead
milestone: M4
request-from: lead
---
## Goal
ADR 0203's preparation item: extend `tools/placeholder_audit.py` (today `LAST_CHAPTER = 9`) with a `--act 2` scope over Ch10–Ch16 and Hollowmere's visit, report only, and write `docs/kb/qa/act2_final_inventory.md` from it, with owners from act2_tracks.md.

## Acceptance criteria
- [ ] The scope runs headless; its tests; the inventory file with every row owned.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). ADR 0203 names integration-qa for this. It is tools work, allowed before the gate.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log
