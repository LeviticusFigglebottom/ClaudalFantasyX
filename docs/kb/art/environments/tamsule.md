# Tamsule Port: Design Notes

Owner: Environment Artist (M3-C07-04, the port half). Lighting review: Rendering. Story:
[act1_ch07.md](../../story/beats/act1_ch07.md) B01–B03, B08, B10 and §10 item 4, [bible §5.3](../../story/bible.md).
Grade target: [color script](../color_script.md) `ch07` (noon). Colours: [palette.json](../palette.json). Companion
sheet: [tamsule_bell.md](tamsule_bell.md) (the Bell, its galleries and Oruvel's moorings). Format: [haluna.md](haluna.md).
Zone: `game/levels/ch07/tamsule/` (act1-chapters places the kit, M3-C07-02's greybox ids kept). Kit: the Tamsule Bell kit
(`assets_src/environments/kits/tamsule_bell/`), its `port.py` (shophouses, boardwalk, gilded boards, from M3-ENV-01)
and `market.py` (this sheet's pieces). Preview: `game/levels/_tests/tamsule_port_kit/`.

**The feeling in one line:** the most crowded, gilded noon in the game, a town of boards and boats packed so tight you
cross the river on other people's hulls, and above it all the Bell, holding its breath.

**What the place is.** Tamsule is a stilt city on a river mouth. The Tidecup fills it: floating markets jammed hull
to hull, banners in every side's colours, gilded lacquer signboards on every house-front, and the Bell on its
gantry over the Bell Reach to the north. The party comes in by barge at the river-mouth quay (B01). They walk the
port's loop (B02): the floating market, the stilt lane, the gantry foot. Tavi finds Rhen among the market boats by
the gantry (B03). The afternoon goes on as if nothing happened (B08), and they leave from the harbour on a coastal
trader (B10).

**Influences** (references.md §2, transformed):
- **Southern river-market towns** → decks of planks on piles, joined by plank bridges and by the boats themselves.
  Every market boat is a shop: the goods are the colour.
- **Burmese and Thai gilded lacquer boards** (bible §5.3) → the kit's `tb_signboard`: black lacquer, gilded border,
  **original glyph strokes from a seeded grammar** (tb_common.signboard). No real script is copied. No religious
  figure appears, and the Order's Level is never shown.
- **Our original:** the **side colours**. Each Reefball side's colours (cloth dyes) are strung across the lanes as
  bunting. Oruvel's sea-blue and bone runs along the gantry foot only, and nobody has taken it down.

## 0. Layout and frame

The greybox's frame is kept (`tamsule_layout.json`, M3-C07-02):
- x is east and −Z is north; the decks' tops are at y 0;
- the river surface is at **y −1.6**, 1.6 m under the decks, the Bell kit's `DECK_Y`, so the shophouses and
  boardwalks share one waterline;
- the riverbed is at −5.1.

| Greybox block | Kit pieces | Notes |
|---|---|---|
| `Quay` (0, 20), 14 × 8 | `port_deck_8m` × 2, `mooring_post`, the barge alongside (Brine Shoals `vendor_boat` as the hired barge) | B01's landing; the river mouth opens south. |
| `Market` (0, 4), 24 × 16 | `port_deck_8m` × 6, `market_stall` × 4, `market_boat_a/b` moored round it, `bunting_12m` across | The floating market: the decks are islands, and the boats between them are the shops. |
| `StiltLane` (−20, 4), 12 × 6 | `boardwalk_8m`, `shophouse_a/b` along its back (north) with their boards out | The `Signboard` block becomes the shophouses' own vertical boards. |
| `GantryFoot` (0, −14), 16 × 12 | `port_deck_8m` × 4, `signboard_gilded` × 2 (the lane boards), `bunting_12m` in Oruvel's colours | The Bell rises beyond: its axis at **(0, −75)** in this frame (the kit's real Bell has galleries out to r 41, so the greybox's stand-in at z −40 moves north; nothing in the port reaches it). |
| `MarketBoats` (14, −12), 10 × 8 | `market_boat_a/b` × 4, packed, with a plank walk over them | Tavi's run (TP06). |
| `Harbour` (24, 10), 10 × 12 | `port_deck_8m` × 3 with a rail on the water side, `mooring_post` × 3, the Corrow kit's `trader_boat` | B10's casting off. |
| `*Bridge` | `plank_bridge_4m` (scaled along its length to fit the gap) | Rope rails on both sides. |

## 1. Kit pieces (dimensions in metres; origins on the deck top, y 0)

| Piece | What it is | Key dimensions |
|---|---|---|
| `port_deck_8m` | A market deck on 3 × 3 piles to the riverbed: bearers, a plank deck (planks along X), the pile heads proud with rope collars. `port_deck_8m_rail` adds a rail on the +Z side. | 8 × 6, deck y 0, piles to −5.1 |
| `plank_bridge_4m` | A plank bridge along X, arched 0.15 m, on two pile bents, with rope hand-lines on posts both sides | 4 long × 2.4 wide |
| `market_stall` | A deck stall: four posts, a woven awning dyed in a side colour, a lacquered counter (black plinth and posts, the red front in three gold-edged sunk panels, a black top on a gilt edge, a cloth runner hanging over it), baskets and wrapped bundles of goods bound both ways with cord, a small gilded board hung from the awning's front | 3 × 1.6 × 2.6 high |
| `market_boat_a` | The watch-boat's crescent hull (8 m), loaded: baskets, wrapped bundles in the cloth dyes, jars, a sun umbrella on a pole, a gilded bow eye | 8.0 × 1.9 |
| `market_boat_b` | A shorter (6 m) boat with an awning frame over stacked trays and hanging bunches | 6.0 × 1.7 |
| `bunting_12m` | A rope across a lane from post to post, sagging 0.8 m, 20 two-sided pennants in one side's colours (the slot is the dye: place with a material override for another side) | 12 long |

Existing pieces reused: `shophouse_a/b`, `boardwalk_8m`, `signboard_gilded` (port.py); `mooring_post`, `watch_boat`
(waterline.py); the Bell's own pieces on its axis.

**Budgets** (LOD0 / LOD1): deck 3,000 / 200; bridge 2,000 / 120; stall 4,000 / 300; boat 9,000 / 600; bunting
1,200 / 150. The market packs about 40 boats and stalls in one frame; at noon the shadows carry it, so LOD1 starts
at 60 m.

## 2. Materials

Every slot is the Bell kit's own (`tb_*`, `materials.py`):
- timber, piles, lacquers, gold, woven, rope, the cloth dyes;
- the signboard's gilded glyph material.

No new material. The goods' colour is the cloth dyes (sand, red, indigo, sea-blue, faded teal) and the lacquers: the
noon grade's saturation (×1.18) does the rest.

## 3. Composed camera shots (`ch07`, 12:15)

| Shot | Lens | Camera | Frame | Story beat |
|---|---|---|---|---|
| TP01 ◆★ | 24 mm | 2.8 m above the water, 60 m out at the river mouth (0, 1.2, 80), looking north | The quay and the market decks across the lower third, boards and bunting, the Bell filling the top half beyond: held 3 s. | B01: a festival around a held breath. |
| TP02 | 35 mm | On the quay (3, 1.6, 22), looking north-west | The barge tying up, the market's awnings behind. | B01's line. |
| TP03 ◆ | 35 mm | Market deck (6, 1.6, 10), looking north-west across two boats | Boats hull to hull between the decks, goods, umbrellas, boards. | The floating market. |
| TP04 | 28 mm | Stilt lane (−14, 1.6, 6), looking west | The lane's shophouses on the right with their vertical boards out, bunting overhead. | B02 rail. |
| TP05 ◆ | 24 mm | Gantry foot (0, 1.4, −10), tilted up 25°, looking north | The lane boards and Oruvel's bunting, the Bell's skirt and the drop high above. | B02: the gantry foot. |
| TP06 | 35 mm | (4, 1.7, −8) looking east across the market boats | A wide across moored boats for Tavi's run. | B03. |
| TP07 ◆ | 50 mm | Two-shot on the boats' plank walk (12, 1.6, −10), looking east | Rhen frame-left in three-quarter back, Tavi frame-right facing camera. | B03: the line. |
| TP08 | 35 mm | The trader's stern at the harbour (31, 2.2, 14), looking west | Tamsule and the Bell behind as they pull away. | B10. |
| TP09 | 65 mm | The trader's stern, looking north-west to the moorings under the Bell | Oruvel's moorings in the Bell's shade; Pio's band on the last ring. | B10's look back (a proposal). |

## 4. Review checklist

- No real-world script on any board, and no religious figure or Order mark anywhere in the port.
- The Bell is visible from every exterior shot in the port, and dominant in TP01.
- The market reads as packed: no TP03 frame with more than a third of empty deck.
- Oruvel's colours appear only at the gantry foot, and nobody comments on them.

## Revisions

- 2026-10-27 (env-art, M3-C07-04): first issue. The port's kit extends the Tamsule Bell kit (`market.py`); the
  greybox's frame is kept, with the Bell's axis moved north to (0, −75) so its real galleries clear the port.
