---
id: M3-HER-1140
title: "ADR 0041 (Act I at final quality): env-art's items in the placeholder inventory (15: 9 high, 2 medium, 4 low)"
role: environment
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
**env-art** owns Prologue–Ch4 zones, the shared kits, and the arenas used there. This task carries those rows; the inventory's "env-art" section is the live list.

## Acceptance criteria
- [ ] Every row of the inventory's "env-art" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [ ] The audit lists nothing for env-art: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "env-art" line.

## The rows as first audited (2026-10-28)
- **high**, Prologue: `game/levels/prologue/prologue.tscn`: zone greybox: 37 visible primitive/CSG meshes (22 CylinderMesh, 8 BoxMesh, 4 SphereMesh, 3 CapsuleMesh), under City 37
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: zone greybox: 26 visible primitive/CSG meshes (26 BoxMesh), under Greybox 26
- **high**, Ch1: `game/levels/ch01/oruvel_underway/oruvel_underway.tscn`: zone greybox: 36 visible primitive/CSG meshes (36 BoxMesh), under Greybox 36
- **high**, Ch2: `game/levels/ch02/haluna/haluna.tscn`: zone greybox: 11 visible primitive/CSG meshes (6 CylinderMesh, 3 BoxMesh, 1 SphereMesh, 1 TorusMesh), under HalunaMood 10, NPCs 1
- **high**, Ch3: `game/levels/ch03/first_verse/first_verse.tscn`: zone greybox: 15 visible primitive/CSG meshes (6 CSGCylinder3D, 4 CSGBox3D, 3 CSGSphere3D, 1 CSGCombiner3D, 1 CylinderMesh), under Shrine 12, Island 1, PoolWater 1, Bell 1
- **high**, Ch3: `game/levels/ch03/shell_shrine/shell_shrine.tscn`: zone greybox: 1 visible primitive/CSG meshes (1 BoxMesh), under Dressing 1
- **high**, Ch4: `assets/environments/arenas/derelict_deck_night/derelict_deck_night.tscn`: battle arena greybox: 7 visible primitive/CSG meshes (7 SphereMesh), under Lamps 7
- **high**, Ch4: `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: zone greybox: 4 visible primitive/CSG meshes (4 BoxMesh), under Greybox 4
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: zone greybox: 41 visible primitive/CSG meshes (41 BoxMesh), under Greybox 41
- **medium**, Ch2: `game/levels/ch02/haluna/haluna.tscn`: visible mesh named as a placeholder: banyan_placeholder (2 node(s))
- **medium**, Ch2: `game/levels/ch02/haluna/haluna.tscn`: visible mesh named as a placeholder: windbreak_placeholder (98 node(s))
- **low**, all: `assets/environments/kits/haluna/banyan_placeholder.glb`: asset file named as a placeholder
- **low**, all: `assets/environments/kits/haluna/windbreak_placeholder.glb`: asset file named as a placeholder
- **low**, all: `assets/environments/kits/tamsule_bell/materials/tb_drop_proxy.tres`: asset file named as a placeholder
- **low**, all: `assets/environments/kits/tamsule_bell/reefball_drop_proxy.glb`: asset file named as a placeholder

## Notes (integration-qa)
- 2026-10-29 ~23:40 integration-qa: **the audit lists nothing for this owner on lead/gate-big18** (full scan; 2 items
  in all, both env-art-b's). The owner can tick the boxes and send this to review (reviewer: qa).

## Review log
