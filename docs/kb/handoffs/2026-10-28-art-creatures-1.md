# Handoff — art (creatures) — 2026-10-28 #1

## Done
- **M3-CRE-645** (status review, reviewer art): polished the three Act II creatures whose first renders read plain
  at battle distance (the "parts look primitive" audit, approved PC render fce2e82).
  - **gallery_ray:** 4,504 triangles (budget 5k). Adds a keel with tubercles, pectoral bulges and grooves, eye sockets
    and brow ridges, rimmed spiracles, a barbed and banded whip tail, a darker trailing edge and freckles. The idle
    tip curl grows out along the wing. The weak point is one closed `spawn_wound` lens on the camera-side spiracle's
    shut valve (ADR 0151).
  - **glass_skate:** 3,638 triangles (budget 4k). Adds thornback rows on the midline, shoulders and tail, a `sand_wet`
    margin rim, taller darker turrets with black lid rings, and modelled spiracles.
  - **ridge_lynx:** 7,304 triangles (budget 8k). Adds a wedge muzzle, nose leather, whisker pads with spots,
    whiskers, a mouth line and a longer chin. The KO's head yaw is halved so the muzzle stays above the snow.
  - Bones, clip names and contact times are unchanged. Every clip stays grounded with no new allow-list entry.
    Sheets, the Act II README counts and materials.json `_doc`s are amended.

## In progress
- Nothing.

## Exact next step
- Run a PC render of the review shots `creature_gallery_ray`, `creature_glass_skate` and `creature_ridge_lynx`
  (HYMN_SHOTS) and refresh their baselines. The art reviewer then appends to the task's Review log. If the ray's
  freckles or the skate's thorns read too faint in the engine, raise their contrast (the ray's `freckle` mix, the
  skate's thorn heights in `thorns()`).

## Known issues
- No render was made (the session rule): the checks are numpy/PIL preview sheets from the GLB vertices, not the
  engine. The existing baselines for the three review shots will now differ.
- validate_data's one warning (haluna shrine_offering.glb listed but missing) predates this task.
- test_creature_portraits fails on the missing portrait PNGs, as before.

## Files touched
- assets_src/creatures/gallery_ray/build_gallery_ray.py, materials.json; assets/creatures/gallery_ray/gallery_ray.glb
- assets_src/creatures/glass_skate/build_glass_skate.py, materials.json; assets/creatures/glass_skate/glass_skate.glb
- assets_src/creatures/ridge_lynx/build_ridge_lynx.py, materials.json; assets/creatures/ridge_lynx/ridge_lynx.glb
- docs/kb/art/creatures/act2/gallery_ray.md, glass_skate.md, ridge_lynx.md, README.md
- docs/kb/tasks/M3/M3-CRE-645-plain-creatures-polish.md
