# 0040 — No accessory slot; equipment stays weapon plus armor with ability slots

- **Status:** accepted
- **Date:** 2026-10-27
- **Roles affected:** ui-menus (progression, menus), act1-chapters, combat, design
- **Author role:** lead

## Context
ui-menus asked for a ruling. Three Act I items have no home because `equip_slots` is only weapon and armor:
- the Oruvel Float;
- the sailmaker's needle;
- the Reefball outfitter's stock.

SPEC §6.5 defines equipment as **weapons and armor carrying up to four ability slots**, customised in the Customize menu. Pillar 4 (tactical clarity) favours a small, readable loadout.

## Options
1. Add a third accessory slot. That departs from §6.5, adds a third axis to every balance table, and opens a menu page for three items.
2. Keep two slots, and give each item a home inside the existing systems.

## Decision
Option 2. Equipment stays weapon plus armor (SPEC §6.5).
- **The Oruvel Float:** a key item. Its effect is a field ability or story gate, checked through `Game.get_flag`/inventory, never equipped.
- **The sailmaker's needle:** a Customize material. It crafts an ability into an empty slot at a defined cost (for example a sea or water ability), in line with §6.5's "crafts abilities ... using items".
- **The Reefball outfitter's stock:** Reefball-only gear, held in the Reefball team or loadout data the minigame owns (`game/minigames/reefball/**`) and shown on the Reefball menus. It never touches battle equipment.

## Consequences
- The battle equipment model and balance tables don't change.
- ui-menus implements the three homes above. act1-chapters adjusts any dialogue or flow that says "equip" for these items.
- If a future act truly needs a third slot, it needs a superseding ADR and a SPEC change.
