---
id: M3-MNU-03
title: Key items view on the Items page (SPEC §6.11 "full item/key-item menu")
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-03]
milestone: M3
request-from: ui
reviewer: narrative
---
## Goal
SPEC §6.11 asks for a full item and key-item menu. Key items are listed in the bag today but have no view of their own. Add a Key Items view to the Items page: each key item with its description and where it came from or what it opens, if data says so.

## Acceptance criteria
- [x] A Key Items tab or view on the Items page; no use action; descriptions from item data.
- [x] Keyboard, mouse and pad parity; screenshot viewed; tests.

## Notes
- **Built:** `ItemsMenuModel` gains `view` (VIEW_BAG, VIEW_KEY), `next_view`, `view_label`; the bag leaves key items out, the key view lists `Inventory.ids_in(&"key")` with no count column, and `item_line` says "A key item. It is kept, not used." there. `ItemsMenu` draws Bag / Key Items tabs in the title row (`items_menu.json` `tabs`), switches on ui_page_up / ui_page_down (the shoulders) or a tab click, hides the sort line on the key view, and has a help line per view. Loc keys appended to menus_items.csv (`ITEMS_MENU_VIEW_*`, `ITEMS_MENU_HELP_KEY`, `ITEMS_MENU_KEY_NOTE`, `ITEMS_MENU_KEY_EMPTY`); `ITEMS_MENU_HELP` now names Page Up and Down.
- **No invented data:** items.json key rows carry only name_key and desc_key, so the view shows the description only (chapter flow files grant some key items, but that is not item data).
- **Changed behaviour:** Page Up / Down no longer jump a page in the bag (the wheel and Up / Down remain); key items left the bag view.
- **Screens:** `items_menu` and `items_menu_use` re-rendered (tabs; the bag without the lantern) and viewed; new `items_menu_key` (four key items, cursor on Glass Net-Float) viewed and baselined.

## Review log
