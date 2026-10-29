---
id: M3-HER-1142
title: "ADR 0041 (Act I at final quality): creatures's items in the placeholder inventory (2: 2 high, 0 medium, 0 low)"
role: character
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
ADR 0041: everything a player meets from the title to the end of Ch9 reaches final quality. integration-qa's audit
(`python3 tools/placeholder_audit.py`, docs/kb/qa/act1_final_inventory.md) lists what is still placeholder.
**creatures** owns regular enemies and wildlife. This task carries those rows; the inventory's "creatures" section is the live list.

## Acceptance criteria
- [ ] Every row of the inventory's "creatures" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [ ] The audit lists nothing for creatures: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "creatures" line.

## The rows as first audited (2026-10-28)
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: hound is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: inquisitor is a capsule stand-in

## Notes (integration-qa)
- 2026-10-29 ~23:40 integration-qa: **the audit lists nothing for this owner on lead/gate-big18** (full scan; 2 items
  in all, both env-art-b's). The owner can tick the boxes and send this to review (reviewer: qa).

## Review log
