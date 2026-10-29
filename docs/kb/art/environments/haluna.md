# Haluna, Saltgrass Causeway, Shell Shrine: Mood Brief

Owner: Art Director (M1-ART-01). Build: Environment Artist (M1-ENV-01 mood test, then M2 slice). Lighting: Rendering.
Story: [act outline Ch2–3](../../story/beats/act_outline.md), [vertical-slice beat sheet](../../story/beats/vertical_slice.md) (the running order and in-world times below follow it), [decisions_log](../../story/decisions_log.md), [bible §5.1](../../story/bible.md). Grade targets: [color script](../color_script.md) `ch02` and `ch03`. Colors: [palette.json](../palette.json).
Zones: `game/levels/ch02/haluna/`, `game/levels/ch03/saltgrass_causeway/`, `game/levels/ch03/shell_shrine/`.

**The feeling in one line:** the most loved place in the game, in the brightest light in the game, preparing to send a girl away. Every frame says *home* and *departure* at once.

**Influences** (references.md §2): Ryukyuan coastal village (red tile, white mortar, coral walls, windbreak trees) **+** Polynesian outrigger and navigation culture **+** our own originals: tide-walls that breathe, lintel-gulls, wake-shells, and the Shell Shrine's fan roofs.

---

## 0. Layout, Orientation, and Lighting Sub-frames

**Geography (world north = −Z):** Haluna sits on the **east-facing** crescent beach of a low coral island, about 420 m from tip to tip, so dawn rises over the sea (Cutscene A). The Saltgrass Causeway leaves from the beach's north tip and runs **north-east for about 600 m** in-world (about 280 m of playable path, compressed with cuts) to the tidal islet of the Shell Shrine. The shrine's entrance faces **west**, back toward the village, so at sunset Asha walks out into the sun (Cutscene B).

**Tide datum:** `tide_line_y = 0.0` at mean sea level. High water is +0.9 m, and low water (when the causeway is exposed) is −0.7 m. Every weathering shader reads `tide_line_y` and the current water height from one global uniform.

**GI recommendation** (to be recorded in each level README by Environment): Haluna and the causeway use **SDFGI** (open exteriors, plus a time-of-day change for the night variant). The Shell Shrine interior uses **LightmapGI** baked per lighting state (pre-flood and post-flood), plus reflection probes at each basin. This is final only after Rendering measures it on the recommended tier.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill | Sea-glow | LUT |
|---|---|---|---|---|---|---|---|
| `ch02_noon` | **Haluna gameplay; M1-ENV-01 mood test** | 12:30 | 74° / 165° | `#FFF1E4` (5,700 K), energy 3.2 | sky `#9ED8EE` at 0.65 | 0 | `lut_ch02_noon`: Act I reference. Sat ×1.12, S-curve 0.45, teal toe `#0E4A55`, highlights roll off to `#FFF8EE`. Exposure 0.65 (EV100 15.0 intent). |
| `ch02` (color script) | Cutscene A (B01) | 06:20 | 6° / 95° | see color script | | 0.04 | `lut_ch02_dawn` |
| `ch03_causeway` | Causeway gameplay, low tide | 14:30 | 52° / 250° | `#FFEAD8` (5,300 K), energy 3.0 | sky `#A9DCF2` at 0.6 | 0 | `lut_ch02_noon` with +200 K warmth |
| `ch03_steps` | Cutscene B part 1 exterior: Rhen and Toma on the outer west steps, sea behind them (S06, B08; `.dlg` node `steps`) | 17:30 | 14° / 262° | `#FFD3AF` (4,200 K), energy 2.6; rim `sun_gold` 1.2 (characters) | `#7FA6CC` at 0.45 | 0 | `lut_ch03_sunset` at 60%, S-curve 0.45, sat ×1.05. Exposure 0.75. Full frame: [color script, "Ch3 sub-frame `ch03_steps`"](../color_script.md) |
| `ch03` (color script) | Cutscene B part 2, the first verse (S09, S10; B09) | 18:05 | 6° / 268° | see color script | | 0.04 | `lut_ch03_sunset` |
| `ch03_boss` | Drownbell, rising tide (C08–C10, B10). **Phase 1** | 18:15 | 2° / 270° | `#FF9F46` lin (1.000, 0.347, 0.061), ~2,500 K, energy 2.0 | afterglow `#5A7FA8` at 0.35 | 0.04 | `lut_ch03_sunset` at 100%, toe held at `deep_teal_shadow` |
| `ch03_boss` **phase 2** (flood) | The flood rig's 8 s rise drives this blend | ~18:20 | 0.5° / 271° (the sun touching the sea) | same color, energy 2.0 → 1.2 over the 8 s rise | `#5A7FA8` at 0.35 → 0.30 | 0.04 → 0.06 | as phase 1, toe deepened 10% so the `spawn_wound` polyps read against dark water |
| `ch03_shrine_int` | Shrine interior (S01–S05, S07, S08) | (any) | oculus shafts only | sun through 3 oculi, `#FFF1E4`, plus bounce from the pools | `#3FD0C9`-tinted bounce at 0.4 | — | `lut_ch02_noon`, S-curve 0.55 |
| `ch02_night` | Return to Haluna (Ch3 end, B11), Ch4 wake | 21:30 | — | oil lamps `#FFB16E` | moon `#9DB4D9` at 0.25 (≤ 2.5 × sea-glow, color script rule 3) | **0.12** | `lut_ch04_wake`. Exposure 1.1 |

**Lighting notes for the slice's afternoon and evening** (M1-ART-03, following [N-07](../../story/decisions_log.md)):
- **The day runs in order:** causeway 14:30 → shrine interior → the steps at 17:30 → the verse at 18:05 → the Drownbell at 18:15 → the dock at 21:30. Each grade is darker and warmer than the one before it, until night. Nothing jumps back toward noon.
- **The Drownbell comes after the song.** It is no longer a gold-afternoon fight (the old `ch03_boss` 17:30 light is now `ch03_steps`). At 18:15 the sun is 2° above the western sea, so the party fights in the afterglow of the verse, running back toward Haluna and **into** the sun (the causeway runs north-east, so the return is south-west). The low sun backlights the bell's hood and throws long shadows toward the camera in C08.
- **Phase 2 is the sunset.** The flood rig's rise also drives the light: the sun touches the horizon, the key falls to 1.2, and sea-glow rises from 0.04 to 0.06, because open sea after sunset must glow (color script rule 3). Cyan `spawn_wound` polyps under dark water read better here than they did in gold light, which was Narrative's point.
- **Scene glimmer energy (`hymn_glimmer.a`) per sub-frame:** `ch02` 0.6 (the nine held motes), `ch03_shrine_int` 1.2 (bound Ilun), `ch03` 2.5 (lift), `ch03_boss` 1.5 (held, from the bell), `ch03_steps` 0 (no glimmer on the steps). Because sea-glow is gated on `a > 0`, `ch03_steps` shows no sea-glow, which is correct while the sun is at 14°.

**Exposure, key product and water per sub-frame** (M1-ART-04, [ADR 0014](../../decisions/0014-light-units-exposure.md); water looks in the [color script](../color_script.md), "Water looks"). Exposure is `Environment.tonemap_exposure`. k = exposure × key energy says which palette `onscreen_hex` column (−1 / 0 / +1 = k 0.5 / 1 / 2) a sun-facing surface reads in. Water absorption is the shared base σ (2.0, 0.5, 0.42) m⁻¹ × `absorption_scale`. **These replace the v0 physical triples (R 0.45, G 0.065, B 0.045), which rendered near-white.**

| Sub-frame | Exposure | k (key) | Water look, scale (σ m⁻¹) | `col_deep` | Validated on screen (0.3–1 · 1–4 · 4–15 · > 15 m) |
|---|---|---|---|---|---|
| `ch02_noon` | 0.65 | 2.1 | `lagoon_clear` ×1.5 (3.0 / 0.75 / 0.63) | `#0E4A55` | `#5FB2B7` · `#4FACB2` · `#17818C` · `#186D7B` (pass, ΔE_ok ≤ 0.068 to the palette ramp) |
| `ch02` dawn | 0.75 | 1.8 | `lagoon_low_sun` ×1.5 | `#0E4A55` | as `ch03` (the same low-sun class) |
| `ch03_causeway` | 0.65 | 1.95 | `lagoon_clear` ×1.5; tidepools the same material | `#0E4A55` | as `ch02_noon` |
| `ch03_steps` | 0.75 | 1.95 | `lagoon_low_sun` ×1.5 | `#0E4A55` | `#207176` · `#206E74` · `#1B5253` · `#2B4D4E` |
| `ch03` | 0.80 | 2.1 | `lagoon_low_sun` ×1.5 | `#0E4A55` | `#165159` · `#184F58` · `#1B3E39` · `#2A3C37` |
| `ch03_boss` | 0.80 | 1.6 → 1.0 | `lagoon_low_sun` ×1.5; the flood plane is the same material | `#0E4A55` | as `ch03`; phase 2's darker key deepens it further, as intended for the polyps |
| `ch03_shrine_int` | 0.75 (proposed; set at the mood frame) | (oculus shafts) | shrine pools and channels: `lagoon_clear` ×1.5 (river shader for channels) | `#0E4A55` | not yet: interior light, re-check at the mood frame |
| `ch02_night` | 1.1 | 0.3 (lamp pools 1.3) | `night_sea` ×1.0 (2.0 / 0.5 / 0.42) | `#061A2B` | sea `#003845` (glow 0.12) against `#002734` (glow 0); moonlit stone `#424E5C` (rule 3 pass) |

The causeway's pools are 0.1–0.5 m deep, so at ×1.5 they read as sand tinted pale aqua with sharp caustics (references §1.7, the 0–0.3 m row), as the `water_shallows` view shows.

---

## 1. Haluna Beach and Village

### 1.1 Mood
High-noon warmth, white mortar lines on red roofs, turquoise flats, and the trade wind always moving something: nets, palm fronds, awning cloth. The village is preparing farewell food and garlands, so festival color appears in **small saturated notes** (garlands of frangipani, indigo and sea-blue awnings, red lacquer on the chapel door), never in large surfaces. Under the brightness there are three quiet signs of the ending: the wake-shell wall, the lintel-gulls all facing the sea, and the small foreign whiteness of the Order chapel.

### 1.2 Kit pieces (module grid 0.5 m; heights from the ground plane)
| Kit | Pieces | Key dimensions and parameters |
|---|---|---|
| **Tide-wall** | Straight, curved (R = 12 m and R = 24 m), wind-gap, gate opening, steps over the wall, end cap, collapsed section | Segments are 2.0 m long, 1.4–1.8 m tall, and 0.7 m thick at the base with a 6° batter. Dry-stacked coral blocks 0.25–0.5 m, parametric (seeded). Wind-gaps are 0.15 m slots every 3rd segment, set at 0.6–1.2 m height. |
| **House** | Coral base wall (0.9 m), timber post frame (0.15 m posts), board or woven-panel infill, hipped roof, shade deck (a front veranda 1.8 m deep), doors, shutters, ridge cap with **lintel-gull** | Footprints are 4 × 5, 5 × 6, and 6 × 8 m. Roof pitch 25°, eaves 0.9 m. Red tile (`roof_clay`) with **white lime mortar lines** (`mortar_white`) on every ridge and tile course, which is the village's graphic signature from above. |
| **Lintel-gull** | 3 carving variants (wings folded, half-raised, crying) | 0.6–0.9 m long, sun-silvered wood (`timber_weathered`), and **always facing the sea** (a placement rule enforced by the scatter tool: yaw = toward the nearest sea normal ±10°). |
| **Storehouse** | A raised granary on 6 stilts (1.2 m) | 3 × 4 m, thatch roof. |
| **Order chapel** | A single small building, 6 × 9 m | Whitewashed coral with `order_marble` trim, a small gilded bowl-dome cupola (1.6 m across), a red lacquer door with a gold Level emblem. It is the only Order building in Haluna, and it must look **imported**: cleaner, harder-edged, and straighter than anything around it. |
| **Wake-shell wall** | A curved wall 7 m long and 2.2 m high at the causeway head, set with carved shells | 400–600 shells (scatter, 6–14 cm), each with a procedurally carved name glyph. A recent shell for Asha (Ch4) is the cleanest and whitest. **Confirmed by Narrative ([N-03](../../story/decisions_log.md)):** this is the shrine wall of the Pilgrim's Wake, the Shell Shrine's *outer wall*, begun on the village side so the names can be visited at any tide. The Ch2 side scene happens here (H08). In Ch2 it has one clean, empty gap at shoulder height, waiting for Asha's shell. |
| **Dock** | Pilings, plank deck (0.3 m planks), mooring posts, ladder, end platform | The deck sits 1.4 m above mean sea level, 38 m long. **This is also the final shot of the game** (`ending_dock`), so build it to hero quality now. |
| **Boats** | Outrigger canoes (5, 7, and 9 m), a beached hull with a hole | Lashed construction, sea-blue and red bands painted at the bow. |
| **Nets and racks** | Drying net racks, fish-drying racks, a glass net-float cluster (salt-glass, 8–15 cm) | Nets are alpha cards with wind sway. |
| **Market** | Stall frames and awnings (cloth, 2 × 3 m) | Awnings in `indigo_dye`, `sea_blue_cloth`, and `sand_cloth`. A maximum of 1 red awning in view. |
| **Props** | Water jars, baskets, oil lamp posts (iron and brass, a 2.2 m post), leaf-boats, garlands, a fish basket, reefball (a woven sphere), sandals by doorways | |
| **Save shrine** | A shell-niche in a coral pillar with a perpetual oil flame | The save-shrine look is pending Architect and UI (M1-ARC-03). Here it is styled to Haluna. |

### 1.3 Vegetation (procedural; M1-ENV-02 builds the first three)
| Plant | Role | Notes |
|---|---|---|
| Coconut palm | The skyline silhouette; shade | 8–22 m, curved trunks leaning seaward 5–25°, fronds `palm_green` with dried brown fronds at 15%. |
| Frangipani | Festival note; garlands | 3–6 m, open branching, petals `frangipani` with a sun-gold throat. Fallen petals as decals on the lanes. |
| Saltgrass | Beach-head and causeway ground cover | 0.3–0.8 m, `saltgrass` with dry tips, and a strong wind response (0.9). |
| Windbreak tree (an original, dense-leafed evergreen) | Rows behind houses; dark value masses | 6–10 m, a columnar dark crown, `foliage_shadow`-heavy. It provides the dark shapes that frame bright lanes. |
| Screw-pine (stilt roots, spiral leaves) | Beach edge | 3–6 m, prop roots. |
| Sea hibiscus | Lane hedges | Yellow flowers fading to red-orange. Keep them small in frame. |
| Beach vine | Ground creeper on sand above the tide | Purple flowers at 5% density. |
| One hero banyan | At the chapel court | 14 m, aerial roots. It is the oldest living thing in the village. |
| Seagrass | Shallows (underwater) | It makes the turquoise read as depth variation. |

### 1.4 Materials (Haluna)
`coral_stone` → `coral_stone_weathered` (walls), `mortar_white` (roofs and walls), `roof_clay`, `timber_weathered`, `thatch`, `sand_dry` / `sand_wet`, `order_marble` + `gold_leaf` (chapel only), `salt_glass` (floats), cloth swatches. Stone weathering follows §4.

---

## 2. Saltgrass Causeway

### 2.1 Mood
Exposure. A thin path of old stone slabs and coral boulders across tidal flats, with saltgrass hissing in the wind, tidepools flashing, and a **huge sky** (60% of most frames). This is the first stretch of the pilgrimage (pillar 3), and the shots should make the path read as a line leading somewhere that doesn't come back. The light is warm afternoon on the way out (14:30). On the way back, after the verse, it is the last of the sunset (18:15, the sun at 2°, then on the horizon), with the tide coming in, so the zone moves from bright and open to ember and threatened.

### 2.2 Kit pieces
| Kit | Pieces | Parameters |
|---|---|---|
| **Causeway slabs** | Flat slab (1.2 × 2.4 m), tilted and broken slab, sunk slab, slab steps | Ancient grey coral-limestone, edges heavily eroded (VC.A), and slabs set 0.2–0.4 m above the low-water flats. |
| **Coral boulders** | Procedural (seeded noise displacement plus erosion), 0.5–3 m | Barnacled and algae-banded per §4, sitting in the wet zone. |
| **Tidepools** | Basin meshes (1–6 m) with water volumes 0.1–0.5 m deep | Anemone-like forms, small crabs, and urchin-like spines (all original). Caustics are sharp in the pools. |
| **Pilgrim marker posts** | Timber poles 2.4 m tall every 20 m, strung with shells and faded cloth strips | Some leaning, one broken. They are the path's rhythm. |
| **Lit Age fragment** | A half-buried white ceramic section (a conduit ring 3 m across) | One per zone, with a faint `glimmer_bound` glint in a crack (emission 0.6). It hints at the past. |
| **Wreck rib** | A small boat's ribs in the sand | |
| **Drownbell arena** | A widened causeway disc 30 m across, with a central sunk area | The **flood rig** lifts the water plane from −0.7 to +0.6 m over 8 s (phase 2) and drives the weathering wet-line uniform live. |

### 2.3 Vegetation
Saltgrass (dominant, 70% ground cover above −0.2 m), beach vine, sparse mangrove seedlings at the islet end (0.5–1.5 m), and seagrass in the channels.

---

## 3. Shell Shrine

### 3.1 Mood
A small, quiet, sacred place: cool after the glare outside, lit by three oculus shafts falling on water. **Architecture idea (original):** the roof is made of overlapping **stone fan-shells**, like scallop shells set in tiers, rising to a central oculus. Inside, water runs through carved channels between three great rotatable **shell-basins** (the puzzle), toward an inner pool and the sealed Vowbound chamber. The surfaces have nacre inlay: mother-of-pearl bands along the channels that shimmer when water flows. The shrine should feel **tended**: swept, with fresh leaf-boats on the steps. This is the one temple the village loves.

### 3.2 Kit pieces
| Kit | Pieces | Parameters |
|---|---|---|
| **Fan-shell roof** | Fan shells (1.5, 3, and 5 m radius), ridge ribs, oculus ring | Coral-limestone with ribbed grooves, plus white mortar at the joints (to tie it to Haluna). |
| **Walls and columns** | Curved wall modules (R = 9 m), columns carved like stacked shell whorls (0.5 m diameter, 4 m tall) | |
| **Channels** | Straight, bend, T-junction, spillway, sluice | Carved stone 0.4 m wide and 0.25 m deep, lined with nacre inlay bands. Flowmap-driven water (SPEC §8.2.1). |
| **Shell-basins ×3** | A rotatable basin 2.2 m across on a pedestal, with 3 spouts | Rotation in 90° steps over 1.2 s (ease in-out). The active spout's channel lights with a faint water shimmer (no glimmer: this puzzle is about water). |
| **Inner pool and chamber door** | An octagonal pool 7 m across, and a chamber door that floods open | The door is a carved shell valve that sinks into the floor as the pool level rises. |
| **Side pool** | A drainable pool 3 m across hiding the **net-float charm** (salt-glass, 6 cm, with a small glint) | |
| **Ilun's chamber** | A dome 12 m across, a floor pool, and a net-pattern lattice in the ceiling | The light through the lattice throws **net-shaped caustics** on the water and walls, which is Ilun's signature. |
| **Exterior** | Steps, a landing, sea stones, an offering shelf with leaf-boats | The entrance faces west. |

### 3.3 Materials
Coral-limestone (`coral_stone`, fresher than the causeway: this place is tended), `mortar_white`, nacre inlay (base `bone`, with a thin-film iridescence of hue shift ±40° by view angle at 0.3 strength: **an optional shader request** to Rendering), wet stone, and `salt_glass`. There is **no gold** in the Shell Shrine. It is a village temple, not an Order one. That distinction matters for Ansedra later.

---

## 4. Stone Weathering Layers (SPEC §8.2.7; shared by all three zones)

A single triplanar stone shader stacks layers in this order. Each layer is driven by **vertex color** (painted procedurally by the kit generator) and by **world height relative to `tide_line_y`**.

| Order | Layer | Driver | Look |
|---|---|---|---|
| 1 | Base stone | Material | Triplanar, 1.2 m tile, sharpness 4. |
| 2 | Erosion and edge wear | **VC.A** (curvature bake × noise) | Rounds edges and opens pits, and lightens albedo by 8% on convex edges. |
| 3 | Algae band | Height: `tide_line_y − 0.4` to `+0.1` | Green-brown `#4A5A2E` at 40–80% coverage, roughness 0.3, slightly slimy sheen. |
| 4 | Barnacle and limpet crust | Height: `−0.6` to `+0.3`, masked by noise | A bump-only relief layer plus a pale `bone` speckle. |
| 5 | Salt crust | **VC.G** × height band `+0.1` to `+2.0` (the spray zone) | `#E8E4D8` crystalline crust at 30–60% coverage, roughness 0.85, gathered in crevices (cavity). |
| 6 | Moss and lichen | **VC.R** × (normal.y > 0.6, or the north-facing shade side) × height > `+1.5` | Moss `palm_green` darkened 30%. Grey-green and orange lichen spots (`#C08A3A` at 10%) on sun sides. Inland walls only. |
| 7 | Wetness | **VC.B** (splash, puddles) **or** height < the current water height + a capillary band of 0.25 m | Albedo ×0.55, roughness → 0.12, plus a puddle normal flatten. The wet line updates live with the tide (essential for the Drownbell flood). |

Vertex-color channel meanings are therefore **R moss, G salt, B wet, A erosion.** This is a cross-role convention, and the kit generators must write it.

---

## 5. Composed Camera Shots (SPEC §6.6, §8.4: 10+ per art-complete zone)

The conventions: lens is full-frame equivalent focal length. **Godot `Camera3D.fov` is vertical** (keep_aspect = KEEP_HEIGHT), so vFOV = 2·atan(12 / mm), and the table gives both. Height is camera height above the local ground or water. Framing uses the rule of thirds unless stated. **◆ marks the five shots of the M1-ENV-01 mood test** (graded to `ch02_noon`).

### 5.1 Haluna (`ch02_noon` unless noted)
| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| H01 ◆ | 24 mm (53.1°) | 6 m above water, 180 m offshore, looking west | Beach crescent along the lower third, palms and red roofs in the middle band, cumulus over the top 55%. The tide-wall reads as one white curved line. **Also the close of Cutscene A** under the `ch02` dawn grade (`grade=ch02`): the sun is low behind the camera, so the beach is front-lit peach and three small figures walk up the path. | Home, whole and bright, seen from the sea that will take her away. |
| H02 ◆ | 35 mm (37.8°) | 1.6 m | The tide-walled lane curves away left to right. The wall fills the left frame edge, houses the right, and the sea shows through a wind-gap at the vanishing point. | The village breathes with the wind. Leading lines toward the sea. |
| H03 ◆ | 85 mm (16.1°) | 3.5 m (roof ridge) | A lintel-gull in foreground silhouette, 40% of the frame height, facing right toward the sea. Red roofs and white mortar lines fall away out of focus. | Watchfulness. The warning that will come. |
| H04 ◆ | 28 mm (46.4°) | 1.2 m | Dock planks as leading lines to outriggers, drying nets backlit, turquoise shallows with seagrass patches. | Ordinary work, ordinary life, worth keeping. |
| H05 | 35 mm (37.8°) | Rhen's eye: 0.4 m lying in the shallows, rising to 0.9 m with `rhen sit_up`; about 1.6 m standing in the "Get up" branch | **Cutscene A, `ch02` dawn.** H05 is Rhen's POV, and its height follows his eye. Asha kneels, filling the right third, with a low gold rim from the sunrise behind her over the sea. The staff is a vertical on the left third. **In the "Get up" branch** (line 026) Rhen is on his feet, leaning on Toma (Toma's shoulder is a soft shape at the left frame edge). H05 is taken at his standing eye-line, Asha has risen to stand in the right third, and the lens, axis and rim are the same. There is no lying-down POV and no offered hand ([N-17](../../story/decisions_log.md)). | Waking into kindness. She smiles first. Her name, and, if he stayed in the water, her offered hand. |
| H06 | 50 mm (27.0°) | 1.0 m, about 3.5 m from the pair | **Cutscene A, `ch02` dawn.** A side-on two-shot from the north along the waterline, looking south. Asha kneels seaward on the left third, in profile facing right, with her bare left shoulder and braid toward the lens and the sunrise rim on her profile. **Her face must read**, because the facial beat plays here. Rhen lies in the shallows on the right third with the brass lantern (oil-lit, `oil_lamp`) between them. Toma's spear tip enters frame right at 1/3 height. In the grief turn, the **nine held motes** are in the water around Rhen and drift toward frame left, out to sea, under Asha's knees (color script `ch02`, ≤ 1% of the frame). | The joke, the spear, the half-beat stillness at the lantern (recognition, not alarm), and then the dead leaving in the water. |
| H07 ◆ | 24 mm (53.1°) | 1.7 m | The chapel court: the white chapel framed by the hero banyan's aerial roots, its red-and-gold door the only hard rectangle in a soft frame. | Faith imported into a village. The cleanest building is the most foreign. |
| H08 | 65 mm (20.9°) | 1.4 m | The wake-shell wall with Grandmother Osu's hand resting on one shell. Shallow DOF (f/2.8, focus 2 m). The causeway is a soft line behind. | Names of the ones who went. The Pila side scene. |
| H09 | 28 mm (46.4°) | 1.6 m | The market under awnings: dappled light through indigo and sea-blue cloth, villagers wrapping farewell food. Saturated small notes, a pale ground. | A festival for a departure. |
| H10 | 42 mm (30.0°) | 1.5 m, from the dock end, looking back along the planks (reframed 10-28, M3-ENV-746: the dock now leads in and the windows read) | **`ch02_night`.** The village with oil-lamp windows, the faint sea-glow in the foreground water, and stars over the roofs. | Rhen asks to come. Warm lamps against a glowing sea. *(`ending_dock` uses this dock with the camera on the planks about 4 m shoreward of Asha, at 1.5 m and 50 mm, looking out to sea, the opposite direction to H10. She starts across the dock end, side-on to the lens, looking out over the water to frame left with her left shoulder toward camera, then turns about 50° to her left to look back at Haluna, so her nose line ends about 40° off the lens axis toward camera ([ADR 0020](../../decisions/0020-kerrid-restaging.md)): a front three-quarter on her face, with the dark, star-filled sea behind her ([N-17](../../story/decisions_log.md), [N-19](../../story/decisions_log.md)).)* |

### 5.2 Saltgrass Causeway (`ch03_causeway`; C08–C10 are `ch03_boss`, 18:15)
| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| C01 | 18 mm (67.4°) | 1.8 m | The causeway head: the path snakes from the bottom center to the shrine islet, small on the horizon at the right third. Saltgrass on both sides, sky 60%. | The pilgrimage begins (pillar 3). |
| C02 | 50 mm (27.0°) | 1.5 m, tracking side-on | Asha, Toma, and Rhen in profile against the lagoon and sky. Toma leads, Asha is center, Rhen trails and drifts. The spacing between them shows the relationships. | Three voices, walking together. |
| C03 | 100 mm (13.7°) | 0.3 m | A tidepool close-up with an original crab and anemone forms sharp, and the party's feet passing, out of focus, beyond. | Small life at the margin of a big story. |
| C04 | 35 mm (37.8°) | 1.2 m | A receding row of shell-strung marker posts, one broken in the foreground. | Many have walked this before, and none came back. |
| C05 | 28 mm (46.4°) | 0.8 m | The half-buried Lit Age ceramic ring, with a faint teal glint in its crack. The party is small beyond it. | The past under the sand. The first sight of bound light in the slice. |
| C06 | 65 mm (20.9°) | 1.0 m | Saltgrass moving in the foreground (soft), the party small in the middle ground, the shrine islet beyond. | Wind and exposure. |
| C07 | 24 mm (53.1°) | 0.6 m, tilted up 20° | The palette-variant flier silhouetted against bright cumulus, with Rhen in the lower left. | Readable sky for the encounter that teaches Rhen's niche (pillar 4). |
| C08 | 18 mm (67.4°) | 8 m | The Drownbell arena from above, looking south-west toward Haluna: the widened disc, the tide sliding in from both sides, the bell's hood breaking the surface against the sun 2° above the sea (ember, not gold), long shadows toward the lens. The wounds bleed **held** motes (`glimmer_held`, sinking seaward); the wound surfaces are `spawn_wound`. The party runs in from the bottom of frame (the cut from S09 on the second toll). | The tide turns. The song called it. |
| C09 | 35 mm (37.8°) | 0.5 m (just above the rising water) | Phase 2: the flooded causeway, spawn-polyps glowing `spawn_wound` cyan beneath the surface, the party knee-deep, the sun touching the horizon and sea-glow starting in the water. | The water takes the path. |
| C10 | 24 mm (53.1°) | 1.0 m, tilted up 30° | Ilun's first summon: manta wings spanning the frame, net-shaped light thrown across the water and onto the party. His face is shown for the first time. He is **bound light** (`glimmer_bound`, steady; his light moves only with his body, with no flicker, no trails, and no shed motes) until his Ch20 release. | The dead stepping in front of the living. |

### 5.3 Shell Shrine (`ch03_shrine_int`; S06 is `ch03_steps`; S09 and S10 are `ch03` sunset)
| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| S01 | 35 mm (37.8°) | 1.6 m | The approach across the last tidepool: the tiered fan-shell roof against the sky, the west-facing entrance centered, leaf-boats on the steps. | Arrival at a loved place. |
| S02 | 24 mm (53.1°) | 1.7 m | The threshold looking in: the first oculus shaft falling on the first basin, with volumetric fog density 0.02 to show the shaft. | Sacred light. Cool after the glare. |
| S03 | 18 mm (67.4°) | 6 m, pitched down 60° | Overview of the three basins and the channel network, read like a diagram. The active channel shimmers. | Puzzle clarity (pillar 4): the player sees the whole system. |
| S04 | 50 mm (27.0°) | 1.0 m | Water spilling over a rotating basin's lip into a nacre-lined channel, caustics on the floor. | Water obeying a gentle hand. |
| S05 | 40 mm (33.4°) | 0.8 m | The drained side pool, with the net-float charm glinting in the silt. | A secret, rewarded. |
| S06 | 50 mm (27.0°) | 1.3 m | **`ch03_steps`, exterior, 17:30.** Rhen and Toma sitting on the outer (west) entrance steps, the sea behind them, a gap of air between them. The camera is at the south end of the steps looking north-north-west, so the 14° sun is frame-left, about 70° off axis: a warm three-quarter key on both faces, with the glitter path behind them. The low afternoon sun is warm on the stone, and the shadows lengthen through the scene (16:00 → 18:00 in story time). | "Do you know what a Cantor is?" "...Someone who sings?" |
| S07 | 28 mm (46.4°) | 1.2 m, from behind Rhen and Toma | The chamber door sinking as the pool floods. Rhen and Toma are soft shoulders at the left and right frame edges (they speak from there). Asha is small, alone, center frame: she turns back to them for the exchange, then walks in. | Alone, by rite. |
| S08 | 18 mm (67.4°) | 1.5 m, tilted up 15° | A single held frame of Ilun's chamber: net caustics on the dome, the spectral manta overhead, Asha at the pool edge at one-tenth of the frame height. Ilun is **bound light** (`glimmer_bound`, energy 1.2, perfectly still; the only moving light is the caustics). His face is turned away or lost in the lattice light: save it for C10. Glimmer ≤ 15% of the frame. | Meeting the dead. Scale and tenderness. The same stillness as the Lit Age ring (C05). |
| S09 | 85 mm (16.1°) | 1.6 m, west of the door looking east | **Cutscene B:** Asha in the doorway, sunset gold on her face (she faces west, toward Haluna and the sun, to sing), Ilun's motes **rising** off her skin (`glimmer_lift`, slow spirals, ≤ 10% of the frame), the first band new on her sleeve. No gold on her face: the gilt line is never worn in the slice ([N-04](../../story/decisions_log.md)). | The first verse, sung aloud. |
| S10 | 65 mm (20.9°) | 1.7 m | The reverse on Rhen: a sunset rim on his hair tips, his face in soft fill. He is in the left third, looking right. The fill must hold his face within 1.5 stops of the rim, because the shot **holds**: a cut in on line 043 (the second sung line), then at least 6 s on his face through lines 044–046 with no blend and no cutaway, while his face layers `surprised` into `grief` ([N-13](../../story/decisions_log.md)). | "...where did you learn that?" |

---

## 6. Review Checklist for This Zone
- [ ] Every shot passes the grayscale value check (references.md §1.2): a clear focal value contrast, with darks concentrated in one or two shapes.
- [ ] Gold ≤ 5% of the frame (measured with the debug swatch-mask view), and red ≤ 8%.
- [ ] Lintel-gulls all face the sea. No Order gold outside the chapel.
- [ ] The wet line tracks the tide in C08 and C09.
- [ ] Shadows are teal, not grey (sample shadowed sand: hue between 170° and 200°).
- [ ] H10 has sea-glow at 0.12 and stars. The dock is built to hero quality for the reversed `ending_dock` shot.
- [ ] H06: exactly nine held motes on every preset, cyan, sinking seaward, ≤ 1% of the frame. Asha's face reads in profile.
- [ ] S08 and C10: Ilun's light is steady `glimmer_bound`, with no flicker, no drift, and no shed motes. S09 has the only rising light in the slice.
- [ ] C08–C09 play after the verse (`ch03_boss`, 18:15): the sun is a low ember in C08 and on the horizon in C09, never afternoon gold.

## Revisions
- 2026-10-22 (art-stream-2, M1-ART-03): synced with the final vertical-slice script. The Drownbell was re-timed from 17:30 to 18:15 (after the 18:05 verse, [N-07](../../story/decisions_log.md)), with a phase-2 flood blend. The old 17:30 light became `ch03_steps` (S06). H06 was reframed as a side-on two-shot so Asha's facial beat reads, and given the nine held motes. Vowbound bound light (N-05) was added to S08 and C10. The wake-shell wall placement was confirmed (N-03). Sea-glow for `ch02`/`ch03` went from 0.03 to 0.04 (the palette floor).
- 2026-10-23 (art-stream-3, M1-ART-04): `ch03_steps` is fully defined (color script "Ch3 sub-frame `ch03_steps`"), with rim, exposure and composition for S06; `ch03_the_first_verse.dlg` node `steps` now uses it. Added exposure (ADR 0014), key product and **validated water looks** per sub-frame, replacing the v0 physical absorption numbers. `ch02_night` moon 0.25 checked against the new night value rule.
- 2026-10-23 (environment-stream-3, M1-ENV-01 rework; **proposed, pending Art Director sign-off**, as review-sweep-F asked): (1) **H01 re-staged** to 120 m offshore at 8 m above the water (was 180 m at 6 m), still looking west with the horizon at about 0.36 of frame height, so the village and roofs read as a band, not a dotted line, and the surf wash reads as a varied beach edge. (2) **H04 drops "backlit"** from "drying nets backlit": at 12:30 the sun is 74° up behind the camera's right shoulder, so nets cannot be backlit. The nets are now opaque tannin-brown twine (`timber_weathered`) on a rack turned square to the lens. (3) **`ch02_noon` has no fog**: the row never called for it, so the mood frame's depth and volumetric fog were removed instead of being added here. (4) H03 is reframed with the camera 0.3 m lower and tilted up about 4°, so the near roof is a strip in the lower fifth. Red is 5.2% of the frame (HSV mask), inside the 8% budget, with no close-up exception needed.
- 2026-10-28 (Lead fast-track, the human's playtest of Cutscene A): Asha and Rhen crouched alike, facing the same way, and lying Rhen's KO pose was under the wash at the old mark. **Re-staged** (supersedes the H05/H06 rows' staging until Art revises them): `Spawns/Beach` (Rhen's intro mark) moves 3 m up the beach to (-4, 0.18, 8), where the wash is a film and his face, cheek to the sand on the sea side, stays clear of the water. Asha kneels at his left side at (-4.75, 0.2, 8.2), turned 310° so she faces in across his body toward his head and shoulders, leaning over him with her eyeline on his face. Toma, `kneel_beside_rhen`, `rhen_shallows` and `rhen_lantern` (now on his lantern) move with them. **H05** is no longer Rhen's POV: a 35 mm two-shot from the sea side at 0.8 m, favouring Asha's face, with Rhen's face above the dialogue box. **H06** keeps 50 mm from the south-east, at 0.7 m and 4.1 m (still key-lit), favouring Rhen's face for his joke, with Asha's face in three-quarter and Toma's spear entering frame left. Both shot ids hold their line in shots.json (`hold_line`).
