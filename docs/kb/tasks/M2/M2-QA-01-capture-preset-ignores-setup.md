---
id: M2-QA-01
title: "capture_preset ignores a shot's setup block (globals, node properties, viewport), so its GPU frames aren't the shot"
role: qa
status: todo
owner_session: ""
reviewer: rendering
depends_on: []
milestone: M2
request-from: "rendering"
---
## Goal
Found by M2-RND-10 on the PC GPU. `tools/gpu_bench/capture_preset.tscn` renders a shot from
`tests/screenshots/shots.json` under a graphics preset, but it never applies the shot's `setup` block. The capture
rig (`tests/screenshots/capture.tscn`, through `CaptureSetup`) does apply it.

What that does:
- Shots that pin a mood, a storm preset, `unbinding`, `exposure_flash` or `hymn_wind_time` render differently
  through `capture_preset`. One example: `undertow_landfall_ch08` came out at 0.312 mean OkL against the capture
  rig's 0.263, at a different storm distance.
- `capture_preset` frames compared with the lavapipe baselines, or with each other across tools, can mislead. The
  `--node-set` workaround needs values in `str_to_var` form (`&"night"`, not `night`).

## Acceptance criteria
- [ ] `capture_preset` applies a shot's `setup` (globals, nodes, viewport, time_scale) the way `capture.gd` does
      (reuse `CaptureSetup`). The preset is applied after the setup, and `--node-set` overrides go on top.
- [ ] A test pins it: a shot with a `nodes` setup renders the same node values through both tools.
- [ ] `--node-set` documents the `str_to_var` value form, or accepts bare strings.

## Review log
