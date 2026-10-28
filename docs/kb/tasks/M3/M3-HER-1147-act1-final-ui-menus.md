---
id: M3-HER-1147
title: "ADR 0041 (Act I at final quality): ui-menus's items in the placeholder inventory (3: 0 high, 3 medium, 0 low)"
role: ui
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
**ui-menus** owns UI. This task carries those rows; the inventory's "ui-menus" section is the live list.

## Acceptance criteria
- [ ] Every row of the inventory's "ui-menus" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [ ] The audit lists nothing for ui-menus: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "ui-menus" line.

## The rows as first audited (2026-10-28)
- **medium**, all: `assets/ui/portraits/heroes/kerrid_neutral.png`: no menu portrait for kerrid (the page shows an initial)
- **medium**, all: `assets/ui/portraits/heroes/liss_neutral.png`: no menu portrait for liss (the page shows an initial)
- **medium**, all: `assets/ui/portraits/heroes/ysolde_neutral.png`: no menu portrait for ysolde (the page shows an initial)

## Review log
