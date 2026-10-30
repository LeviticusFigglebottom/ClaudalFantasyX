---
id: M3-HER-1141
title: "ADR 0041 (Act I at final quality): env-art-b's items in the placeholder inventory (11: 11 high, 0 medium, 0 low)"
role: environment
status: todo
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC, claude/env-art-b)"
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
ADR 0041: everything a player meets from the title to the end of Ch9 reaches final quality. integration-qa's audit
(`python3 tools/placeholder_audit.py`, docs/kb/qa/act1_final_inventory.md) lists what is still placeholder.
**env-art-b** owns Ch5–Ch9 zones and the arenas used there. This task carries those rows; the inventory's "env-art-b" section is the live list.

## Acceptance criteria
- [ ] Every row of the inventory's "env-art-b" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [ ] The audit lists nothing for env-art-b: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "env-art-b" line.

## The rows as first audited (2026-10-28)
- **high**, Ch5: `assets/environments/arenas/ash_terrace_lanternfall/ash_terrace_lanternfall.tscn`: battle arena greybox: 14 visible primitive/CSG meshes (14 SphereMesh), under Lamps 14
- **high**, Ch5: `game/levels/ch05/ashcrown/ashcrown.tscn`: zone greybox: 40 visible primitive/CSG meshes (40 BoxMesh), under Greybox 40
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: zone greybox: 47 visible primitive/CSG meshes (47 BoxMesh), under Greybox 47
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: zone greybox: 2 visible primitive/CSG meshes (2 BoxMesh), under Greybox 2
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: zone greybox: 24 visible primitive/CSG meshes (24 BoxMesh), under Greybox 24
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: zone greybox: 1 visible primitive/CSG meshes (1 BoxMesh), under Greybox 1
- **high**, Ch8: `game/battle/arenas/wall_head_storm.tscn`: battle arena greybox: 43 visible primitive/CSG meshes (38 BoxMesh, 5 CylinderMesh), under Walk 1, Joint0 1, Joint1 1, Joint2 1, Joint3 1, Joint4 1, Parapet 1, Merlon0 1
- **high**, Ch8: `game/battle/arenas/wall_head_storm.tscn`: arena wall_head_storm is still the greybox scene (encounters ch08_stair_hold_1, ch08_stair_hold_2, ch08_stair_hold_3, undertows_reach)
- **high**, Ch8: `game/levels/ch08/coilspire/coilspire.tscn`: zone greybox: 7 visible primitive/CSG meshes (7 BoxMesh), under Greybox 7
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: zone greybox: 8 visible primitive/CSG meshes (8 BoxMesh), under Greybox 8
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: zone greybox: 58 visible primitive/CSG meshes (58 BoxMesh), under Greybox 58

## Notes (env-art-b, 2026-10-28)
`python3 tools/placeholder_audit.py` (with its runtime scan) on `claude/env-art-b` @ 8ca4c492: **37 items, none for
env-art-b** (audio 12, characters 3, creatures 4, creatures-b 4, env-art 12, integration-qa 2). The rows were fixed by
M3-ENV-1300 to 1322 (the zones' kit dressing with `greybox.hide_all` and no kept blocks, the Ch5–Ch9 arenas on
their kits, the Lanternfall votives, the seawall storm arenas replacing `wall_head_storm`) and M3-RND-26/27 (the Bell's
drop and column, the Coilspire storm wall). The inventory file is integration-qa's to re-write (`--write`).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** The full audit (import + runtime scan of every Act I
  zone, variant and arena) on the merged tree, which was big16 + every track head (17:40) and then also Pell's row
  (18:30), lists **nothing for env-art-b**. Both criteria hold. act1_final_inventory.md on claude/hero-integration shows it.
- 2026-10-29 ~20:00 integration-qa: **reopened.** The Lead re-routed two rows here from env-art (who can't close
  them): `assets/environments/kits/tamsule_bell/reefball_drop_proxy.glb` and `materials/tb_drop_proxy.tres`. Both
  are named as placeholders, and the Bell's held drop is rendering's (M3-RND-26). Rename them, or replace them with
  the final drop, and re-run the audit.
- 2026-10-29 ~23:40 integration-qa: on lead/gate-big18 these two are **the only rows left in all of Act I**
  (`tb_drop_proxy.tres`, `reefball_drop_proxy.glb`, both low: names only).
