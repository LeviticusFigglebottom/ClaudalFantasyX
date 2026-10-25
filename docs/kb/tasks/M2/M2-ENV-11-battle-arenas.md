---
id: M2-ENV-11
title: Per-encounter battle arenas at final quality (dawn tideline beach, sunset causeway disc)
role: environment
status: review
owner_session: "env-art"
depends_on: []
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
M2-review blocker from the Lead: every fight uses the battle sandbox's greybox (sand, dais, sea). Build
per-encounter battle arenas at final quality, around the sandbox's slot layout:
- `tideline_dawn`: Haluna's beach at dawn, the first battle (`ch02` dawn, color script and haluna.md §0).
- `causeway_disc_sunset`: the Drownbell arena (haluna.md §2.2: a widened causeway disc 30 m across with a central
  sunk area; `ch03_boss` 18:15, the sun 2° over the western sea), with room and an anchor for the boss and the
  flood rig's water plane (battle_vfx.md "The Drownbell").

## Acceptance criteria
- [x] The arena contract written in `docs/kb/tech/battle_arenas.md`.
- [x] `assets/environments/arenas/tideline_dawn/tideline_dawn.tscn` and
      `assets/environments/arenas/causeway_disc_sunset/causeway_disc_sunset.tscn`, each with its own
      WorldEnvironment, Sun and dressing, a flat clear floor under every sandbox slot, and no camera.
- [x] New geometry is kit modules in `assets_src/environments/kits/haluna/` (every other kit output
      byte-identical, `verify_blender_builds --job haluna_kit`: 72 identical), with PROVENANCE rows.
- [x] Two shots (one per arena) on an Environment preview scene with the sandbox slot layout, camera framing and
      stand-ins; viewed and approved.
- [x] Unit test: each arena loads, has WorldEnvironment + Sun, a clear floor over the slots, no camera.
- [x] Swap-in note for battle-presentation and m2-slice.

## The contract (full text: docs/kb/tech/battle_arenas.md)
An arena is `assets/environments/arenas/<arena_id>/<arena_id>.tscn` with a `BattleArena` root
(`game/world/arenas/battle_arena_root.gd`) that carries its own `WorldEnvironment`, `Sun` (one DirectionalLight3D) and
dressing, built around the sandbox's slot layout at the origin. The slot markers and BattleCamera stay in the battle
scene. Within 1.0 m of every slot nothing rises over y = 0.05, and 70% of the ground there is the floor; nothing
crosses the camera-to-slot lines at chest height; no camera. Its sea is an `ArenaSea` named `Sea` that publishes
`hymn_water_level` only while visible. Optional `CameraHints` (Marker3Ds), `BossAnchor`, `FloodAnchor`.

## Swap-in note (battle-presentation `claude/battle-presentation`, m2-slice)
Battle-presentation adopted the contract at 972131e (encounter `arena` ids, `arenas.json`, its `BattleArena`
loader). Once this branch merges: repoint `arenas.json` to `assets/environments/arenas/<id>/<id>.tscn` and
re-approve `battle_arena_tideline`, `battle_arena_causeway` and `drownbell_flood` after viewing them. The loader keeps
the arena's `Sun` at the battle root, so `flood.sun_node` stays `"Sun"`. This side's root class is now
`BattleArenaRoot`, so it doesn't collide with the loader's `BattleArena`. m2-slice: nothing to wire. Full text:
`docs/kb/tech/battle_arenas.md` § Swap-in.

## Notes (2026-10-24, env-art)
- **Kit (`arenas.py`, registered in build.py):** `arena_tideline_ground` (27360 / 1984 tris), `causeway_disc`
  (57892 / 21320), `arena_causeway_flats` (38364 / 3280), `arena_causeway_arms` (23112 / 2568). The grounds use the
  new `kit_ground` material (env_ground). Every other kit .glb is byte-identical; kit_manifest.json only gains the four rows.
- **`causeway_disc` is a standalone piece** (the parent's B06 causeway field zone, M2-ENV-10, places it too):
  origin at the disc centre on the tide datum, radially symmetric (no facing needed). Paving 30.2 m across (rings
  to r 15.1 m), 31.7 m over the foundation wall (r 15.85); walked top y = 0 (flat to ±1 cm on the inner rings, the
  outer two rings tipped and some slabs missing); sunk area 7.0 m across: a step ring at -0.36 (r 2.6-3.5), the
  pool floor at -0.95, the bell's socket kerb at -0.72 (r 0.8-1.25); the wall's foot at -1.55. The arena places it
  at (0, 0, -5.5).
- **Scenes are generated** by `arena_scenes.py` from its tables. Prop heights come from the terrain functions, and
  a tools test checks the committed .tscn files are reproduced byte for byte.
- **New sky shader** `env_sky_low_sun.gdshader`: a warm horizon towards the sun's azimuth, a broad glow, planar
  cloud bands, and a third gradient stop that keeps the sunset magenta-free. Early captures were black because a
  `pow()` of a slightly negative base gave NaN in the radiance cubemap. The bases are now clamped.
- **Grades:** `zone_lut.py --grade ch02_dawn | ch03_sunset` (the noon LUT is byte-identical).
- **VegetationScatter** gains an optional `ground` (instances drop onto a mesh by TriangleMesh ray, with a height
  range) and `placed`. The default behaviour is unchanged.
- **Gotcha:** a new kit .glb's .import needs `import_script/path` set to haluna_kit_post_import.gd. Without it
  the materials don't map and the vertex masks show as albedo. import_settings.py doesn't set it.
- **Shots (viewed, approved):**
  - `battle_arena_tideline_dawn`: crisp dawn beach. The low sun from frame right throws the fighters' long
    shadows west across the sand, and the dark stand-ins read hard against the pale sand. Behind them are the
    swash and lagoon (right), the dune with palms and saltgrass (left), and pilgrim posts leading north to the
    headland. The sky is a soft peach-lilac dawn. It could be richer, but it does not steal from the fight.
  - `battle_arena_causeway_disc_sunset`: ember sky with the horizon band, and the ring paving with the sunk pool
    holding water behind the bell. The causeway arm runs to the shrine islet with its palms on the horizon. The
    tide flats show sandbars. The cyan bell stand-in pops. The party reads as dark figures on the lit orange
    paving, with party slot 0 inside the bell's long 2° shadow (noted as a known limit).
- **Gates:** gdlint and gdformat clean (game, tests); validate_data 0/0; taskboard --check OK; Godot tests
  battle_arenas 7/7, vegetation 17/17, water 31/31; tools unittest 546 OK (393 s); verify_blender_builds
  haluna_kit 72 identical; the two shots compare at RMSE 0.
- **Known limits:** no character rim (stand-ins aren't on light layer 2). Arena stone stays on the High weathering
  tier on every preset. About 6.7 MB of new .glb files (repo binaries risk).

## Review log
