# Pemakar Town and the Terraces of Ash: Mood Brief

Owner and build: Environment Artist (M3-ENV-03). Lighting review: Rendering. Gameplay placement: m2-slice (swap-in notes in `docs/kb/handoffs/live/env-art.md`).
Story: [act outline Ch5](../../story/beats/act_outline.md), [bible §4 Rites (leaf-boats) and §5.2](../../story/bible.md), [ADR 0020](../../decisions/0020-kerrid-restaging.md) (Kerrid at the festival's edge), [kerrid.md](../../story/characters/kerrid.md), [decisions_log](../../story/decisions_log.md) (Ashcrown, Lightning). Grade: [color script](../color_script.md) `ch05`. Colours: [palette.json](../palette.json). References in words only: [references.md](../references.md) §2 (Balinese and Javanese stepped terraces, volcanic stone and water channels; Thai and Burmese lacquer and gold leaf).
Zone: `ch05/pemakar` (`game/levels/ch05/pemakar/`, not built yet). Ashcrown (`ch05/ashcrown`) is a later task; here it is only a silhouette on the crown.
Kit: `assets_src/environments/kits/pemakar/` → `assets/environments/kits/pemakar/`. Preview: `game/levels/_tests/pemakar_kit/`.

**The feeling in one line:** a festival among graves. A dark mountain under a breathing plume turns, for one night, into a waterfall of small fires, and every light is somebody's dead going down to the sea.

**Influences** (references.md §2): stepped hillside terraces with water channels running down every slope and dark volcanic stone (Balinese and Javanese) **+** black-and-red lacquer with small gold-leaf figures (Thai and Burmese) **+** our own originals: open-hand gates, ash-stone graves with lamp niches, Lit Age copper veins running down the tiers, and the leaf-boat channels that are built to carry offerings, not only water.

**Checked against the story (before any geometry):**
- Act outline Ch5: Lanternfall "a thousand leaf-boats on the terrace channels, among the graves" → the channels run *through* the cemetery tiers, and the graves stand on both banks (§2.2). Kerrid "appears at the festival's edge" → the lights stop at a terrace end that opens on the dark (P04). The smith's side scene → a smithy on the market tier (§2.2, P07). The temple trial walks a strike "down the stair-mountain's copper veins, tier by tier" → the copper veins are visible in the town's terrace walls, running from the crown towards the sea (P08), so the trial reads as something the town has lived beside.
- Bible §5.2: "Steep green volcanoes cut into rice and taro terraces, with water channels running down every slope"; "terrace cemeteries sit beside the paddies, so festivals happen among graves"; temples are stair-mountains crowned by a lacquered red pavilion; gateways are **open-hand gates** (two stone forearms, palms cupped towards each other); every household keeps a black-and-red lacquer shrine-box with gold-leaf figures; "Lit Age copper veins the tiers". Bible §4: leaf-boats are folded palm-leaf trays with a pinch of rice and a lit wick.
- ADR 0020 / kerrid.md: Kerrid wears a straw cape, says one line to Asha, and nobody hails him. No glimmer from him in Ch5 (no rope-burn glow): P04 is lit by the last festival lamp only.
- Color script `ch05`: lamp key 2,700 K at 1.6, festival night 20:00, sea-glow 0.08, LUT boosts oranges and reds and keeps volcanic stone neutral-cool "so a thousand flames read". The emotional note ("the leaf-boats drift downhill toward the sea, and the sea-glow at the bottom receives them") fixed the direction of P01: **looking down the mountain to the sea**, not up it.

---

## 0. Layout, Orientation, and Lighting Sub-frames

**Geography (world north = −Z, +Y up, metres):** Pemakar climbs the **south face** of the stair-mountain, from the sea road (+8 m) to the upper cemetery tiers (+34 m). The crown and its caldera are about 750 m north and 320 m up; the ash-plume rises from the caldera lip and leans **west** on the trade wind, so at dusk it stands dark against the afterglow. The sea lies south, below the town. Ashcrown sits on the crown's lip, in silhouette from every town shot.

**The terraces.** Each tier is a contour arc around the mountain's axis (centre about 150 m north of the town's foot), a 2.4 m retaining wall of fitted volcanic blocks with a 7 m tread behind it. Tiers are of four kinds, bottom to top: market (houses, smithy, workshops), house tiers, **paddies** (flooded rice and taro, the water a mirror), and **cemeteries** (graves on the tread, the channel along its front edge). A main stair climbs straight up the middle through an open-hand gate at each cemetery tier, with a cascade channel beside it.

**The channels (the festival's architecture).** Every tier has a stone-lined channel along the front of its tread. It runs along the contour and spills over the wall to the tier below at one end, alternating ends, so the water (and on Lanternfall night, the boats) zig-zags down the mountain. The stair cascade beside the main stair drops straight down, one spill per tier. A boat launched at the top reaches the sea road in about twelve minutes, which is about how long the Lanternfall song lasts.

**Water datum:** `tide_line_y = 0.0` at the sea. The town is far above it, so the weathering shader's algae, barnacle and tide-wet layers are **off** in the Pemakar materials, and the salt layer is re-purposed as **ash fall** (§4).

**GI recommendation:** SDFGI is not useful at night with point lights. Pemakar uses no GI at night; lamp pools are direct OmniLights (shadows only on the nearest few), plus a low sky ambient. Ashcrown (13:00) chooses its own.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill | Sea-glow | LUT |
|---|---|---|---|---|---|---|---|
| `ch05_dusk` | Arrival in town; the first boats launched; the graves at dusk (P02, P03, P05, P08, P12) | 19:05 | −4° / 285° (just set, WNW) | lamps `#FFA757` (2,700 K), energy 1.6 in their pools | sky afterglow: horizon `#E0702E` (`ember_orange`) at 0.35 in the west, zenith `#1A2440`; a sky fill `#3A4A6A` at 0.35 | 0.04 (the palette floor: the sun has only just gone) | `lut_ch05_lanternfall` at 70%. Exposure 0.95, S-curve 0.5, sat ×1.1 |
| `ch05` (color script) | Lanternfall at its height; the smithy at night; Kerrid at the edge (P01, P04, P06, P07, P09, P10, P11) | 20:00 | −18° / 0° | lamps `#FFA757` 1.6; rim `#E0702E` 0.9 (characters) | `#3A4A6A` at 0.25 (sky) | **0.08** | `lut_ch05_lanternfall`. Exposure 1.05, S-curve 0.55, sat ×1.15 |
| `ch05_temple` | Ashcrown at 13:00 | — | — | later task (Ashcrown) | | 0 | |

**Lighting notes:**
- **The dusk is in the arrival, not in a new grade of the festival.** The color script's festival frame is 20:00, full night. The party arrives at about 19:00, as the first boats are lit on the upper tiers, so the first Lanternfall shots (P03 among the graves, P05 the boat) are at dusk, with the afterglow still on the western horizon behind the plume. By P01 (the waterfall of fires) it is 20:00. The light declines between the two, and nothing jumps back.
- **The order of values (color script rule 3, practical-keyed night):** (1) wick flames and the forge; (2) the stone, water and leaves inside their pools; (3) the glowing sea; (4) the sky and the plume's ember underside; (5) shadow. Each lamp pool must fall off to the frame's ambient (no frame-wide key). Shadows go to `night_sky` teal-navy, never neutral black.
- **The plume** carries the scene's only non-practical warm light: a dull ember underside (the caldera's glow) at about the brightness of the sea-glow, never brighter than the lamp pools. No lightning in the town frames (it is the temple's; one far flicker is allowed in P11).
- **No glimmer** in Pemakar town shots (`glimmer_held` is in the frame row only for the sea-glow gate: `hymn_glimmer.a` 0.8, nothing emits it on screen).

---

## 1. Mood

Dark stone, dark leaves, and pale ash, made beautiful by thousands of small warm lights. The stone is the darkest in Act I (`volcanic_stone`, nearly black) and is dusted pale on every upward face with ash, so a terrace reads as dark verticals and pale horizontals even at night. The paddies are mirrors. The channels are lined with lights moving slowly downhill, and the spills drop them, one at a time, to the next tier. Between the channels stand the graves: low dark steles, each with a lamp niche, some with fresh frangipani laid on top. Laterite brick houses, black-and-red lacquer and copper verdigris give the small saturated notes. Above everything the plume leans across the sky. It is gorgeous and it is a funeral.

**Three quiet signs of the decline:** ash on every leaf and lintel, refreshed daily (the mountain is breathing harder); grave rows that run on past the lit tiers into the dark (more dead than lamps); and the copper veins, once Lit Age conduits, green and broken where the terraces were cut through them.

---

## 2. Kit Pieces

Module grid 0.5 m; heights from the tread or ground the piece stands on. All pieces are `<piece>` + `<piece>-lod1` (LOD1 at 70 m, chained per vegetation.md "One LOD at every distance"). Triangle budgets are LOD0 / LOD1.

### 2.1 Terraces and water
| Piece | Dimensions and parameters | Budget |
|---|---|---|
| `terrace_wall_4m` | A 4.0 m retaining-wall module, 2.4 m tall, 6° batter, fitted polygonal volcanic blocks (0.3–0.8 m, seeded, irregular courses, tight joints), coping stones 0.25 m on top. Its back is never seen. | 9,000 / 1,400 |
| `terrace_wall_copper` | As above, with a **Lit Age copper vein**: a 0.12 m verdigris conduit inlaid in the blocks, running down the face at a slant, broken at one joint with raw copper showing. | 9,500 / 1,500 |
| `terrace_tread_4m` | A 4.0 × 7.0 m tread of ash soil (a displaced grid with a 2% fall to the front for drainage), dark earth showing through the ash in a worn path band. | 900 / 120 |
| `terrace_channel_4m` | A 4.0 m stone-lined channel set on the front of the tread: dressed kerbs 0.15 m, 0.36 m wide inside, 0.22 m deep, water surface 0.05 m below the kerb tops (slot `kit_channel_water`). Wet kerb tops (VC.B). | 1,800 / 260 |
| `terrace_spill` | The drop: the channel's end turns out over the wall through a carved spout lip, a falling sheet (`kit_water_spill`, 2.4 m) and a catch basin 1.0 × 0.8 m on the tier below. Spout stones wet; splash darkening on the wall under the sheet. | 3,600 / 520 |
| `paddy_tread_4m` | A flooded paddy module 4.0 × 7.0 m: a low bund (0.25 m) of ash soil around a water plane 0.12 m deep, with rice/taro stubble rows breaking the mirror. | 1,600 / 200 |
| `stair_flight` | One tier's straight stair, 2.0 m wide, 2.4 m rise over 4.2 m run (12 risers of 0.2 m), cheek walls of volcanic blocks, worn and ash-dusted treads (the centre line is clean, walked). | 7,500 / 1,100 |
| `stair_cascade` | The stair's cascade channel for one tier: a 0.4 m channel stepping down beside the stair in three small falls (slot `kit_channel_water` and `kit_water_spill`). | 2,600 / 400 |

### 2.2 Graves, gates, lamps and offerings
| Piece | Dimensions and parameters | Budget |
|---|---|---|
| `grave_stele_a` | An **ash-stone** (original): a dark volcanic stele 0.45 × 0.95 × 0.18 m on a two-step plinth, top rounded like a shoulder, with a **lamp niche** (0.14 m) cut through near the top, a carved tide-line band, the names cut in a framed panel of terrace script and darkened with soot (M3-ENV-705), and an offering ledge. Ash on the shoulders, lichen orange spots. | 1,600 / 220 |
| `grave_stele_b` | A family stone: wider (0.9 × 0.75 m), three niches in a row, older, one corner broken off. | 2,000 / 260 |
| `grave_cairn` | A poor grave: a cairn of rounded stones (0.6 m) with a flat capstone and one niche stone. | 1,400 / 200 |
| `grave_curb` | A low kerb (0.18 m) round a family plot, 2.0 × 1.2 m, with pale ash gravel inside. | 900 / 140 |
| `open_hand_gate` | The paired gateway at a stair head: two carved stone forearms 3.2 m tall rising from a plinth, 2.4 m apart, the palms cupped towards each other over the walkway, the fingers just short of touching. Volcanic stone with ash in the knuckles. **Original design; not a split-gate profile.** | 9,000 / 1,300 |
| `lamp_pillar` | A stone lamp pillar 1.2 m: a squared shaft, a dish of oil with a wick flame (slot `kit_wick_flame`), soot on the dish's underside. Placement note: one per ~6 m of stair, and one at each gate. | 900 / 140 |
| `leaf_boat_lit` | A folded palm-leaf tray 0.22 m long (the Haluna `leaf_boat` hull, re-used by import), a pinch of rice (`bone`) and a wick with a flame. Built for MultiMesh: both LODs share one origin. | 260 / 40 |
| `shrine_box` | A household lacquer shrine-box on a short post (1.1 m): black lacquer with red panels and a thin gold-leaf figure band (≤ 5% of the box). | 900 / 140 |

### 2.3 Town
| Piece | Dimensions and parameters | Budget |
|---|---|---|
| `house_pemakar_a` | 5 × 6 m house: a volcanic stone plinth 0.8 m with three steps, laterite brick walls to 2.6 m, dark timber posts at the corners, a steep **two-tier hipped roof** (pitch 45°, then 35° on the upper tier) of dark palm-fibre thatch, laterite-tile ridge with a copper finial. A red lacquer door and shutters. | 9,000 / 1,300 |
| `house_pemakar_b` | 4 × 5 m house with a front veranda 1.5 m deep on four posts, single steep hipped roof, laterite walls. The lacquer workshop variant: drying racks of red-lacquered trays on the veranda. | 9,000 / 1,300 |
| `smithy` | Open-sided forge shed 6 × 5 m: four timber posts on stone plinths, a fibre-thatch roof with a smoke gap at the ridge, a stone **forge hearth** with a laterite-brick hood and chimney (forge mouth slot `kit_forge_glow`), an anvil on a stump, a quench trough, a tool rack, and a stack of copper ingots. The side scene's set. | 12,000 / 1,800 |
| `copper_outcrop` | A bedrock outcrop 3.5 × 2.0 m where a terrace cut exposed copper ore: dark volcanic rock with two branching green-and-copper veins (`kit_copper_vein`). | 3,500 / 500 |

### 2.4 Skyline (silhouette pieces)
| Piece | Dimensions and parameters | Budget |
|---|---|---|
| `mountain_massif` | The stair-mountain above the town: about 1,400 m across, crown 320 m above the town's foot, its south face cut into terrace bands (quantised contours, softened), the caldera lip notched at the top. Volcanic stone with moss (VC.R) on the bands. | 14,000 / 3,500 |
| `ashcrown_silhouette` | Ashcrown as a skyline shape only: a stepped stair-mountain of seven tiers (each smaller), 42 m tall, a lacquered pavilion at the top (red, dark at night) and a **copper spire** 14 m above it. | 6,000 / 900 |
| `ash_plume` | The plume as a lofted, billowing volume 420 m tall, rising from the caldera and leaning west, with an ember underside (slot `kit_plume_ember`) on its lowest 15%. | 7,000 / 1,800 |
| `ash_plume_near` | (M3-ENV-11) The same plume for close views (Ashcrown's crater, rim and forecourt, inside ~900 m): `ash_plume`'s own surface (the same noise, seeded by `ash_plume`) sampled 160 × 128 instead of 64 × 52, the creases between the heads rounded, the normals smoothed over the grid and bent 30% toward the column's radial direction, and the small heads carried in UV2.x for `env_ash_plume`'s `billow_shade`. LOD1 **is** `ash_plume`'s LOD0. The town keeps `ash_plume` (it is 900 m away). | 42,000 / 7,000 |

**Vegetation:** frangipani (`frangipani_a`/`_b` from the vegetation set) over the graves, as on the Low Reaches; it is the grave tree here too. Rice and taro are in the paddy modules. A fern and a sugar-palm are wished for (vegetation task; not in this kit).

---

## 3. Materials (against palette.json)

| Slot | Shader | Palette | Notes |
|---|---|---|---|
| `kit_volcanic_stone` | weathering | `volcanic_stone` `#3A3A3F` | Vesicular, fine-grained, slightly cool; ash fall in G (§4); lichen orange spots (`#C08A3A` 10%) on sun sides; moss on north faces of lower tiers. |
| `kit_volcanic_dressed` | weathering | `volcanic_stone` +1 | The graves, gates and kerbs: dressed faces, shallower pits, the same ash. |
| `kit_volcanic_far` | weathering (no detail) | `volcanic_stone` | The massif: 8 m tile, moss bands. |
| `kit_laterite_brick` | weathering | `laterite` `#A8573A` | House walls, chimney: bricks 0.24 × 0.08 m, soot above the forge. |
| `kit_ash_soil` | weathering | ash over `volcanic_stone` and `laterite` flecks | Treads and paddy bunds. |
| `kit_fibre_thatch` | weathering | `lacquer_black` `#1D1916` lifted to `#2E2924` | Dark palm-fibre thatch; ash on the slopes. |
| `kit_timber_dark` | weathering | `timber_weathered` smoked ×0.7 | Posts, beams, stumps. |
| `kit_laterite_tile` | weathering | `laterite` | Ridge tiles. |
| `kit_copper_vein` | Standard | `bronze_patina` `#5F8A78` | Verdigris conduit, metallic 0.3, rough 0.6. |
| `kit_copper_raw` | Standard | `hair_copper` `#A65A2A` | Broken vein ends, ingots, finials: metallic 1.0, rough 0.35. |
| `kit_iron` | Standard | `lacquer_black` | Anvil, tools. |
| `kit_lacquer_red`, `kit_lacquer_black`, `kit_gold_leaf` | Standard | `lacquer_red`, `lacquer_black`, `gold_leaf` | Doors, shrine-boxes. Gold ≤ 5% of any frame, red ≤ 8%. |
| `kit_channel_water`, `kit_paddy_water` | Standard | `abyss_navy` `#061A2B` albedo | Dark, low roughness (0.04 / 0.08): they are mirrors for the flames and the sky. |
| `kit_water_spill` | env_water_spill (Haluna's) | — | Falling sheets. |
| `kit_leaf_boat` | Standard | `palm_green` `#3E7A3A` | Leaf, green side out, backlit. |
| `kit_rice` | Standard | `bone` | |
| `kit_wick_flame` | Standard, emissive | `oil_lamp` `#FFB16E` | Flames of boats and lamps (emission 4). |
| `kit_forge_glow` | Standard, emissive | `ember_orange` `#E0702E` | The forge mouth (emission 3). |
| `kit_plume`, `kit_plume_ember` | Standard | `storm_slate` `#3E4A57` darkened; `ember_orange` underside (emission 0.25) | |

**Ash** is not a palette swatch yet. Proposed swatch `ash_fall` `#8C8882` (a warm neutral grey, inside the albedo floor and ceiling; luminance about between `cold_blue_stone` and `coral_stone_weathered`), for the Art Director to adopt or replace. Until then the kit uses it only through the weathering layer.

---

## 4. Weathering in Pemakar (the haluna.md §4 stack, re-purposed)

The vertex-colour convention is unchanged (**R moss, G salt, B wet, A erosion**), so the shared `env_weathering` shader dresses the kit. The tide layers do not apply this high above the sea, so the Pemakar materials set them as follows:

| Layer | Pemakar use |
|---|---|
| 1 base | Volcanic stone (vesicular), laterite brick, ash soil, fibre thatch, dark timber. |
| 2 erosion (VC.A) | As Haluna: rounded edges, pits; edges lighten only 4% (dark stone looks chalky if pushed). |
| 3 algae, 4 barnacles | **Off.** |
| 5 salt → **ash fall** | VC.G is written as **ash**: the generator paints it by upward-facing normal × noise (ash settles on every top, ledge and lintel, and gathers in crevices), and the material sets `col_salt` to `ash_fall`, the height band to the whole mountain, coverage 0.35–0.75, roughness 0.95. |
| 6 moss and lichen (VC.R) | Moss on shaded north faces of walls and on the massif's terrace bands; lichen orange spots on sun-facing graves. |
| 7 wet (VC.B) | Painted on channel kerbs, spill lips and the wall under each spill (splash), and on paddy bunds. |

---

## 5. Composed Camera Shots

Conventions as haluna.md §5: lens is full-frame equivalent; Godot `Camera3D.fov` is vertical, vFOV = 2·atan(12 / mm). Height is above the local tread. ◆ marks the shots built in the kit preview; ★ the two registered as screenshot baselines.

| # | Sub-frame | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|---|
| P01 ◆★ | `ch05` 20:00 | 35 mm (37.8°) | 4 m, on the water off the harbour, about 130 m south of the town's foot | Looking **north, up** the mountain from the sea: the boats that reached the sea drift out from the shore in the foreground (small flames on the sea-glow); the sea road's lamps; the town's tiers at the foot with the stair up their middle; the pilgrims' stair of lamps climbing straight on up the face to Ashcrown on the rim; the far terrace bands lit with boats left and right, thinning toward the crest; the plume leaning west across the top, dark against the stars, a dull ember at the vent. | A mountain turned into a waterfall of small fires, falling to the sea that receives them. |
| P02 ◆ | `ch05_dusk` | 35 mm (37.8°) | 1.6 m, on the market tier at the foot of the main stair | Looking north up the stair through the first open-hand gate; house tiers on both sides with lit doorways; the stair's lamp pillars lead up; the plume leans across the top third against the afterglow on the left. | Arrival: a town that climbs, and something breathing above it. |
| P03 ◆★ | `ch05_dusk` | 28 mm (46.4°) | 1.3 m, on a cemetery tread beside the channel | Looking west along the channel: it runs from the lower-left foreground towards a spill at the right third, carrying a loose line of boats; grave steles on both banks, niche lamps lit, a frangipani overhead; the lower tiers fall away on the left with more lights; the afterglow and the plume's dark lean beyond. | Among the graves: the festival is for them. |
| P04 | `ch05` | 50 mm (27.0°) | 1.6 m | The east end of a cemetery tier where the lamps stop: the last lit stele on the left third, a dark figure in a straw cape standing beyond the light (Kerrid), the unlit graves running on into the dark behind him. | The edge of the festival. A stranger who has held a stair. |
| P05 ◆ | `ch05_dusk` | 100 mm (13.7°) | 0.35 m above the channel kerb | One leaf-boat sharp (rice, wick, flame), its reflection in the dark water; three more soft behind; the spill lip out of focus at the right. | One light for one person. |
| P06 ◆ | `ch05` | 50 mm (27.0°) | 1.0 m on the tier below a spill | The falling sheet over the dark wall, lit by the boats tipping over the spout; the catch basin full of drifting lights; wet stone under the sheet. | Going down, one tier at a time. |
| P07 ◆ | `ch05` | 28 mm (46.4°) | 1.5 m, in the smithy's open side | The forge mouth glowing, the anvil in its pool, copper ingots catching it, the quench trough; through the open side the festival lights on the tiers above. | The smith whose son drowned in Oruvel; work in the middle of a festival. |
| P08 ◆ | `ch05_dusk` | 50 mm (27.0°) | 1.2 m | A terrace wall with the Lit Age copper vein slanting down the stones and on down the walls below; the copper outcrop at the foot; one lamp pillar. | The veins the strike will run down: foreshadowing the trial. |
| P09 | `ch05` | 24 mm (53.1°) | 0.8 m at a paddy bund | A flooded paddy mirroring the lights of the tiers above and the plume; rice stubble breaking the reflections. | The festival doubled. |
| P10 | `ch05` | 18 mm (67.4°) | 1.7 m on the sea road (P01 now covers most of this from the water) | Looking up the whole south face: walls stacked, spills as threads of light, the plume and Ashcrown above. The establishing shot of Lanternfall from below. | The whole mountain at once. |
| P11 | `ch05` | 135 mm (10.2°) | from the upper tier | Ashcrown on the crown: the tiers and the copper spire against the plume's ember underside; one far flicker of dry lightning in the plume. | The next trial, already waiting. |
| P12 | `ch05_dusk` | 35 mm (37.8°) | 1.6 m in a house lane | A lane between laterite houses: lacquer shrine-boxes at the doors with small lamps, ash on the steps, a lacquer workshop's racks of red trays. | Ordinary lives, each with its dead in a box by the door. |

---

## 6. Review Checklist for This Zone
- [ ] Grayscale value check: darks concentrated in the stone, lights in the flames; each shot has one clear focal light shape (references.md §1.2).
- [ ] The value order in §0 holds: flames > lit stone and water inside the pools > sea-glow > sky and plume > shadow. Each pool falls off to the frame's ambient.
- [ ] Gold ≤ 5% and red ≤ 8% of any frame; volcanic stone reads neutral-cool, not brown.
- [ ] Shadows go teal-navy (`night_sky`), never neutral black.
- [ ] Ash reads on every upward face at gameplay distance (pale horizontals, dark verticals).
- [ ] No glimmer on screen in the town shots; no lightning except P11.
- [ ] Boats move only downhill; every channel has a spill at its downstream end.

## Revisions
- 2026-10-24 (env-art, M3-ENV-03): first version, before geometry. Adds the `ch05_dusk` sub-frame for the arrival and the first boats (the color script's `ch05` festival frame stays 20:00). Proposes the `ash_fall` swatch.
- 2026-10-24 (env-art, M3-ENV-03, after the lavapipe passes): **P01 turned round.** Looking down from the stair head, the town filled the frame as a few lit bands and the sea was a flat teal field; the mountain, the plume and Ashcrown, which carry the chapter, were behind the camera. From the water looking north the whole festival reads at once, and the emotional note still holds (the boats arriving on the sea in the foreground). The preview adds, for that view: the **pilgrims' stair** (a line of lamps straight up the face from the town to Ashcrown), a **sea road** of lamps along the shore, and the **boats on the sea** (billboard lights, like the far lights). The plume is fog-free (the ch05 warm fog turned it brown at 900 m), darker and lumpier, with a thin afterglow rim only while the sun is just down. `stair_cascade` (§2.1) is not built: the cross channels and spills carry the water, and the stair's lamp pillars carry the line of light in P02; it stays on the wish list.
- 2026-10-24 (env-art, M3-ENV-09B): **Ashcrown on the rim is the Ashcrown kit's building.** The preview layout and the Lanternfall arena (through `town_to_arena`) place the Ashcrown kit's exterior pieces (`ashcrown_tiers`, `flying_stair`, `crown_pavilion`, `forecourt`, `pilgrim_causeway`) at the kit's origin, the rim point (0, 306.72, −682), yaw 0, in place of `ashcrown_silhouette`; each placement names its kit (`kit_dir`, `materials_dir`) and its LOD1 distance (600 m, the Ashcrown preview's), so from the town and the arena they draw their LOD1 and the far and near temple are one mesh. The interior pieces, `plume_vent` and `crest_ground` are left out (the massif stays the ground here). `ashcrown_silhouette` (§2.4) is no longer placed; it is still built as the Ashcrown kit's reference numbers (test_ashcrown_kit).
- 2026-10-24 (env-art, M3-ENV-11): **a near plume.** `ash_plume_near` (§2.4) and a `near` group in `env_ash_plume` (a sky-coloured lift on the side away from the sun and, in part, all round, for billows in the temple's or the rim's shadow; back-scatter through the edges looking sunward; the vent's ember on the foot; the billow shading from UV2.x; a bumped billow normal inside ~240 m; `alpha_mottle`, so a near plume can be solid). Every near parameter defaults to 0 (alpha_mottle to the old 0.4) and fades out by `near_fade_m`, so `kit_plume` and the town's plume render exactly as before (P01, P03 and the Lanternfall arena compare at rmse 0). Found on the way: close up the plume's 3% see-through showed the crater rim through it (the "near-black" side was partly that), so the near material sets `opacity` 1 and `alpha_mottle` 0.04.
- 2026-10-27 (env-art, M3-ENV-1214, for act1-chapters' Ch5 swap): the harbour pieces (`harbour_quay`,
  `sea_cut_weir`, `wake_wall`) and the top tier's `crown_bell` (`pemakar_harbour.py`), placed in the preview (the
  weir where the bottom channel meets the shore). A `day` mood for B11 (16:30): `pemakar_day_environment.tres`,
  a low-sun sky with the colour script's temple-frame blue carried down the mountain, a shadowing `Sun`, the
  festival out. Shots P04 (the harbour) and P11 (the weir from the sea), both by day.
