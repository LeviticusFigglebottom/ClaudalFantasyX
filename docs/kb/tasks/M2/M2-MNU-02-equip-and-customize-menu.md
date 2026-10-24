---
id: M2-MNU-02
title: The Equip menu (weapon and armor per hero, stat-delta preview, ability slots, Customize)
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M1-PRG-02, M1-PRG-03]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
Equipment, ability slots and Customize exist as logic (`EquipmentBag`, `EquipmentEffects`, `Customize`) with no menu, and live battles never apply worn gear (the TODO in `BattleVitals.setup`). Gear bought at the Net-Rack Forge must be wearable and must count in battle.

## Acceptance criteria
- [ ] Per hero: weapon and armor, each piece's ability slots (filled and empty).
- [ ] Choosing a piece previews the stat delta (and abilities gained or lost) before committing; refusals said in words (`equip_error`, `unequip_error`).
- [ ] Customize: craft an ability into an empty slot (`Customize.craft`), with the recipe, the items held and the shortfall shown first.
- [ ] Live battles apply worn gear (`EquipmentEffects.modifier()` between the Lattice and the vitals in `BattleVitals.setup`), with a test.
- [ ] Keyboard, controller and mouse; UiSettings honoured; screenshots; tests.

## Notes

## Review log
