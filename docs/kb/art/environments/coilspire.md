# Coilspire, the Headland Temple: Design Notes

Owner: Environment Artist (M3-ENV-10). Lighting: Rendering (the Undertow itself is Rendering's `UndertowStorm`;
Virel at rest is Rendering's and Character's, not the kit's). Gameplay placement (spawns, triggers, the trial's
key logic, collision tuning): m2-slice (swap-in note in the task file).
Story: [act outline Ch8](../../story/beats/act_outline.md) (Asha binds Virel at Coilspire, "open and close the
copper flues so the beacon's fire climbs the spire"; Liss finds the line-marks in the stone; the beacon is
Corrow's whole defence, with the stair), the [Ch8 beat sheet](../../story/beats/act1_ch08.md) B03 to B08 (the
keeper's hut and the keeping flame, the headland path, the four-tier flue trial, tier 3's stuck key and the mark
behind it, the tier-2 side flue and its sealed lamp-niche, the crown chamber open to the sky on the seaward side,
the beacon gallery and the great key, the run back) and its §9 Environment request 3, [bible §5.4](../../story/bible.md)
("a hollow stone spire on the headland where storms always break ... the old copper flues coiled through its walls
still draw the flame"), [ADR 0017](../../decisions/0017-act-one-restaging.md) (c) (nothing bound is used
against the storm: the beacon is fire and copper, nothing else). Grade: [color script `ch08`](../color_script.md)
("Coilspire interior: copper green-cyan"). Colours: [palette.json](../palette.json).
**One building:** Corrow's skyline piece `coilspire_headland` ([corrow.md §2](corrow.md), generator
`assets_src/environments/kits/corrow/cw_far.py`) is this temple seen from 480 m. This kit is that building up
close: the same position, height law, flues, cage and stone (§0 "The far piece, matched").
Zone: `game/levels/ch08/coilspire/`. Kit: `assets_src/environments/kits/coilspire/`. Preview:
`game/levels/_tests/coilspire_kit/`.

**The feeling in one line:** a hot, patient chimney of warm stone on the last rock of the coast, its copper
veins gone sea-green, holding one small fire up against the whole storm.

**Influences** (references.md §2, in words): Khmer laterite (the same porous rust-red blocks as Corrow's wall,
dry-laid in courses); the masonry fire-towers of old coasts, where a beacon basket burned on a tapering stone
tower and a keeper lived at its foot; copper still-houses and organ lofts, where green-patinated pipes run in
long curves along walls and are opened and shut by hand-wheels. **Our originals and transformations:** a
fire-tower → **a chimney you climb**: the fire is not carried up, it is *drawn* up, by three copper flues coiled
round the outside of the spire like vines (bible §5.4), so the building's ornament is its machine;
still-house valves → **flue-keys**: copper hand-wheels on the inner wall where a coil passes behind it, rubbed
bright where nine hundred years of hands have turned them; the Watchers' breaking-wave crown (corrow.md) carved
once, as the lintel over the door, so the temple and the wall share a hand. No real temple's plan or tower
profile is copied.

**Act I rule (references.md "No grimdark desaturation in Act I").** The exterior is the `ch08` storm frame:
warm laterite and green copper against a slate sky. The interior is the copper frame: green-cyan in the shade
(rule 5: teal shadows, never grey), warm where the braziers are. Nothing is desaturated toward mud.

---

## 0. Layout, Orientation, and Lighting

**Geography (world north = −Z, +X east; the Corrow preview's world frame).** The Coilspire headland closes
Corrow's bay at its east horn: a whaleback of dark rock about 260 × 180 m, rising to about +42 m, its cliffs
on the sea side. Corrow places it at world (318, 178) with yaw −30° (`cw_preview_layout.HEADLAND`); in its own
frame (*headland frame*: +Z local is the cliff side, toward the open sea to the south-south-west; −X local
points back west-north-west along the seawall to Corrow) the spire stands at local (−18, −12), on ground at
**+39.29 m**. The seawall runs into the headland's west flank; its walk (+12 m) meets the ground at arc length
s ≈ 266 m (local ≈ (−108, −16)), and that is where the stair-watch's **wall-gate** opens onto the path.

```
                         N (-Z world)                       local frame: -X = WNW (Corrow), +Z = SSW (sea)
         Corrow's seawall (walk +12) ====\\
                                  wall-gate *  (s 266, +12.2)
                                     \  laterite steps, north flank (lee)
                                      \___    ___  crest
                                          \__/   \__  forecourt (+41.3)
                                                    [door NW]  COILSPIRE  (spire 46 m, beacon on top)
                                         keeper's hut (NNE, lee) ┘   crown opening faces SSW (the open sea)
             open sea (storm_grey)                       cliffs to the sea (SSW .. ESE)
                                          the storm front comes in from the SOUTH-EAST
```

- **The approach** (`headland_path`): about 99 m of laterite steps and flags, 2.2 m wide, from the wall-gate
  (+12.0 m, level with the walk) up the headland's lee (north) flank, over the crest and along it to the
  spire's forecourt (+38.9 m): 27 m of climb in about 158 treads (a step at every 0.18 m of rise, long flags on
  the level), cut into the rock where the ground is rough, with wind-bent scrub on both sides and the sea
  audible either way. The path's line and grade are the kit's own (`cs_common.PATH`: a smoothed, never-falling
  version of the rock under it), and the ground is graded to it (`coilspire_ground`).
- **The spire** stands on a small levelled forecourt (radius 9 m). Its **door** faces north-west, back down
  the path toward Corrow (spire angle 195°, §2); the **keeper's hut** leans on its north-north-east flank (in
  the lee), and one copper flue rises out of the hut's roof (the hearth inside feeds it).
- **The crown chamber** opens to the sky on the seaward side, toward the **south-south-west** and the open sea
  (spire angle 92°, between two flues at that height), with the low sun off to its right.
- **The beacon gallery** rings the spire 3.4 m below the top: from it the sea in every direction, Corrow's wall
  curving away to the west, and the storm coming in from the south-east (B07).

**Frames.** *Headland frame*: origin at the headland's centre at the datum (y 0 = mean sea level), the frame
Corrow's `coilspire_headland` is built in. *Spire frame*: origin on the spire's axis at its base ground level
(+39.29 m in the headland frame), axes as the headland's; spire angle α is measured in the local x-z plane
from +X toward +Z (a point on the spire is (r cos α, y, r sin α)), which is also how `cw_far` lays its flues.
Both are placed in the world at the headland's transform (spire pieces at world (308.41, 39.29, 158.61),
yaw −30°).

**The far piece, matched** (`cw_far.py`, read-only; tests compare the two): the outer face follows
`r(y) = 1.9 + 3.6 · (1 − y/46)^1.4` m (5.5 m at the base, 1.9 m at the top, 46 m tall, the footing to −4 m);
three copper flues of 0.3 m radius stand 0.25 m proud of it and coil 1.25 turns each from +3 to +42 m
(α = k·120° + t·450°), their heads turning into the wall just under the gallery; the beacon cage is eight iron bars from r 1.5 m at the top rising 3.2 m and leaning out
to a ring of r 1.8 m, the fire in its middle. The stone is the same laterite (the far piece's jointless carved
slot at 480 m; the courses read here). What the far piece does not show, being under a pixel at 480 m: the
gallery (a 1.1 m balcony), the slits, the hut.

**The section** (spire frame, heights above the base):

| Level | y (m) | Inner radius | What is there |
|---|---|---|---|
| Footing, plinth | −4 … 0.0 | (outer 5.5 → plinth 6.2) | the plinth course, one step up from the forecourt (−0.35 m) |
| **Tier 1**: the base hall | floor 0.0 | 4.4 | the door (NW), the hearth arch (NNE: the keeping flame, shared with the keeper's hut), the tier-1 brazier on a round dais in the middle, the first flight |
| **Tier 2** landing | 9.0 | 3.6 | a D-shaped landing corbelled out of the wall (151° of it), its flue-keys and brazier; the side flue and its sealed lamp-niche |
| **Tier 3** landing | 18.0 | 2.8 | further round; tier 3's seized key (Liss's, the one at 188°) and the mark behind it |
| **Tier 4** landing | 27.0 | 2.2 | further round again; the last keys |
| **Crown chamber** | floor 35.0 | 1.7 | open to the sky on the seaward side (1.6 × 3.2 m, 35.3 … 38.5 m); a grate over the well in the floor; the crown stair spirals round its wall to the gallery door, crossing the opening above its lintel; Virel's chamber; the beacon grate glowing overhead at 45.6 m |
| **Beacon gallery** | 42.6 | (outside) | a ring balcony on twelve corbels, an iron rail, the great flue-key facing the storm (70°); its door at 224° |
| Top, beacon | 46.0 … 49.2 | 1.4 | the rim, the basket and its fire in the iron cage |

The wall thins from 1.1 m at the base to 0.5 m at the top. Each tier's landing covers the circle beyond a chord
(151° of the wall, its chord a quarter of the radius off the axis), so the middle of the spire stays open: the
**well**, and from the base hall you look straight up past every landing to the grate in the crown floor. The stairs are single stone treads
cantilevered from the wall (0.2 m rise, 0.3 m going at their middle, 1.0 m wide below tier 3, 0.85 m above),
climbing along the wall from the end of one landing's arc to the start of the next (`cs_common.plan`: the
first flight leaves the hall beside the door and never crosses the door or the hearth below head height). The draught itself runs in
the copper, not in the hall (beat sheet B05: "the draught that copper flues pull up through the spire's
walls"): each coil passes behind the wall at every tier, and where it does a **flue-key** wheel stands on the
inner wall, with a copper riser up the wall from the key and a feed into that tier's brazier; a landing that
covers only one coil's crossing gets a second key on its brazier's riser. Tier 1's keys tap the roots' ducts
under the hall floor. Copper salts have bloomed through the stone where the coils pass behind it, so the three
flues show inside as green-cyan helices on the walls. Narrow slits light each flight.

**Tide datum:** `tide_line_y = 0.0` (Corrow's). The temple is 41 m above the sea and above all spray; only the
path's foot at the wall-gate (+12 m) is in the salt band's reach.

**GI recommendation:** exterior as Corrow (SDFGI on GPU tiers; sky ambient + SSAO on Low and lavapipe). The
interior: **LightmapGI** on GPU tiers, baked for the trial's states (braziers lit tier by tier) once m2-slice
has the zone; on lavapipe a copper-green ambient + SSAO, the braziers and the sun through the slits.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill | Fog | Exposure | LUT |
|---|---|---|---|---|---|---|---|---|
| `ch08` (color script) | The headland path and the forecourt under the storm (B08's run back; the gallery in B07) | 16:00 | 30° / 250° | `#FFE4CE` (~4,900 K), 2.0 | `#5E6E80` at 0.5 (Corrow's storm sky) | `#5E6670`, volumetric 0.03 (off on lavapipe) | 0.80 | `lut_ch08_storm` (Corrow's) |
| `ch08_coilspire_int` (this kit; the color script names it, no row yet) | The trial (B05), the crown chamber (B06) | as `ch08` outside | the sun through the slits and the crown opening | the braziers, `oil_lamp` `#FFB16E` (~2,900 K) at 2.0 per tier, range 8 m (the hall's 3.2, range 10 m); the keeping flame `#FFB16E` 1.6; the beacon's glow down through its grate 1.4, range 10 m | ambient `#5A7E78` (bronze_patina, lifted) at 2.0: the copper green-cyan | `#24443F`, 0.006 | 1.5 (the sky through the openings at 0.45) | `lut_ch08_coilspire_int`: darks and mids split-toned toward `#3E7468` (0.28), a teal toe `#0E4A55` (0.6), only the bright warm pools (the fire, 10–45° above value 0.3) spared, copper hues kept, saturation ×1.0, S-curve 0.55 |

The beat sheet's `ch08_day` (the noon arrival on the path, B04) is Art and Rendering's new frame and not yet in
the color script: the kit takes any frame, and the preview shows the path in `ch08`, as B08 sees it.

**Exposure, key product and water** (ADR 0014): exterior exposure 0.80, k = 1.6 (Corrow's). The sea is
Corrow's `storm_grey`.

**Value structure.** Exterior: the slate sky is the dark-mid upper half; the sunlit laterite of the spire and
the steps is the brightest large value; the copper coils are a mid green against it, brighter where the sun
catches their tops; the beacon is the hottest point. Interior: a dark green-cyan well; the brightest values are
the braziers and their pools of warm light, the slit shafts, and the beacon grate at the top of the well, so
the eye climbs the spire as the fire does (pillar 4: the trial's goal is always visible).

---

## 1. Mood by Moment

1. **The headland path (B04, B08; F02).** Laterite steps climbing a dark whaleback of rock, scrub flattened
   inland by the wind, the sea loud on both sides; ahead the spire, its copper coils green against the slate
   sky, the beacon a point of fire on top. On the run back, the same steps going down toward the wall.
2. **The keeper's hut (B03; F01).** A rubble lean-to in the spire's lee; inside, Fenn's driftwood basket and the
   hearth arch, the keeping flame burning low in the wall's thickness, visible from the hut and from the hall.
3. **The trial (B05; F03, F04).** A hushed, hot, climbing temple: a round hall, a dais and a brazier, landings
   on alternate sides going up into the dark, copper key-wheels on the walls, slits of storm light, and the
   beacon grate glowing at the very top. Each lit brazier adds a pool of warm light one tier higher.
4. **The crown chamber (B06; F06, F07).** A narrow round room, the stair coiling round it, the whole seaward
   side open to the sky and the sea; the grate overhead glowing.
5. **The gallery (B07; F08, W08).** A ring of stone and an iron rail 84 m above the sea; the beacon roaring
   overhead; the storm wall coming in from the south-east; Corrow's wall curving away west.

---

## 2. Kit Pieces

Origins: headland pieces in the **headland frame** (place them all at the headland's transform), spire pieces
in the **spire frame** (all at the spire's), props at their own base (placed by the layout). +Y up.

| Kit | Pieces | Key dimensions and parameters |
|---|---|---|
| **Ground** | `coilspire_ground` (headland frame) | The headland's own height field (`cw_far.headland_height` with its seed: the same rock as Corrow's far piece), graded to the path (a 2.6 m terrace on its centre line blending out over 4 m, cut banks of rock where the ground stood above it) and to the forecourt (r 9 m, blending out by 15 m). A tensor grid, 1.25 m along the path and round the spire, 13 m at the rim. Rock on the steep faces, wind-burnt turf on the flats (per triangle by slope). |
| **The path** | `headland_path` (headland frame) | Laterite treads on the profile: a tread at every 0.18 m of rise (the going falls where the path is steep), long flags on the level, each tread two or three slabs across 2.2 m; kerb stones on both edges every 0.9 m; dished and worn in the middle. |
| **Scrub** | `scrub_clump_a`, `scrub_clump_b` | Wind-bent shrubs: a few gnarled stems leaning 30–40° to local −Z (inland: the sea wind), a low canopy combed the same way, built of small leaf clusters with gaps between them and bare twig tips through it (M3-ENV-705). 1.6 × 1.0 m and 2.4 × 1.3 m. |
| **The spire** | `coilspire_shell` (spire frame) | The hollow stone body, −4 → +46 m, on the law above: outer face in 0.5 m courses (grooved joints to +8 m), inner face, the top rim; the plinth; openings with stone reveals: the door (195°, 1.7 × 3.0 m) under a carved breaking-wave lintel, the hearth arch (260°, 1.8 × 1.5 m), eight slits (0.35 × 1.4 m) along the flights (each nudged clear of the flues), the crown opening (92°, 1.6 × 3.2 m), the gallery door (224°, 0.9 × 2.0 m); the gallery (r −0.12 … +1.15 m at 42.6 m, twelve corbels at 15 + 30k° so the flues' heads fall between them, an iron rail). The inner face carries the coils' verdigris bloom (VC.G). The crown above the gallery and the inner face above tier 4 are smoke-darkened (`cs_laterite_sooted`). |
| **The flues** | `coilspire_flues` (spire frame) | The three copper coils on the far law, a strap and a collar every 3 m, a stone boot at each root (k 0 and 1 into the plinth; k 2 through the hut's roof), their heads turning into the wall at +42 m, just under the gallery. All copper is verdigris (VC.G high) except where hands go. |
| **The tiers** | `coilspire_tiers` (spire frame) | The base hall's paved floor and dais; three D-landings (0.45 m slabs on corbels, a worn kerb on the well edge); the crown floor (a grate over the well, a notch where flight 4 comes up, clear of the opening); five helical flights (tier to tier and the crown stair); the copper risers on the inner wall (key to key to brazier); the tier-2 side flue and its sealed lamp-niche (a stone press against the wall with a riveted copper door); the beacon grate at 45.6 m. |
| **Flue-keys** | `flue_key` (housing), `flue_key_wheel` | Housing: a copper collar on a stub out of the wall and a damper drum, origin on the wall's face, +Z into the room. Wheel: 0.9 m, six spokes, a rim rubbed bright, origin on its axle, +Z its axis (so m2-slice turns it about local Z). The great key on the gallery is the same pair at 1.6 ×. |
| **Braziers** | `tier_brazier` | A wrought-iron tripod (0.9 m) holding a copper bowl (0.8 m) with a bed of embers (emissive `ember_orange`, low: the flame itself is VFX). |
| **The beacon** | `beacon_basket` (spire frame, origin at the top centre, +46 m) | The iron cage on the far law (eight bars, the ring) and inside it a deep iron basket on the rim with a bed of coals and the fire core (emissive `ember_orange`, the far piece's). |
| **The keeper's hut** | `keepers_hut` (spire frame) | A lean-to of small coursed stones (`cs_rubble`) on the spire's lee flank (centred on 260°, 6.0 m along the wall, 3.4 m deep), a laterite slab roof falling away from the spire (3.4 → 2.3 m), a plank door and a shuttered window toward the path, inside the hearth arch's mouth with its ember bed, a driftwood basket, a stool. |

**Budgets (triangles, LOD0 / LOD1):** ground 18,000 / 2,000; path 16,000 / 900; scrub 2,000 / 160 each; shell
40,000 / 2,000; flues 14,000 / 900; tiers 30,000 / 1,600; key housing 2,500 / 200; key wheel 2,500 / 160;
brazier 3,000 / 200; beacon 5,000 / 400; hut 12,000 / 700. LOD1 begins at 70 m and every piece is a chain
(`<piece>`, `<piece>-lod1`) per vegetation.md "One LOD at every distance".

## 3. Materials (palette.json names)

| Slot | Shader | Look |
|---|---|---|
| `cs_laterite` | weathering (Corrow's `laterite_blocks` by mesh UV in metres) | the spire's coursed outer face: `laterite` `#A8573A`, the same dry-laid blocks as the wall, salt-dulled and wind-scoured (no sea salt band this high, a little lichen on the lee) |
| `cs_laterite_inner` | weathering (`laterite_blocks`) | the inner face: the same blocks, dry, dulled by smoke; its salt layer is copper salts (`#6E9E8E`), bloomed in the joints along the coils' paths behind the wall |
| `cs_laterite_sooted` | weathering (`laterite_blocks`) | the crown above the gallery outside and the inner face above tier 4: nine hundred years of beacon smoke, laterite darkened toward `lacquer_black` warmed, never black |
| `cs_laterite_carved` | weathering (Corrow's jointless `laterite`) | the lintel, corbels, dais, reveals, stair treads, path treads and kerbs: paler where worn (VC.A) |
| `cs_paving` | weathering (`laterite`, larger tile) | the hall floor and the landings: worn smooth by feet, dusty with soot |
| `cs_copper` | bronze (the Tamsule Bell's `env_bronze.gdshader`, Haluna detail maps; no new map) | the flues, risers, keys and brazier bowls: `bronze_patina` `#5F8A78` verdigris (VC.G) over dark copper, worn bright where VC.A says, rain-streaked; always mostly green (half-and-half reads as camouflage) |
| `cs_copper_worn` | standard (metallic) | the key wheels' rims and spokes and the grate's rim where hands go: copper toward `brass`, rubbed bright |
| `cs_iron` | standard | brazier tripods, the cage, the rail, the basket: dark wrought iron, heat-blued near the fire |
| `cs_ember` | standard, emissive | the braziers' and the hearth's embers: `ember_orange` at emission 2.5 (low: a bed, not a flame) |
| `cs_beacon` | standard, emissive | the beacon fire: `ember_orange` at 6, as the far piece's `cw_beacon` |
| `cs_rock` | weathering (Haluna `coral_stone`, darkened) | the headland's rock: `volcanic_stone` toward `cold_blue_stone`, the far piece's `cw_headland` at a closer tile |
| `cs_turf` | weathering (Brine Shoals `mud`, tinted) | wind-burnt turf on the crest: `saltgrass` dulled toward olive, brown in the hollows |
| `cs_scrub` | weathering (Haluna `canopy_cluster`, tinted) | the scrub's canopy: `foliage_shadow` toward `palm_green`, salt-burnt on the windward side |
| `cs_rubble` | weathering (`laterite_blocks` at half size) | the keeper's hut: small roughly coursed stones, old lime-wash gone grey in patches |
| `cs_timber` | weathering (Haluna `timber`) | the hut's door, lintel, the scrub's stems: `timber_weathered` |
| `cs_interior_dark` | standard | the hut's interior beyond the door: `#2A2622` |

Weathering channels follow haluna.md §4 (**R moss, G salt, B wet, A erosion**).

---

## 4. Composed Shots (vFOV = 2·atan(12 / mm); heights above the local ground or floor)

**◆** marks the preview views built in `coilspire_kit/`. Beat-sheet ids in brackets.

| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| K01 ◆ [F02] | 28 mm (46.4°) | 1.6 m on the path half-way up (s 50 m), looking up it to the south-east | The steps climbing away between scrub, the spire on the crest at the right third, its coils side-lit by the WSW sun against the slate storm, the beacon burning on top. Sky ≈ 55%. | The pilgrimage's last climb to the edge of the land. |
| K02 ◆ [F01] | 35 mm (37.8°) | 1.6 m on the forecourt, NW of the door | The door under its wave lintel, the keeper's hut leaning in the lee to the left, the copper flue climbing out of its roof and round the spire. | The keeper's door and the fire's root. |
| K03 ◆ [F03] | 18 mm (67.4°) | 1.3 m in the base hall beside the dais, looking straight up the well | The landings and the stair spiralling up into teal dark, the risers green on the walls and the copper bloom on the stone, the grate glowing at the top of the well. | The trial at a glance (pillar 4): the goal is always in view. |
| K04 ◆ [F04] | 50 mm (27.0°) | 1.5 m on the tier-3 landing | A flue-key on the inner wall at chest height, the riser running up from it, the brazier's warm light from the side. | Fire obeying a patient hand. |
| K05 ◆ [F06] | 24 mm (53.1°) | 1.6 m on the crown stair's tenth tread (where the others wait), looking down and out of the crown opening | The opening's stone reveals framing the storm sea and the headland's cliffs; the stair's treads coiling up the wall at the right of frame. | Where Virel waits, open to the sea. |
| K06 ◆ [F08] | 24 mm (53.1°) | 1.6 m on the gallery's south side, looking along it to the south-east | The spire's wall on the left, the great key and the rail curving away, the sea and the storm beyond. | "It is wider than the sky." |
| K07 ◆ [W08] | 135 mm (10.2°) | 1.6 m on the gallery, looking west-north-west | Corrow's seawall and its low town under the storm (Corrow's kit as the backdrop). | What the beacon is for. |
| K08 ◆ (review) | 28 mm (46.4°) | Corrow's C01 camera | The temple from Corrow's wall: the near kit standing where the far piece stands. | One building (the match check). |
| K09 | 50 mm (27.0°) | 1.2 m in the hut | Fenn at the hearth arch, the keeping flame. (Cinematics.) | "Fires don't carry tales. I do." |

**Registered baselines (at most two):** K01 and K03 (§6).

## 5. Review Checklist

- [x] The near temple and Corrow's far piece are one building: position, height, taper, flues and cage (K08 and
      `tools/tests/test_coilspire_kit.py`).
- [x] Exterior grayscale: the sunlit laterite is the brightest large value against the slate sky; the beacon
      the hottest point.
- [ ] Interior: green-cyan shade, never grey (rule 5); warm only at the braziers, the hearth, the slits and the
      grate; the grate is visible from the base hall (K03).
- [ ] The laterite stays warm (hue 10–40°) outside; the copper stays green-cyan, not blue and not olive.
- [x] Nothing glows that is bound: the only emissives are embers and the beacon fire (ADR 0017 (c)).
- [x] Red ≤ 8%, gold 0%.

## 6. The Preview (M3-ENV-10)

`game/levels/_tests/coilspire_kit/coilspire_preview.tscn` composes the kit in Corrow's world frame (its README lists
the files): the graded headland, the path and 70 scrub clumps, the spire with its flues, tiers, beacon and hut,
ten flue-keys and the great key, four braziers; and, as a second dresser, Corrow's kit as Corrow's preview places it
(without its far headland), so the gallery looks back at the real wall. The rig's two phases are `ch08` (outside)
and `ch08_coilspire_int`. Triangles, LOD0 / LOD1: shell 35,930 / 712; flues 12,228 / 840; tiers 14,374 / 632;
ground 13,216 / 1,536; path 6,684 / 66; hut 1,594 / 36; beacon 1,936 / 392; brazier 820 / 168; key 260 / 72;
wheel 936 / 156; scrub 848 / 24 each. Kit on disk 4.4 MB in 26 files, the largest 1.2 MB.

Read of the final captures (lavapipe, 960 × 540):
- **K01** (baseline `coilspire_k01_headland_path`): the strongest exterior: the laterite steps climbing the dark
  whaleback to the spire, the three green coils winding up it side-lit by the WSW sun, the beacon cage burning on
  top against the slate storm. Weak: the treads still read a touch orange and regular, the scrub is simple lumps,
  the far rock is coarse (the far piece's resolution away from the path).
- **K03** (baseline `coilspire_k03_well`): the interior at a glance: the spiral of treads and alternate landings
  climbing into teal dark, the copper risers and the coils' green bloom on warm stone, the grate a warm point at the
  top of the well. It carries pillar 4 (the goal in view) and pillar 2.
- **K02** the door under its wave lintel with the brazier glowing inside, the hut of small stones, a flue rising
  out of its roof; **K04** a flue-key close (the bright rim on green copper); **K05** the crown opening from the
  crown stair, the sea far below; **K06** the gallery: wall, great key, rail and the storm sea (a strong frame
  too); **K07** Corrow's wall and low town under a heavy warm haze (Corrow's environment and plain inland apron:
  the weakest view); **K08** the match check: from Corrow's C01 camera the near temple stands exactly where the
  far piece stands, the same size and taper, the coils now visible.
- Known limits: the interior is lit by an ambient fill and the braziers on lavapipe (no GI), so the slits' light
  shafts barely read; Virel, the flames and the beacon's roar are VFX and not in the kit; Liss's mark behind the
  tier-3 key is a decal for m2-slice / VFX (the kit leaves the stone plain there); the hut's interior is minimal;
  the path's treads are blocks with a worn top, not dished.

## Revisions
- 2026-10-24 (env-art, M3-ENV-10): first version, written against the act outline Ch8, the Ch8 beat sheet
  (B03 to B08, §7 F-shots, §9 request 3), bible §5.4, the colour script `ch08` row and corrow.md (the far
  piece's generator `cw_far.py` read for its dimensions), before any geometry.
- 2026-10-24 (env-art, M3-ENV-10, after the preview): the spire's base is at +39.29 m (the first version misread
  it); the far coils run from +3 to **+42 m** (cw_far's y = 3 + t (H − 7)), so their heads turn into the wall
  under the gallery, the gallery has twelve corbels set between them, and the crown opening moved from 130° (WSW)
  to **92° (SSW, the open sea)**, the only gap between two flues at that height; the landings cover 151°, not
  220°, so the middle of the well is open and the grate shows from the hall (a 220° D covered the axis); the crown
  stair climbs from 60° and crosses the opening above its lintel, flight 1 starts at 160°; tier 1's second key
  moved to 88° (clear of flight 1); the great key faces the storm at 70°; the copper is the Tamsule Bell's
  `env_bronze` (no new map) and always mostly verdigris; the inner face carries the coils' copper bloom; the hut
  is `cs_rubble` (the blocks at half size); the interior frame's values are the ones that read on lavapipe
  (ambient `#5A7E78` 2.0, exposure 1.5, the LUT's split tone 0.28 with a 0.6 teal toe); K05 is taken from the
  crown stair.
