---
id: M3-UI-209
title: "Request: Act II greybox triggers for the shops, inns and save shrines (Quellan, Ansedra, Hollowmere, and the temple shrines)"
role: cinematics
status: blocked
blocked-by: ADR 0041
owner_session: ""
reviewer: ui
depends_on: [M4-C12-02, M4-C13-02, M4-C14-02]
milestone: M4
request-from: ui
---
## Goal
The Lead routed "the Act II shops, inns and shrine travel stops" to ui on 2026-10-27 at 23:37, with request tasks to act1-chapters for the payloads. ui-menus has added the data rows. What's missing is a trigger in each zone, plus a `Shrine` spawn where there's a shrine. These are layout edits in zones you own, the same as M3-UI-204 for Tamsule. Placement is yours.

The data rows:
- **Shops** (`game/data/items/shops.json`; strings in `game/data/loc/towns_act2.csv`; Progression may retune the stock):
  - `quellan_trader` (on `ch12_reached_quellan`);
  - `ansedra_purveyor` (on `ch13_started`);
  - `hollowmere_chandler` (on `ch15_reached_hollowmere`).
- **Inns:**
  - `quellan_inn` ("The Red Banner", the inn whose door is your `inn_door` mark);
  - `hollowmere_inn`.

## Acceptance criteria
- [ ] **Quellan (Ch12):**
  - `{"id": "trader", "activation": "interact", "prompt_key": "SHOP_PROMPT", "requires_flag": "ch12_reached_quellan", "payload": {"shop": "quellan_trader"}}`;
  - an inn trigger at the inn door, `{"payload": {"inn": "quellan_inn"}}`;
  - a `Shrine` spawn with a shrine trigger `{"save_shrine": "quellan_shrine"}`;
  - the `locations.json` shrines row `{"id": "quellan_shrine", "location_id": "ch12/quellan", "spawn": "Shrine"}`.
- [ ] **Ansedra (Ch13):**
  - a purveyor trigger `{"shop": "ansedra_purveyor"}`;
  - a `Shrine` spawn, trigger and row `ansedra_shrine`.
  - After Ch14 the party are heretics. Both should then go dark: a trigger `requires_flag` / unless-flag, once Ch14's beat sheet names the flag.
- [ ] **Hollowmere (Ch15, and Act III's base):**
  - a chandler trigger `{"shop": "hollowmere_chandler"}`;
  - an inn trigger `{"inn": "hollowmere_inn"}`;
  - a `Shrine` spawn, trigger and row `hollowmere_shrine`.
- [ ] **Temple shrines, where the beat sheets want a save before a boss:**
  - Lowlight (before the north hall);
  - Keth Pass (the first landing, before the terrace);
  - Reedhollow.

  Each needs a `Shrine` spawn, a `{"save_shrine": "<id>"}` trigger, and a `locations.json` row. The validator checks that the spawn exists.
- [ ] **Then ui:**
  - adds each shop, inn and shrine POI to `zone_maps.json` (M3-UI-206's entries);
  - checks the travel list over the new shrines.

## Review log
- 2026-10-28, ui-menus: **paused (ADR 0041, the human's refocus on Act I at final quality).** What is built stays on claude/ui and merges as is; nothing is reverted. Resume when a new ADR lifts the pause.
