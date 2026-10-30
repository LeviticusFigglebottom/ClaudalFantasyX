---
id: M2-ENV-06
title: Haluna kit to final quality (textures, materials, kit geometry, props), measured against the palette
role: environment
status: review
owner_session: "env-art"
depends_on: [M1-ENV-01]
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art queue item 3: bring Haluna's kit to M2 "final-quality art" (SPEC §10). The mood test
passed M1 as a prototype; at final quality the tide-wall stones read as white pillows, the ground is one
flat sand tone, the drowned Lit Age ruins glow as white posts in H01/H04, and the house infill is flat.
This pass covers the Environment-owned parts: `assets_src/environments/kits/haluna/**` (textures,
materials, kit geometry) and `game/shaders/environment/**`. Set dressing in the moved Haluna scenes
(`game/levels/ch02/haluna/**`, m2-slice) goes to m2-slice as swap-in notes or request tasks.

## Acceptance criteria
- [x] Coral stone: vuggy reef limestone (solution holes, fossil grain, two stone tones), per-block value
      spread, thinner spray-zone salt on village walls; flat-faced broken-coral blocks, not pillows.
- [x] Ground: broad value drift on dry sand, a high-water wrack line, leaf litter on turf (env_ground).
- [x] Drowned ruins: biofilm drip stains, less salt, greyed below lit_ceramic.
- [x] House infill, timber and thatch checked at H02/H04 range; props checked for placeholders (the two trees are M2-ENV-07).
- [x] The five haluna shots (and `haluna_h10_dock_night` once it is on the integration branch)
      re-captured, viewed side by side with the old baselines, each drift listed with its RMSE and why,
      palette checks (`tests/screenshots/palette_checks.json`) still passing, then re-approved.
- [x] `verify_blender_builds.py --job haluna_kit` byte-identical.

## Notes
### Pass 1 (2026-10-24, env-art)
- **Coral stone** (`kit_textures.build_coral_stone`): solution holes (thresholded fBm, gathered in patches,
  shadowed warm brown-grey inside), fossil branch-coral grain, a few fissures instead of a Voronoi net,
  and broad patches of `coral_stone` vs `coral_stone_weathered`. Albedo std 0.028 → 0.095 (mean 0.87 →
  0.77, still inside the floor/ceiling). Material: `variation_value` 0.2 (per block), `cavity_darken`
  0.38, `ao_strength` 0.75, `normal_strength` 1.5, spray salt `Vector2(0.15, 0.4)` (was the shader
  default 0.3–0.6, which whitened the walls to plaster).
- **Tide-wall blocks** (`walls.py`): edge radius 3.5 → 1.8 cm and displacement 6 cm @ 17 cm → 4 cm @
  26 cm (`BLOCK_*` constants): flat-faced broken coral, not pillows. Same triangle counts.
- **Ground** (`env_ground.gdshader`, new `breakup` group, defaults only, so no scene edit): dry-sand
  macro drift ±12 % at 18 m, a ragged wrack line of dried weed at high water (+0.9 m), leaf litter on
  turf.
- **Drowned ruins** (`build_coral_concrete` + material): biofilm drip stains under every lip, salt
  `Vector2(0.15, 0.35)` (was 0.4–0.7 under DROWNED's salt 0.9), algae 0.6–0.95, `col_tint` `#D2D4CB`.
- **Woven infill and thatch:** sun-greyed tint `#DCD3C6`, per-panel spread 0.22, deeper weave cavity;
  thatch normal 1.8, cavity 0.5, spread 0.18.
- **Shots** (lavapipe, viewed side by side with the old baselines, then re-approved): h01 rmse 0.01584
  (ruins grey, not white; wall line breaks up), h02 0.06091 (the tide walls: the intended main change),
  h03 0.01360 (near roof cap and far walls), h04 0.01108 (thatch, far ruins), h07 0.01049 (ground drift,
  far walls). Palette checks: 19 ok, 0 failed (same 19 as before). H02 shadowed wall face: L median
  0.50 → 0.41, p05–p95 0.43–0.70 → 0.31–0.59.
- Only the haluna_mood shots use these files (checked every shot scene's resources).
- **Still open:** the stilt-house wall at H04 is one flat panel (village.py geometry: posts, a frame);
  the placeholder banyan and windbreak (M2-ENV-07); bare village ground in H07 (dressing: m2-slice's
  scene, a request once ENV-07 lands); `haluna_h10_dock_night` once m2-slice's ENV-02 is on the
  integration branch.
- Gates: verify_blender_builds `--job haluna_kit` 31 identical; Godot `--filter=environment` 11,
  `haluna` 13, `post_import` 17, all green; validate_data 0 errors; taskboard --check clean.

### Pass 2 (2026-10-24, env-art)
- **Stilt house and storehouse walls** (`village.frame_wall`): timber girts and battens lashed over the
  woven infill, and a window with a propped shutter on each side wall of the stilt house. Each piece
  draws the framing from its own rng (`<piece>_frame`), so nothing else in the piece moves. stilt_house
  9590 tris (budget 14000), storehouse_stilt 4442 (7000).
- **Thatch:** per-course age (re-laid courses paler) and rain-runoff greying in the texture; a measured
  blue-weighted gain on the material: the H04 roof read Oklab L 0.625 C 0.098 against `thatch` 0
  (`#A78754`, L 0.642 C 0.079); now `#AA8453`, L 0.639 C 0.081.
- H02 roof tile measured `#CF8773` (L 0.69, C 0.094), between `roof_clay` 0 and +1; left as is.
- Shots: h04 rmse 0.00595 against pass 1 (viewed: the framed wall and greyer thatch), re-approved;
  h01 0.00147 (stilt houses far off), h02, h03, h07 0.00000. Palette checks 19/19.
  verify_blender_builds haluna_kit 31 identical.

### Pass 3 (2026-10-24, env-art)
- **Lintel-gulls** get their own material slot, `kit_carved_wood` (new; PROVENANCE row): triplanar grain at
  carving scale, sun-silvered tint, soft cavity. The loft UVs had stretched `kit_timber`'s board grain into
  hard stripes. H03 gull region: median `#4D453A` (L 0.395, p05–p95 0.20–0.78) → `#5B4F43` (L 0.436, hue 67°
  on `timber_weathered`, p05 0.24). h03 rmse 0.01308, viewed and re-approved; h01 0.00150, h02 0.00042,
  h07 0.00048, h04 0 (distant gulls; left).
- Gates: haluna 13, post_import 17; verify haluna_kit 31 identical; tools unittest 495 OK; validate_data.

### Pass 4 (2026-10-24, env-art)
- **House infill** (`village.house`): a sill girt over the coral base in every woven bay and a batten in each
  blind bay (`frame_wall`, the piece's own `<name>_frame` rng, so windows and doors don't move). house_tile_a
  13978, _b 11753, _c 18547 tris (budget 22000). Mostly under the eave shadow at H02 range: h02 rmse 0.00044
  (baseline left). verify haluna_kit identical; kit unittests OK.

- **The dock from `ending_dock`** (haluna.md H10 note): previewed at noon from the framing (camera on the
  planks 4 m shoreward of the end, 1.5 m, 50 mm, looking out to sea; `route_preview.tscn` camera
  `EndingDock`, shot `ending_dock_noon` in `route_preview_shots.json`). The planks, the end edge and the
  drowned columns beyond read well; no change. The night look is m2-slice's ENV-02.

### Close (2026-10-24, env-art)
- After merging claude/m2-slice, `haluna_h10_dock_night` with this branch's kit: rmse 0.00545 against
  m2-slice's baseline, under the limit; viewed (lamp-lit houses, stars, a glowing sea, the new tide walls and
  windbreaks dark against the sky). Left as is. All criteria met; to review.

## Notes (2026-10-28, env-art: finished; h10 is on the integration branch via big13)
- `haluna_h10_dock_night` re-captured on this tree and viewed. The dock at night reads: the warm lamp pools under
  the eaves, the lamps' flames now the kit's `lamp_flame` (M3-ENV-746), and the H10 reframe on the dock. It drifts
  from its baseline on purpose (rmse 0.0224); re-approve. Nothing else open.

## Review log
