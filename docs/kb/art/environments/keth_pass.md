# Keth Pass and the Seeping Terrace: Design Notes

Owner: Environment Artist (M3-ENV-717, sheet first; the kit follows). Lighting review: Rendering. Story:
[act_outline Ch12](../../story/beats/act_outline.md), [ADR 0015](../../decisions/0015-vowbound-element-temple-order.md)
(Cloudloom has nothing frozen; **no ice, frost, glacier or frozen water in any temple or set-piece from Ch12 to Ch15**;
the pass's snow and wind are weather, allowed but not featured). Boss: the creatures track's
[avalanche_ram.md](../creatures/act2/avalanche_ram.md) (on `claude/creatures`). Grade target:
[color script](../color_script.md) `ch12`. Colours: [palette.json](../palette.json). Format: [haluna.md](haluna.md).
Zone: `ch12/keth_pass`, with Quellan (`ch12/quellan`) and Cloudloom (`ch12/cloudloom`) to follow. Kit: `assets_src/environments/kits/haluna/keth.py`
(in the Haluna kit, its import kind and materials, as Iskarra). Arena: `keth_seep_terrace` (the Avalanche Ram).

**The feeling in one line:** an enormous sky, thin cold light, and the few motes up here rising fast. The
breath that doesn't fog (Kerrid) needs a clean dark background, so compose for it.

**What the place is.** The Cold Road over the Keth Pass:
- **Route:** a highland mule-road of laid stone switchbacks, cut into scree under grey crags.
- **Pass-cords:** strung across the road at every saddle, hung with thousands of knotted **keth**. Each knot is a
  name; the Ullari tie them for their dead and walk on.
- **Below the summit:** a **Lit Age terrace wall**, the retaining wall of a drowned-age road far older than the
  pass. Drowned glimmer seeps out of its joints and runs down its face in thin sheets of cold light.
- **The Ram:** a woolback herd drank where the seep runs. One of them grew into the Avalanche Ram.

**Influences** (transformed):
- **High mountain trade passes** (prayer-flag strings across saddles, cairns, stone switchbacks) → the
  **pass-cords**: our own keth, knotted cords in undyed wool and red, with **no flags, no script, no religious
  figures**. A knot is a name.
- **Ancient retaining walls in mountain valleys** (cyclopean terraces) → the **Lit Age terrace wall**: huge fitted
  white-grey ceramic blocks with conduit channels, broken, older than anything around it, weeping light.
- **Our original:** the **seep**. Glimmer that drowned with the old world comes out of the mountain as cold light,
  running like water over the wall (not frozen: ADR 0015), and the grass under it grows pale and too long.

## 0. Layout and lighting

- **Frame:** the road climbs north (−Z) to the saddle. The battle terrace is the old road's level top, 14 m above
  the switchback below, at y 0. The seeping wall rises behind it on the north side, 9 m.
- **Light** (colour script `ch12`, 09:00):
  - key `#FAF6FF` 2.8 from 30° / 140°, hard sun between cloud banks;
  - fill `#7FA6DC` 0.8; fog `#D0DCE8`, thin;
  - exposure 0.65, saturation ×0.9, `lut_ch12_heights`;
  - the seep `glimmer_held` cyan (its rising motes `glimmer_lift`).

  The only warm notes are the red keth.
- **Weather:** wind, and snow in the air on the road (weather, ADR 0015). **None on the battle terrace or the wall:**
  the seep's ground is wet scree and pale grass. **No ice, frost or icicles anywhere** in the arena or on the wall.

## 1. Kit pieces (proposed; metres; LOD0 / LOD1 triangle budgets)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `keth_road_switchback` | A laid-stone switchback module with a dry-stone parapet on the drop side | 10 m run, 3 m wide | 8k / 500 |
| `keth_scree_slope` | A scree-and-crag slope panel, graded to the road (heightfield) | 40 × 40 | 12k / 1k |
| `pass_cord` | A cord across a saddle from cairn to cairn, sagging, hung with 60–120 keth (knotted cords, undyed and red) | 18 m | 6k / 400 |
| `cairn` | A road cairn with knotted cords tied round it | 1.2 × 1.6 | 2k / 150 |
| `lit_terrace_wall` | A 12 m module of the Lit Age retaining wall: cyclopean ceramic blocks, broken coping, conduit channels; the seep sheets down its face (emissive cold light, two-sided strips) | 12 × 9 | 18k / 1.2k |
| `seep_pool` | The pale pool at the wall's foot where the herd drank, with the too-long pale grass round it | r 3 | 4k / 300 |
| `woolback_trough` | A herders' stone trough and a broken herd-gate | 3 × 1 | 2k / 150 |

Materials (proposed, the kit's own): `kp_road_stone`, `kp_scree`, `kp_crag`, `kp_lit_ceramic` (weathered grey-white),
`kp_seep` (emissive, steady cyan, a slow downward flow), `kp_keth_wool`, `kp_keth_red` (the red at full saturation, the
LUT keeps it), `kp_pale_grass`.

## 2. The Avalanche Ram arena (`keth_seep_terrace`)

The terrace top is the battle floor at y 0, 16 × 10 m of old road paving with the scree's edge beyond:
- **Behind the enemy line:** the seeping wall, with the Ram's `BossAnchor` at its foot by the seep pool, where it
  drank.
- **Behind the camera:** the drop to the switchback. Its parapet runs below the camera line.
- **Cast field hazard** (the creatures sheet): stone and scree shed off the wall's broken coping, not snow (ADR
  0015).
- **Hints:** `under_the_wall`, `the_pass_below` (Kerrid's breath frame: the dark crag behind him).

## 3. Composed shots (`ch12`)

| Shot | Lens | Camera | Frame |
|---|---|---|---|
| K01 ◆★ | 24 mm | On a switchback, looking up the pass | The road's zigzag, a pass-cord across the saddle against the enormous sky. |
| K02 ◆ | 50 mm | Close on a cord | Keth knots in wool and red, wind-moved, a hand-tied one at the front. |
| K03 ◆★ | 35 mm | Below the terrace | The Lit Age wall, its seep running down in cold light, the pale grass. |
| K04 | 85 mm | The road in shade | Kerrid's breath frame: a figure against the dark crag, the others' breath fogging. |

## 4. Review checklist

- No ice, frost, glacier, icicle or frozen water in the arena, on the wall or in Cloudloom (ADR 0015). Snow only as
  weather on the road.
- The keth have no script and no flags; the knots carry the names.
- The seep's light is steady and runs down; motes near it rise fast (`glimmer_lift`, the heights).

## 5. Quellan and Cloudloom (`ch12/quellan`, `ch12/cloudloom`)

**Quellan** (bible §5): the Ullari highland town below the summit.
- **Fabric:** dry-laid grey stone houses, one and two storeys, built into the slope with flat turf-edged roofs.
- **Awnings:** every doorway and yard is shaded by a **woven awning** on poles, in undyed wool with the red
  weft-bands that the keth also use.
- **Town:** narrow stepped lanes; the pass-cords run across the lanes too.

**Cloudloom** (bible §5; ADR 0015, N-15: Holy, Hesk; **stone, cord and sky, not ice**): a weaving-hall cut into the
summit rock.
- **Shell:** the walls are the rock itself, dressed smooth and white inside; the floor is white stone.
- **Roof:** there is none. A lattice of timber beams spans the hall, and from every beam hang thousands of keth.
- **Noon:** the sun comes straight down through the open roof, and the cords' shadows fall on the white floor like
  writing. Ysolde reads them, and lies about what they say.
- **Centre:** the old loom-frame where Hesk is bound.

**Light at noon** (`ch12` key, high): sun 75° / 180°, key `#FAF6FF` 3.0, fill `#7FA6DC` 0.6, the floor's bounce white.
The shadow-writing needs hard shadows (the shadow blur low). No snow or ice inside; the thin wind stirs the cords.

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `cloudloom_hall` | The rock-cut hall: white dressed walls 9 m, the white stone floor, the beam lattice over the open roof, the loom-frame on its dais at the centre, the entrance cut on +Z | 24 × 16 | 16k / 1.2k |
| `keth_curtain` | One beam's hang of keth: 240 cords, 1.2–4 m, undyed and red, knotted (two-sided strips, so they cast the writing) | 6 m | 4k / 300 |
| `quellan_house` | A dry-stone highland house, two storeys into the slope, flat turf-edged roof, a door with a woven awning | 6 × 5 × 6 | 7k / 500 |
| `woven_awning` | A freestanding awning: four poles, undyed wool with red weft-bands, sagging | 3 × 2.5 | 1.5k / 120 |

| Shot | Lens | Camera | Frame |
|---|---|---|---|
| K05 ◆★ | 24 mm | Cloudloom's floor, looking up | The beam lattice and the keth against the open sky. |
| K06 ◆★ | 35 mm | The floor at noon | The cords' shadows written across the white stone, a figure reading them. |
| K07 ◆ | 28 mm | A Quellan lane | Stepped stone, the awnings, a pass-cord across the lane. |

## 6. Quellan's inn and well, Hesk's dais, and the swap for act1-chapters' Ch12 greybox (M4-C12-02; M3-ENV-734)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `quellan_inn` | The inn (Ysolde's confession to Asha that night): the houses' dry stone, two rows of shuttered windows in the front, a timber gallery along it, the turf roof, the red banner over the door | 10 × 8 × 5 | 12k / 700 |
| `quellan_well` | The square's well: a dry-laid ring 0.9 m high, posts and a windlass, the rope to a bucket on the rim, a stone trough beside it | 1.6 (+ trough) | 2.5k / 200 |
| `hesk_dais` | Hesk's place at the north end of Cloudloom's hall: the hall's white stone in two steps (0.4 m), a woven mat with red weft-bands, a low stone seat | 6 × 3 | 3k / 200 |

**Swap** (the greybox's block ids → pieces):
- **Keth Pass:**
  - `Flight*Cliff` → `keth_scree_slope`; the flights themselves → `keth_road_switchback`; `Flight*Parapet` and
    `Flight*Cord*` → `pass_cord`.
  - `KnotPost` and `Knots` → `pass_cord`'s end post; `RamArena` and `TerraceWall` → the `keth_seep_terrace` arena's
    `keth_terrace_ground` and `lit_terrace_wall`.
  - `Saddle` and `Snowfield` → `keth_terrace_ground` (no ice; ADR 0015); a `cairn` at the saddle.
- **Quellan:**
  - `House*` and `Roof*` → `quellan_house`, its awning toward the street; `Inn`, `InnRoof`, `InnBanner` →
    `quellan_inn`; `Well` → `quellan_well`.
  - `Terrace` → `keth_terrace_ground`; the `woolback_trough` and `woven_awning` along the street.
- **Cloudloom:**
  - `Hall`, `HallWall*` and `Beam*` → `cloudloom_hall`; the `Keth*_*` hangings → `keth_curtain`.
  - `HeskDais` → `hesk_dais`; `StairCliff` and `StairParapet` → `keth_road_switchback` and `pass_cord`.

## Open question (for the creatures track)

`avalanche_ram.md` gives the Ram fleece "matted into plates of ice", an ice beard, and snow shed by its cast. ADR
0015's rule covers set-pieces from Ch12 to Ch15, and the Ch12 boss is one. Proposal: the locks are **matted with
silt and seep-crust** (pale, glassy, the seep's mineral), not ice, and the cast sheds scree. Raised in env-art's
live log for the creatures track.

## Revisions

- 2026-10-27 (env-art, M3-ENV-717): first issue, the sheet before the kit (the Lead's queue item 4).
- 2026-10-27 (env-art, M3-ENV-717): the arena pieces are built in the Haluna kit (`keth.py`, `kit_keth_*` materials,
  other kits' crag, shingle and paving textures read as they are). `keth_terrace_ground`, `lit_terrace_wall`,
  `seep_pool`, `pass_cord`, `cairn`, `keth_far_ridges`; `lut_ch12_heights` from `keth_zone_lut.py`. The arena
  `keth_seep_terrace` puts the pool at (−9, −4.2), clear of the slots' floor, the Ram's `BossAnchor` beside it, and
  a pass-cord across the terrace behind the enemy line. The switchback, scree-slope module and the Quellan and
  Cloudloom pieces follow with the zone.
- 2026-10-27 (env-art, M3-ENV-717): the Cold Road's zone pieces. `keth_road_switchback` is a 10 m module climbing
  1 m, with a laid-stone bed, a dry-stone parapet on the drop side and the cut bank's scree; modules chain end to
  end. `keth_scree_slope` is a 40 × 40 m panel. `woolback_trough` is the trough with its broken herd-gate. Quellan's
  and Cloudloom's pieces follow with those zones.
- 2026-10-27 (env-art, M3-ENV-717): §5 Quellan and Cloudloom, and their pieces: `cloudloom_hall` (the rock-cut
  hall, the beam lattice over the open roof, the loom-frame), `keth_curtain` (one beam's 240 keth, two-sided so they
  cast the floor's writing), `quellan_house` and `woven_awning`. Nothing frozen.
- 2026-10-28 (env-art, M3-ENV-734): §6, the inn, the well, the dais and the Ch12 greybox swap.
- 2026-10-30 (env-art, M4-A2P-042): the three Ch12 zones dressed (`tools/act2/ch12_keth_dressing.py`).
  - **Built from the greybox.** §6's modules don't fit it. The flights climb 6 m in 28, against the switchback's 1 in
    10. The cliffs run up beside a rising road. The cords run post to post up the slope. The houses are 8 m and the
    hall 28 × 40. So `keth_zones.py` builds each zone's ground (walks level under their stones, scree falling from
    the drop sides, crag behind every cliff block, turf on the flats) and its stone:
    - `keth_pass_road` and `keth_pass_arena`: road stones on every flight and landing; dry-stone parapets following the
      slope; the low walls; the cord posts with knotted cords between them; the knot post; the saddle's road band.
    - `quellan_town` and `quellan_houses_n/_s`: the street and square paved, the houses on the greybox's footprints,
      the terrace's walls, the road up.
    - `cloudloom_temple`: the approach and stair, the hall's white floor, its walls in dressed courses to 9 m, and the
      beam lattice with a beam over every row of keth.
  - **Kit pieces placed round them:**
    - `lit_terrace_wall` ×2 and `seep_pool` behind the Ram's terrace;
    - `pass_cord` and cairns at the saddle;
    - `quellan_inn` on its block, and `quellan_well`;
    - twelve `keth_curtain` (2,880 cords) over the hall's rows, clear of the aisle;
    - `hesk_dais`, and `keth_far_ridges`.
  - **Kit change.** The house, inn and the built walls take the road's granite (`M_DRYSTONE`); the volcanic crag read
    black. Their roof turf is the new `kit_keth_turf`, because `kit_keth_grass` (the cards' flat colour) read as snow
    on roofs and flats, which ADR 0015 forbids.
  - **The mount** is chapters' (M4-A2P-0421). The slate's deep shade at a walker's eye goes to a real-GPU check
    (env-art's PC-QUEUE).

