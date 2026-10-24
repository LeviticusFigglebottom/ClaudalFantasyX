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
- [ ] Coral stone: vuggy reef limestone (solution holes, fossil grain, two stone tones), per-block value
      spread, thinner spray-zone salt on village walls; flat-faced broken-coral blocks, not pillows.
- [ ] Ground: broad value drift on dry sand, a high-water wrack line, leaf litter on turf (env_ground).
- [ ] Drowned ruins: biofilm drip stains, less salt, greyed below lit_ceramic.
- [ ] House infill, timber and thatch checked at H02/H04 range; props checked for placeholders.
- [ ] The five haluna shots (and `haluna_h10_dock_night` once it is on the integration branch)
      re-captured, viewed side by side with the old baselines, each drift listed with its RMSE and why,
      palette checks (`tests/screenshots/palette_checks.json`) still passing, then re-approved.
- [ ] `verify_blender_builds.py --job haluna_kit` byte-identical.

## Notes

## Review log
