---
id: M1-RND-05
title: Graphics quality presets backend
role: rendering
status: review
owner_session: rendering-stream-1
reviewer: environment
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §4.2 settings: GI, shadows, volumetrics, SSR, SSAO/SSIL, render scale/FSR, AA.

## Acceptance criteria
- [x] Low/Medium/High/Ultra presets as data (`game/data/settings/graphics_presets.json`, with per-setting option lists)
- [x] Applied at runtime to Environment and viewport settings (`GraphicsSettings.apply()` / `execute()`, plus RenderingServer globals and the `gi_voxel` VoxelGI group)
- [x] Unit-tested mapping (`tests/unit/test_graphics_settings.gd`, 19 tests; pure `plan()` asserted headlessly)

## Notes
- Delivered 2026-10-22 by rendering-stream-1. The API, gate semantics, verified 4.6 API names, and the per-preset budget are in `docs/kb/tech/graphics_settings.md`. **The budget numbers are estimates.** Nothing has been measured on a GPU yet (M1-QA-01).
- A custom-override layer sits on top of the preset and persists to `user://settings.cfg` section `[graphics]` (other sections are preserved).
- Every planned API name, constant, and argument count is re-verified against the running Godot through ClassDB in CI.
- Follow-ups for other roles: loc rows for the `*_key` fields (Systems/UI), VoxelGI nodes tagged `gi_voxel` (Environment), and the settings-menu UI (UI).
- Reviewer (Environment): check that gate semantics ("a setting only turns an authored feature off") and the GI ceiling (off < voxel_gi < sdfgi) fit how zones will author GI, fog, and SSR.

## Review log
