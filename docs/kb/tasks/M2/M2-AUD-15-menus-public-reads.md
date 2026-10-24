---
id: M2-AUD-15
title: "Request (menus): public reads so refusals, Customize's arming and board pans can be heard"
role: ui
status: todo
owner_session: ""
depends_on: [M2-AUD-14]
milestone: M2
request-from: audio
---
## Goal
Audio listens to the menus and never edits them (ADR 0031). M2-AUD-14 found four moments it cannot hear, because the
state is private on claude/menus:
- ItemsMenu: a refused use. The result exists only in the page's private `_notice`.
- FormationMenu: a refused pick or move (also only in `_notice`).
- EquipMenu Customize (RECIPES): the first, arming Confirm. It exists only in `_armed`.
- LatticeBoardView: a drag pan. `pan` also moves on every cursor move, and the drag flag is private.
- ZoneMapView: the map doesn't pan at all yet. If it gets a pan, audio already has a sound for it (`ui_map_pan`).

## Acceptance criteria
- [ ] A public read (for example `is_refused()`, `is_armed()`, `is_dragging()`) or a signal for each moment above.
  Audio then adds a watch row in game/data/audio/ui_sfx.json.

## Notes

## Review log
