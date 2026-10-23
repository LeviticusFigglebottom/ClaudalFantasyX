---
id: M1-RND-08
title: Water and glimmer follow-ups (review-sweep-B)
role: rendering
status: doing
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-08-water-glimmer; water items first)
depends_on: [M1-RND-01, M1-RND-02, M1-RND-03, M1-ENV-01]
milestone: M1
request-from: "environment"
---
## Goal
Environment-side findings on water and glimmer, scheduled after the Undertow and mood-test streams that consume both have merged.

## Acceptance criteria
- [ ] Global tide/water-level uniform (stone weathering, Drownbell flood)
- [ ] Zone-level hymn_sea_glow global decoupled from mote energy (water + glimmer)
- [ ] Caustics: less uniform Voronoi web, no visible tiling; pattern exposed as material param (Shell Shrine nets)
- [ ] Glimmer: fixed-count non-respawning field mode (H06 needs exactly 9 on every preset)
- [ ] Glimmer: local-space option so bound fields follow moving hosts
- [ ] glimmer_bound baseline; spiral rate vs lifetime; .dlg cue args mapped to field params
- [ ] Dusk released motes: warmer halo, density gradient; held motes spawn low over water
- [ ] Water: NaN at the anti-solar pixel (sun about 5° up, behind the camera; suspect normalize(L+V)) blooms into a white disc (found by the Undertow stream)
- [ ] Water: SSS paints saturated green bands across open sea with a low sun behind the camera
- [ ] Water: SSS crests read as large pale patches from high cameras at noon (Art, M1-ART-04)

## Notes
- 2026-10-23 PC GPU session claims this task and starts with the three water items (NaN at the anti-solar pixel, SSS green bands, SSS crest patches), which need a real GPU to see. Glimmer and caustics items stay open unless noted below.

## Review log
