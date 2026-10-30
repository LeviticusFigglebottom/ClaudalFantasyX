---
draft: pre-gate
zone: ch13/lamp_archive (the Lamp Archive's reading room)
kit: ansedra.py (archive_stacks)
task: M4-A2P-043
author: env-art-b, 2026-10-30
---
# The Lamp Archive: kit spec

**The read:** the Order's library of Lit Age records, kept in plain sight. Black-lacquer ledger cases under a white
vault, and the Cantor roll on its lectern. Three days of reading (C6), and the same few hands across four hundred
years. Nobody says the word (act2_plan §2a).

## The greybox it replaces
The `ReadingRoom` (20 × 32, walls 8 m); `DoorStep`; ten `Stack*` blocks (five rows a side, 5 × 6 × 1); the
`LedgerTable` and the `RollTable`. Spawn `Door`; trigger `to_city`; shot `R01`.

## Pieces
| Piece | Source | Where |
|---|---|---|
| `archive_stacks` | exists (one 7 m bay: two cases across a 2.4 m aisle, ladder, the Cantor roll's lectern) | five bays along the room at a 7 m pitch (the art sheet), the last bay's lectern facing the door. The greybox's stack rows become the cases |
| `lowlight_nave_bay` | exists (reused for the vault) | the reading room's white vault, four bays, in Order marble |
| **`reading_table`** | **new** (`b_ansedra.py`) | the two tables: lacquered, the ledgers open on them, a reading weight, an **unlit** oil lamp (the Order's light is daylight) |
| **`ledger_stack`** | **new**, small | piles of ledgers and rolled lists on the tables and floor (the three days' work, more each day: a per-day variant flag) |
| **`clerestory_window`** | **new** | high windows in the vault: grey daylight is the room's only light |

## Materials
| Slot | Look |
|---|---|
| `kit_lacquer_black` (**flat**) | the cases: `zl.lacquer` black, worn at the shelf lips |
| `kit_lacquer_red` (**flat**) | the shelves: `zl.lacquer` red |
| the ledgers' spines | cream and red (the kit's own) |
| `kit_order_marble` | the vault, cold white |
| `kit_gold_leaf` (**flat**) | the Level lines on the cases, the cold gold look |

## Lighting
- Grey daylight from the clerestories, `#C8C4BA` key at 0.8 falling in long shafts across the aisles; fill
  `#8A96A4` 0.4. No lamp lit. Exposure ~0.85; LUT from `lut_ch13_still`.
- **Day by day (C6):** day 1 morning, day 2 noon, day 3 late afternoon. One `variants` row each, with the sun's
  azimuth through the windows. The light moves; the room doesn't.

## Shot list
| Id | Frame |
|---|---|
| `R01` | the door: the aisle to the lectern |
| `ch13_archive_aisle` | eye height in an aisle: cases both sides, the ladder |
| `ch13_archive_table` | over the reading table: the pages side by side (the document reader's in-world frame) |
| `ch13_archive_roll` | the Cantor roll on its lectern under a shaft of light |
