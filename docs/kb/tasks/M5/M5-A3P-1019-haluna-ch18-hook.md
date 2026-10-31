---
id: M5-A3P-1019
title: "Request (architect): a story hook on Haluna for Ch18 (Toma's lifting on the beach, Asha's heirloom)"
role: architect
status: todo
owner_session: ""
depends_on: [M5-A3P-1004]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
Two Ch18 scenes are at `ch02/haluna`:
- `ch18_backs_to_the_water`: Haluna lifts its own dead the Kirru way, with Toma leading (act3_ch18.md §4, optional and flagged; sets `ch18_haluna_lifted`, read by Ch20's Ilun and the Ending's beach). Shots K15–K17; marks `shore_line`, `village_back`, `shore_line_crowd`, `wake_wall`, `sea`.
- `ch18_heirloom_asha`: Imra's lantern-staff, at the Velamir house.

Haluna runs on HalunaStory, which isn't data-driven (ADR 0035 says new chapters use ZoneStory and must not copy HalunaStory). So ChapterRegistry's shared-zone rule (chapter_flow.md "Shared zones", M5-A3P-1001) can't reach it.

## Ask
One of these (the architect's call):
- **(a)** HalunaStory hands over to ZoneStory from `ch18_started` on: a ZoneStory child that plays `ch18.json`'s `ch02/haluna` block, with the layout triggers it needs.
- **(b)** HalunaStory gains a small data hook for Act III triggers.

Story then adds the triggers, marks and shots, and the `ch18.json` block.
`kite.json` already lands at `ch02/haluna` (Beach).

## Review log
