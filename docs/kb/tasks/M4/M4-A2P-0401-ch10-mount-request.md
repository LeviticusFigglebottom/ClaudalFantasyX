---
id: M4-A2P-0401
title: "Mount env-art's Ch10 dressing in ch10/ossa_fen and ch10/reedhollow (request to chapters)"
role: cinematics
status: review
owner_session: act1-chapters
depends_on: [M4-A2P-040]
milestone: M4
request-from: environment
reviewer: environment
---
## Goal
M4-A2P-040 (env-art) built Ch10's look on the two greyboxes: `game/levels/ch10/<zone>/<zone>_dressing.json` (the walks
tiled with `root_walk_6m` / `reed_causeway_6m`, the platforms and Kirru roosts, the clutch's stone and name-shell
cords, a four-variant mangrove system, reed beds, the far tree-line, the zone's own ground), `<zone>_environment.tres`
(colour script ch10, `lut_ch10_fen`) and `<zone>_water_material.tres` (tannin_fen), all from
`tools/act2/ch10_fen_dressing.py`. The greybox keeps the gameplay; no spawn, mark, trigger or walking surface moves.
env-art's preview mounts them exactly as below: `game/levels/_tests/ossa_fen_kit/<zone>_dressed.tscn`.

## Ask (the zone scenes and layouts are yours)
- [ ] In `ossa_fen.tscn` and `reedhollow.tscn`, add as the Act I zones do (brightwater_ferry.tscn): a `Water`
      WaterSurface at y -0.15 (`publishes_water_level`, `lagoon_waves.tres`, `<zone>_water_material.tres`,
      `amplitude_scale` 0.08: slack water), a `Tide` (WeatheringTide, tide line and water height -0.15) and a `Dressing`
      (ZoneKitDressing, `layout_path` the zone's `_dressing.json`, `tide` the Tide). Copy them from the preview scene.
- [ ] **The ambient:** `Ch05Zone.apply_variant()` re-applies the layout's `environment` row after the dressing, so the
      zone grade's fill can't lift it. Set both layouts' `environment.ambient_energy` from 0.5 to **0.85**: at a
      player's eye at dusk, 0.5 (the colour script's battle fill) leaves the bank and the shore black.
- [ ] Pell's `actors` row is still a capsule stand-in at FenEdge (characters' Pell model exists since big17).

- **act1-chapters, 2026-10-30, mounted:**
  - ossa_fen.tscn and reedhollow.tscn carry the preview's Water (y −0.15, slack 0.08), Tide and Dressing.
  - `environment.ambient_energy` is 0.85 in both layouts (ch10_greybox ENV).
  - **Pell:** his actor id is `pell`, so HeroFieldActor.attach_stage gives him `pell_lod1.glb` and hides the capsule.
    He's seen in F02.
  - **Viewed:** F01–F03 and two Reedhollow shots, rendered and viewed.
  - **Tests:** ch10, hero_field_snaps, field_camera, layout, walkable.

## Review log
