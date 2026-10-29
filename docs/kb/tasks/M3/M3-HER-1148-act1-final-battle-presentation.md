---
id: M3-HER-1148
title: "ADR 0041 (Act I at final quality): battle-presentation's items in the placeholder inventory (5: Act I bosses with no set-piece VFX)"
role: rendering
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
**battle-presentation** owns battle VFX. Only the Drownbell has a boss set piece (boss_vfx.json, BattleBossVfx). The
other Act I bosses fight with the generic element hit effects only.

## Acceptance criteria
- [ ] Each boss below has its set piece (a boss_vfx.json row: telegraphs, phase changes, the KO). Or the task records
      why the generic effects are final for that boss (then the audit learns to skip it).
- [ ] The audit lists nothing for battle-presentation.

## The rows as first audited (2026-10-28)
- **medium**, Ch1: `game/data/vfx/battle/boss_vfx.json#hullgnaw`: boss hullgnaw has no set-piece VFX (generic hit effects only)
- **medium**, Ch4: `game/data/vfx/battle/boss_vfx.json#spar_wraith`: boss spar_wraith has no set-piece VFX (generic hit effects only)
- **medium**, Ch5: `game/data/vfx/battle/boss_vfx.json#cinder_matron`: boss cinder_matron has no set-piece VFX (generic hit effects only)
- **medium**, Ch6: `game/data/vfx/battle/boss_vfx.json#stillguard_inquisitor`: boss stillguard_inquisitor has no set-piece VFX (generic hit effects only)
- **medium**, Ch8: `game/data/vfx/battle/boss_vfx.json#undertows_reach`: boss undertows_reach has no set-piece VFX (generic hit effects only)

## Review log
