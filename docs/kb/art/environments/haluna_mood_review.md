# Haluna mood test: SPEC §8.4 art-complete checklist (M1-ENV-01)

Owner: Environment (environment-stream-2). Reviewer: Rendering. Brief: [haluna.md](haluna.md) §1, §4, §5.1 (the five
◆ shots), graded to the `ch02_noon` sub-frame ([color_script.md](../color_script.md), Act I). Zone:
[`game/levels/_tests/haluna_mood/`](../../../../game/levels/_tests/haluna_mood/README.md).

**Bottom line.** This is the M1 five-shot test, not an art-complete zone. The bar in SPEC §8.4 is 10+ shots
passing review, performance held on the recommended tier, approved baselines, and no visible placeholders.
This test meets one of the four (the baselines are approved and committed). Two shots (H03, H04) are close
to the intended frame. Three (H01, H02, H07) read correctly but are clearly short of final. My honest
estimate is that the zone is **about 40% of the way to art-complete** for these five frames, and about 15%
of the way for the whole Haluna zone. The biggest single gap is the sky.

## What was built

| Part | Where |
|---|---|
| Procedural kit (31 pieces, seeded, byte-identical rebuilds) | `assets_src/environments/kits/haluna/` → `assets/environments/kits/haluna/*.glb` |
| Tiling textures (11 sets, 512², plain numpy) | `kit_textures.py` → `assets/environments/kits/haluna/textures/` |
| Materials (28, generated from one table) | `materials.py` → `assets/environments/kits/haluna/materials/` |
| Stone and timber weathering shader (4 tiers) | `game/shaders/environment/env_weathering{_low,_medium,,_ultra}.gdshader` + `env_weathering_body.gdshaderinc` |
| Ground, wake-shell and cumulus sky shaders | `env_ground.gdshader`, `env_wake_shell.gdshader`, `env_sky_cumulus.gdshader` |
| Zone grade LUT `lut_ch02_noon` | `assets_src/environments/kits/haluna/zone_lut.py` → `game/levels/_tests/haluna_mood/lut_ch02_noon.png` |
| Mood scene and the data-driven dresser | `game/levels/_tests/haluna_mood/haluna_mood.tscn`, `haluna_layout.json` |
| Tests | `tests/unit/test_environment_shaders.gd`, `tools/tests/test_haluna_kit.py` |

**Kit pieces.** Village timber and thatch: `timber_stilt_post`, `timber_deck_2m`, `timber_railing_2m`,
`roof_thatch_hip`, `roof_tile_hip`, `house_tile_a/b/c`, `storehouse_stilt`, `stilt_house`, and
`lintel_gull_a/b/c` (folded, half-raised, crying). Festival notes: `awning_cloth` (indigo, sea-blue or sand
per placement) and `garland_string`. Ruined Lit Age coral-concrete: `ruin_column_broken`, `ruin_slab`, and
`ruin_wall_sunk`, with rebar stubs. Walls: `tidewall_straight`, `tidewall_windgap`, `tidewall_gate`, and
`wakeshell_wall` (520 carved shells, with the one empty gap). Shrine: `roof_fan_shell`. Waterfront:
`dock_haluna`, `outrigger_7m`, `net_rack`. Chapel: `order_chapel`. Placeholders: `banyan_placeholder`,
`windbreak_placeholder`, `shell_shrine_massing`. The weathering parameters are `kit_common.Weathering`
(moss, salt, wet, erosion, noise scale), with presets FRESH, VILLAGE and DROWNED.

**Weathering shader.** It implements all seven layers of haluna.md §4 in order: base, erosion (VC.A),
algae band, barnacles, salt (VC.G × spray band), moss and lichen (VC.R × up- or north-facing × inland), and
wetness (VC.B, or below the live water height plus a 0.25 m capillary band). Bands are measured relative to
`tide_line_y`, and `WeatheringTide` writes `water_height_y` live, so a flood rig only has to animate one
float (unit-tested). There is a `paint_cover` layer for lime wash and dyes. The tiers:

| Tier | Base | Detail | Barnacle relief | Extra |
|---|---|---|---|---|
| Low | mesh UV | one top-down sample | none | |
| Medium | triplanar | dominant axis | none | |
| High | triplanar | triplanar | screen-space bump | |
| Ultra | triplanar | triplanar | screen-space bump | macro octave, sharper layer edges |

## Per-shot review against the colour script and brief

All five shots use `ch02_noon`: sun at 74° elevation and 165° azimuth, key `#FFF1E4` at energy 3.2, sky fill
0.65, AgX white 12, exposure 0.65 (ADR 0014), then the LUT; water is the colour script's validated `lagoon_clear` look. There is no glimmer and no sea-glow, because noon has neither (colour
script rule 3 applies only after sunset), so none was added. The shots are at 960×540, with 24 settle
frames and FXAA (the rig holds the weather clock still under capture).

### H01 ◆ `haluna_h01_village_from_sea`: 24 mm, 6 m, 180 m offshore, looking west
- **Matches:** turquoise lagoon water (it reads as `turquoise_shallow` → `lagoon_teal` through the AgX + LUT
  path), the beach and the white mortar line of the beach-head tide-wall, palms and red roofs in the middle
  band, and cumulus banking over the top half of the frame. The drowned Lit Age columns, wall and slab
  stand in the foreground right third. This is the "gorgeous and doomed" note: the old world drowning in
  front of the living village.
- **Misses:** the village is a thin band, and the roofs read as a red dotted line. At 180 m and 6 m the
  brief's geometry cannot make the crescent curve read, so the beach is nearly a straight line. The
  cumulus are far better than before but still show march banding (vertical striations), grain, and soft
  edges. They lack the hard sunlit tops of the references. The ruins are pale and simple next to the
  painted references: no algae curtains, no coral growth, no birds.
- **Verdict:** composition passes; fidelity does not (about 45%).

### H02 ◆ `haluna_h02_tidewall_lane`: 35 mm, 1.6 m, the tide-walled lane
- **Matches:** the lane curves away from left to right, the wall fills the left frame edge, houses with
  red tile and white mortar seams stand on the right, the sea shows at the vanishing point through the gate,
  palms are against the sky, and frangipani garlands are strung across the lane as the festival note.
  Shadows are teal-blue, not grey.
- **Misses:** the dry-stacked coral reads as courses of pillows. The blocks are still too regular, too
  rounded and too uniform in value. The lane ground is a flat pale field with no footworn texture, litter or
  fallen petals. The wind-gaps are invisible at this distance. The houses' woven infill is in deep shade and
  reads only as a dark band.
- **Verdict:** reads correctly; materials short (about 40%).

### H03 ◆ `haluna_h03_lintel_gull`: 85 mm, 3.5 m, the lintel-gull
- **Matches:** the half-raised gull fills about 40% of the frame height and faces right, toward the sea
  (the dresser rule yaws every gull to the shore normal ±10°). The red roofs and white mortar fall away out
  of focus (CameraShot DOF), with the sea on the horizon. The adze facets read as carving.
- **Misses:** the wood grain on the gull is stretched stripes, because it uses the plank UVs. The ridge-roll
  end cap at the lower right shows raw coral texture through the lime wash. The tile crowns are almost flat
  at this lens.
- **Verdict:** the best of the five (about 55%).

### H04 ◆ `haluna_h04_dock`: 28 mm, 1.2 m, the dock
- **Matches:** the plank leading lines run to the end platform, outriggers are moored, the stilt house
  frames the right, and the shallows are turquoise with caustics. The Shell Shrine's fan roof sits small on
  the horizon islet on the left third, and drowned columns stand at the dock end. Pillar 3 holds: the path
  leads somewhere.
- **Misses:** the brief's "drying nets backlit" cannot happen under a 74° sun. The nets are alpha-blended
  veils that barely read, so this needs a dawn variant or a reframed shot. The planks are clean and new
  rather than sun-silvered. The stilt-house thatch is flat. There are no seagrass meshes (the patches are
  only in the ground shader).
- **Verdict:** composition passes (about 50%).

### H07 ◆ `haluna_h07_chapel_court`: 24 mm, 1.7 m, the chapel court
- **Matches:** the white chapel and its red lacquer door (the only hard rectangle) sit framed by the
  banyan's aerial roots and crown, with dappled sky-lit shade on the court. The gilded bowl-dome reads. The
  chapel is crisper than anything else in the village, which is the "imported" note.
- **Misses:** the banyan is a PLACEHOLDER (cluster cards). Its roots are straight dark poles, and its trunk
  is out of frame. The chapel has no gold Level emblem detail at this distance and no wear at all. The court
  is bare sand with tufts, with no paving or offerings.
- **Verdict:** reads correctly; the hero tree is missing (about 40%).

### Zone checklist (haluna.md §6)
- [x] Gulls all face the sea (dresser rule). No Order gold outside the chapel.
- [x] Shadows are teal, not grey. Shaded sand is sky-lit blue-teal in H07 and H02.
- [ ] Grayscale value check: not run. There is no debug swatch-mask view yet (a Rendering tool).
- [ ] Gold ≤ 5% and red ≤ 8%: estimated by eye (the gold dome is under 1% in H07; the red roofs are about
  6–8% in H02, close to the limit). Not measured.
- [ ] The wet line in C08/C09 is not in this test. The live wet line is implemented and unit-tested
  (`WeatheringTide`).

## Performance (CPU only; GPU estimated)

> These are lavapipe CPU numbers on a 4-vCPU sandbox under a load of 12–22. They are not GPU numbers.

| Shot | Capture (load + 24 frames) | Approx. CPU per frame, 960×540 |
|---|---|---|
| H01 | 35 s | ~1.3 s |
| H02 | 53 s | ~1.6 s |
| H03 | 39 s | ~1.4 s |
| H04 | 34 s | ~1.2 s |
| H07 | 42 s | ~1.4 s |

- **Scene contents:** about 240 wall segments, 38 houses with 38 gulls, 88 palms, 14 frangipani, 49
  windbreaks, a banyan, and 5,600 MultiMesh grass clumps. LOD0 ends at 75 m (LOD1 is 12–2,000 triangles),
  so in H01 nearly everything draws at LOD1. LOD0 triangles in view (estimated from piece counts, not measured): roughly 0.4 M (H02) to 0.9 M (H07,
  under the banyan).
- **Costs, ranked by ablation on lavapipe:** SDFGI roughly tripled the frame cost (load + 24 frames went
  from ~35 s to ~150 s for H07), and it is off; see the GI note below. The cumulus sky runs at half
  resolution, with 64 steps plus 2 light samples per step. It is the largest remaining term on clear-sky
  frames.
- **GPU estimate (±2×, from operation counts):** on an RTX 3060 at the High tier, at 1440p with FSR2 at 0.77:
  - weathering surfaces: ~1.5 ms (12 texture fetches per pixel for triplanar base + detail)
  - sky: ~1.0 ms (half resolution, 64 steps × 3 noise lookups)
  - water: ~1.5 ms (per water.md)
  - foliage overdraw: ~1.5 ms
  - shadows and post: ~3 ms

  That puts the zone in the 8–10 ms range: plausibly inside 1440p60, but **unmeasured**. Low and Medium
  drop triplanar and halve the detail fetches. The sky has no tier variant yet, and `cloud_steps` should
  scale with the preset.

## GI

SDFGI is the shipping choice for this open exterior. The committed frames use **SDFGI off** (sky ambient +
SSAO), because on lavapipe SDFGI crushed every shaded surface to near black over 16, 30 and 40 frames. That
breaks colour-script rule 5. The measurements and the request to re-test on a GPU are in the zone README.

## Placeholders (tagged PLACEHOLDER in `.glb` node extras and in `kit_manifest.json`)

| Piece | Visible in | Why |
|---|---|---|
| `banyan_placeholder` | H07 | The hero banyan isn't built (vegetation stream). This one has a cluster-card crown and straight roots. |
| `windbreak_placeholder` | H01, H02, H07 | The windbreak tree isn't built. These have a cluster-card crown. |
| `shell_shrine_massing` | H04 (tiny) | A distant massing. The shrine's walls, columns and channels are M2 work. |
| Ground seagrass, lane litter | H01, H04 | Shader patches only, with no meshes or decals. |

## Gap analysis to the full SPEC §8.4 bar

1. **Ten or more shots.** The brief has 10 Haluna shots (H01–H10). This test covers 5. H05 and H06 need
   characters and the `ch02` dawn grade. H08 needs Osu. H09 needs the market (stalls and awnings exist).
   H10 needs `ch02_night`: oil lamps, sea-glow at 0.12, and stars. The causeway (C01–C10) and the shrine
   (S01–S10) are separate zones.
2. **Sky.** This is the largest visual gap. It needs one of two fixes:
   - Rendering's signature sky (SPEC §8.1), with TAA-friendly jitter, so the banding and grain resolve
     temporally.
   - A higher step count with blue-noise dithering.

   Cumulus edges need a sharper, eroded silhouette.
3. **Material depth.** The kit textures are 512² procedural tiles. They need:
   - curvature and AO bakes per piece, instead of the current vertex approximations
   - a second detail normal
   - real coral growth and algae geometry on the drowned ruins
   - sun-silvered plank variation
4. **Coral walls.** They need a proper polygonal dry-stack generator. Today they are rounded boxes in
   courses.
5. **Hero vegetation.** The banyan, windbreak, screw-pine, seagrass and sea hibiscus are not built.
6. **Performance on the recommended tier.** Unmeasured (there is no GPU runner). SDFGI is unverified.
7. **Value and colour checks.** They need the swatch-mask debug view, to measure the gold and red limits
   and run the grayscale check.
8. **Placeholders.** The three tagged pieces above must be replaced before the zone can pass.

## Requests raised (not edited here; they belong to other roles)
- **Lead:**
  - a `hymn_tide` vec2 global in `project.godot` (the shaders are ready for the one-line switch)
  - an ADR folding the vertex-colour packing convention (R moss, G salt, B wet, A erosion) into the
    conventions ADR
- **Rendering:**
  - re-test SDFGI on a GPU
  - adopt `zone_lut.py` into the LUT tool
  - fold `env_sky_cumulus` into the signature sky work, with a tier variant
  - add preset → weathering-tier mapping in `graphics_presets.json` (`WeatheringTide.PRESET_QUALITY` until
    then)
- **Vegetation:** the hero banyan and the windbreak tree, to replace the placeholders.
- **Art:** H04's "backlit nets" conflicts with a 74° noon sun. Either move H04 to a lower sun or drop the
  backlight note.
- **QA:** the baselines folder is now about 11 MB, against the 5 MB guideline in screenshots.md. These five
  shots add 3.2 MB.

## Rework after review-sweep-F (2026-10-23, environment-stream-3)

The sky blocker (B1) and should-fixes S1–S6 have been addressed. Each one now has a numeric check in
`tests/screenshots/palette_checks.json`, run on the baselines by `tools/tests/test_palette_check.py`. The
before and after numbers are in the M1-ENV-01 task notes. What remains: the cumulus is still a mood-test sky.
The cells are soft-edged and read slightly airbrushed at 960×540, and the signature sculpted sky is
Rendering's R&D. The banyan is still a placeholder (shaded roots now read about one stop under the shaded
sand, not at the toe). My estimate rises from ~40% to ~55% of art-complete for the five frames.
