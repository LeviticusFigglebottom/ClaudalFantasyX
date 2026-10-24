---
id: M2-UI-05
title: Shop and inn menus for Haluna (the slice's B03 systems on show)
role: ui
status: todo
owner_session: ""
depends_on: [M1-PRG-02]
milestone: M2
request-from: cinematics
---
## Goal
Request from the m2-slice track. The beat sheet's B03 puts "the equipment shop, the inn, and the first save shrine" on show in Haluna. The shrine exists. The shop logic exists (`game/progression/shop.gd`, `game/data/items/shops.json`), but there's no shop UI and no inn.

## Acceptance criteria
- [ ] A shop menu over `Shop` (buy and sell, prices in lume, refusal reasons shown) that a field Interactable opens with a payload such as `{"shop": "<shop id>"}`.
- [ ] An inn: rest for a price, which heals the party like a shrine, with no save.
- [ ] Loc keys for every string; tests.
- [ ] Cinematics then places a shopkeeper and an innkeeper in Haluna (M2-FP-14 or a follow-up).

## Review log
