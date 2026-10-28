---
id: M3-RND-21
title: A volumetric smoke column for the Brine Shoals' burning camp (replaces the kit's stand-in plume shader)
role: rendering
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC, claude/env-art-b; rendering's zone and kit looks, Lead 2026-10-28)"
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
- [x] A smoke column that reads at 5–150 m in the `ch06` light: grey to grey-brown, darker core, lit tops,
      glowing when backlit, warmed at the base by the fire; bends downwind (the preview's wind is toward 240°).
- [x] Deterministic under the capture (no `TIME`; `hymn_wind_time` or the capture's held clock).
- [ ] Works on the Low preset (a fallback is fine) and costs under 0.3 ms at High 1440p for four columns.
- [ ] Drops into `game/levels/_tests/brine_shoals_kit/` (the four plumes and two lying bands in
      `brine_shoals_layout.json`), with the two baselines re-approved after viewing.

## Notes
- The stand-in's parameters are in `assets_src/environments/kits/brine_shoals/bs_materials.py` (`bs_smoke`).
- Smoke must never use glimmer colours or rising gold motes (references.md §1.4 rule 10).

## Notes (env-art-b, 2026-10-28)
- `SmokeColumn` (`game/vfx/smoke/`, data `game/data/vfx/smoke_column.json`, docs `docs/kb/tech/smoke.md`) is a raymarched column in a bounding box. It is drawn on the box's back faces without a depth test and clipped by the depth buffer, so there are no shells up close and the smoke reads from inside the column. It is grey to grey-brown, with a darker core, lit tops, a backlit glow, a fire-warmed base, and a downwind lean. The billows rise on `hymn_wind_time`.
- It replaces the shells in `ch06/brine_shoals`: ZoneKitDressing's new `smokes` rows, on the Smoke block.
- Viewed: `ch06_brine_camp` at clocks 40 and 44, and `ch06_brine_road`. Tests: `tests/unit/test_smoke_column.gd`.
- **Low preset:** 12 steps; it still reads as a column.
- **Cost:** unmeasured, so that criterion is still open. It goes to the PC's QA pass, as M3-RND-26's did.
- **Still open:**
  - The kit preview drop-in and its two baselines are env-art's, requested in **M3-ENV-1324** (the camp arenas too).
  - The tier hook is the Architect's, requested in **M3-ARC-1324**.

## Review log
