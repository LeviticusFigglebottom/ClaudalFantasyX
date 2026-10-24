---
id: M2-ENV-08
title: The village-to-causeway-head route and the village props at final quality (kit pieces + swap-in layout)
role: environment
status: review
owner_session: "env-art"
depends_on: [M2-ENV-06]
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art queue item 5: the slice's one route between the village and the causeway head at final
quality. Haluna's layout (`game/levels/ch02/haluna/haluna_layout.json`, m2-slice) dresses houses, walls, the
dock and palms, but none of haluna.md §1.2's props and none of §2.2's causeway pieces exist, so the walk from
the lanes to the causeway head (the wake-shell wall, Osu, the save shrine) is bare sand.

## Acceptance criteria
- [x] Causeway-head kit (haluna.md §2.2, Environment-owned): causeway slabs (flat 1.2 x 2.4 m, tilted/broken,
      sunk, slab steps), coral boulders (0.5–3 m, seeded, barnacle/algae bands per §4), pilgrim marker posts
      (2.4 m, shells and faded cloth strips; a leaning and a broken variant), the half-buried Lit Age ring
      (3 m, a faint `glimmer_bound` glint in a crack), a wreck rib.
- [x] Village props (§1.2): water jars, baskets, an oil lamp post (2.2 m), a fish-drying rack, a salt-glass
      net-float cluster, a market stall frame (for the existing awnings), sandals by a doorway. Reuse the shrine
      kit's leaf-boats (M2-ENV-03) rather than building a second set.
- [x] Each piece: LOD0/LOD1 within a budget, chained LODs, vertex-colour weathering, PROVENANCE rows,
      `verify_blender_builds` byte-identical.
- [x] A swap-in note for m2-slice: the exact `haluna_layout.json` entries (piece, position, yaw) that dress the
      route from the north lanes to the causeway head, plus collision `piece_rules` for the new pieces.
      Previewed in an Environment-owned scene (not m2-slice's) with at least one composed view, viewed.

## Notes (2026-10-24, env-art)
- **Pieces** (all in the `haluna_kit` Blender job; `verify_blender_builds --job haluna_kit` 49 identical):
  - `causeway.py`: `causeway_slab_flat` (972 / 12 tris), `causeway_slab_broken` (2088 / 24),
    `causeway_slab_steps` (2916 / 36), `coral_boulder_a/b/c` (0.7 / 1.5 / 2.8 m, 2496–3264 / 300–408; a
    fused-lobe coral head, budget raised to 3600 / 450 because they sit beside the path),
    `pilgrim_marker_post` (+ `_leaning`, `_broken`; 685 / 15), `lit_age_ring` (1348 / 144, the glint only on
    LOD0), `wreck_rib` (754 / 168).
  - `props.py`: `water_jar` (524), `basket_set` (564), `oil_lamp_post` (353), `fish_drying_rack` (1122),
    `net_float_cluster` (2166), `market_stall` (1884), `sandals` (108). Leaf-boats: the shrine kit's (ENV-03).
- **Materials** (`materials.py`, PROVENANCE rows): `kit_causeway_stone` (the village coral greyed by
  `#C4C1B8`, heavy algae and barnacles, thin salt: "ancient grey coral-limestone"), `kit_earthenware`
  (laterite paint over the coral-concrete aggregate), `kit_brass`, `kit_dried_fish`, `kit_lamp_flame`
  (`oil_lamp`, 0.6), `kit_glimmer_glint` (`glimmer_bound` at emission 0.6, haluna.md §2.2).
- **First look and fixes** (lavapipe, viewed): slabs and boulders first rendered as flat white plates and
  smooth pale eggs (DROWNED salt 0.9 whitened them; the displacement was too broad). Now grey-brown,
  algae-banded, eroded edges; boulders lumpy. Drying fish first read as paddles; now split fish with tails.
- **Preview** (Environment-owned, not a registered shot): `game/levels/_tests/haluna_mood/route_preview.tscn`
  inherits the mood world and places `route_layout.json` on its terrain through `RoutePreviewDresser`
  (never rebuilds the terrain). Views: `route_preview_shots.json` (`route_wide`, `route_causeway`,
  `route_props`), captured with `capture.tscn -- --manifest=res://game/levels/_tests/haluna_mood/route_preview_shots.json`.
  On this branch the wake-shell wall at (-14.6, -122) isn't there yet (m2-slice's ENV-04), so the offerings
  stand by a tide wall in the preview.
- **Tests:** `tools/tests/test_haluna_kit.py::RouteKitTests` (post heights, slab size, lamp slots, the ring's
  glint, the ancient-stone slot, every new slot has a .tres, every route-layout piece is in the manifest);
  the existing kit tests cover budgets, determinism and weathering channels for the new targets.
- **Swap-in (m2-slice):** see env-art.md "Swap-in notes". The Haluna shots don't drift (no existing piece or
  material changed; the layout doesn't name the new pieces).
- Gates: kit unittests 16 OK; Godot post_import 17, haluna 13, environment 11; gdlint/gdformat clean;
  validate_data 0 errors; verify haluna_kit 49 identical.

## Review log
