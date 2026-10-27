---
id: M3-UI-100
title: Battle HUD for Ch8's set-piece fights (timeline entries, locked/unavailable heroes, intercept floats, the stair meter)
role: ui
status: todo
owner_session: ""
depends_on: [M3-CMB-01]
milestone: M3
request-from: cinematics
---
## Goal
M3-CMB-01 (ADR 0100, `docs/kb/design/set_piece_battles.md`) added scripted timeline entries, objective victories, party locks and ward skills to the battle engine for Ch8's evacuation set piece. The engine and the Attack row, ward targeting and `scripted_escape` result panel are wired. The HUD still needs:
- **Timeline:** the encounter `entries` (the Climb, the Surge, Pell's Storm-Call telegraph) drawn on the turn-order timeline, distinct from foes.
- **Party locks:** the Swap and formation menus greyed for a `locked_active` hero (`locked_key`) and an `unavailable` one (`unavailable_key`), with the reason shown.
- **Floats:** for intercepts (Hold the Stair), counters (Stand Firm) and withdrawals (foes leaving on an objective win).
- **Stair meter:** a HUD for the objective quota (`engine.objective_count` against `objective.quota`), carried across the three waves.

## Acceptance criteria
- [ ] Each piece reads the engine state named above. It needs no new engine API; if it does, request one from combat.
- [ ] Screenshots of a Ch8 wave and the Reach once M3-C08-02 builds the fights.

## Review log
