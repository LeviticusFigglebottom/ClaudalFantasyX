---
id: M3-ENV-707
title: "Corrow kit: Ch8's story pieces for act1-chapters (M3-ENV-1203): barracks, wall-gate, kites, hoist rig, trader, Marra's step; then the mole and the Bastion"
role: environment
status: doing
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-04]
milestone: M3
request-from: cinematics
reviewer: rendering
---
## Goal
act1-chapters' request M3-ENV-1203: the Corrow blocks that still draw as greybox. Build kit pieces on each block's
footprint (sizes from `game/levels/ch08/corrow/corrow_layout.json` and `corrow_collision.json` on `claude/act1-chapters`).

## Acceptance criteria
- [x] **Batch A** (`assets_src/environments/kits/corrow/cw_story.py`, job `corrow_kit`; every older piece identical):

  | Block | Piece | Size (x, y, z m) | Origin / facing |
  |---|---|---|---|
  | `Barracks` | `stillguard_barracks` | 12.7 x 4.25 (roof) x 6.7 | foot centre; doors on +Z |
  | `WallGate` | `wall_gate` | 1.0 x 4.2 x 6.2 | foot centre; the walk runs along X, the leaves span Z |
  | `Kites` | `kite_line` | 83 x 14 x 1.6 (strings drop 12 m) | the line's centre |
  | `KitesHigh` | `kite_line_high` | 40 x 17 x 0.8 (strings drop 15 m) | the line's centre |
  | `MarraStep` | `marra_step` | 1.5 x 0.75 x 1.0 | foot centre |
  | `HoistPins` / `HoistRope` / `Basket` | `hoist_pins` / `hoist_rope` / `hoist_basket` | 1.9 x 0.3 x 0.2 / 4 m / 0.8 x 0.6 x 0.8 | centred |
  | `Trader` | `trader_boat` | 6.4 (yard) x 9.9 (mast) x 12.1 | keel foot centre; bow -Z |

  Reuse from other kits through ZoneKitDressing's per-piece `kit_dir`: `NetRacks` → Haluna `net_rack`; `Chandler` →
  Haluna `market_stall` + `awning_cloth`; `Chapel` → Haluna `order_chapel` (6 x 9 m: the Order builds one chapel;
  its long side along the platform); `Shrine` → Brine Shoals `level_stone_shrine`.
- [ ] **Batch B:** the harbour mole (`MolePier`, `MoleEnd`, the sea stair `MoleRamp` / `MoleOverParapet` /
      `MoleDown`) and the Bastion (`BastionPlatform` revetment and paving, `BastionRim*`).
- [ ] `Flood`, `Lake`: water surfaces, with Rendering (not kit pieces).
- [ ] act1-chapters places them; PC renders of the Ch8 shots; view and approve.
