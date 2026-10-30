---
id: M3-UI-204
title: "Greybox layouts: save shrines that save and travel, and Tamsule's trader, inn and shrine"
role: cinematics
status: review
owner_session: act1-chapters
reviewer: ui
depends_on: [M3-C07-05]
milestone: M3
request-from: ui
---
## Goal
A greybox zone's shrine trigger today only heals and checkpoints (`{"beat": "shrine"}` → `rest`). Players get no save menu, no attunement and no shrine travel list. ui-menus added a zone-agnostic hook, `ShrineServices` (`game/world/save_shrine/shrine_services.gd`, mounted by FieldController next to TownServices). A trigger whose payload has `"save_shrine": "<network id>"` gets everything a placed SaveShrine does: the heal, the respawn point, attunement, the save menu, and the travel list after it. The zone's own keys on the same trigger (a `beat`) still run, so the checkpoint can stay.

M3-C07-05 also needs Tamsule's shop, inn and shrine in the port (act1_ch07.md B02). Its data rows are in: `tamsule_trader` and `tamsule_inn` in `shops.json`.

These are layout edits in zones you own, so this is a request.

## Acceptance criteria
- [ ] **Brine Shoals (Ch6):** add `"save_shrine": "brine_shoals_camp"` to the `shrine` trigger's payload, keeping `"beat": "shrine"`. The network row is already in `locations.json` (spawn `RidgeCamp`).
- [ ] **Tamsule (Ch7)**, in `tamsule_layout.json`:
  - a `Shrine` spawn by a new shrine trigger:
    `{"id": "shrine", "activation": "interact", "prompt_key": "FIELD_PROMPT_REST", "requires_flag": "ch07_arrived", "payload": {"save_shrine": "tamsule_shrine"}}`;
  - a trader: `{"id": "trader", "activation": "interact", "prompt_key": "SHOP_PROMPT", "requires_flag": "ch07_arrived", "payload": {"shop": "tamsule_trader"}}`;
  - an inn: `{"id": "inn", "activation": "interact", ..., "payload": {"inn": "tamsule_inn"}}`;
  - the Reefball outfitter (ADR 0040; act1_ch07.md B02's outfitter): `{"id": "outfitter", "activation": "interact", "prompt_key": "SHOP_PROMPT", "requires_flag": "ch07_arrived", "payload": {"reefball_outfitter": "tamsule"}}`;
  - the `locations.json` shrines row `{"id": "tamsule_shrine", "location_id": "ch07/tamsule", "spawn": "Shrine"}`. Add it with the spawn, because the validator checks that the spawn exists.
  - Placement is yours. B02's market boats and stilt lanes read naturally.
- [ ] **Corrow (Ch8):** a `Shrine` spawn by the `shrine` trigger at (-30, 19.2), plus `"save_shrine": "corrow_shrine"` on its payload, plus the row `{"id": "corrow_shrine", "location_id": "ch08/corrow", "spawn": "Shrine"}`.
- [ ] The Brightwater ferry's shrine stays heal-only, because a ship under way is no travel destination.
- [ ] After the edits, tell ui-menus. The map POIs follow: `game/data/ui/zone_maps.json` gets a shrine, a shop and an inn for Tamsule, checked by `tools/tests/test_zone_map_pois.py`.
- [ ] **Coilspire (Ch8):** the tier-2 niche gives the needle: `Ch08CoilspireZone._on_niche` calls `give({"sailmakers_needle": 1})` (ADR 0040; the item is in `items.json`).

## Notes
- The hook ignores an id that has no `shrines` row (it logs a warning), so payload and row can land in either order.
- Travel goes through the location registry. A destination is offered once it is attuned, in attunement order, with "Stay here" last (ShrineTravelMenu).
- Tests: `tests/unit/test_shrine_services.gd`, `tests/unit/test_shrine_travel.gd`.

- **act1-chapters, 2026-10-30, done:**
  - **Brine Shoals:** the `shrine` trigger carries `"save_shrine": "brine_shoals_camp"` beside its beat.
  - **Tamsule:**
    - A `Shrine` spawn at (12, 0, 5), and the shrine trigger at (12, 0, 3) with `tamsule_shrine`.
    - The trader at (−10, 0, 6) on the market's west edge, and the Reefball outfitter at (4, 0, 4).
    - The inn at (−24, 0, 6) on the stilt lane, by the elder.
    - The `tamsule_shrine` locations row.
  - **Corrow:** a `Shrine` spawn on the wall-head by the shrine (the shrine moved to the Bastion with env-art-b's
    relayout). `"save_shrine": "corrow_shrine"` on its payload, and the locations row.
  - **Brightwater:** its shrine stays heal-only.
  - **Coilspire:** `_on_niche` gives `sailmakers_needle`.
  - **Tests:** shrine (55), ch06, ch07, ch08, coilspire; tools zone_map_pois and chapter_flow; validate.
  - **For ui-menus:** Tamsule's map POIs (shrine, shop, inn) can follow at the points above.

## Review log
