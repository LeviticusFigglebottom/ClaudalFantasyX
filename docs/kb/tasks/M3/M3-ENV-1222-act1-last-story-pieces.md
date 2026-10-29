---
id: M3-ENV-1222
title: "Act I's last greybox story pieces: Ch4's islet landing (rock, gangplank, wrapped name board, gangway gate) and Coilspire's flue gates, niche seal and wright's mark"
role: environment
status: todo
owner_session: ""
depends_on: [M3-C04-1204, M3-C08-1210]
milestone: M3
request-from: cinematics
---
## Goal
act1-chapters' "parts look primitive" sweep (TRACK-RULES, self-directed backlog): every other dressed Act I zone now
draws its story pieces from a kit (Ch6 and Corrow have no greybox left). These blocks still draw as boxes because no
kit piece exists. Each needs a piece on the block's footprint (sizes from the layouts on `claude/act1-chapters`); when
it lands, act1-chapters places it (`tools/act1/ch04_ferry_dressing.py`, `tools/act1/ch08_coilspire_dressing.py`) and
drops the id from `greybox.keep`.

| Zone | Block | Footprint (x, y, z m) | What |
|---|---|---|---|
| ch04/brightwater_ferry | `IsletRock` | 10 × 1 × 18, top y 0 (walkable) | the islet's landing rock the ferry lies off (act1_ch04.md C4-08, C4-15): wet basalt and coral, a worn landing face on its ferry side (-x) |
| ch04/brightwater_ferry | `Gangplank` | a ramp 3.65 m long, 1.6 wide, level at y 0, ferry (x 3.35) to islet (x 7) | the ferry's gangplank across to the islet, with its two hand-lines (the `GangplankRailN/S` collision stays) |
| ch04/brightwater_ferry | `NameBoardWrapped` | 2 × 0.3 × 0.6 | the ferry's name board taken down and wrapped in sailcloth (C4-15's 2 s hold); the Brightwater kit's `terrace_name_board` under cloth |
| ch04/brightwater_ferry | `SternGate` | 0.3 × 1 × 1 | the gate that closes the starboard gangway |
| ch08/coilspire | `Gate_t1` .. `Gate_t4` | 0.3 × 2.8 × 1.6 | a wright's grille across each flight at its third tread, which the flue trial opens (they hide) |
| ch08/coilspire | `NicheSeal` / `Niche` | 0.6 × 1 × 1 / 0.2 × 0.8 × 0.8 | the tier-2 side flue's sealed niche and the niche behind it (B05) |
| ch08/coilspire | `WrightMark` | 0.5 × 0.5, a decal | the Saltwright wright's mark scratched by the seized flue (tier 3) |

Not here: `Virel` (the Fire Vowbound: creatures/characters) and `StormWall` (the storm seen from the gallery: rendering's
VFX), which stay greybox until those land.

## Acceptance criteria
- [ ] Each piece built, reproducible, with PROVENANCE rows and its LOD chain, fitting its footprint.
- [ ] act1-chapters places them and asks for the shots (ch04_ferry_deck, ch08_coilspire_hall).

## Notes (2026-10-29, env-art)
- **The Ch4 half is built:** the Brightwater kit's `bf_landing` pieces (M3-ENV-746: the islet rock, the gangplank with its hand-lines, the wrapped name-board, the stern gate) are placed by `tools/act1/ch04_ferry_dressing.py` on their blocks; viewed in `brightwater_landing_f06` (10-29). The Coilspire half (Ch8) is env-art-b's.

## Review log

## Notes (env-art-b, 2026-10-28)
- **The Coilspire half is done** (ADR 0041 moved Ch5–Ch9 to env-art-b): `flue_gate`, `niche_seal`, `lamp_niche`,
  `wright_mark` in the Coilspire kit (`b_trial.py`), placed on `Gate_t1..4`, `NicheSeal`, `Niche`, `WrightMark` by
  `tools/act1/ch08_coilspire_dressing.py`; the StormWall block now carries Rendering's UndertowStorm. Only `Virel` stays
  greybox in Coilspire (the Vowbound's body: creatures-b). The Ch4 half (the islet landing) is env-art's.
