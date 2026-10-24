---
id: M3-RND-21
title: A volumetric smoke column for the Brine Shoals' burning camp (replaces the kit's stand-in plume shader)
role: rendering
status: todo
owner_session: ""
depends_on: [M3-ENV-02]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
The Ch6 raid burns a Saltwright camp in daylight (brine_shoals.md, colour script `ch06`). M3-ENV-02 ships the
kit's `smoke_plume` mesh (three nested, bent, open tubes, UV.y = height 0..1, UV2.y a per-plume offset) drawn by
`game/shaders/environment/env_smoke_plume.gdshader`: a simple unshaded column (N·V soft silhouette, world fBm
billows on `hymn_wind_time`, forward scatter toward the sun, a near-camera fade). It reads at range (shots
`brine_b01_arrival`, `brine_b05_barge_channel`) but shows its shells up close and cannot take shadow or the
volumetric fog's light.

## Acceptance criteria
- [ ] A smoke column that reads at 5–150 m in the `ch06` light: grey to grey-brown, darker core, lit tops,
      glowing when backlit, warmed at the base by the fire; bends downwind (the preview's wind is toward 240°).
- [ ] Deterministic under the capture (no `TIME`; `hymn_wind_time` or the capture's held clock).
- [ ] Works on the Low preset (a fallback is fine) and costs under 0.3 ms at High 1440p for four columns.
- [ ] Drops into `game/levels/_tests/brine_shoals_kit/` (the four plumes and two lying bands in
      `brine_shoals_layout.json`), with the two baselines re-approved after viewing.

## Notes
- The stand-in's parameters are in `assets_src/environments/kits/brine_shoals/bs_materials.py` (`bs_smoke`).
- Smoke must never use glimmer colours or rising gold motes (references.md §1.4 rule 10).

## Review log
