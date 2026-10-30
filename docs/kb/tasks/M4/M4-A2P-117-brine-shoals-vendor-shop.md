---
id: M4-A2P-117
title: "Request: the Brine Shoals camp vendor sells as the Ch4 ferry's \"Purser's Chest\""
role: progression
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To Progression (economy: `game/data/items/**`), from the Lead's Act I read-through. The Brine Shoals camp vendor
(`game/levels/ch06/brine_shoals/brine_shoals_layout.json`, trigger `vendor`, `"shop": "brightwater_purser"`) opens the
Ch4 ferry's shop, titled "The Purser's Chest" (`game/data/items/shops.json:6`, `location: brightwater_ferry`). On a
wreck-ridge camp, act1_ch06 B08 has "a travelling vendor's boat".

## Acceptance criteria
- [ ] A `brine_shoals_vendor` shop with its own name (loc key) and stock tier.
- [ ] act1-chapters points the trigger at it (one-line layout change; noted on M4-A2P-116).

## Review log
