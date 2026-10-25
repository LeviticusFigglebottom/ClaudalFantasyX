# The Tamsule Bell, the Tidecup Arena: Design Notes

Owner: Environment Artist (M3-ENV-01). Lighting review: Rendering. The water drop's look: PC GPU (pc-gpu.md).
Story: [act outline Ch7](../../story/beats/act_outline.md), [bible §5.3](../../story/bible.md), [decisions_log N-12](../../story/decisions_log.md) (the arena's construction and rite) and N-20's supersession note (the Ch7 side scene is Tavi's moorings), [ADR 0017](../../decisions/0017-act-one-restaging.md), [ADR 0020](../../decisions/0020-kerrid-restaging.md) (h). Grade target: [color script](../color_script.md) `ch07`. Colours: [palette.json](../palette.json). Format: [haluna.md](haluna.md).
Zone: `game/levels/ch07/tamsule_bell/` (m2-slice or the Ch7 zone track builds it from this kit). Kit: `assets_src/environments/kits/tamsule_bell/`. Preview: `game/levels/_tests/tamsule_bell_kit/`.

**The feeling in one line:** the brightest, most crowded noon in the game, gathered around a held breath of sea that nobody questions, and under it a row of empty posts where a drowned town used to tie up.

**What the place is (story, condensed).** The Tidecup is Reefball's great match, played inside the **Tamsule Bell**: a colossal Lit Age bronze bell with salt-glass panels, **hung mouth-down** from a timber gantry that Tamsule has added to for centuries. Seawater hangs inside the bell's mouth as a slightly flattened drop. It weeps a thin column from its lowest point into a catch-pool where children swim, and players enter by swimming *up* that column. The goal is a ring at the top of the drop, at the surface: a score is *bringing the float up*, because the game began as a drowning-rescue drill (N-12). The water is held by bound glimmer in the bell's ribs, so at rest it is perfectly still. It is beautiful and quietly wrong. The Order "sanctified" it instead of breaking it, and Liss says aloud that it is glimmer-tech; nobody answers. No Order official is in the frame. Toma (who played here for Haluna as a boy) and Asha watch from the galleries. Tavi Orse captains Oruvel's side, names the whole town before the match, and afterwards asks Asha to bless Oruvel's empty moorings under the Bell.

**Influences** (references.md §2, each with its transformation):
- **Burmese and Thai lacquer and gilded signboards** (bible §5.3) → Tamsule's **shop and side boards**: black lacquer boards with gilded borders and *original* abstract glyph strokes (no real script, no religious figure), hung from eaves, gallery facades and boardwalks. Gold stays on the boards, finials and thin bands, as small notes.
- **Stilt-and-boardwalk river towns of the southern coasts** → the **stilt galleries**: raked timber stands on piles in the river, so boats pass and moor *under* and *inside* the ring, and the port's nipa-thatched shophouses on piles.
- **Bronze casting traditions of the south (large temple and ship bells)** → transformed into **one Lit Age object no living foundry could make**: a 36 m bell with a glass waist, worn green as a civic monument, not a temple bell. It is never struck. Its relief bands carry our own rescue-drill motifs: **the hand-line** (a twisted-cord band) and **the float-ring row** (raised rings), never a deity, a script or the Order's Level.
- **Our original:** the **accreted gantry**. Six raking legs, each a bundle of three trunks spliced from lengths of different ages: the oldest at the foot black lacquer, the newest at the top bare sun-silvered timber, red-lacquered repair splints lashed on, bronze straps over the splices. The town's history is the frame that holds the bell.

**IP differentiation (N-12, SPEC §2).** Not a floating orb over an open bowl stadium. Everything here says *bell*: the bronze skirt and sound-bow lip, the hanging yoke and hangers, the drop held in the mouth rather than in empty air, the falling column you swim up, the goal ring at the surface at the *top*, the galleries on piles over the water, and the moored boats underneath. No translucent stadium sphere, no sideways nets, no stadium rim lights.

---

## 0. Layout, Orientation, and Lighting

**Geography (world north = −Z):** Tamsule is a stilt city on a river mouth (bible §5.3). The river runs south to the sea. The Bell stands in the **Bell Reach**, the widest pool of the mouth, about 300 m across, with the city on both banks (west and east) and upstream (north), and the open mouth and the sea to the south. The galleries ring the Bell, open at the **north gap** (the processional boat lane from the city, with two gilded lane boards) and the **south gap** (out to the sea).

**Arena origin and datum.** The arena origin is the **bell axis at the river datum**: `(0, 0, 0)` is mean water level in the Bell Reach, directly under the drop. Every ring piece (bell, goal ring, gantry legs and head, galleries, platforms, pennant lines, catch-pool) is authored with its origin on this axis, built at azimuth 0 (north), so a dresser places it by **rotation about Y only**: a piece at azimuth `a` gets `rotation.y = −a`. Azimuth runs clockwise from north: a point at azimuth `a`, radius `r` is `(r sin a, y, −r cos a)`. Tide: the river mouth is brackish and almost tideless during the Tidecup (the Calm); `tide_line_y = 0.0` and the water stays at 0.0 ± 0.1 m. The weathering algae and wet bands sit on the piles and the pool rim at that line.

**Plan (radii from the axis):**

| Ring | Radius | Height (y) | Contents |
|---|---|---|---|
| Drop (PC GPU) | 0–14.0 m | 20.0–43.0 | The held water; centre at y 31.5 (§1, the contract) |
| Weep column (PC GPU) | 0–0.8 m | 0.35–20.0 | From the drop's lowest point into the catch-pool |
| Catch-pool | 0–12.0 m (wall to 13.2) | coping +0.6, water +0.35, floor −2.2 to −2.5 | Lit Age basin, swimming steps on the south side |
| Moorings | 13–27 m | piles −3.5 to +1.5 | Boats tie up under the Bell; **Oruvel's six posts at r 21, azimuth 19–51°** (north-east), empty |
| Gantry legs | base 29 m, head 15 m | −3.5 to 58.0 | Six legs at azimuth 0, 60 … 300; the collar tie at y 50.5 |
| Captains' platforms | 13–32 m | deck +2.0, prow +2.46 | Two lacquered jetties at azimuth 90 (east) and 270 (west), prows at the pool rim |
| Galleries | 32–41.1 m | walkway +2.4, top tier +10.4, shade-cloths +12.2 to +14.2 | Six 50° segments at azimuth 40, 90, 140 (east) and 220, 270, 320 (west) |
| Pennant lines | 21.9 → 37.2 m | 34.0 → 12.3 | From the legs at azimuth 60, 120, 240, 300 down to the shade-cloths |
| Port edge | 90–135 m | boardwalk +1.6 | Three rows of stilt shophouses and a boardwalk on the east, west and north banks |

**The bell stack:** catch-pool water +0.35 → drop bottom (weep point) +20.0 → bell rim +27.0 → glass waist +30.15 to +41.0 → drop centre +31.5 → drop top (the goal ring) +43.0 → crown ports +44.6 → inner apex +47.4 → outer apex +49.0 → hangers to the gantry head +58.0. The drop's lower 7 m hangs out of the mouth, clear above the galleries' shade-cloths (+14.2), so it reads from the river mouth and from the port.

**GI recommendation:** **SDFGI** in the shipped zone (an open exterior about 300 m across, one lighting state). The preview renders with SDFGI off (sky ambient 0.7 + SSAO), the same lavapipe finding as Haluna (haluna_mood README): Rendering to re-test SDFGI on the GPU runner. A reflection probe under the Bell (box 40 × 28 × 40 m centred at y 12) catches the drop and the pool for the bronze underside.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill | Sea-glow | LUT |
|---|---|---|---|---|---|---|---|
| `ch07` (color script) | **All Ch7 Bell shots**, the match, the side scene | 12:15 | 78° / 180° | `#FFF3E7` (~5,800 K), energy 3.2 | sky `#9ED8EE` at 0.7 | 0 | `lut_ch07_festival`: sat ×1.18 (the game's peak), S-curve 0.45, teal toe `#0E4A55`, highlights roll off to `#FFF8EE`. The kit's preview LUT is generated (`zone_lut.py`); the colour script's hue pushes (boards warm, the drop cyan) are Rendering's when its LUT tool exists |

**Exposure, key product and water** (ADR 0014): exposure 0.65, k = 0.65 × 3.2 = 2.1, so sun-facing surfaces read in the palette's `+1` column. Water look **`lagoon_clear` ×1.5** (σ 3.0 / 0.75 / 0.63 m⁻¹), `col_deep` `#0E4A55`, as the colour script's ch07 row. The river over the 3.5 m silt bed reads lagoon teal; the catch-pool (2.2 m over pale Lit Age ceramic) reads luminous turquoise. Haze: the preview uses depth fog (`#D8ECF2`, density 0.0012, aerial perspective 0.35) for the far banks instead of the frame row's volumetric 0.003, which costs too much on lavapipe; Rendering sets the shipped value.

**Light under the Bell (the zone's value idea).** The sun at 78° from the south throws the bell's 36 m shadow almost straight down, 5.7 m to the north. So the catch-pool and the inner moorings sit in **a disc of shade** in the middle of the brightest frame in the game, lit from above by sunlight *through the drop* (caustic shimmer on the pool, the posts and the bell's underside, once PC GPU's drop casts it) and by the glass waist. That disc is the frame's concentrated dark (references §1.2): the galleries, the gantry and the sky stay high-key around it. Vertical surfaces everywhere are relatively dim at this sun height (the gallery risers are woven light screens for that reason).

**Bound light.** The bell's inner ribs carry thin **`glimmer_bound`** conduits (emission 1.8, the frame row), steady, never flickering, never shedding motes. They show through the glass waist and from below. Measured on the preview (HSV mask): ≤ 0.2 % of the frame in every shot, T05 (the set piece) included, well inside the day limit of 3 %. The drop's own light (if any) is PC GPU's to define with the same rule.

---

## 1. The Water-Drop Contract (agreed volume and anchor, for PC GPU)

The drop's **look** is PC GPU R&D (surface, refraction, caustics, the weep column, the at-rest stillness). Environment builds everything around it and leaves this volume. PC GPU had no Reefball R&D on any branch when this was written (2026-10-24), so these numbers are Environment's proposal and the shared contract until PC GPU answers. To change them, change `bell.py` (`DROP_*`, the bell profiles), this table and the preview together; `tools/tests/test_tamsule_bell_kit.py` and `tests/unit/test_tamsule_bell_kit.gd` check them.

| Item | Value |
|---|---|
| Node | `SphereAnchor` (Marker3D), a direct child of the arena root. Its child `Drop` is the placeholder (`reefball_drop_proxy.glb`, tagged PLACEHOLDER in its glTF extras and the kit manifest), placed with an identity transform; PC GPU replaces `Drop` and keeps the anchor |
| Anchor position | `(0, 31.5, 0)` in arena space: the drop's **centre** |
| Shape | Oblate spheroid (a slightly flattened drop, N-12), **horizontal radius 14.0 m, vertical semi-axis 11.5 m** (ratio 0.82). A small weep cusp at the bottom is the look's to add |
| Lowest point (weep) | `(0, 20.0, 0)`; marker `ColumnAnchor` |
| Top (the surface) | `(0, 43.0, 0)`; marker `GoalRingAnchor`. The bronze goal ring (`goal_ring.glb`, radius 1.6 m, bar 0.12 m) is Environment's and hangs there from the inner apex on three rods |
| Weep column | From the weep point down to the catch-pool water at y +0.35; radius 0.8 m at the top tapering to 0.6 m (a swimmer fits). Its splash lands at the pool centre |
| Clearance | The bell's inner surface stays **≥ 2.0 m** from the drop's surface everywhere above the rim (measured 2.26 m at its closest, at y 33.2). The rim's inner radius is 16.4 m at y 27.0, where the drop is 12.9 m across its radius. No bell vertex lies inside the drop (tested) |
| Air pocket | 4.4 m between the surface (y 43.0) and the inner apex (y 47.4), where the goal ring hangs; lit by the 12 crown ports |
| Visibility | The drop is seen below the rim (its lower 7 m hangs out of the bell), through the 48 glass bays of the waist (y 30.15–41.0), and from directly beneath. Above y 41 the bronze crown hides it |
| Still at rest | Perfectly still, no ripples until bodies move it (bound light, N-12). At the Great Unbinding it falls (a Ch18 revisit shows the empty bell over a full catch-pool) |

---

## 2. Kit Pieces (dimensions in metres; ring pieces have their origin on the arena axis)

Triangle counts are the committed LOD0 / LOD1 (`assets/environments/kits/tamsule_bell/kit_manifest.json`); budgets in brackets.

| Piece | What it is | Key dimensions | Tris (budget) |
|---|---|---|---|
| `tamsule_bell` | The bell: a revolved bronze shell. **Sound bow** (y 27–30.15, solid, 1.8 m thick at the lip) with the hand-line cord band and a row of 36 float-rings in relief; **glass waist** (y 30.15–41): 24 bronze meridian ribs (0.9 m wide, 0.4 m proud), a mid-rail, and 48 salt-glass bays (about 3.3 × 5 m); **shoulder and crown** (y 41–49) solid and flattened like a bell's head, with continued low ribs, a second cord band, 12 bossed crown ports at y 44.6 and 6 crown loops. Bound-light conduits run up every rib's inner face | rim outer r 18.15, inner r 16.4; 22 m tall | 51,328 / 5,360 (60,000 / 6,000) |
| `gantry_leg` | One raking leg: three lashed trunks (0.72 m) from a Lit Age ceramic plinth in the riverbed (r 29) to the head (r 15, y 58), spliced in lengths of different ages, rope lashings every 3.5 m, four red repair splints, bronze straps at the splices, a black band with a thin gilded line at the head; the collar tie (y 50.5) and its knee braces to the next leg clockwise | 63 m long | 4,098 / 726 (14,000 / 1,400) |
| `gantry_head` | The hexagonal head frame at y 58 (r 15) of squared hewn beams, six radial beams to a central bronze **yoke drum** with a red-lacquered cap and a gilded finial, black corner caps with small gilded finials, and six bronze hangers down to the crown loops | 30 m across | 6,484 / 612 (18,000 / 1,800) |
| `goal_ring` | The bronze ring at the drop's surface, hung from the inner apex on three rods | ring r 1.6, rods to y 47.35 | 1,180 / 224 (2,400 / 300) |
| `gallery_segment_a/b/c` | 50° of stilt gallery: piles in the river, a front walkway at y 2.4 with a lacquered rail, red cap rail and gilded finials, 5 bench tiers (rise 1.6, going 1.5) with woven risers and benches, raking under-frame, an outer **boarded screen band** (y 6.8–11.7) with lacquered posts and a gilded board, and three festival shade-cloths on posts. The three variants differ only in their cloth dyes; only `_c` carries the one red cloth | r 32–41.1; y −3.5 to 14.4; inner arc 28 m | 10,997 / 1,329 (36,000 / 3,600) |
| `captain_platform` | A lacquered jetty from the gallery front to the pool rim, a raised prow step (the naming place) with an upswept prow-board like a boat's bow, and a carved float-post carrying a woven float (Reefball's ball) and a small gilded side-board | 19 m long, 3.2 m wide, deck y 2.0 | 4,422 / 98 (9,000 / 900) |
| `pennant_line` | A rope from a gantry leg (r 21.9, y 34) sagging down to a gallery's shade-cloths (r 37.2, y 12.3), with 30 two-sided pennants in the cloth dyes | 21 m | 252 / 164 (1,200 / 200) |
| `catch_pool` | The Lit Age basin: a ring wall of pale ceramic-concrete with a rounded coping and a bronze inlay ring, a dished floor, swimming steps on its south side, 24 bronze mooring rings on its outer face | r 12.0 (outer 13.2); coping y 0.6; floor y −2.2 to −2.5 | 9,384 / 624 (16,000 / 1,600) |
| `mooring_post` | One timber mooring pile with a rope collar | 0.34 × 5.0 (y −3.5 to 1.5) | 408 / 63 (1,200 / 150) |
| `oruvel_moorings` | Oruvel's six posts in a shallow arc, banded sea-blue and bone (Low Reaches colours), their rope ends slack in the water and frayed, an empty name-board peg on the first post, and a string of five wake-shells tied beneath it | arc 12 m | 3,440 / 270 (7,000 / 700) |
| `watch_boat` | A Tamsule river boat: a crescent hull rising at both ends, black lacquer with a red sheer strake, a gilded eye-ring at the bow, thwarts, a woven barrel canopy | 8.0 × 1.9 m | 2,924 / 160 (8,000 / 800) |
| `shophouse_a` / `shophouse_b` | Port-edge stilt shophouses: piles, a shop deck, an open front with propped shutter-boards, a timber upper floor with windows, a **two-tier nipa-thatch hip roof** with flared eaves and a lacquered frieze between the tiers, gilded ridge finials, and a gilded signboard (vertical, hung out from the corner on `a`; horizontal on a balcony rail on `b`) | 8 × 10 and 7 × 9 m, 11–12 m tall | 14,626 / 1,084 and 14,806 / 1,060 (20,000 / 2,000) |
| `boardwalk_8m` | Port-edge boardwalk module on piles, rail on the river side | 8.0 × 3.0 m, deck y 1.6 | 2,400 / 96 (3,000 / 300) |
| `signboard_gilded` | A free gilded side-board on a lacquered post frame with a red cap | 0.9 × 3.2 board, 4.5 m tall | 228 / 48 (1,600 / 200) |
| `reefball_drop_proxy` | **PLACEHOLDER** for PC GPU's drop: the contract spheroid and the column, origin at the drop's centre | §1 | 4,384 / 304 (8,000 / 800) |

**LODs.** Every piece carries `<piece>` and `<piece>-lod1`. The `tamsule_bell_kit` import rules chain them per vegetation.md "One LOD at every distance" (`LodChain`: LOD0 is the visibility child of LOD1, which switches at **120 m** with a 3 m margin and ends at 3,000 m). LOD0 holds longer than Haluna's 70 m because the ring pieces are 30–40 m across and the establishing view is from 150 m.

**Vertex-colour weathering (haluna.md §4 convention: R moss, G salt, B wet, A erosion).** Timber, stone and cloth use the shared weathering shader. The bronze uses the kit's **`game/shaders/environment/env_bronze.gdshader`**, which reads the same channels as bronze phenomena: **G → verdigris and salt bloom** (crevices, undersides, the shaded north side), **A → worn bright bronze** (proud edges: the patina rubbed away on the cord bands, rings and rib arrises), **B → wet streaks** (the lip and the inner face, where the drop's spray runs), **R → grime** (undersides). A world-space vertical streak term draws verdigris runs down the metal.

---

## 3. Materials (palette.json)

| Material | Base | Notes |
|---|---|---|
| `tb_bell_bronze` | worn bronze `#5E4528` (brass darkened), metallic 0.9, rough 0.5 | `bronze_patina` `#5F8A78` verdigris at 55–95 % coverage, `#8DB3A2` pale bloom in crevices, worn edges back to `brass` `#B08D57`. **No gold:** the Bell is old, original glimmer-tech, never Order gold (Liss) |
| `tb_salt_glass` | `salt_glass` `#BFE6E0` at α 0.3, rough 0.05 | Double-sided, slight green. The drop shows through as cyan |
| `tb_port_glass` | deep glass `#2E6E6A`, rough 0.06 | The crown ports |
| `tb_glimmer_conduit` | `glimmer_bound` `#4FB3B0`, emission 1.8 | Steady. Inner rib faces only |
| `tb_lacquer_black` | `lacquer_black` `#1D1916` paint over timber, rough 0.36 | Old gantry lengths, rails, posts, frames; erosion shows grey timber at worn edges |
| `tb_lacquer_red` | `lacquer_red_deep` `#7A1712` paint, rough 0.33 | Repair splints, knee braces, rail caps, the yoke cap. Measured ≤ 0.1 % of any preview frame (budget 8 %) |
| `tb_gold_leaf` | `gold_leaf` `#D4A437`, metallic 1.0, rough 0.28 | Board borders and glyphs, finials, thin bands. Measured ≤ 2.1 % of any preview frame (T08, the board close-up; budget 5 %) |
| `tb_signboard` | `lacquer_black` board, rough 0.24 | The gilded border and glyph strokes are geometry in `tb_gold_leaf` |
| `tb_timber` | `timber_weathered` `#7E6A55`, sun-silvered | Decks, benches, the newest gantry lengths, the gallery screen band |
| `tb_pile_timber` | `timber_weathered` darkened | Piles: algae band at the waterline, barnacles below |
| `tb_lit_ceramic` | `lit_ceramic` `#DCE3E0` over coral-concrete | The catch-pool and the gantry plinths: pale, cool, smooth; algae at the waterline |
| `tb_woven` | woven panel, sun-greyed | Gallery risers, the boat canopy |
| `tb_roof_nipa` | the thatch texture, rain-greyed and darker than Haluna's | Shophouse roofs |
| `tb_cloth_*` | `indigo_dye`, `sea_blue_cloth`, `faded_teal_cloth`, `sand_cloth`, and one `lacquer_red` | Shade-cloths and pennants: festival colour as **many small saturated notes** (references §1.1). One red cloth in the arena (`gallery_segment_c`, placed once) |
| `tb_paint_sea_blue`, `tb_paint_bone` | `sea_blue_cloth` `#3C78A8`, `bone` `#E6DAC0` | Oruvel's mooring bands |
| `tb_rope`, `tb_float_weave`, `tb_wake_shell`, `tb_interior_dark` | lashing fibre `#9C7E5A`; `sand_cloth`; the Haluna wake-shell shader; `#2B2622` | Lashings and ropes; the woven float; Oruvel's wake-shells; dark shop interiors |
| `tb_drop_proxy` | `turquoise_shallow` `#3FD0C9` at α 0.45 | **Placeholder only.** PC GPU replaces it |

The kit adds **no textures**: timber, stone, cloth, thatch and the bronze's detail all use the Haluna kit's procedural texture set (`assets/environments/kits/haluna/textures/`), read-only.

---

## 4. Composed Camera Shots (`ch07`, 12:15)

Conventions as haluna.md §5: full-frame-equivalent lens; Godot `Camera3D.fov` is vertical, vFOV = 2·atan(12 / mm). Positions are in arena space (azimuth, radius, height above the datum). **◆** marks the preview's composed views (`game/levels/_tests/tamsule_bell_kit/`, cameras `Cameras/T01`–`T08`); **★** the two registered baselines.

| # | Lens (vFOV) | Camera | Framing | What the shot is about |
|---|---|---|---|---|
| T01 ◆★ | 24 mm (53.1°) | 2.8 m above the water, 150 m out in the river mouth at azimuth 191°, looking north | The whole Bell right of centre: gantry, the green bell and the drop hanging out of its mouth in the upper-middle band, the pennant lines falling to the galleries, the gallery ring and its shade-cloths as a band across the middle, the port's thatched rows left and right, a watch-boat in the foreground water. Sky 45 %. | A festival held around a held breath of sea. |
| T02 ◆ | 35 mm (37.8°) | West gallery, second tier (azimuth 266°, r 35.9, eye 6.8 m), looking east and up 16° | The drop and the glass waist fill the top half, the column falls to centre, two gantry legs frame it, the east galleries and their shade-cloths make the band across the bottom. | Where Toma and Asha sit. The game he played as a boy. |
| T03 ◆★ | 24 mm (53.1°) | 0.9 m above the water at azimuth 20°, r 28, looking south-west under the Bell | **Tavi's side scene.** Oruvel's empty sea-blue and bone posts across the foreground, receding to the left; the pale catch-pool rim and the column falling into it in the middle ground; the bell's mouth, the drop and the conduits overhead; legs and pennant lines framing; the galleries beyond. | The empty places where Oruvel tied up. |
| T04 ◆ | 35 mm (37.8°) | On the east jetty (azimuth 91°, r 23.5, eye 3.6 m), looking west at the column | The float-post and woven float centre, the upswept prow-boards at the bottom, the column just right of centre falling from the drop, two legs framing the frame symmetrically, the west galleries beyond. A frontal, ritual composition. | Naming the ones who didn't come up. |
| T05 ◆ | 18 mm (67.4°) | 0.85 m above the catch-pool (south steps, r 6), tilted up 58° | The column rising into the drop, the bell's mouth a ring around it, the rib conduits radiating like a wheel, the legs converging. Set piece. | Swim up into it. |
| T06 ◆ | 85 mm (16.1°) | East bank, 12 m up (azimuth 78°, r 95), looking west-up at the head joint | The accreted legs (black old lengths, silvered new ones, rope lashings, red splints), the hewn head frame, the yoke's red cap and gilded finial, the green crown with its ports, against the sky. | Tamsule has added to it for centuries. |
| T07 ◆ | 100 mm (13.7°) | The south-east gallery's top tier at its end (azimuth 165.5°, r 40.5, y 11.6), looking up at the waist | Bronze ribs under verdigris with salt bloom, two salt-glass bays with the drop's water behind them, the conduit lines beyond the glass, the float-ring row along the bottom. | "The Bell is glimmer-tech." Nobody answers. |
| T08 ◆ | 35 mm (37.8°) | 1.6 m on the east boardwalk (azimuth 120°, r 91.5), looking west | A gilded board in the right foreground, the gallery's boarded screen band with its own boards, the bell rising over it. | A hundred languages, one bell. |
| T09 | 65 mm (20.9°) | 1.4 m on the north gallery gap's boat lane, looking south | The column, the drop and, beyond the south gap, the open sea. (Cinematics: the match's last breath.) | — |
| T10 | 24 mm (53.1°) | Underwater, 1 m below the catch-pool surface, looking up | Children's legs in the turquoise pool, the column entering from above. (Underwater stack, Rendering.) | Where children swim. |

---

## 5. Review Checklist for This Zone
- [x] Every preview shot passes a grayscale read: high-key sky, galleries and bronze around the darker legs and the shade under the Bell (lavapipe).
- [x] Gold ≤ 5 % and red ≤ 8 % of every preview frame (measured: gold ≤ 2.1 %, red ≤ 0.1 %).
- [x] No Order symbol, no Order gold, no Order official anywhere in the kit.
- [x] Bound light is steady `glimmer_bound`, ≤ 3 % of the frame (measured ≤ 0.2 %).
- [ ] Shadows teal, not grey, including the disc under the Bell: check on the GPU runner with SDFGI.
- [x] The drop placeholder sits exactly on the §1 contract, and the bell clears it by ≥ 2 m (2.26 m).
- [x] Oruvel's moorings are empty: no boat, no name-board on the peg.

## Revisions
- 2026-10-24 (env-art, M3-ENV-01): first version, then updated to the built kit after the lavapipe iteration: the bell stack rose 6 m (drop centre y 25.5 → 31.5) so the drop's lower part clears the galleries from outside; the galleries went from 7 tiers to 5; the gantry base moved to r 29 (from 27) for clearance and lost its low tie (it crossed every view under the Bell); T02 moved to the second tier, T03 to 24 mm, T04 onto the jetty at 35 mm, T07 to a gallery end (the shade-cloths covered the first positions). The drop contract (§1) is Environment's proposal; PC GPU had no Reefball R&D on any branch at this date.
