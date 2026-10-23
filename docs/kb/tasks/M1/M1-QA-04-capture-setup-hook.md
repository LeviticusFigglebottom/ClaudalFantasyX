---
id: M1-QA-04
title: Screenshot capture: per-shot setup hook
role: qa
status: todo
owner_session: ""
depends_on: [M1-QA-01]
milestone: M1
request-from: "rendering"
---
## Goal
A per-shot `setup` dictionary in shots.json (globals, node properties, time) instead of camera-detection hacks in scenes.

## Acceptance criteria
- [ ] setup supports shader globals, node property overrides, and a fixed time
- [ ] Existing shots unchanged (baselines still pass)
- [ ] Documented in qa/screenshots.md

## Notes
-

## Review log
