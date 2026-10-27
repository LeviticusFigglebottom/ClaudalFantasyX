---
id: M3-ENV-08
title: "Ch4 Brightwater Crossing: the ferry deck at sea (kit at final quality)"
role: environment
status: review
owner_session: "env-art"
depends_on: [M2-ENV-06]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Act I zone kit, filed by env-art after the Lead's M3 queue emptied (the Lead's no-idle directive, 2026-10-24).
Ch4 "The Pilgrim's Wake" from docs/kb/story/beats/act_outline.md, zone `ch04/brightwater_ferry`: the ferry deck at sea, its passengers' spaces, rigging, the derelicts it passes, and the night sea (colour script `ch04`). Check it against M3-ENV-06's `derelict_deck_night` arena, built from Brine Shoals, so the two decks read as kin.

Gameplay placement (spawns, triggers, NPCs, collision tuning) is m2-slice's: hand it over as swap-in notes (below;
docs/kb/handoffs/live/env-art.md is the Lead's to merge).

## Acceptance criteria
- [x] **Design notes first:** `docs/kb/art/environments/<zone>.md` in the haluna.md format (mood in one line,
      layout and orientation, lighting sub-frame and grade from color_script.md, kit table with dimensions,
      materials against palette.json, composed shot list with lenses), reviewed against the act outline and the
      story bible before any geometry; references in words only (references.md).
      → `docs/kb/art/environments/brightwater_ferry.md` (committed 5c57ae3e before any geometry, checked against
      act_outline Ch4, act1_ch04.md C4-09 to C4-15 and its §7/§9, bible §5.1, color_script `ch04`; revised after
      the preview, see its Revisions); references.md gained the coastal-trader row.
- [x] A procedural kit in `assets_src/environments/kits/<zone>/` with its own Blender job, LOD0/LOD1 within
      budgets and chained per vegetation.md "One LOD at every distance", vertex-colour weathering per haluna.md
      §4, materials written by script, PROVENANCE rows, `verify_blender_builds` byte-identical, every file under
      5 MB, no reference images, packs or AI generation.
      → `assets_src/environments/kits/brightwater_ferry/` (11 pieces), job `brightwater_ferry_kit` (pinned at 4
      threads: the glbs, manifest, 27 materials and the grade LUT; 40 outputs identical), its own import category
      `brightwater_ferry_kit`.
- [x] An Environment-owned preview scene with composed views of the design notes' key shots, viewed on lavapipe
      and iterated to final quality (pillar 2, the palette, the colour script). Register at most the two most
      telling shots as screenshot baselines (the repo's binary budget).
      → `game/levels/_tests/brightwater_ferry_kit/` (7 views, eleven capture rounds); baselines
      `brightwater_b02_awning`, `brightwater_b03_rail_drowned`.
- [x] Tests for anything with runtime code; a swap-in note for m2-slice.
      → `tools/tests/test_brightwater_ferry_kit.py` (22), `tests/unit/test_brightwater_preview.gd` (5); the kind in
      both post-import KINDS lists; swap-in note below.

## Notes
- **Kit** (generators import the Haluna kit's `kit_common.py` and `village.py` (the lintel-gull) and the Brine
  Shoals kit's `bs_common.py` (heightfield) read-only; the Haluna material writers are loaded by path as
  `haluna_materials`; no other kit's file edited):
  - The ship (one origin, bow to −Z, main deck y 0, waterline y −1.6): `ferry_hull` (hull with the sheer sweep and
    raked forefoot, tar / red wale / sea-blue topsides, flat main deck and poop at +0.9, bulwarks with two
    gangways, the open quarter rail, main hatch under a tarpaulin, fore hatch grating, poop ladders, rudder and
    tiller, bowsprit, the stem-gull, windlass, chain-plates, fife rails, the stern and bow lantern crooks),
    `ferry_rig` (two masts, the Low Reaches lugs bellied to port, shrouds to the chain-plates with ratlines on the
    main, stays, halyards, sheets, the lookout's perch at +11.6 m), `ferry_deckhouse` (lime-wash over a sea-blue
    dado, lit windows, the Order niche inside), `ferry_awning`, `ferry_cargo`, `ferry_skiff` (on its davits).
  - Props: `passenger_bundles` (one place: bundles, basket, mats, bedroll, gourd), `ferry_lantern` (the flame at
    `bf_props.LANTERN_FLAME`, 0.23 m below the ring).
  - The drowned: `derelict_hulk_a` (listed, dismasted, stove in), `derelict_hulk_b` (bow up, a rag of sail),
    `reef_awash`. Built by the ferry's own hull generator (`bf_common.HullForm`), with `arena_derelict_deck`'s
    plank, seam and thickness proportions (tested), so the ferry and every derelict read as kin.
  - 27 materials (`bf_materials.py`, palette.json hex), grade LUT `lut_ch04_crossing` (`bf_zone_lut.py`:
    M3-ENV-06's `ch04_wake` with the sea's teal spared).
- **Triangles, LOD0 / LOD1:** ferry_hull 26845/4031; ferry_rig 6906/500; ferry_deckhouse 2340/724; ferry_awning
  1394/152; ferry_cargo 3648/864; ferry_skiff 3936/298; passenger_bundles 1256/282; ferry_lantern 392/168;
  derelict_hulk_a 13572/1293; derelict_hulk_b 5538/526; reef_awash 3920/320. Budgets in each module's
  `TRI_BUDGET`. Kit on disk: about 4.2 MB, largest file ferry_hull.glb 1.8 MB.
- **Swap-in for m2-slice** (zone `game/levels/ch04/brightwater_ferry/`):
  - Scene: dress with `HalunaDresser` from a layout like `game/levels/_tests/brightwater_ferry_kit/brightwater_ferry_layout.json`
    (generated by `assets_src/environments/kits/brightwater_ferry/bf_preview_layout.py`: copy its tables, never
    reference the `_tests` file from shipped scenes). Kit dir `res://assets/environments/kits/brightwater_ferry/`.
    The six ship pieces, the nine lanterns and the passengers' places share the ship's origin: put them under one
    `Ferry` node so the ship can be placed (and rocked, if wanted) as one.
  - Anchors (the ship's frame; the preview's world = ship + (0, 1.6, 0)): the main deck **y 0** (z −13 … +7.6),
    the poop **y 0.9** (z +7.6 … +12.4) by the ladders at x ±2.62, z +7.0 … +7.6; the **gangways** at
    z −2.6 … −1.6 on both sides (C4-09's gangplank; C4-11's derelict lies an oar's length off to starboard there);
    the deckhouse door at (0, 0, 3.4), the **Order niche / save point** at (0, 0, 7.0) inside; the purser by the
    cargo (x ±1.8, z 0 … 1.6); the passengers under the awning (z −7.2 … −3.2); Ysolde and Asha at the starboard
    rail (z −1.6 … +1.5); Imbe at the tiller (0, 0.9, 11 … 12); the lookout's perch (0, 11.6, 2.4).
  - Collision: the kit exports no `-col` proxies. Walkable: the main deck (a box inside
    `bf_common.FERRY.half_beam_at(z)` − 0.05, y 0), the poop (y 0.9), the ladders (ramps). Block: the bulwarks to
    `FERRY.rail_y(z)`, the main hatch coaming (2.44 × 2.04 m, 0.45 m), the fore hatch, the deckhouse walls except
    the door, both masts and fife rails (the main's forward of its mast), the cargo stacks
    (x 1.3 … 2.2 and −2.2 … −1.3, z −0.9 … 1.7), the awning posts, the windlass and bitts. **The ferry is never
    attacked (ADR 0017 (d)): no encounter volume anywhere on it.**
  - Lighting: the preview's `ch04` Environment (`lut_ch04_crossing` is a kit asset, safe to reference), the Moon
    `#9DB4D9` at 0.28 low in the east (88°, 16°), sea-glow 0.12 on a `night_sea` copy, and the layout's `lamps`
    lit as `BrightwaterFerryPreview.build_lamps` does (copy it: every light keeps `light_volumetric_fog_energy` 0).
    The daylight `ch04_derelict` sub-frame for C4-11 to C4-14 is Rendering's (beat sheet §9).
- **Follow-up:** **M3-ENV-08B** (todo), the *Seventh Terrace*, one hero ship for Ch1's mooring and Ch4's derelict
  (boardable deck, galley, hold, name-board, sails set and lowered), from this kit's hull generator.
- **Known limits:** the ship is still in the preview; the rig's leads are tubes without blocks at every lead; the
  deckhouse's fore wall reads as dark boards where the door lantern cannot reach (B05); the far sea at deck height
  mirrors the sky more than it glows (hence the moon in the east); the volumetric fog is off on lavapipe.

## Notes
- Arena lamps and lights near a dense FogVolume set `light_volumetric_fog_energy = 0`
  (the Lead's rule; `tools/tests/test_fog_lamps.py`). The preview's lanterns follow it (tested).

## Review log
