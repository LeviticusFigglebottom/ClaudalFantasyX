# Ossa Fen and Reedhollow: Design Notes

Owner: Environment Artist (M3-ENV-718; the sheet first, then the kit). Lighting review: Rendering.
- **Story:** [act_outline Ch10](../../story/beats/act_outline.md); the glossary's Kirru terms (clutch, farewell-tide,
  name-shell).
- **Boss:** the creatures track's [mangrove_drowner.md](../creatures/act2/mangrove_drowner.md) (on `claude/creatures`).
- **Grade target:** [color script](../color_script.md) `ch10`. Colours: [palette.json](../palette.json). Format:
  [haluna.md](haluna.md).
- **Zones:** `ch10/ossa_fen` (the mangrove estuary) and `ch10/reedhollow` (the Kirru roost-village).
- **Kit:** in the Haluna kit as `ossa_fen.py`, with its import kind and materials (as Iskarra, Keth and Lowlight).
- **Arena:** `ossa_fen_roots` (the Mangrove Drowner).

**The feeling in one line:** the answer the game is built around. A grey fen and white egrets; a clutch with their
backs to the water; motes rising straight up into a gap in the cloud. The only warm thing in the frame is release.

**What the place is.** Ossa Fen is the Kirru's mangrove estuary:
- Brown-black tannin channels wind between islands of prop-rooted mangroves. Each tree stands on a cage of arched
  roots, barnacled at the tide line, grey-green crowns above.
- Mudbanks and root-mats show at low water. Reed beds fill the slack water.
- Reedhollow is the Kirru roost-village: woven reed-and-pole roosts raised on the mangroves' own roots, with the
  clutch's name-shells hung on cords at the water's edge. They are the living's own tokens: the Kirru keep nothing
  of their dead (bible §8). A blank one is an exile's.

**The Drowner's tree.** Where the Drowner took root, a great old mangrove has died:
- its crown is bare and bleached (`bone`);
- its roots are black and wet below the water;
- nothing green grows over it.

The creature *is* the root cage. The arena gives it the dead tree's trunk and bare crown above, and room in the
water below.

**Influences** (transformed):
- **Tropical mangrove estuaries** (prop roots, tannin water, egrets, mudskippers) → the trees and water read as they
  are, under our grey dusk. The root arches are exaggerated a step for silhouette.
- **Stilt and raised-platform villages in tidal forests** → Reedhollow's roosts are woven reed shells on poles, sized
  for the Kirru (tall, heron-like). No human doorways, no shrines.
- **Our original:** the **name-shells** on cords at the water's edge. The farewell-tide is sung there.

**IP check (SPEC §2).** No ice or frost (ADR 0015 does not apply here, but the fen is warm anyway). No human ritual
forms are borrowed for the Kirru.

## 0. Layout and lighting

- **Datum:** the channels' water at −0.15. Mudbanks and root-mats stand to y 0.
- **Light** (colour script `ch10`, 18:20 overcast dusk; the cloud breaks for the farewell-tide):
  - sun 2° / 275°, key `#FFFEFA` 0.9;
  - fill `#6F7E8E` 0.5; rim `#FFE9B8` 0.6;
  - sky `#4A5868` / `#9A9488`; fog `#5A6A62`, dense;
  - exposure 0.9, saturation ×0.85, `lut_ch10_fen` (greens to grey-teal; only the lifting motes keep full saturation).
- **Water:** `tannin_fen`: σ 0.6 / 1.4 / 4.0 (red absorbed least), deep `#3A2A18`. Still and mirror-dark in the
  slack, caustics off.

## 1. Kit pieces (proposed; metres; LOD0 / LOD1 triangle budgets)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `fen_bank_ground` | A mudbank and root-mat island, heightfield, flat at y 0 in its middle, shelving into the water | 40 × 30 | 14k / 1k |
| `mangrove_tree` | A living mangrove: a cage of 10–16 arched prop-roots, a leaning trunk, a crown of leaf clusters | 8 × 10 | 10k / 700 |
| `mangrove_dead` | The Drowner's tree: a great dead mangrove, its bare bleached crown and trunk; its roots open on one side, where the creature sits | 12 × 16 | 12k / 800 |
| `reed_bed` | A slack-water reed bed (two-sided blade cards) | 6 × 4 | 3k / 200 |
| `kirru_roost` | A woven reed roost-shell on four poles, Kirru-sized | 3 × 5 | 5k / 400 |
| `name_shell_cord` | A cord between two poles at the water's edge, hung with carved name-shells | 6 m | 2k / 150 |
| `fen_far_mangroves` | The far tree-line round the channels (low-poly silhouette ring) | r 120 | 4k / 600 |

Materials (the kit's own): `kit_fen_mud`, `kit_fen_bark` (timber_weathered grey-brown, black and wet below the tide
line), `kit_fen_bark_dead` (bone), `kit_fen_leaf` (grey-green clusters), `kit_fen_reed`, `kit_fen_reed_weave`,
`kit_fen_shell`.

## 2. The Mangrove Drowner arena (`ossa_fen_roots`)

The battle floor at y 0 is a mudbank's level top, 12 × 9 m, with a mat of small surface roots that stays under the
slots' metre:
- **Behind the enemy line:** the dead mangrove. Its bare crown fills the upper frame. The `BossAnchor` stands in the
  water at its foot, among its roots: (−8.2, −0.15, −3.8), at the water line, so the creature's own roots stand in it.
- **Round it:** living mangroves on their roots, reed beds in the slack, the far tree-line in the fog.
- **Behind the camera:** the channel the party came up.
- **Hints:** `the_dead_crown` (looking up into the bare branches) and `the_channel` (back down the water).

## 3. Composed shots (`ch10`)

| Shot | Lens | Camera | Frame |
|---|---|---|---|
| F01 ◆★ | 28 mm | On the water in a channel, 1 m up | The mangroves closing over the tea-dark water, root cages reflected, an egret on a root. |
| F02 ◆★ | 35 mm | Reedhollow's edge at dusk | The clutch with their backs to the water; the name-shell cords; the motes rising into the cloud gap. |
| F03 ◆ | 24 mm | Under the dead tree | The Drowner's mangrove: bare bleached crown, black roots, nothing green. |
| F04 | 50 mm | Close on a name-shell cord | The clutch's carved shells, one scraped blank (an exile's, not the dead's). |

## 4. Review checklist

- Greens are grey-teal under the grade; nothing in the fen is saturated except the rising motes.
- The water is brown-black tea, never green or blue.
- The dead tree has no green on it.

## 4. The walks (M3-ENV-733, `reedhollow.py`), and the swap for act1-chapters' Ch10 greybox (M4-C10-02)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `root_walk_6m` | A Kirru root-walk: split mangrove poles laid across two bearer roots and lashed; the rails are prop-roots arching up out of the water along both edges, with a lashed pole along their tops | 6 × 3.6, rails 0.5 | 6k / 300 |
| `reed_causeway_6m` | Reedhollow's causeway: bound reed fascines laid across, on pole pilings; paired stakes and a twisted reed rope for rails | 6 × 3.6, rails 0.5 | 6k / 300 |
| `reed_platform_6m` | A 6 × 6 m reed platform on pilings, with a bound edge-roll | 6 × 6 | 8k / 300 |
| `clutch_stone` | The clutch's stone on the shore, worn flat on top by Kirru feet, three scratched lines where they stand to sing | 1.2 × 0.8 | 1.5k / 100 |

All walking tops are level at y 0, matching the greybox (3.6 m strips with 0.5 m rails at z ±2.0).

**Swap** (the greybox's block ids → pieces; each strip is tiled along its length with a 6 m piece, turned to the
block's `yaw`):
- **Ossa Fen:** `Walk*`, `Pocket` and `Exit` → `root_walk_6m`. Their `*Rail*` blocks are in the piece. Their `*Trunk*`
  blocks → `mangrove_tree`, rooted beside the walk (a trunk 2.5 m or more off the walk's centre line).
- **Ossa Fen:** `Bank` → `fen_bank_ground`; `Clearing`, `DrownerRoots` → the `ossa_fen_roots` arena's own pieces
  (`fen_bank_ground`, `mangrove_dead`); `PocketEnd` → `reed_platform_6m`.
- **Reedhollow:** `Causeway` and `Ring*` → `reed_causeway_6m`; their `*Trunk*` blocks → `mangrove_tree`.
- **Reedhollow:** `HousePlatform*` → `reed_platform_6m`, and its `House*` → `kirru_roost` set on it.
- **Reedhollow:** `Shore` → `fen_bank_ground` (or a `reed_platform_6m` pair); `ClutchStone` → `clutch_stone`; the
  name-shell cords (F02, F04) → `name_shell_cord` at the shore's water edge.
- **Both zones:** `reed_bed` in the slack water off the walks, and `fen_far_mangroves` round both.

## Revisions

- 2026-10-27 (env-art, M3-ENV-718): first issue, the sheet before the kit (the Lead's queue item 4: the Ch10 boss).
- 2026-10-27 (env-art, M3-ENV-718): the arena is built.
  - **Pieces.** `ossa_fen.py` makes `fen_bank_ground`, `mangrove_tree`, `mangrove_dead`, `reed_bed` and
    `fen_far_mangroves`, with six `kit_fen_*` materials. The leaves are cards from the coastal leaf atlas, re-tinted.
  - **Grade.** `lut_ch10_fen` comes from `fen_zone_lut.py`.
  - **Arena.** `ossa_fen_roots` (battle_arenas.md). The anchor moved to (−8.2, −0.15, −3.8), so it stands in water,
    and the dead tree leans straight at it. `kirru_roost` and `name_shell_cord` follow with the zone.
- 2026-10-28 (env-art, M3-ENV-733): §4, the walks and the Ch10 greybox swap.
