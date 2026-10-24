# The Tamsule Bell, the Tidecup Arena: Design Notes

Owner: Environment Artist (M3-ENV-01). Lighting review: Rendering. The water drop's look: PC GPU (pc-gpu.md).
Story: [act outline Ch7](../../story/beats/act_outline.md), [bible §5.3](../../story/bible.md), [decisions_log N-12](../../story/decisions_log.md) (the arena's construction and rite) and N-20's supersession note (the Ch7 side scene is Tavi's moorings), [ADR 0017](../../decisions/0017-act-one-restaging.md), [ADR 0020](../../decisions/0020-kerrid-restaging.md) (h). Grade target: [color script](../color_script.md) `ch07`. Colours: [palette.json](../palette.json). Format: [haluna.md](haluna.md).
Zone: `game/levels/ch07/tamsule_bell/` (m2-slice or the Ch7 zone track builds it from this kit). Kit: `assets_src/environments/kits/tamsule_bell/`. Preview: `game/levels/_tests/tamsule_bell_kit/`.

**The feeling in one line:** the brightest, most crowded noon in the game, gathered around a held breath of sea that nobody questions, and under it a row of empty posts where a drowned town used to tie up.

**What the place is (story, condensed).** The Tidecup is Reefball's great match, played inside the **Tamsule Bell**: a colossal Lit Age bronze bell with salt-glass panels, **hung mouth-down** from a timber gantry that Tamsule has added to for centuries. Seawater hangs inside the bell's mouth as a slightly flattened drop. It weeps a thin column from its lowest point into a catch-pool where children swim, and players enter by swimming *up* that column. The goal is a ring at the top of the drop, at the surface: a score is *bringing the float up*, because the game began as a drowning-rescue drill (N-12). The water is held by bound glimmer in the bell's ribs, so at rest it is perfectly still. It is beautiful and quietly wrong. The Order "sanctified" it instead of breaking it, and Liss says aloud that it is glimmer-tech; nobody answers. No Order official is in the frame. Toma (who played here for Haluna as a boy) and Asha watch from the galleries. Tavi Orse captains Oruvel's side, names the whole town before the match, and afterwards asks Asha to bless Oruvel's empty moorings under the Bell.

**Influences** (references.md §2, each with its transformation):
- **Burmese and Thai lacquer and gilded signboards** (bible §5.3) → Tamsule's **shop and side boards**: black lacquer boards with gilded borders and *original* abstract glyph strokes (no real script, no religious figure), hung vertically from eaves and gallery ends. Gold stays on the boards and finials only, as small notes.
- **Stilt-and-boardwalk river towns of the southern coasts** → the **stilt galleries**: raked timber stands on piles in the river, so boats pass and moor *under* the spectators.
- **Bronze casting traditions of the south (large temple and ship bells)** → transformed into **one Lit Age object no living foundry could make**: a 36 m bell with a glass waist, worn as a civic monument, not a temple bell. It is never struck. Its relief bands carry our own rescue-drill motifs: **the hand-line** (a twisted-cord band) and **the float-ring row** (raised rings), never a deity, a script or the Order's Level.
- **Our original:** the **accreted gantry**. Six raking legs, each a bundle of trunks of different ages: the oldest at the bottom black and crazed, newer splints and braces lashed on above in redder lacquer, every repair left visible. The town's history is the frame that holds the bell.

**IP differentiation (N-12, SPEC §2).** Not a floating orb over an open bowl stadium. Everything here says *bell*: the bronze skirt and sound-bow lip, the hanging yoke and chains, the drop held in the mouth rather than in empty air, the falling column you swim up, the goal ring at the surface at the *top*, the galleries on piles over the water, and the moored boats underneath. No translucent stadium sphere, no sideways nets, no glowing stadium rim lights.

---

## 0. Layout, Orientation, and Lighting

**Geography (world north = −Z):** Tamsule is a stilt city on a river mouth (bible §5.3). The river runs south to the sea. The Bell stands in the **Bell Reach**, the widest pool of the mouth, about 300 m across, with the city on both banks (west and east) and upstream (north), and the open mouth and the sea to the south. The galleries ring the Bell, open at the **north gap** (the processional boat lane from the city) and the **south gap** (out to the sea).

**Arena origin and datum.** The arena origin is the **bell axis at the river datum**: `(0, 0, 0)` is mean water level in the Bell Reach, directly under the drop. Every ring piece (bell, gantry legs, galleries, platforms, catch-pool) is authored with its origin on this axis, built at azimuth 0 (north), so a dresser places it by **rotation about Y only**. Azimuth runs clockwise from north: a point at azimuth `a`, radius `r` is `(r sin a, y, −r cos a)`. Tide: the river mouth is brackish and almost tideless during the Tidecup (the Calm); `tide_line_y = 0.0` and the water stays at 0.0 ± 0.1 m. The weathering algae and wet bands sit on the piles and the pool rim at that line.

**Plan (radii from the axis):**

| Ring | Radius | Height (y) | Contents |
|---|---|---|---|
| Drop (PC GPU) | 0–14.0 m | 14.0–37.0 | The held water; centre at y 25.5 (§1, the contract) |
| Weep column (PC GPU) | 0–0.8 m | 0.35–14.0 | From the drop's lowest point into the catch-pool |
| Catch-pool | 0–12.0 m | rim +0.6, water +0.35, floor −2.2 | Lit Age basin, children's swimming steps on the south side |
| Moorings | 13–27 m | piles −3.5 to +1.4 | Boats tie up under the Bell; **Oruvel's posts at azimuth 30–50°** (north-east), empty |
| Gantry legs | base 27 m, head 14 m | −3.5 to 52.0 | Six legs at azimuth 0, 60 … 300 |
| Captains' platforms | 13–30 m | deck +2.0 | Two lacquered jetties at azimuth 90 (east) and 270 (west), prows at the pool rim |
| Galleries | 30–42 m | deck +2.4, top tier +13.6, canopies to +17.5 | Six 50° segments: azimuth 15–165 (east) and 195–345 (west) |
| Port edge | 70–140 m | boardwalk +1.6 | Stilt shophouses and boardwalks on the east, west and north banks |

**The bell stack:** catch-pool water +0.35 → drop bottom (weep point) +14.0 → bell rim +21.0 → drop centre +25.5 → glass waist +24 to +35 → drop top (the goal ring) +37.0 → crown ports +39.5 → inner apex +42.7 → outer apex +44.9 → yoke and hangers to the gantry head +52.0.

**GI recommendation:** **SDFGI** in the shipped zone (an open exterior about 300 m across, one lighting state). The preview renders with SDFGI off (sky ambient + SSAO), the same lavapipe finding as Haluna (haluna_mood README): Rendering to re-test SDFGI on the GPU runner. A reflection probe under the Bell (box 40 × 22 × 40 m centred at y 8) catches the drop and the pool for the bronze underside.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill | Sea-glow | LUT |
|---|---|---|---|---|---|---|---|
| `ch07` (color script) | **All Ch7 Bell shots**, the match, the side scene | 12:15 | 78° / 180° | `#FFF3E7` (~5,800 K), energy 3.2 | sky `#9ED8EE` at 0.7 | 0 | `lut_ch07_festival`: sat ×1.18 (the game's peak), S-curve 0.45, teal toe `#0E4A55`, highlights roll off to `#FFF8EE`; gilded boards pushed warm, the drop pushed cyan; caustics under the Bell may clip to white |

**Exposure, key product and water** (ADR 0014): exposure 0.65, k = 0.65 × 3.2 = 2.1, so sun-facing surfaces read in the palette's `+1` column. Water look **`lagoon_clear` ×1.5** (σ 3.0 / 0.75 / 0.63 m⁻¹), `col_deep` `#0E4A55`, as the colour script's ch07 row. The river over the 3.5 m silt bed reads lagoon teal; the catch-pool (2.2 m over pale Lit Age ceramic) reads luminous turquoise. Fog: albedo `#D8ECF2`, volumetric density 0.003 (the frame row) for the far banks' aerial perspective.

**Light under the Bell (the zone's value idea).** The sun at 78° from the south throws the bell's 36 m shadow almost straight down, 4.5 m to the north. So the catch-pool, the moorings and the platforms' prows sit in **a disc of shade** in the middle of the brightest frame in the game, lit from above by sunlight *through the drop* (caustic shimmer on the pool, the posts and the bell's underside) and by the glass waist glowing. That disc is the frame's concentrated dark (references §1.2): the galleries, the gantry and the sky stay high-key around it. Tavi's side scene happens in that shade.

**Bound light.** The bell's inner ribs carry thin **`glimmer_bound`** conduits (emission 1.8, the frame row), steady, never flickering, never shedding motes. They show through the glass waist and at the rim from below. They must stay under the day glimmer limit (3 % of frame) except in the column shot T05, which is the set piece (≤ 35 %). The drop's own light (if any) is PC GPU's to define with the same rule.

---

## 1. The Water-Drop Contract (agreed volume and anchor, for PC GPU)

The drop's **look** is PC GPU R&D (surface, refraction, caustics, the weep column, the at-rest stillness). Environment builds everything around it and leaves this volume. These numbers are the shared contract: if PC GPU needs a different size, change them here and in pc-gpu.md together, and the kit's clearance test (`tools/tests/test_tamsule_bell_kit.py`) moves with them.

| Item | Value |
|---|---|
| Node | `SphereAnchor` (Marker3D) in the zone, a direct child of the arena root. Its child `Drop` is the placeholder (`reefball_drop_proxy`, tagged PLACEHOLDER); PC GPU replaces `Drop` and keeps the anchor |
| Anchor position | `(0, 25.5, 0)` in arena space: the drop's **centre** |
| Shape | Oblate spheroid (a slightly flattened drop, N-12), **horizontal radius 14.0 m, vertical semi-axis 11.5 m** (ratio 0.82). A small weep cusp at the bottom is the look's to add |
| Lowest point (weep) | `(0, 14.0, 0)`; marker `ColumnAnchor` |
| Top (the surface) | `(0, 37.0, 0)`; marker `GoalRingAnchor`. The bronze goal ring (`goal_ring`, radius 1.6 m, bar 0.12 m) is Environment's and hangs here from the crown on three rods |
| Weep column | From the weep point to the catch-pool water at y +0.35; radius 0.8 m at the top tapering to 0.6 m (a swimmer fits). Its splash ring lands at the pool centre |
| Clearance | The bell's inner surface stays **≥ 2.0 m** from the drop's surface everywhere above the rim (closest: 2.0 m at y 26). The rim's inner radius is 16.4 m at y 21.0, where the drop is 12.9 m |
| Visibility | The drop is seen: below the rim (its lower 7 m hangs out of the bell), through the 48 glass bays of the waist (y 24–35), and from directly beneath. Above y 35 the bronze crown hides it, except through the 12 crown ports (an air pocket 2–5 m deep lies between the surface and the inner apex) |
| Still at rest | Perfectly still, no ripples until bodies move it (bound light, N-12). At the Great Unbinding it falls (a Ch18 revisit shows the empty bell over a full catch-pool) |

---

## 2. Kit Pieces (dimensions in metres; ring pieces have their origin on the arena axis)

| Piece | What it is | Key dimensions | Budget (LOD0 / LOD1 tris) |
|---|---|---|---|
| `tamsule_bell` | The bell: a revolved bronze shell. **Sound bow** (y 21–24, solid, 1.8 m thick at the lip) with the hand-line cord band and the float-ring row in relief; **glass waist** (y 24–35): 24 bronze meridian ribs (0.9 m wide, 0.4 m proud), a mid-rail at y 29.5, and 48 salt-glass bays (about 3.3 × 5.2 m); **shoulder and crown** (y 35–44.9) solid, with 12 bossed crown ports at y 39.5 and 6 crown loops on top. Bound-light conduits run up the inner face of every rib | rim outer r 18.0, inner r 16.4; height 23.9 | 60,000 / 6,000 |
| `gantry_leg` | One raking leg: three lashed trunks (0.7–0.9 m) from the riverbed at r 27 to the head at r 14, y 52, with braces, splints and rope lashings of different ages; black lacquer below, redder above, gilded caps on the head joint | 56 m long, 9° rake | 14,000 / 1,400 |
| `gantry_head` | The hexagonal head ring at y 52 (r 14), six radial beams to a central bronze **yoke**, and six bronze hanger bars down to the bell's crown loops | 30 m across | 18,000 / 1,800 |
| `goal_ring` | The bronze ring at the drop's surface, hung from the crown on three rods | ring r 1.6, rods to y 42.7 | 2,400 / 300 |
| `gallery_segment` | 50° of stilt gallery: piles in the river, a front walkway at y 2.4 with a lacquered rail and gilded finials, 7 bench tiers (rise 1.6, going 1.6), raking under-frame, woven back screen, and three festival shade-cloths on posts | r 30–42; y −3.5 to 17.5; inner arc 26 m | 36,000 / 3,600 |
| `captain_platform` | A lacquered jetty from the gallery front to the pool rim, ending in a raised prow step where the captain stands to name the drowned, and a carved post carrying a woven float (Reefball's ball) | 17 m long, 3.2 m wide, deck y 2.0 | 9,000 / 900 |
| `catch_pool` | The Lit Age basin: a ring wall of pale ceramic-concrete, a dished floor, and swimming steps on its south side | r 12.0 (outer 13.2); rim y 0.6; floor y −2.2 | 16,000 / 1,600 |
| `mooring_post` | One timber mooring pile with a rope collar | 0.35 × 5.0 (y −3.5 to 1.5) | 1,200 / 150 |
| `oruvel_moorings` | Oruvel's six posts in an arc, banded sea-blue and bone (Low Reaches colours), their rope ends slack in the water, an empty name-board peg, and one wake-shell string tied to the first post | arc 12 m | 7,000 / 700 |
| `watch_boat` | A Tamsule river boat: a crescent hull with a lacquered eye-ring at the bow and a woven barrel canopy | 8.0 × 1.9 m | 8,000 / 800 |
| `shophouse_a` / `shophouse_b` | Port-edge stilt shophouses: piles, a deck, an open front with shutters, a timber and woven upper floor, a **two-tier hip roof** with flared eaves, and a gilded signboard (vertical on `a`, horizontal over a balcony on `b`) | 8 × 10 m footprint, 11–12 m tall | 16,000 / 1,600 |
| `boardwalk_8m` | Port-edge boardwalk module on piles | 8.0 × 3.0 m, deck y 1.6 | 3,000 / 300 |
| `signboard_gilded` | A free gilded side-board for gallery ends and boat lanes | 0.9 × 3.2 m | 1,600 / 200 |
| `reefball_drop_proxy` | **PLACEHOLDER** for PC GPU's drop: the contract spheroid and the column, so compositions can be judged. Tagged in the glTF extras and the kit manifest | §1 | 8,000 / 800 |

**Vertex-colour weathering (haluna.md §4 convention: R moss, G salt, B wet, A erosion).** Timber and stone use the shared weathering shader. The bronze uses the kit's **`env_bronze.gdshader`**, which reads the same channels as bronze phenomena: **G → verdigris and salt bloom** (crevices, under ledges, the shaded north side), **A → worn bright bronze** (proud edges, the rim lip, rope-worn crown loops), **B → wet streaks** (below the lip and under the rim, where the drop's spray runs), **R → grime** (the underside). A world-space vertical streak term draws verdigris runs down from every horizontal ledge.

---

## 3. Materials (palette.json)

| Material | Base | Notes |
|---|---|---|
| `tb_bell_bronze` | worn bronze from `brass` `#B08D57` darkened to `#7A5C38`, metallic 0.9, rough 0.42 | `bronze_patina` `#5F8A78` verdigris at 35–70 % coverage on the shell, `#8DB3A2` pale bloom in crevices, worn edges back to `brass`. **No gold:** the Bell is old, original glimmer-tech, never Order gold (Liss) |
| `tb_salt_glass` | `salt_glass` `#BFE6E0` at α 0.35, rough 0.05 | Double-sided, slight green. The drop shows through as cyan |
| `tb_glimmer_conduit` | `glimmer_bound` `#4FB3B0`, emission 1.8 | Steady. Inner rib faces only |
| `tb_lacquer_black` | `lacquer_black` `#1D1916` paint over timber, rough 0.35 | The old gantry and gallery frames; erosion shows grey timber at worn edges |
| `tb_lacquer_red` | `lacquer_red_deep` `#7A1712` paint, rough 0.32 | Newer gantry splints, rail caps. **≤ 8 % of any frame** (it is a sign of repair, not a surface) |
| `tb_gold_leaf` | `gold_leaf` `#D4A437`, metallic 1.0, rough 0.28 | Board borders and glyphs, finials, the gantry's head caps. **≤ 5 % of any frame** |
| `tb_signboard` | `lacquer_black` board | The gilded border and glyph strokes are geometry in `tb_gold_leaf` |
| `tb_timber` | `timber_weathered` `#7E6A55` | Sun-silvered piles, decks, benches (Haluna's timber texture) |
| `tb_pile_timber` | `timber_weathered` darkened | Piles: algae band at the waterline, barnacles below |
| `tb_lit_ceramic` | `lit_ceramic` `#DCE3E0` over coral-concrete | The catch-pool: pale, cool, smooth from a thousand years of swimmers; algae at the waterline |
| `tb_woven` | woven panel, sun-greyed | Gallery back screens, the boat canopy |
| `tb_roof_shingle` | roof tile texture tinted `laterite` `#A8573A` → darker | Shophouse roofs (a port town's, darker and browner than Haluna's red) |
| `tb_cloth_*` | `indigo_dye`, `sea_blue_cloth`, `faded_teal_cloth`, `sand_cloth`, and one `lacquer_red` | Gallery shade-cloths: festival colour as **many small saturated notes** (references §1.1). At most one red cloth in view |
| `tb_paint_sea_blue`, `tb_paint_bone` | `sea_blue_cloth` `#3C78A8`, `bone` `#E6DAC0` | Oruvel's mooring bands |
| `tb_rope` | lashing fibre `#9C7E5A` | Lashings, mooring ropes |
| `tb_float_weave` | `sand_cloth` `#C9B48E` | The woven Reefball float on the captains' posts |
| `tb_drop_proxy` | `turquoise_shallow` `#3FD0C9` at α 0.45 | **Placeholder only.** PC GPU replaces it |

---

## 4. Composed Camera Shots (`ch07`, 12:15)

Conventions as haluna.md §5: full-frame-equivalent lens; Godot `Camera3D.fov` is vertical, vFOV = 2·atan(12 / mm). Positions are in arena space. **◆** marks the preview's composed views; **★** the two registered baselines.

| # | Lens (vFOV) | Camera | Framing | What the shot is about |
|---|---|---|---|---|
| T01 ◆★ | 24 mm (53.1°) | 4 m above the water, 150 m south-south-west in the river mouth, looking north-north-east | The whole Bell: gantry and bell in the upper-middle third, the drop hanging out of the mouth catching the sun, the gallery ring as a band across the lower third with its shade-cloths, the port-edge roofs left and right, a watch-boat in the foreground water. Sky 40 %. | A festival held around a held breath of sea. |
| T02 ◆ | 35 mm (37.8°) | West gallery, top tier (y 14.8 eye), looking east and up 18° | Shade-cloth edge across the top of frame, the benches falling away in the lower third, the drop centre frame with the glass waist above it, the east gallery across the water as a crowded band. | Where Toma and Asha sit. The game he played as a boy. |
| T03 ◆★ | 28 mm (46.4°) | 1.5 m above the water on Oruvel's moorings (azimuth 40°, r 20), looking south-west toward the axis | **Tavi's side scene.** The empty sea-blue and bone posts lead from frame-left into the shade under the Bell; the catch-pool rim and the column in the middle ground; the bell's dark mouth and the glowing drop fill the top of frame; the sunlit galleries beyond. | The empty places where Oruvel tied up. |
| T04 ◆ | 50 mm (27.0°) | 1.2 m above the water at the pool rim (azimuth 140°, r 14), looking west-north-west along the east platform | The east captain's prow and float-post in the left third, the column a vertical in the right third, the drop above, the west platform beyond. | Naming the ones who didn't come up. |
| T05 ◆ | 18 mm (67.4°) | 0.5 m above the catch-pool water (south steps, r 6), tilted up 58° | The column rising from the pool into the drop, the bell's mouth a ring around it, the rib conduits and the glass bays glowing. Set piece: glimmer ≤ 35 %. | Swim up into it. |
| T06 ◆ | 85 mm (16.1°) | East bank, 12 m up a shophouse balcony (r 95), looking west-up at the north-east leg's head joint | The accreted leg: black old trunks, red newer splints, rope lashings, the gilded cap, the bell's shoulder and crown loops behind. Sky behind. | Tamsule has added to it for centuries. |
| T07 ◆ | 100 mm (13.7°) | Top tier of the south-east gallery (r 41, y 15.5), looking up at the bell's waist | Two bronze ribs with verdigris runs, a salt-glass bay with the drop's water behind it, the teal conduit line along the inner rib. | "The Bell is glimmer-tech." Nobody answers. |
| T08 ◆ | 35 mm (37.8°) | 1.6 m on the east boardwalk (r 80, azimuth 120°), looking west-north-west | Gilded signboards in the foreground right, the boardwalk leading into frame, the Bell rising over the roofs. | A hundred languages, one bell. |
| T09 | 65 mm (20.9°) | 1.4 m on the north gallery gap's boat lane, looking south | The column, the drop and, beyond the south gap, the open sea. (Cinematics: the match's last breath.) | — |
| T10 | 24 mm (53.1°) | Underwater, 1 m below the catch-pool surface, looking up | Children's legs in the turquoise pool, the column entering from above. (Underwater stack, Rendering.) | Where children swim. |

---

## 5. Review Checklist for This Zone
- [ ] Every shot passes the grayscale value check: high-key galleries, sky and bronze around the one concentrated dark under the Bell.
- [ ] Gold ≤ 5 % and red ≤ 8 % of every frame (gold only on Tamsule's boards, finials and head caps; red only on repairs, rail caps and at most one cloth).
- [ ] No Order symbol, no Order gold, no Order official anywhere in the zone.
- [ ] Bound light is steady `glimmer_bound`, ≤ 3 % of the frame (T05 ≤ 35 %).
- [ ] Shadows teal, not grey, including the disc under the Bell.
- [ ] The drop placeholder sits exactly on the §1 contract, and the bell clears it by ≥ 2 m.
- [ ] Oruvel's moorings are empty: no boat, no name-board on the peg.

## Revisions
- 2026-10-24 (env-art, M3-ENV-01): first version. The drop contract (§1) is Environment's proposal; PC GPU had no Reefball R&D on any branch at this date, so it records the size and anchor the kit is built around.
