---
id: M2-UI-201
title: "Bestiary page and Read panel: show the creature's live portrait (CreaturePortrait)"
role: ui
status: review
owner_session: "claude/ui"
reviewer: character
depends_on: [M2-CRE-10]
milestone: M2
request-from: character
---
## Goal
The creatures track (claude/creatures) ships `game/creatures/creature_portrait.tscn` (`CreaturePortrait`): a live 3D
portrait of an enemy's battle model in its own small world with a transparent background. Put it on the bestiary
page (`game/ui/bestiary/`) and, if it fits, the Read panel (`game/ui/battle/read_panel.gd` / `enemy_page_view.gd`).

## Acceptance criteria
- [x] The bestiary page shows the selected entry's portrait: instance the scene, call `show_enemy(id)`; when it
      returns false (no model yet) the page keeps its current layout.
- [x] A never-read entry shows the portrait as a silhouette or not at all (UI's call; the portrait has no
      silhouette mode yet: ask character if you want one).
- [x] The bestiary shots (`bestiary_menu`, and the field menu's if it shows the page) re-approved after viewing.

## Notes
- Renumbered at the Lead's big7 merge (2026-10-24): filed by creatures as M2-UI-16, which collided with claude/ui's M2-UI-16 (objective system, filed later but already merged and referenced). M2-UI-26 is the next id free across all branches. Older handoffs still say M2-UI-16.
- API: `show_enemy(id: StringName) -> bool`, `clear()`, `has_creature()`. Framing, clip and time come from
  `game/data/creatures/creatures.json` `portrait` (defaults, per-creature overrides). Default size 256×256; the
  container stretches its viewport, so size it in the layout.
- Cost: one SubViewport rendering a ~5–20k-triangle model. Disable it (`clear()`) when the page closes.
- Review shot of all portraits: `creature_portraits` (claude/creatures).

## Implementation notes (claude/ui, 2026-10-24; reviewer: character)
- `game/ui/bestiary/bestiary_portrait_slot.gd` (`BestiaryPortraitSlot`) instances `creature_portrait.tscn` and calls
  `show_enemy(id)`. BestiaryMenu puts the EnemyPageView and the slot in one VBox, so the slot takes only the height
  the page leaves under the text, and the portrait sits square in its bottom-right corner (`bestiary_menu.json →
  portrait`: `min_px` 160, below which it hides; `max_px` 400). It can never cover text at any text size or language.
  When `show_enemy` returns false (no model), the slot is empty and the page layout is unchanged.
- **Never-Read entries: a silhouette (UI's call).** The party has met the foe (that is how it is in the book), so its
  shape is no secret, but a Read is what shows its colours, which fits the "Not Read" tag in the list. Done UI-side
  with `game/ui/shaders/silhouette.gdshader` on the portrait container (every drawn pixel takes the theme role
  `silhouette_role`, `outline` = night sky, at `silhouette_alpha`, coverage kept), so the portrait needs no
  silhouette mode and character has nothing to add.
- `BestiaryMenu.close()` and an empty book call `clear()` (frees the model, stops the SubViewport).
- **Read panel: no portrait.** In battle the foe already stands on the stage beside the panel, the panel is sized to
  leave the timeline and the command menu uncovered (M2-UI-29 pins), and a second SubViewport in battle costs render
  time for nothing new. `read_panel.gd` / `enemy_page_view.gd` are unchanged.
- Captures: the portrait holds creatures.json's `portrait` clip at `clip_time` (paused), so two `bestiary_menu`
  captures were byte-identical (`cmp`); no capture-time fix needed. `bestiary_menu` re-approved after viewing (the
  Lantern Eel in colour bottom-right; the Reef Crab silhouette checked in a scratch capture). `battle_read_panel` and
  `field_menu` captured and compared at rmse 0 (unchanged; the field menu shot does not open the bestiary), so not
  re-approved.
- Tests: `tests/unit/test_bestiary_portrait.gd` (colour vs silhouette and the theme tint, follows the cursor, no model
  shows nothing, close clears and stops the viewport, empty book, square corner fit between min_px and max_px).
  `test_pseudo_loc_screens` (M2-UI-28) and `test_aspect_layouts` (M2-UI-29) stay green.
- Docs: `docs/kb/tech/ui.md` (module table and the Bestiary menu bullets).
- **Renumbered again (Lead merge, big8, 2026-10-24):** big7's M2-UI-26 collided with claude/ui's M2-UI-26 (input parity audit, ADR 0036). Now M2-UI-28, the next id free across all branches.
- **Renumbered to M2-UI-201 (ui-menus, 2026-10-25):** M2-UI-28 collides with pseudo-loc's M2-UI-28. M2-UI-201 is from the ui-menus id block, so it cannot collide again.

## Review log
