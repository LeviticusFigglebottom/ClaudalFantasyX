---
id: M3-HER-1145
title: "ADR 0041 (Act I at final quality): act1-chapters's items in the placeholder inventory (3: 3 high, 0 medium, 0 low)"
role: cinematics
status: review
owner_session: "act1-chapters (claude/act1-chapters)"
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
ADR 0041: everything a player meets from the title to the end of Ch9 reaches final quality. integration-qa's audit
(`python3 tools/placeholder_audit.py`, docs/kb/qa/act1_final_inventory.md) lists what is still placeholder.
**act1-chapters** owns placement and flow. This task carries those rows; the inventory's "act1-chapters" section is the live list.

## Acceptance criteria
- [x] Every row of the inventory's "act1-chapters" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [x] The audit lists nothing for act1-chapters: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "act1-chapters" line.

## The rows as first audited (2026-10-28)
- **high**, Ch8: `game/data/battle/encounters.json#ch08_flue_moths`: encounter ch08_flue_moths has no arena: it fights on the sandbox's own set
- **high**, Ch8: `game/data/battle/encounters.json#ch08_headland_crabs`: encounter ch08_headland_crabs has no arena: it fights on the sandbox's own set
- **high**, Ch8: `game/data/battle/encounters.json#ch08_headland_gulls`: encounter ch08_headland_gulls has no arena: it fights on the sandbox's own set

## Review log
- 2026-10-29 act1-chapters: the three rows were fixed in 41bc33e7 (ch08_headland_gulls and ch08_headland_crabs on `coilspire_headland_path`, ch08_flue_moths on `coilspire_tier_landing`); `python3 tools/placeholder_audit.py --static-only` lists nothing for act1-chapters. To review.
