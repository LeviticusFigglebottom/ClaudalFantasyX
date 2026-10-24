---
id: M2-ENV-11
title: Final kits for the two battle arenas (Ch2 tideline at noon, the Saltgrass Causeway at the ch03_boss sunset)
role: environment
status: todo
owner_session: ""
depends_on: [M2-BPR-07]
milestone: M2
request-from: combat
---
## Goal
M2-BPR-07 added per-encounter battle arenas with greybox geometry: `game/battle/arenas/tideline_noon.tscn` (encounter
ch02_tideline) and `game/battle/arenas/causeway_dusk.tscn` (the Drownbell, color script Ch3 grade). Dress them at
slice quality with the Haluna / causeway kits.

## Acceptance criteria
- [ ] Keep the contract: the arena scene's children `WorldEnvironment`, `Sun` and `Arena` (with `Arena/Sea`, the flat
      sea the Drownbell's flood rig replaces) replace the sandbox's; extra lights are fine. The fighters' marks are the
      sandbox's (party at +x, foes at -x around the origin), and the battle camera looks from +z: keep the dais area
      clear and flat (y = 0) within about 5 m of the origin.
- [ ] The grade stays the color script's (tideline: ch02_noon; causeway: Ch3, sun 6 deg, key #FFAE67 2.6).
- [ ] The causeway's road sits under the flood's top (+0.6 m) so the flood takes the path (B10).
- [ ] Re-approve `battle_arena_tideline`, `battle_arena_causeway` and `drownbell_flood` after viewing.

## Notes
- Docs: docs/kb/tech/battle_presentation.md "Arenas". Data: game/data/battle/arenas.json.

## Review log
