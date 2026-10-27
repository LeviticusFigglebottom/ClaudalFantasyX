---
id: M3-CRE-611
title: "Ambient wildlife in the slice zones: gulls, shore crabs, fish in the shallows"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-02]
milestone: M3
request-from: lead
---
## Goal
Non-combat ambient life so the slice zones read as living: gulls wheeling and settling, small crabs on the sand that
scatter from the player, fish shoals in the shallows. Cheap (MultiMesh or simple rigs), deterministic, data-placed.

## Acceptance criteria
- [x] Wildlife models from source (the creature kit), with PROVENANCE rows and jobs
- [x] A WildlifeLayer node and per-zone placement data; budgets (draw calls, ms) measured
- [x] Tests, a review scene and shot; handed to the zone owners with a one-node integration note

## Notes
- 2026-10-24 character (creatures worktree): design sheet, budgets and the zone-owner note in
  `docs/kb/art/wildlife.md`.
- **Models** (creature kit geometry, `assets_src/wildlife/common/wildlife_kit.py` `export_static`, unskinned):
  `assets/wildlife/gull/gull.glb` (`gull_flying` 1,280 tris, `gull_perched` 1,192; 84 KB), `shore_crab.glb`
  (1,064; 36 KB), `shoal_fish.glb` (186; 8 KB). One material slot each on the new
  `game/world/wildlife/wildlife.gdshader` (the creature surface without emission, plus a vertex stage: gull flap,
  perched head turn and nod, crab leg gait, fish body wave, all driven by MultiMesh custom data, no `TIME`).
  Jobs `wildlife_gull`, `wildlife_shore_crab`, `wildlife_shoal_fish` verify identical; PROVENANCE rows for the
  three GLBs and three `.tres`.
- **Where they live:** `assets/wildlife/<id>/` with its own `wildlife` import category
  (`game/data/import/wildlife.json`, `wildlife_post_import.gd`, added to `KINDS` in both post-import tests), not
  `assets/creatures/`: the creature validators want a battle row and the battle clip set for every creature, and
  wildlife has neither.
- **Runtime:** `WildlifeLayer` (one node per zone, `zone_id` = location id) reads
  `game/data/world/wildlife/<zone>.json` and the kinds/budgets file `wildlife.json`; `WildlifeGullFlock`,
  `WildlifeCrabBeach`, `WildlifeShoal` are headless and seeded from the zone id. Four MultiMeshes per zone (four
  draw calls; perched gulls and crabs cast shadows), no collision. Off-screen groups pause, groups past 120 m hide.
- **Measured** (headless debug build, dressed Haluna, HalunaTerrain ground): all groups simulated 0.27 ms/frame
  average (0.56 worst); in-zone at the BeforeBattle spawn 0.19 ms (2 groups active, 5 paused); looking away
  0.06 ms. Budget 1.0 ms.
- **Zone data written:** `ch02_haluna.json` (2 flocks / 8 gulls on tide-wall tops, house ridge ends, dock and
  net-rack posts, the stilt-house peak; 2 crab beaches / 12; 3 shoals / 38) and `ch03_saltgrass_causeway.json`
  (4 gulls on the marker posts, 8 crabs, 5 fry in the tide pool). Validated by `tools/validate_wildlife.py`
  (run from validate_data.py).
- **Zone owners (m2-slice / env-art) must add:** one `WildlifeLayer` node at the zone origin with
  `zone_id = &"ch02/haluna"` in `haluna.tscn` (and `&"ch03/saltgrass_causeway"` for the causeway, e.g. in
  GreyboxZone.build with its location_id). Not done here: those scenes are theirs.
- Review: `game/levels/_tests/wildlife/wildlife_stage.tscn`, shot `wildlife_stage` (approved, rmse 0 on recapture).

## Review log
