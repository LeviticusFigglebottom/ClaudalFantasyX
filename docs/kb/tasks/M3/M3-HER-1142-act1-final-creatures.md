---
id: M3-HER-1142
title: "ADR 0041 (Act I at final quality): creatures's items in the placeholder inventory (2: 2 high, 0 medium, 0 low)"
role: character
status: done
owner_session: "creatures (session_01UPFyE7ob7hr4Skv4cw3rtN)"
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
- [x] Every row of the inventory's "creatures" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [x] The audit lists nothing for creatures: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "creatures" line.

## The rows as first audited (2026-10-28)
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: hound is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: inquisitor is a capsule stand-in

## Notes (creatures, 2026-10-29)
- The audit's live row (act1_final_inventory.md on claude/hero-integration): **high**, Ch8, `corrow.tscn`: "figure is
  a capsule stand-in". The figure is the cyan silhouette in the storm wall (act1_ch08 W22). It is now
  `corrow_storm_figure` in `game/data/world/npc/zones/ch08_corrow.json`: the Oruvel diver's crowd body
  (`crowd_man_lean_a`) drawn as one `#5fd6e0` silhouette (NpcSilhouette; docs/kb/tech/field_npc.md "Silhouette rows").
  Its capsule is hidden. Tests: test_crowd_villagers (a synthetic silhouette row and the real Corrow zone).
- The first-audited Brine Shoals rows (hound, inquisitor) were already closed (M3-CRE-658 and characters).

## Review log
- 2026-10-29 ~23:50 integration-qa (qa, reviewer): **accepted, done.** The full audit (import + runtime scan) on
  lead/gate-big18 lists nothing for this owner. Act I has 2 items left in all, both env-art-b's (M3-HER-1141).
