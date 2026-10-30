# Lowlight and the Sunken Vey: Design Notes

Owner: Environment Artist (M3-ENV-716, sheet first; the kit follows). Lighting review: Rendering. Story:
[act_outline Ch11](../../story/beats/act_outline.md), [ADR 0015](../../decisions/0015-vowbound-element-temple-order.md)
and [ADR 0016](../../decisions/0016-act-two-restaging.md) (nothing frozen; no founders' records here). Boss: the
creatures track's [lamp_engine.md](../creatures/act2/lamp_engine.md) (on `claude/creatures`). Grade target:
[color script](../color_script.md) `ch11`. Colours: [palette.json](../palette.json). Format: [haluna.md](haluna.md).
Zones: `ch11/sunken_vey` (the drowned galleries) and `ch11/lowlight` (the temple, half underwater). Kit (to build): in the Haluna
kit as `lowlight.py` (its import kind and materials, as Iskarra and Keth). Arena: `lowlight_engine_hall` (the Lamp Engine).

**The feeling in one line:** silent, gorgeous, dead. A turquoise lagoon lies still under a grey sky; Lit Age light
bleeds from every conduit, and in the hall below, a machine is still trimming its lamps for a congregation that
drowned.

**What the place is.** The Sunken Vey is a Lit Age gallery town drowned to its second storeys: arcades and lamp
galleries standing in still turquoise water, strangler-figs splitting the white ceramic. Lowlight is its temple, half
underwater:
- its upper halls are dry, its nave knee-deep;
- below the sanctum, the **engine hall** holds the Lamp Engine, still running;
- the drowned inner sanctum lies at the foot of a Lit Age **well-shaft**, where the deep's cold water wells up and
  drowned glimmer sifts down through it like silt (ADR 0015). **Nothing here is frozen.**

Rhen admits he is Dace's son here, Liss reads a Saltwright housing-mark on a conduit, and Pell kneels before his
sister.

**Influences** (transformed):
- **Flooded colonnaded halls of southern Asia** (stepwells, temple tanks): the still water inside architecture,
  steps going down into it. → Ours: Lit Age white ceramic (the Iskarra palette, `lit_ceramic`) gone green at the
  waterline. The steps lead to a well-shaft, not a tank.
- **Lamp-stands and votive lamp galleries** → the conduits: copper-and-glass Lit Age light lines along every
  cornice, the light bound and still (`glimmer_bound`), never flickering.
- **Our original:** the **lamp galleries**, tiers of empty glass lamp niches up the nave walls, each with its
  bronze trim-arm. They are the Lamp Engine's work: it has kept every lamp trimmed for four hundred years.

**IP check (SPEC §2).** No frozen lake, no ice, no snow imagery (ADR 0015, 0016). No founders' records or truth
reveal in this place (ADR 0016: that is the Ch13 Lamp Archive). The boss is a lamp-stand, not a guardian beast.

## 0. Layout and lighting

- **Frame:** the temple's nave axis runs north–south, the altar end (the sanctum) north (−Z). The lagoon's still
  water is the datum, y 0. The nave floor is 0.45 m under it (knee-deep), the dry upper galleries at +5.6 and
  +11.2. The engine hall is a lower storey whose floor is −0.6 under the lagoon. The well-shaft drops from the
  sanctum's floor to −24.
- **Light** (colour script `ch11`, 12:30 overcast):
  - key `#F3F2FF` 1.4 from 65° / 200°, through the broken vault;
  - fill `#7FA3A8` 0.7; fog `#8A9A98`;
  - exposure 0.75, saturation ×0.85, `lut_ch11_vey`;
  - the conduits `glimmer_bound` 2.0, the only warm-coloured light the copper's.

  Inside the engine hall the daylight is a grey shaft through a collapsed vault bay. The Engine's own lamps are the
  key: twelve bound lights, teal-white, steady. At its release: `glimmer_lift`, a 3 s warm lift, the foreshadowing.
- **Water:** `overcast_lagoon` (absorption ×1.5), perfectly still in the halls (no wind reaches), the conduit light
  reflected long.

## 1. Kit pieces (proposed; metres; LOD0 / LOD1 triangle budgets)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `vey_arcade_bay` | One bay of a two-storey Lit Age arcade, white ceramic over grey stone, drowned to the first storey's springing; a strangler-fig root mat over the upper pier on variant b | 6 × 4 × 12 | 12k / 900 |
| `vey_gallery_bridge` | A lamp-gallery walk (iron and ceramic) spanning between two arcades at +5.6 | 6 × 1.8 | 4k / 300 |
| `lowlight_nave_bay` | One nave bay of the temple: piers, a ribbed vault (broken on variant b), the lamp niche tiers up the walls, the conduit along the cornice | 8 × 18 × 16 | 24k / 1.5k |
| `lowlight_sanctum` | The sanctum: an apsidal chamber, the well-shaft's mouth in its floor with a bronze rim, the steps down | r 7 | 18k / 1.2k |
| `well_shaft` | The Lit Age shaft to −24, ribbed, with a spiral stair and the deep's upwelling at its foot (the drowned sanctum where Nhoa is bound) | r 3.5 × 24 | 14k / 900 |
| `engine_hall` | The engine hall below the sanctum, arena-shaped (see §2): a square hall with a ring of piers, a collapsed vault bay for the light, water at −0.6 over a stepped floor, the Engine's trimming rail round the walls | 20 × 20 × 9 | 26k / 1.6k |
| `conduit_run` | A copper-and-salt-glass light line, 4 m, with brackets (the zone strings them along cornices); `conduit_housing` with a **Saltwright housing-mark** (the mark Liss reads) | 4 m | 1.5k / 120 |
| `lamp_niche_tier` | A tier of six empty glass lamp niches with bronze trim-arms | 4 × 1.2 | 3k / 200 |
| `strangler_fig` | A fig strangling a ceramic pier (vegetation stream's shader, our mesh) | 3 × 9 | 8k / 600 |

Materials (proposed new slots, the kit's own): `ll_ceramic` (lit_ceramic, gone green with algae below +0.6), `ll_stone`
(grey dressed stone), `ll_copper` (env_bronze, verdigris), `ll_salt_glass`, `ll_conduit_bound` (emissive, steady),
`ll_iron`, `ll_root` (fig bark). The water is the shared ocean shader in `overcast_lagoon`.

## 2. The Lamp Engine arena (`lowlight_engine_hall`)

The hall is built to the battle contract (battle_arenas.md):
- **Floor:** the battle floor at y 0 is a dry stone dais in the flooded hall, 10.8 × 8.2 m (off-centre toward the
  party), with the water round it at −0.15 and lapping the dais steps. The Engine stands in the water at its
  knees, so the boss anchor is at (−6.4, −0.6, −2.6) on the flooded floor, off the dais on the enemy side.
- **Behind the enemy line:** the trimming rail and the hall's back wall, lit by the Engine's lamps.
- **Behind the camera:** the stair down from the sanctum.
- **Above:** the collapsed vault bay throws one grey shaft onto the water behind the foes. Six metres clear above
  the slots.
- **Hints:** `under_the_shaft`, `the_lamps`.

## 3. Composed shots (`ch11`)

| Shot | Lens | Camera | Frame |
|---|---|---|---|
| L01 ◆★ | 24 mm | On the water at the Vey's mouth, 1.2 m up | The drowned arcades receding in perspective, conduits lit along the cornices, the temple's broken vault at the end, the grey sky. |
| L02 ◆ | 35 mm | The nave, knee-deep, at the west aisle | The lamp-niche tiers going up both walls, every lamp trimmed and dark, the sanctum's steps at the end. |
| L03 | 50 mm | Close on a conduit housing | The Saltwright housing-mark in the copper (Liss's line). |
| L04 ◆ | 18 mm | The well-shaft's mouth, looking down | The spiral stair going down into teal, silt-light sifting. |
| L05 ◆★ | 28 mm | The engine hall's stair head | The Engine in the water under the grey shaft, its lamps lit. |

## 4. Review checklist

- Nothing frozen anywhere (no ice, frost or snow imagery), and the glimmer sifts **down**, like silt.
- The conduits are steady: no flicker, no pulse (color rule 2).
- No records or text a player could read as the founding truth (that is Ch13's Lamp Archive).

## 5. The walks and the swap for act1-chapters' Ch11 greybox (M4-C11-02; M3-ENV-735)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `vey_gallery_walk_6m` | A gallery walk on the drowned arcades' roofs: ceramic slabs (flat-shaded) on the top course, a cornice, a ceramic balustrade each side (0.5 m at z ±2.0), the arcade's upper arch each side dropping into the lagoon | 6 × 3.6 | 6k / 300 |
| `lowlight_lamp_bench` | The atrium's bench (Rhen and Liss's side scene): a ceramic seat on stone ends, a back with a ledge of three empty glass lamp housings, the conduit's copper under it | 2.4 × 0.9 × 1.3 | 2.5k / 150 |

**Swap** (the greybox's block ids → pieces; strips tiled with 6 m pieces turned to the block's `yaw`):
- **Sunken Vey:**
  - `GalleryIn*`, `GalleryOut*`, `GallerySide` → `vey_gallery_walk_6m`; their `*Rail*` blocks are in the piece.
  - Their `*Pillar*` blocks → `ruin_column_broken`, or `vey_arcade_bay` where a whole bay should show.
  - `Landing`, `Court`, `FigEnd` → `vey_arcade_bay` rows round a paved court. Over 12 m those need the court
    floor; `keth_terrace_ground` is the wrong stone, so use `vey_gallery_walk_6m` side by side.
  - `Conduit` → `conduit_run` + `conduit_housing` (the mark Liss reads); `Fig` → `strangler_fig`.
- **Lowlight:**
  - `Atrium` and `HallWay` → `lowlight_nave_bay` rows (their walls are the bays'); `GateStep` → the bay's floor.
  - `LampBench` → `lowlight_lamp_bench`, with `lamp_niche_tier` on the wall above it.
  - `Hall` and `LampEngine` → the `engine_hall` (the arena's own, at the hall's scale).
  - `ShaftLanding`, `WellShaft` and `Sanctum` → `well_shaft` and `lowlight_sanctum`; `Waterline` → the zone's water.

## Revisions

- 2026-10-27 (env-art, M3-ENV-716): first issue, the sheet before the kit (the Lead's queue item 4).
- 2026-10-27 (env-art, M3-ENV-716): the arena is built. In the Haluna kit's `lowlight.py` (`kit_lowlight_*`
  materials) are `engine_hall`, `conduit_run` and `lamp_niche_tier`, with `lut_ch11_vey` from `lowlight_zone_lut.py`.
  The arena is `lowlight_engine_hall` (battle_arenas.md). The dais moved off-centre and the boss anchor to
  (−6.4, −0.6, −2.6), so the Engine stands in the water past the steps, as §2 meant. The Vey's and the temple's zone
  pieces follow.
- 2026-10-27 (env-art, M3-ENV-716): `conduit_housing`, with **the Saltwright housing-mark** (L03). It is stamped
  3 mm proud: a circle (15 cm on the housing) crossed by three fine parallel lines slanted 30°, which is the
  Saltwrights' camp-sign as on Ch6's chalk marks, over two small round seats side by side ("pair-built", Liss's word
  in Ch6). Rhen's lantern takes the same mark (M3-ENV-719, Character).
- 2026-10-27 (env-art, M3-ENV-716): the zone's architecture:
  - `lowlight_nave_bay`, and `lowlight_nave_bay_broken` with its vault open and the rubble fallen;
  - `well_shaft`, the ribbed drum with its spiral stair 24 m down and the bronze rim;
  - `vey_arcade_bay`, two storeys of pointed arches with the lamp gallery's corbels;
  - `vey_gallery_bridge`.

  Then `lowlight_sanctum` (the apse round the well's mouth) and `strangler_fig` (root strands fused round a 1.2 m
  pier; the banyan's bark and leaf). The zone kit is complete.
- 2026-10-28 (env-art, M3-ENV-735): §5, the gallery walk, the lamp bench and the Ch11 greybox swap.
- 2026-10-30 (env-art, M4-A2P-041): the two Ch11 zones dressed (`tools/act2/ch11_lowlight_dressing.py`).
  - **Built from the greybox.** §5's 6 m `vey_gallery_walk_6m` runs its balustrade the walk's whole length, but the
    greybox's rails stop 3.6 m short of every junction. The nave bay and the engine hall stand piers in the walked
    floor and close every wall, where the greybox has open floors and doorways. So both zones' walks and rooms are
    built from the greybox in the kit's language:
    - `vey_zones.py`: `sunken_vey_walks_w/_court/_walks_e`, the walks at their own lengths with the balustrade on the
      rail blocks; the paved landing, court and fig end; the court's parapets; the conduit stand; Lowlight's gate
      facade. Also `sunken_vey_ground`, the bed with the drowned street conduits still lit, in `kit_vey_silt`.
    - `lowlight_zones.py`: `lowlight_atrium/_hall/_well`, the rooms on the greybox's walls, with a pointed arch over
      every doorway, engaged piers, three niche tiers, the cornice conduit and pointed vaults. The atrium and the hall
      each have a broken bay. The hall has the trimming rail and the twelve trimmed lamps. The well has its flights
      under a sloped vault, and the drowned sanctum under a dome on pendentives with the shaft's oculus.
  - **Kit pieces placed round them:**
    - `vey_arcade_bay` rows round the court and receding from the landing;
    - `ruin_column_broken` on the pillars;
    - `strangler_fig` on piers and columns, and a hollow one at the fig end;
    - `conduit_housing` on the stand, the mark facing `conduit_mark`;
    - `lowlight_lamp_bench`, and `well_shaft` (scaled to the mouth);
    - `lowlight_nave_bay(_broken)` over the gate.
  - **The grade.** The arena's sky with its deck turned to the overcast's greys, because its warm cloud deck read as a
    sunset over open water. The water is still: no crest foam, the detail ripple damped. In Lowlight the foam is off,
    and the hall's flooded floor is a 3 cm film.
  - **The mount and the open questions** (the well's mouth, wading, underwater) are chapters' (M4-A2P-0411).

