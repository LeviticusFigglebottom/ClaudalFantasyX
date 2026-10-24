---
id: M2-UI-16
title: Objective system (data-driven objective lines from story flags)
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
The human's top priority: the playable intro never tells the player where to go. Our design is original; the bar is that a player always knows the next step. Objectives come from data keyed by story flags (the slice beats B01–B11, docs/kb/story/beats/vertical_slice.md).

## Acceptance criteria
- [x] `game/data/flow/objectives.json`: ordered rows `{id, line_key, requires: [flags], until: flag, zone?: zone id, target?: {zone, poi}, side?: bool}`; validated (flags declared, loc keys exist, targets name a POI in zone_maps.json).
- [x] `ObjectiveTracker` (node-free): the current main objective for a zone and the side ones, from a flag reader; tests over every slice step.
- [x] First-pass rows for the slice; a request task to m2-slice to keep them current as beats change.

## Notes
objectives.json + check_objectives in validate_data; ObjectiveTracker (node-free) with tests over every slice step (test_objective_tracker.gd); first-pass rows B01-B11; request task M2-FP-28 (filed as M2-FP-25; renumbered at the big7 merge) to m2-slice.

## Review log
