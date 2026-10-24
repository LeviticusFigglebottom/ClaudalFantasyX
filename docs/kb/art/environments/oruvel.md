# Oruvel, the Raft-Town: Design Notes

Owner: Environment Artist (M3-ENV-07). Lighting: Rendering (the Undertow and its `ch01_arrival` / `ch01_landfall`
presets are Rendering's). Gameplay placement (spawns, triggers, NPCs, collision): m2-slice (swap-in note in the
M3-ENV-07 task file). The drowned city under the rafts is the sibling sheet [oruvel_underway.md](oruvel_underway.md).
Story: [act outline Ch1 "Lamp-Diver"](../../story/beats/act_outline.md) (zones, the gulls, the Rising, Hullgnaw on a
breaking raft, Kell's wick), the Ch1 beat sheet [act1_ch01.md](../../story/beats/act1_ch01.md) C1-07 to C1-15, its §4
(Kell's chandlery), §5 (the net-pen hull), §7 (shot ids O01–O18) and §9 Environment request 1, [bible §3
Oruvel](../../story/bible.md) ("a raft-town of lashed hulls moored above a drowned Lit Age district of coral-crusted
concrete towers; lamp-divers go down with oil lanterns to salvage pre-Edict metal and glass"), bible's 1001 AL row
(Kell on the second mooring), decisions_log N-02 (the lantern burns oil), [ADR 0017](../../decisions/0017-act-one-restaging.md)
(Kerrid is not at Oruvel), [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) sweep-H (the lantern hook,
Kell's wick). Grade: [color script `ch01`](../color_script.md) (10:30, the raft-town). Colours:
[palette.json](../palette.json). Zone: `game/levels/ch01/oruvel/`. Kit: `assets_src/environments/kits/oruvel/`.
Preview: `game/levels/_tests/oruvel_kit/`.

**The feeling in one line:** the brightest morning in the game on a poor, loud, patched-together town that floats:
faded paint on every hull, nets drying on every rail, lamps hung everywhere and lit nowhere, and under the clear
water, six metres down, the white crowns of the city they live off.

**Influences** (references.md, in words): floating fishing villages on sheltered bays, where every house is a boat or
stands on lashed drums and the streets are planks between hulls; Pacific outrigger canoes, a slim hull with a float
on two curved booms; old fishing coasts where a worn-out boat is turned keel-up and becomes a shed's roof; river
markets of cook-boats with a clay stove amidships and a smoke hood; the bleached, repainted, re-repainted look of
working boats in strong sun, every plank a slightly different blue. **Our originals and transformations:** the
**keel-roof**: a cabin whose roof is an old hull turned over (keel along the ridge, the stem and stern overhanging the
gables), so a cabin's skyline is a boat's bottom and the ridge is where the town's lintel-gull perches; the **lamp
rails**: every cabin's eave carries a row of iron hooks for the divers' oil lanterns, empty by day except at the
chandler's, where they hang by the dozen; the **tether winch** on the dive raft (a drum, a crank and a pawl over a dive
well, the A-frame and its block above); the **knot tally** (the cook's credit kept in knots on a hanging cord, the
same craft as the Underway's divers' cord); **salvage patches**: white Lit Age ceramic panels and brass sheet nailed
over rotten planking, so the drowned city shows on the town's walls; and the **open-throat lintel-gulls** (Haluna's
carved gull with its throat bored hollow, so a wind off the sea goes through it: C1-11).

**Not Haluna.** Haluna is coral-stone and timber on land: dry-stacked walls, stilt houses, red tile and thatch hips,
white mortar. Oruvel has **no stone, no tile and no thatch at all**: everything is boat timber, rope, canvas and
salvage, everything floats and moves a little, and the roofs are hulls. Haluna's palette is coral and red tile; Oruvel's
is faded hull paint (sea blue, red ochre, yellow ochre, teal, whitewash) over silver timber, on turquoise water.

**Act I rule.** Life at its fullest, so the loss lands (color script `ch01`): high key, saturated where the paint
is, shadows teal under the decks, never grey. The sorrow is not in this frame at all yet; it is in the player's
memory of it later. Nothing glows: it is 10:30 and every oil lamp in the town is out (Kell lights the beacon in the
drill, C1-12, in the storm variant). **No bound light** anywhere (the Lit Age panels on the walls are plain ceramic).
**Kerrid is not here** (ADR 0017): no stranger, no figure on a far hull.

---

## 0. Layout, Orientation, and Lighting

**The frame is the Underway's** (oruvel_underway.md §0): world north = −Z, +X east, metres, **the sea surface at
y 0**. The drowned tower (36 × 12 m, x −18…18, z −6…6) has its broken crown floor 6.4 m down; the Underway's
tether drops into the crown at **(−9.9, 5.2)**. Oruvel is moored over that block and the blocks north and west of it.

```
                                N (-Z)
        net lanes (two rafts, nets between)     the keel-hull (hero, 22 m, three decks)
             (18, -44)                                (-16, -36)  the town's meeting place
                 |                                        |
   Reefball  -- cookboat lane (cookboats moored along a plank walk, x -2..14, z -22)
   pen          |                                        |
   (28, -10)    town rafts (cabins on lashed decks)    second mooring: KELL'S CHANDLERY (-38, -14)
                |          |                             \   (plank bridge west)
                scale-hull (7, -1)        dive raft's neighbour raft (-3, 11)
                       \                 /
                  the DIVE RAFT (well at -9.9, 5.2) ............ outer mooring (-58, 8), open water west
              =========== the drowned tower's crown, 6.4 m down (x -18..18, z -6..6) ===========
                                S (+Z): the open sea, the reef edge, the horizon of O11
```

- **The seaward edge is the south** (+Z): the dive moorings sit on the town's outer edge over the deepest towers,
  and the lintel-gulls all face **south-south-east**, out to sea (yaw so the carving's +X points to (0.35, 0, 0.94)).
  The trade wind blows from the north-east (behind the gulls); on C1-11 it turns and comes from the sea, through
  their throats.
- **The dive raft** (C1-11, the second dive; the surfacing point of C1-07): its dive well is centred over the
  Underway's tether at **(−9.9, 5.2)**, deck top **y 0.75**. The Underway's `hull_keels` (overhead in U01, at
  (−3, 11)) are the bottoms of the **neighbour raft** the dive raft is lashed to; that raft is a `raft_deck_small`
  here, placed at the same point and yaw, so the two sheets agree from above and below.
- **The scale-hull** is the first stop after surfacing (C1-08, ten minutes later): moored 17 m east of the dive raft
  at (7, −1), its counter facing the dive raft across open water and a plank bridge.
- **The town** lies north of the dive moorings: lashed decks of cabins in rows with plank bridges and open water
  lanes between them (the "streets" are water and planks; outriggers tie up everywhere). The **cookboat lane** runs
  east-west at z ≈ −22. The **net lanes** are two long net-drying rafts north-east at (18, −44). The **Reefball
  practice pen** (the net-pen hull, Hullgnaw's arena, C1-13/14) is moored on its own at the east edge, (28, −10).
- **The keel-hull** (the oldest and biggest hull, the town's meeting place, C1-09 bark 6 and C1-12's drill point)
  is at the town's middle, (−16, −36), its long axis east-west, its three decks stepping up toward the stern (west).
- **The second mooring** (Kell's chandlery, C1-10) is a short plank bridge west of the town rafts at (−38, −14): on
  every diver's way from the town to the dive moorings, as the beat sheet needs.
- **The outer mooring** (the *Seventh Terrace*, C1-09 bark 5, O07, O13) is open water west at (−58, 8). The coaster is
  not in this kit (act1_ch01 §9 request 4: one hero prop shared with Ch4; a follow-up task).
- **The drowned city shows through the water** (`lagoon_clear` ×2.0, act1_ch01 §9): the tower's crown at −6.4 m is a
  pale shape under the dive raft from a high camera. The preview places the Underway kit's crown pieces read-only
  under the dive raft to check the read.

**Water and tide.** The lagoon at 10:30 is mid tide, slack and clear: the water look is the colour script's
validated `lagoon_clear` at absorption ×2.0 (σ 4 / 1 / 0.84 m⁻¹, scatter `#1FA3A6`, deep `#0E4A55`), calm waves (the
lagoon set at low amplitude: the town is in the lee of the reef). Decks ride **0.6–0.9 m** above the water (freeboard
by hull size); the bridges between them slope a little and sag under their own weight.

**GI:** SDFGI off on every tier, sky ambient + SSAO (the Haluna README's finding on lavapipe), as Haluna's noon.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill / ambient | Exposure / grade |
|---|---|---|---|---|---|---|
| `ch01` | the whole raft-town by day (O01–O10) | 10:30 | 58° / 120° | `#FFEFE1`, energy 3.0 | `#8FC3E0` 0.6 (the sky's own radiance, ambient from the sky at 0.6) | exposure 0.65 (EV100 14.5), saturation ×1.12 in `lut_ch01_raft` (+8% in cyans and oranges, mild toe lift), the cumulus noon sky with a light fair-weather field (coverage low: "the sky is clear", C1-11) |
| `ch01_storm` | C1-12 to C1-15 (O11–O18) | 11:10–11:28 | (same sun) | — | — | `lut_ch01_storm` (greens to slate, saturation 0.75 over 4 s); the storm variant of this kit: a follow-up (§7) |

**Value structure.** Upper-mid overall (the brightest frame so far): the sky and the sunlit water are the two big
light fields; the hulls carry the saturated notes in a band across the middle third; the darks are the teal shadow
under every deck and in the cabins' doorways. **The focal value is the sunlit faded paint against the turquoise
water** in the wides, and in the close shots the warm brass (the scale, the lamp rack, the winch's pawl).

---

## 1. Mood by Moment

1. **Surfacing (C1-07, O01).** Up out of the Snell window into noon: the town at Rhen's eye level from the water, hull
   after hull in every blue and red the sun has faded, laundry on the cabin lines, nets on the rails, a cabin roof
   that is a boat's bottom, carved gulls on every ridge, children on a roof. The brightest frame in the game so far.
2. **The scale-hull (C1-08, O02).** A small booth on a hull: a brass beam scale on a post, a counter, the chit stamp
   and its ink, and a small brass Level plaque, the Order's only mark in the town. Everything else around it is
   handmade.
3. **Oruvel by day (C1-09, O03–O08).** Plank bridges between rafts, the cookboats smoking along their lane, nets
   strung between poles on the net lanes, the empty practice pen, the keel-hull at the middle with its three decks
   and its gull. Noisy, poor, his.
4. **Kell's stall (C1-10, O09).** A cabin hull under a striped awning on the second mooring: racks of oil lanterns on
   the eave hooks, fat clay oil jars, spools of wick on pegs, a shelf of pigeonholes for the post, a counter worn
   pale by elbows, and the big beacon lamp on the roof, unlit. Warm, cluttered, the most lived-in corner of the town.
5. **The dive mooring (C1-11, O10).** The dive raft over the tower: the winch and its drum of tether, the A-frame's
   block over the dark square of the dive well, the ladder going down into turquoise, the white crown of the tower
   faint below. A gull on the nearest ridge against a cloudless sky.
6. **The net-pen hull (C1-13/14, O15–O17).** A square raft round a netted pool: the boss arena (its storm split is §7).

---

## 2. Kit Pieces (origin at the waterline or the deck as stated, +Y up; hulls built along local +Z, bow at −Z)

Every hull is plank-built: four visible strakes lapped down the sides (each a small step), a rubbing strake and
gunwale cap, a keel and stem/stern posts, the bottom tarred dark below the waterline and the topsides painted. The
paint is one slot, **`ov_hull_paint`**, faded sea blue by default; a placement overrides it (HalunaDresser's
`materials` map) with `ov_paint_red`, `ov_paint_ochre`, `ov_paint_teal` or `ov_paint_white`, so one hull piece gives
five colourways. Decks are planks laid across bearers lashed to the hulls' gunwales (visible coir lashings at every
crossing); floats are bound log pairs and lashed barrels.

| Kit | Pieces | Key dimensions and parameters |
|---|---|---|
| **Hulls** | `hull_outrigger`, `hull_cabin` | Outrigger: 6.5 m × 0.8 m beam, 0.55 m deep, a float log on two curved booms (2.2 m out), a thwart and a paddle; origin at the waterline. Cabin hull: 10 m × 2.6 m, 1.2 m deep, open, side benches and a mast step; origin at the waterline, gunwale at +0.55. |
| **Rafts** | `raft_deck`, `raft_deck_small` | Deck: 9 × 7 m planked platform on three 11 m hulls (bows north), deck top **+0.80** above the waterline, fascia boards, cleats and bollards, a bound float log along each long side. Small: 6 × 5 m on two 8 m hulls and four lashed barrel floats, deck top **+0.70**. Origin at the deck's middle at the waterline. |
| **Bridges** | `plank_bridge` | 6.0 m span between deck edges at the same height (y 0 local = both deck tops), 1.1 m wide: two stringers sagging 0.15 m, 18 planks lashed across (one missing), a rope handrail on posts along one side, **lashings wrapped hard round each stringer end and its deck cleat** and two diagonal stay ropes, so the bridge reads as held in tension. |
| **Cabins** | `cabin_keelroof`, `cabin_patched`, `stall_awning` | Keel-roof cabin: 4.0 × 5.6 m footprint, walls of horizontal salvaged hull planks (patches of three old paints), a door with a canvas curtain, a shuttered window, the roof an upturned 7 m hull (its keel the ridge at +3.4 m, stem and stern overhanging the gables 0.7 m), the eave lamp rail with two hooks, a lantern hook by the door; origin at the floor (sits on a deck). Patched cabin: 3.6 × 4.2 m, a plank lean-to roof (ridge +3.0 m, eave +2.2 m), walls patched with **Lit Age ceramic panels** and brass sheet, a water jar on the roof, a laundry line on two poles. Stall: 3.0 × 2.0 m, a counter of crates, a patched canvas awning on four oars, baskets. |
| **Gull** | `lintel_gull_open` | Haluna's crying lintel-gull (village.py, read-only) at 0.70 m with its **throat bored hollow**: a dark bore from the open beak through the head to a round wind-hole at the nape, its rim cut sharp. Faces local +X (the sea). |
| **Heroes** | `keel_hull`, `chandlery`, `scale_hull`, `cookboat`, `dive_raft`, `net_pen` | **Keel-hull:** a 22 m × 6.4 m old trading hull, 2.2 m deep, gunwale +1.1, deck +1.0; three decks: the main deck (the meeting deck, a canvas awning on spars), a deckhouse (8 × 4.6 m, deck on its roof at +3.6 with a rail) and an aft house on that (4 × 3.6 m, a keel-roof, ridge +6.6, the town's biggest gull at the stern ridge), a carved stern post, ladders between decks, lamp rails. **Chandlery:** an 8 m cabin hull with a keel-roof cabin (5 × 3.6 m) on it, the street side open as a counter under a striped awning, **lamp racks** (two rails of 8 unlit oil lanterns), four tall clay oil jars, a **wick board** of 12 spools on pegs, the **post shelf** (a 4 × 3 pigeonhole box), a stool, and the **beacon lamp** on a post on the roof (a 0.6 m brass lantern with a cowl). **Scale-hull:** a 7 m hull with a booth (2.4 × 2 m, a plank roof), the counter, a **brass beam scale** (a 1.2 m beam on a post, two pans on chains, a pointer), the chit stamp and ink tin, a stack of chits, a small **Level plaque** (0.25 m brass, a horizontal bar over a plumb drop: an original mark) on the booth post. **Cookboat:** a 7.5 m hull with a clay stove amidships (a firebox and a pot), a smoke hood of tin on four posts, two cookpots, a rack of bowls, the **knot tally** (a cord hanging from the hood with nine knots), stools on the gunwale plank. **Dive raft:** 7 × 6 m deck on two 9 m hulls, deck top +0.75, a **1.6 × 1.6 m dive well** in the middle, an **A-frame** (3.2 m) over the well with a block, the **tether winch** at the well's side (a 0.5 m drum wound with tether, two cheeks, a crank and a brass pawl), a **ladder** from the well's edge down to −2.4 m, a rack of four diver lanterns (unlit), a basket of lead weights, two coiled tethers, a lamp hook by the well. **Net-pen hull:** a 12 × 12 m square of lashed walkways (1.4 m wide) round a 9.2 m pool, four corner posts (2.4 m) with the practice net hung between them and down into the water, float logs under the walkways, a short ladder. |
| **Props** | `net_frame`, `salvage_heap`, `town_far` | Net frame: four 3.2 m poles in a row (6 m) with two nets draped between them, floats along the head-rope, a basket. Salvage heap: 3 × 2 m of Lit Age ceramic panels, brass pipe lengths, an empty lamp housing, two crates, a basket, a coil of rope. Far town: a 64 × 30 m strip of low hull, cabin and keel-roof silhouettes and masts for 80 m and beyond. |

**Budgets (triangles, LOD0 / LOD1):** outrigger 3,500 / 250; cabin hull 5,000 / 300; raft deck 18,000 / 900;
small raft 12,000 / 600; bridge 5,000 / 200; cabins 10,000 / 500; stall 5,000 / 300; gull 2,800 / 420; keel-hull
28,000 / 1,500; chandlery 24,000 / 1,200; scale-hull 14,000 / 700; cookboat 11,000 / 600; dive raft 18,000 / 900;
net-pen 16,000 / 800; net frame 5,000 / 300; salvage heap 8,000 / 400; far town 5,000 / 1,500. LOD1 begins at 70 m
(the Haluna table); every piece is a chain (`<piece>`, `<piece>-lod1`), so one LOD draws at every distance
(vegetation.md "One LOD at every distance").

## 3. Materials (palette.json names)

| Slot | Shader | Look |
|---|---|---|
| `ov_timber` | weathering (Haluna `timber`) | decks, bridges, cabin walls: sun-silvered `timber_weathered` gone pale grey on the tops, salt in the grain, darker where wet near the water (VC.B and the live tide line) |
| `ov_hull_tar` | weathering (Haluna `timber`) | the hull bottoms below the boot-top: tarred dark brown-black (`#3A3029`), an algae band and barnacles at the waterline (the shader's tide band) |
| `ov_hull_paint` | weathering (Haluna `timber`, painted) | the default topside paint: faded sea blue (`sea_blue_cloth` `#3C78A8` faded to `#5D88A6`), worn through on the edges and strake laps |
| `ov_paint_red`, `ov_paint_ochre`, `ov_paint_teal`, `ov_paint_white` | as above | the colourways: faded red ochre (`roof_clay` `#B5523A` faded to `#A85F4C`), yellow ochre (`dusk_gold` faded to `#C49A5C`), faded teal (`faded_teal_cloth` `#5E9A96`), old whitewash (`#D6D0C4`, under the albedo ceiling) |
| `ov_carved` | weathering (Haluna `carved_wood`) | the gulls, the keel-hull's stern post: one piece of grey driftwood |
| `ov_rope`, `ov_rope_tar` | weathering (Haluna `woven_panel`) | coir lashings `#9C7E5A`; tarred tether and stays `#4E4034` |
| `ov_canvas_sand`, `ov_canvas_red`, `ov_canvas_teal` | weathering (Haluna `woven_panel`, painted) | awnings and curtains: `sand_cloth`, a faded madder stripe (`#A65A4A`), `faded_teal_cloth`; two-sided |
| `ov_net` | standard, alpha hash (Haluna net map) | nets: twine `#8C7A5E`, the Haluna rule (hashed cutout, not blend) |
| `ov_ceramic` | weathering (Haluna `coral_concrete`, painted) | salvaged Lit Age panels on the walls: `lit_ceramic` `#DCE3E0` greyed, a little algae left in the joints, chipped edges |
| `ov_clay` | weathering (Haluna `coral_concrete`, painted) | oil jars, the cookboat's stove: `laterite`-earthenware `#A8573A` |
| `ov_brass` | standard | `brass` `#B08D57`, metallic 0.85, roughness 0.45: the scale, the lamps, the winch pawl, the plaque |
| `ov_iron` | standard | the lamp hooks, the winch's crank and straps: rusted dark iron `#4A3A30` |
| `ov_glass` | standard, translucent | the lantern glasses and float glass: `salt_glass` `#BFE6E0` at 0.55 alpha |
| `ov_wick` | standard | wick spools: undyed cotton, `gauze_white` dulled `#D9D2C2` |
| `ov_lead` | standard | the divers' weights `#55585A` |
| `ov_interior_dark` | standard | doorways, the dive well's shadow, the stove's mouth: `#2B2622` |

**No emissive slot in the kit:** every lamp is out at 10:30. The beacon's flame and the night lamps are the zone's
lights (m2-slice, Rendering), placed at the layout's `lamp_points`. Weathering channels follow haluna.md §4
(**R moss, G salt, B wet, A erosion**): no moss on a raft (R ≈ 0), salt high on everything above the water, wet low on
the hulls; the algae and barnacle layers live only at the waterline (the shader's tide band about the live water).

## 4. Composed Shots (vFOV = 2·atan(12 / mm); heights above the water or the local deck)

Shot ids follow act1_ch01.md §7 (O01–O18 are the beat sheet's; O19–O20 are this sheet's). Lenses are proposals;
Cinematics owns them. **◆** marks the preview shots built in `oruvel_kit/`.

| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| O01 ◆ | 35 mm (37.8°) | 0.35 m above the water, 14 m south of the dive raft, looking north | The town at Rhen's eye level across the water: the dive raft's A-frame and ladder left of centre, the scale-hull right, cabins and keel-roofs stacked behind in faded colours, laundry, nets, gulls on the ridges; the sky the top 45%; turquoise water across the lower third with the hulls' reflections. | Up from the dark into the brightest frame so far: a whole town, his. |
| O02 ◆ | 50 mm (27.0°) | 1.5 m on the dive raft's bridge, across the counter | The scale-hull's booth: the brass scale centred, the stamp and chits on the counter, the Level plaque small on the post at the right; the town soft behind. | A stamp and a scale are enough to show the Order's reach. |
| O03 ◆ | 24 mm (53.1°) | 1.6 m on a plank bridge | A plank bridge leading in from the lower left to a raft of cabins, outriggers tied up in the water lane, the keel-hull's decks rising beyond, nets on the rails. | The town loop: planks over water, everyone's front door a boat. |
| O04–O06 | rail | — | The cookboat lane, the net lanes, the empty practice pen. (Cinematics; the rail cameras of C1-09.) | |
| O07 | 85 mm | — | The *Seventh Terrace*'s name-board (an insert; the coaster is a follow-up, §7). | |
| O08 ◆ | 35 mm (37.8°) | 1.5 m on the deck of the raft south of the keel-hull | The keel-hull broadside: its three decks stepping up to the aft house, the meeting awning, the big carved gull on the stern ridge against the sky. | Where the town meets, and where the drill runs to. |
| O09 ◆ | 65 mm (20.9°) | 1.4 m at the chandlery's counter, shallow depth of field | Kell's counter in focus (the wick board, a spool, the counter's worn edge), the lamp racks and oil jars soft above and behind, the awning's stripe across the top. | Her trade: the light every diver goes down with. |
| O10 ◆ | 85 mm (16.1°) | 1.2 m on the dive raft, low, looking up north-west | The nearest lintel-gull on a keel-roof ridge, 35% of frame height, facing the lens and the sea, its open throat a dark bore; a cloudless blue behind it; the winch's drum soft in the lower left. | Every carved gull faces the sea, and the sky is clear. |
| O11–O18 | — | — | The Rising, the drill, the run, Hullgnaw and going under: the storm variant (§7) and Cinematics. | |
| O19 ◆ | 28 mm (46.4°) | 4.5 m above the water, south-east of the dive raft, looking down 30° | The dive raft from above: the winch, the A-frame and its block over the dark dive well, the ladder going down into turquoise, the tether running down to the tower's pale crown 6 m below; the neighbour raft and the town behind. | The dive mooring over the drowned city: the job, and what it stands on. |
| O20 ◆ | 35 mm (37.8°) | 2.0 m, kit row | Review only: the kit's pieces in two rows on the water, open light. | The kit, side by side. |

**Registered baselines (the repo's binary budget: at most two):** chosen after the preview (§6).

## 5. Review Checklist

- [ ] Reads as a raft culture, not Haluna: no stone, tile or thatch; every roof a hull or planks; everything floats.
- [ ] Paint reads as **faded** (worn edges, laps, five colourways across the town), not as fresh toy colours, and the
      timber is silver-grey, not brown.
- [ ] Nothing emits: every lantern, the lamp racks and the beacon are unlit. No bound light.
- [ ] Every gull faces the sea (south-south-east); the open throat reads at O10.
- [ ] The lashings read as tension (wrapped hard round the stringer ends and cleats), not as loose rings.
- [ ] Act I water: turquoise near, `#0E4A55`-family deep; shadows under the decks teal, not black.
- [ ] Kerrid is not here: no figure, no stranger anywhere in the frames.

## 6. The Preview (M3-ENV-07)

Filled in after the captures.

## 7. Follow-ups

- **The storm variant** (C1-12 to C1-15; act1_ch01 §9 item 1): snapped lashings, separating raft sections, capsized
  hull pieces, the net-pen hull's three-way split (the boss rig), the sea drawn back off the reef. A task of its own,
  as Corrow's fallen state was (M3-ENV-04B).
- **The *Seventh Terrace*** (act1_ch01 §9 item 4): one hero prop for Ch1 (moored, O07, O13) and Ch4 (the derelict),
  the name-board identical in both. A task of its own.
- **The rebuilt variant** (act3_ending E7, `post_credits`): the same moorings rebuilt, not the same hulls.

## Revisions
- 2026-10-24 (env-art, M3-ENV-07): first version, written against the act outline Ch1, the Ch1 beat sheet (C1-07 to
  C1-15, §4, §5, §7, §9 Environment request 1), bible §3 Oruvel, ADR 0017's and ADR 0022's Ch1 watches, the colour
  script's `ch01` row and the sibling oruvel_underway.md (the shared frame, the tether at (−9.9, 5.2), the
  `hull_keels` neighbour raft at (−3, 11)), before any geometry. The layout (seaward edge south, the gulls facing
  south-south-east, the dive raft over the tether, the keel-hull at the town's middle) is this sheet's call.
