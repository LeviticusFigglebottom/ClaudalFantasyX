---
id: M4-CMB-1001
title: "Request (act1-chapters): a drain on enemy skills (heal by a share of the damage dealt), for Act II's fen leech"
role: combat
status: blocked
blocked-by: ADR 0041
owner_session: ""
depends_on: []
milestone: M4
request-from: cinematics
---
## Goal
Creatures' Act II roster gives Ch10's `fen_leech` the role of "a drainer: it heals by what it takes (a first lesson in
denying healing)". The engine has no drain: a skill row field (e.g. `"drain_pct": 50`, the user healed by that share of
the damage it dealt, shown on the HUD) would let `leech_bite` (skills.json, M4-C10-03) carry it. Until then the bite
poisons, and the leech pair's role_answer band is report only.

## Acceptance criteria
- [ ] A skill field for drain in the engine and its tests; formulas.md if it touches a formula.
- [ ] act1-chapters then sets it on `leech_bite` and re-runs `ch10_fen_leeches`.
