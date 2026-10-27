---
id: M3-AUD-811
title: "Request (environment): mark wood and shallow-water ground so the field steps change surface"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
reviewer: audio
depends_on: [M3-AUD-802]
milestone: M3
request-from: audio
---
## Goal
FootstepAudio (M3-AUD-802) plays the ground's own steps: sand, stone, wood and shallow water, walk and run. A scene has
one default surface (game/data/audio/footsteps.json `scenes`, e.g. Haluna is sand). Wood and water need the ground
marked, and no level marks any yet. Audio is listen-only and never edits a level.

## Acceptance criteria
- [x] Areas over wood and shallow water (Haluna's dock and jetty, its shallows, the causeway's planks and pools, and
  later zones' piers and fords). Haluna done (env-art); the causeway is slice-polish's scene (note below). Each is an Area3D (or any node with CollisionShape3D children) in group
  `audio_surface_wood` or `audio_surface_water`, or in group `footstep_surface` with a `surface` meta. An optional
  `surface_priority` int meta decides overlaps: a dock inside a shallows area should be higher.
- [x] The shapes cover where the hero's feet go. Height matters: the feet must be inside the shape.

## Notes
- Names are in footsteps.json `surface_areas`. hero-integration confirmed the body and contacts side (M3-AUD-810).

- **env-art, 2026-10-27:** Haluna.
  - **How.** HalunaDresser builds the areas from the layout's new `footstep_surfaces` key. Each `areas` row is a box
    (`size`, centred at `center` in the frame of `at` turned by `yaw_deg`) with `surface` and `priority`. Each area
    is an Area3D in group `footstep_surface` with the `surface` and `surface_priority` metas. The areas sense nothing
    and sit under a plain Node, `FootstepSurfaces`, which HalunaCollision skips.
  - **Rows.**
    - `dock`: wood, priority 2, in `dock_haluna`'s own frame: the deck at 1.4 m, the box y 1.1–2.1, 38.6 × 4.4 m, so
      the end platform is inside.
    - `lagoon_shallows`: water, priority 1: everything below mean sea level (y −1.5 to 0) over 600 m. Haluna has no
      separate jetty: the dock is the one pier.
  - **Test.** `tests/unit/test_haluna_footstep_surfaces.gd` asks FootstepAudio itself: the deck is wood at three
    points and at the end platform; wading beside the dock is water; the beach above the water stays sand.
  - **For slice-polish:** the causeway (`ch03/saltgrass_causeway`, your scene) is laid stone (`causeway_slab_*`),
    which is already the scene's default, so only its pools want `water` areas. The same rows work in any scene: an
    Area3D in `footstep_surface` with a `surface` meta. Say if you'd rather env-art generate them from
    `saltgrass_causeway_layout.json`.
  - **Later zones** (piers and fords): the zones' kits get rows when their drop-ins are built.

## Review log
