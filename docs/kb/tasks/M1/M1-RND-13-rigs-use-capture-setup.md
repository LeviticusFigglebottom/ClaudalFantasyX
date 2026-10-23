---
id: M1-RND-13
title: Move test rigs' capture detection into shots.json setup
role: rendering
status: doing
owner_session: "worktree-agent-aa764c62452184711"
depends_on: [M1-QA-04]
milestone: M1
request-from: "qa"
---
## Goal
M1-QA-04 added a per-shot `setup` block to `tests/screenshots/shots.json`, covering globals, node properties, viewport properties and `time_scale` (`docs/kb/qa/screenshots.md`, "Per-shot setup"). The rigs can now drop their `CAPTURE_SCENE` checks and their camera-to-mood detection: `water_test_rig.gd`, `undertow_test_rig.gd`, and (Environment) `haluna_mood.gd`.

## Acceptance criteria
- [ ] Each affected shot declares its holds in `setup`: `hymn_wind_time`, `"viewport": {"use_taa": false, "screen_space_aa": 1}`, the storm clock, and the mood as an exported property.
- [ ] The rigs no longer test `scene_file_path == CAPTURE_SCENE`.
- [ ] Every affected shot still compares at RMSE 0.0, or any change is justified and re-approved after a look.

## Notes
- QA measured on `water_shallows`: `"globals": {"hymn_wind_time": 40.0}` reproduces the rig's own hold exactly (RMSE 0.0).

## Review log
