---
id: M2-UI-21
title: Area title cards when the party enters a new location
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Intro audit item 4: entering a location names it, so the pilgrimage reads as a journey through places.

## Acceptance criteria
- [x] `AreaTitleCard`: the location's name (locations.json `name_key`, found by the scene path) in the title serif over a feathered band with a centred gold rule; fades in (rising; reduced motion: no rise), holds, fades out.
- [x] Shown once per location change: not again on a reload of the same location; the title screen forgets, so New Game and Continue show it. Test rooms (`skip_locations`) get none.
- [x] Waits for the field to take input (an opening cutscene or conversation delays it); a menu ends it.
- [x] Attached through `FieldHud.attach`; data `game/data/ui/area_title.json`; tests; a shot.

## Notes
`game/ui/field/area_title_card.gd`, `tests/unit/test_area_title_card.gd`, shot `field_area_title` (driver in `game/levels/_tests/ui_shots/`). `TitleMenu._ready` calls `AreaTitleCard.forget()`.

## Review log
