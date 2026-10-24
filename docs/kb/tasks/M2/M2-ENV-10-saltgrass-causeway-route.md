---
id: M2-ENV-10
title: The B06 Saltgrass Causeway route at final quality (the slice's "one route")
role: environment
status: doing
owner_session: "env-art"
depends_on: [M2-ENV-08]
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
An M2-review blocker from the Lead's intro audit: SPEC §10's "one route" is B06, the Saltgrass Causeway
(`ch03/saltgrass_causeway`, vertical_slice.md B06, haluna.md §2): about 280 m of playable path out over the
low-tide flats from Haluna's causeway head to the Shell Shrine's islet, under `ch03_causeway` (14:30). m2-slice
builds the greybox gameplay (rails, encounters, the three banters' triggers); env-art builds the world and hands
it over with a swap-in note.

## Acceptance criteria
- [ ] Tidal flats ground (exposed at low tide −0.7 m; channels and tidepools fill from the sea plane), the
      causeway's slab path, pilgrim marker posts every ~20 m (one broken, C04), coral heads, saltgrass on 70 % of the
      ground above −0.2 m (haluna.md §2.3), tidepools for C03, the Lit Age ring with its glint (C05), the shrine islet
      on the horizon (C01), and the widened Drownbell disc for B10 (shared with M2-ENV-11's battle arena).
- [ ] A shipped dressing scene (outside `_tests/`, M2-ARC-04) that m2-slice instances, driven by a generated layout,
      all pieces reproducible with PROVENANCE rows, `verify_blender_builds` identical.
- [ ] `ch03_causeway` lighting and grade per haluna.md §0 (sun 52°/250°, key `#FFEAD8` 3.0, sky fill `#A9DCF2` 0.6,
      exposure 0.65, `lagoon_clear` ×1.5 pools).
- [ ] Composed views C01–C07 at the brief's lenses, viewed on lavapipe; register at most two as baselines.
- [ ] A swap-in note for m2-slice (the scene, the path polyline for rails and triggers, banter anchor points,
      collision source).

## Notes (2026-10-24, env-art; pass 1)
- **Generator** `assets_src/environments/kits/haluna/causeway_zone.py`: one height function (`Field`) makes
  both the `causeway_flats` terrain (400 x 330 m, 2 m / 6 m grids, 66000 / 7260 tris, 2.2 MB; env_ground masks
  in the vertex colours) and the layout (`assets/environments/zones/saltgrass_causeway/causeway_layout.json`: 168
  pieces with explicit heights, 7624 saltgrass as baked transforms, the path polyline, the anchors). The path
  is 303 m head to islet. 46 % of the zone is under low water (channels, puddles, pools, sea), 22 % is wet
  flat just above it, 16 % is saltgrass bank.
- **Shipped scene** `assets/environments/zones/saltgrass_causeway/saltgrass_causeway_dressing.tscn` (outside
  `_tests/`): the HalunaMood rig at `ch03_causeway` (sun 52°/250°, key #FFEAD8 3.0, 14:30, water −0.7 m),
  `causeway_environment.tres` (exposure 0.65, ambient 0.6), Haluna's sea and `CausewayDresser`
  (extends HalunaDresser: pieces + baked instances; `path_points()`, `anchors()` for m2-slice).
- **Ground** `kit_causeway_ground` (env_ground): a wide wet band and a tidal-mud wet colour `#8A7D68`
  (sand_wet darkened): in full sun the palette's sand_wet alone renders as pale as a dry beach.
- **Bugs found on the way** (viewed renders): the islet term floored the whole zone at −0.4 m (dry flats, no
  pools); the pools sat inside the bed's ridge and were erased. Both fixed.
- **Preview** `game/levels/_tests/saltgrass_causeway_kit/causeway_preview.tscn`, C01–C07 at the brief's lenses
  (`causeway_preview_shots.json`). Read so far: C01 the path leads away, the islet is small on the horizon;
  C02 slabs, saltgrass and lagoon read well; C04 the broken post in the foreground; C05 the ring reads but the
  framing is loose; C06 the wet flats separate only modestly from the dry banks.
- **Tests:** `tests/unit/test_causeway_dressing.gd` (5: pieces, baked grass, low water, path and anchors);
  `tools/tests/test_haluna_kit.py::CausewayZoneTests` (layout regenerates byte for byte, grass above −0.2 m and
  off the bed, pieces on the height field, pools under low water).
- **Next:** C03 (the tidepool close-up) and C05 framing, the flats' read, the Drownbell disc (waiting on
  M2-ENV-11's `causeway_disc`), registering two shots, the swap-in note.

## Review log
