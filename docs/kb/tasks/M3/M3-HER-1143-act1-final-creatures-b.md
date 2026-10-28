---
id: M3-HER-1143
title: "ADR 0041 (Act I at final quality): creatures-b's items in the placeholder inventory (6: 6 high, 0 medium, 0 low)"
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
**creatures-b** owns bosses and the Vowbound. This task carries those rows; the inventory's "creatures-b" section is the live list.

## Acceptance criteria
- [ ] Every row of the inventory's "creatures-b" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [ ] The audit lists nothing for creatures-b: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "creatures-b" line.

## The rows as first audited (2026-10-28)
- **high**, Ch4: `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: spar_wraith is a capsule stand-in
- **high**, Ch5: `game/levels/ch05/ashcrown/ashcrown.tscn`: matron is a capsule stand-in
- **high**, Ch6: `game/data/battle/enemies.json#stillguard_inquisitor`: foe stillguard_inquisitor fights as a primitive stand-in (no model)
- **high**, all: `game/data/battle/vowbound.json#ilun`: Vowbound ilun is drawn as a primitive (no actor scene)
- **high**, all: `game/data/battle/vowbound.json#kahre`: Vowbound kahre is drawn as a primitive (no actor scene)
- **high**, all: `game/data/battle/vowbound.json#virel`: Vowbound virel is drawn as a primitive (no actor scene)

## Review log
