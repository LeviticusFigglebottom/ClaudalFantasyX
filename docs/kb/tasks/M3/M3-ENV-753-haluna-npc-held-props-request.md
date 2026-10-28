---
id: M3-ENV-753
title: "Haluna: the NPCs' held props as kit pieces (Reed's broom, Neme's bag, Osu's bowl) (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
The Act I inventory (M3-HER-1140) lists 11 primitives under `game/levels/ch02/haluna/haluna.tscn`'s `NPCs/*`.
Three of them are held props, and env-art has built them as Haluna kit pieces. Each matches its primitive's size and
has its origin where the primitive's centre is, so each swap is a drop-in:

| Node | Primitive | Kit piece |
|---|---|---|
| `NPCs/Chapel/Reed/Broom` | CylinderMesh r 0.02, 1.4 m | `res://assets/environments/kits/haluna/hand_broom.glb` (1.4 m palm-rib broom, origin at its middle, along +Y) |
| `NPCs/Neme/Bag` | BoxMesh 0.45 x 0.40 x 0.28 | `res://assets/environments/kits/haluna/woven_bag.glb` (woven bag, rope handle, origin at its centre) |
| `NPCs/Osu/Osu/Bowl` | CylinderMesh r 0.22/0.15, 0.12 m | `res://assets/environments/kits/haluna/clay_bowl.glb` (earthenware bowl, origin at its centre) |

The rest of the 11 are the NPC stand-in bodies (`StandIn`, `Facing`). Those are the villager/character tracks' work,
not this request.

## Acceptance criteria
- [ ] In `haluna.tscn`, the three nodes instance the kit pieces, keeping their transforms. The `Mesh_broom`,
      `Mesh_bag` and `Mesh_bowl` sub-resources and their materials go.
- [ ] `tools/placeholder_audit.py` no longer counts them.
- [ ] Tell env-art, who views the shots that show them (`npc_haluna_chapel`, `slice_neme_table`).

## Notes
- 2026-10-28 (env-art): pieces built and viewed in a scratch preview (M3-ENV-746): a broom, a bag and a bowl that
  read as themselves; PROVENANCE rows and the kit manifest updated.

## Review log
