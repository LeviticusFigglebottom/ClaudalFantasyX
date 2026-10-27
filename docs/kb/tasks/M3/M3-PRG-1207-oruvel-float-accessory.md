---
id: M3-PRG-1207
title: The Oruvel Float, Ch7's Reefball win reward (an accessory; the game has no accessory slot yet)
role: progression
status: todo
owner_session: ""
depends_on: [M3-C07-1206]
milestone: M3
request-from: cinematics
---
## Goal
act1_ch07.md §5.4: a win in the Tidecup opening round gives the **Oruvel Float** accessory ("a woven float charm in
oil-black and brass"; flavour: "Brought up, once, for the ones who didn't come up.") plus lume. The equipment data
has weapon and armour slots only (`game/data/items/equipment.json` `gear_types`), so there is nowhere to put it.
Add the accessory (or whatever slot Progression decides), then put its id in
`game/data/flow/ch07_tidecup.json` `win_reward.items` (act1-chapters will, or do it and say so in its live log).

## Acceptance criteria
- [ ] The item exists with name and description keys; `ch07_tidecup.json` gives it on a win.

## Review log
