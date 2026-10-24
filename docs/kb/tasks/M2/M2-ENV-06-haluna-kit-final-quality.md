---
id: M2-ENV-06
title: Haluna kit to final quality (textures, materials, kit geometry, props), measured against the palette
role: environment
status: doing
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
- [ ] House infill, timber and thatch checked at H02/H04 range; props checked for placeholders.
- [ ] The five haluna shots (and `haluna_h10_dock_night` once it is on the integration branch)
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

## Review log
