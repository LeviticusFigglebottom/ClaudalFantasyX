---
id: M2-ENV-10
title: The B06 Saltgrass Causeway route at final quality (the slice's "one route")
role: environment
status: review
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
- [x] Tidal flats ground (exposed at low tide −0.7 m; channels and tidepools fill from the sea plane), the
      causeway's slab path, pilgrim marker posts every ~20 m (one broken, C04), coral heads, saltgrass on 70 % of the
      ground above −0.2 m (haluna.md §2.3), tidepools for C03, the Lit Age ring with its glint (C05), the shrine islet
      on the horizon (C01), and the widened Drownbell disc for B10 (shared with M2-ENV-11's battle arena).
- [x] A shipped dressing scene (outside `_tests/`, M2-ARC-04) that m2-slice instances, driven by a generated layout,
      all pieces reproducible with PROVENANCE rows, `verify_blender_builds` identical.
- [x] `ch03_causeway` lighting and grade per haluna.md §0 (sun 52°/250°, key `#FFEAD8` 3.0, sky fill `#A9DCF2` 0.6,
      exposure 0.65, `lagoon_clear` ×1.5 pools).
- [x] Composed views C01–C07 at the brief's lenses, viewed on lavapipe; register at most two as baselines.
- [x] A swap-in note for m2-slice (the scene, the path polyline for rails and triggers, banter anchor points,
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

## Notes (2026-10-24, env-art; pass 2, ready for review)
- **Drownbell disc:** M2-ENV-11's `causeway_disc` kit piece now sits on the zone at the `drownbell_disc` anchor
  on the tide datum (paving top y 0, sunk pool −0.95 holding water, foundation foot −1.55; flagged
  `on_datum` in the layout). The ground drops under its foundation wall and comes up to a sand apron at
  −0.35…−0.15; nothing else is scattered within 17.35 m of its centre. The hand-off path walks the paving top.
- **Views:** C03 is now a 0.3 m tidepool close-up across the water; C05 has the half-buried ring large
  in frame with the posts beyond; a new C08 (35 mm, 1.6 m) arrives at the disc. **Baselines (2):**
  `causeway_c02_profile_against_the_lagoon` and `causeway_c08_drownbell_disc_approach`.
- **Test fix:** `test_causeway_dressing.gd` reached the tree through `self` (TestCase is a RefCounted) and never
  parsed; that "5 tests" count in pass 1 was other suites. It now uses the main loop; 4/4 pass.
- **Known limits:** the wet/dry separation on the flats is modest in full noon sun (C06); the disc's paving
  matches the arena exactly, but B10's sunset grade lives in the arena scene, not the route.

## Swap-in note for m2-slice
- **Scene:** instance `res://assets/environments/zones/saltgrass_causeway/saltgrass_causeway_dressing.tscn` as
  the ch03 causeway's environment (it brings its own WorldEnvironment, sun, sea at −0.7 m and dressing). The head
  is at the origin, and the zone runs to about (262, −212).
- **Path:** `$Dresser.path_points()` (CausewayDresser) gives the walked polyline 0.32 m above the walked surface,
  head to islet steps (303 m). Use it for rails, follow camera and triggers.
- **Anchors:** `$Dresser.anchors()` returns `head`, `islet_steps`, `marker_posts` (banter beats every 20 m),
  `broken_post` (C04), `tide_pools` [x, z, r], `lit_age_ring` (the glint and examine point), `drownbell_disc`
  [x, z, r] (the B10 trigger: enter r < 15.1 m), and `low_water_m`.
- **Collision:** no `-col` proxies. Build a trimesh from `causeway_flats-lod1` (7260 tris) and from
  `causeway_disc-lod1` for the disc; the slabs are dressing (walk on the flats under them; the path polyline already rides 0.32 m above).
  Only the bed and the disc are walkable; gate the flats with the path.
- **B10:** the battle itself loads the `causeway_disc_sunset` arena (M2-ENV-11's swap-in note), so the route
  scene needs no sunset state.

## Review log
