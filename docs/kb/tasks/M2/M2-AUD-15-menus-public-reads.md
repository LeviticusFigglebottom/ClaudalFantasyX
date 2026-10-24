---
id: M2-AUD-15
title: "Request (menus): public reads so refusals, Customize's arming and board pans can be heard"
role: ui
status: review
owner_session: "menus (claude/menus)"
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
- [x] A public read (for example `is_refused()`, `is_armed()`, `is_dragging()`) or a signal for each moment above.
  Audio then adds a watch row in game/data/audio/ui_sfx.json.

## Notes
- 2026-10-24 (menus): read-only accessors, no behaviour change:
  - `ItemsMenu.is_refused()`: the line on show is a refused use.
  - `FormationMenu.is_refused()`: a refused pick or move (alongside the existing `plan_refused()`, which is the plan under the cursor).
  - `EquipMenu.is_armed()`: the first of Customize's two Confirms is in; `EquipMenu.is_refused()` too (equip, unequip or craft refusals).
  - `LatticeBoardView.is_dragging()`: a pan by hand (true from the first motion past `drag_px` with the button held until the release); the camera following the cursor never sets it.
  - ZoneMapView is the UI track's, not this track's: no change here.
  - Tests: assertions in test_items_menu, test_equip_menu, test_formation_menu, and a new drag test in test_lattice_menu. Audio adds its watch rows in game/data/audio/ui_sfx.json.

## Review log
