---
id: M2-UI-06
title: Shop and inn menus for Haluna (the slice's B03 systems on show)
role: ui
status: review
owner_session: "m2-slice subagent (M2-UI-06)"
depends_on: [M1-PRG-02]
milestone: M2
request-from: cinematics
reviewer: progression
---
## Goal
Request from the m2-slice track. The beat sheet's B03 puts "the equipment shop, the inn, and the first save shrine" on show in Haluna. The shrine exists. The shop logic exists (`game/progression/shop.gd`, `game/data/items/shops.json`), but there's no shop UI and no inn.

## Acceptance criteria
- [x] A shop menu over `Shop` (buy and sell, prices in lume, refusal reasons shown) that a field Interactable opens with a payload such as `{"shop": "<shop id>"}`.
- [x] An inn: rest for a price, which heals the party like a shrine, with no save.
- [x] Loc keys for every string; tests.
- [ ] Cinematics then places a shopkeeper and an innkeeper in Haluna (M2-FP-14 or a follow-up).

## Notes
- **What.** `game/ui/shop/`: `ShopMenu` + `ShopMenuModel` (Buy / Sell / Leave; stock with "Held N" and the price; the sell page lists the bag and every owned piece with its wearer; Left and Right set how many; every refusal from `Shop.*_error` is said in words, in the danger color, with its numbers), `InnMenu` + `InnMenuModel` (Rest for the price, Leave; the line says an inn does not save), the shared base `TownMenu` (own CanvasLayer 60, pauses the tree like FieldMenu/SaveMenu), and `TownServices`, the zone-agnostic hook: `FieldController._ready` adds it as child `TownServices`, it listens to `FieldEvents.INTERACTED` and opens a menu for `{"shop": id}` / `{"inn": id}` payloads, ignoring everything else. HalunaStory is untouched. Layout: `game/data/ui/shop_menu.json`. Docs: docs/kb/tech/ui.md § Shops and inns; economy.md (Haluna's inn line).
- **Inn logic.** `Inn` (`game/progression/inn.gd`) over a new `shops.json` `"inns"` list (`ItemDB.inns`). A rest pays `price` and requests `EventBus.party_full_heal_requested(inn id)`, the shrine's own heal (`Game.heal_party`: full HP/MP, `shrine_cures`). No save, no shrine flag, no respawn change (tested). Haluna's row: `haluna_inn`, "The Mooring Lamp", opens on `ch02_met_asha`, 30 lume (placeholder for Combat/Progression to tune). Validator: `inns_errors` / `check_inns` in tools/validate_data.py, tests in tools/tests/test_inns_validate.py.
- **Bug fixed on the way.** `FlagReader.from_access(GameFlagAccess.new())` (the call economy.md recommends) read every flag as unset: a Callable doesn't keep its RefCounted alive, so the access was freed at once. `FlagReader` now holds `access`. Test in test_inn.gd.
- **Payloads for Haluna (for the m2-slice track to place):** shopkeeper `{"shop": "haluna_market"}` (items) and/or `{"shop": "haluna_forge"}` (the equipment shop, "The Net-Rack Forge"), `prompt_key = "SHOP_PROMPT"`; innkeeper `{"inn": "haluna_inn"}`, `prompt_key = "INN_PROMPT"`. All three open on `ch02_met_asha` (a closed one opens and says why). Don't add `dialogue` to the same payload (HalunaStory would bark under the menu).
- **Gates.** gdformat/gdlint clean (369 files); validate_data 0 errors / 0 warnings; taskboard --check OK; `python3 -m unittest discover -s tools/tests` 501 OK; Godot full suite 1473 run, 0 failed; coverage OK within baseline (game/battle 99.95%, game/progression 96.69%; inn.gd 100%). Screenshots: new `shop_menu_buy`, `shop_menu_sell`, `inn_menu` baselines approved after viewing; `field_menu`, `field_menu_swell_modes` (rmse 0) and `save_shrine_field` (0.0016) unchanged.

## Review log
