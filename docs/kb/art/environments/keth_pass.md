# Keth Pass and the Seeping Terrace: Design Notes

Owner: Environment Artist (M3-ENV-717, sheet first; the kit follows). Lighting review: Rendering. Story:
[act_outline Ch12](../../story/beats/act_outline.md), [ADR 0015](../../decisions/0015-vowbound-element-temple-order.md)
(Cloudloom has nothing frozen; **no ice, frost, glacier or frozen water in any temple or set-piece from Ch12 to Ch15**;
the pass's snow and wind are weather, allowed but not featured). Boss: the creatures track's
[avalanche_ram.md](../creatures/act2/avalanche_ram.md) (on `claude/creatures`). Grade target:
[color script](../color_script.md) `ch12`. Colours: [palette.json](../palette.json). Format: [haluna.md](haluna.md).
Zone: `ch12/keth_pass`, with Quellan (`ch12/quellan`) and Cloudloom (`ch12/cloudloom`) to follow. Kit (to build):
`assets_src/environments/kits/keth/`. Arena: `keth_seep_terrace` (the Avalanche Ram).

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

## Open question (for the creatures track)

`avalanche_ram.md` gives the Ram fleece "matted into plates of ice", an ice beard, and snow shed by its cast. ADR
0015's rule covers set-pieces from Ch12 to Ch15, and the Ch12 boss is one. Proposal: the locks are **matted with
silt and seep-crust** (pale, glassy, the seep's mineral), not ice, and the cast sheds scree. Raised in env-art's
live log for the creatures track.

## Revisions

- 2026-10-27 (env-art, M3-ENV-717): first issue, the sheet before the kit (the Lead's queue item 4).
