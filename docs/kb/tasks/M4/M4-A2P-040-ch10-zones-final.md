---
id: M4-A2P-040
title: "Ossa Fen and Reedhollow dressed, lit and walkable at final quality, with a mangrove vegetation system"
role: environment
status: doing
owner_session: "env-art (claude/env-art, 2026-10-30)"
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Place the built kit (M3-ENV-718, 733) in both zones per ossa_fen.md's swap map, add a procedural **mangrove** system (SPEC §7.4) with wind, reed beds, the clutch's shore, the farewell-tide's staging space, the grade and LUT, ambient wildlife hooks, and ten composed shots per zone (SPEC §8.4). Merge `e1db6170` (the `kirru_roost` fix) first.

## Acceptance criteria
- [ ] Dressing and collision JSON from generators; ≥10 shots per zone viewed; no seams; walkable tests green.
- [ ] Audit zero for both zones.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch10. Don't rebuild the kit.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **2026-10-30 (env-art):** claimed under ADR 0205 (env-art has no open Act I row; rows 24 and 47-FerryAft are field-camera rows, routed).

- **2026-10-30 (env-art), progress:**
  - **The mangrove system:** `ossa_fen.build_tree` takes parameters; three variants beside the kit tree (`mangrove_tall`
    11 m, `mangrove_low` 6.5 m, `mangrove_young` 4 m) share its wind contract and materials.
  - **The ground:** `fen_zones.py` builds each zone's mud bed from its greybox (level land at y 0, channels 0.6-1.4 m
    down, root-mat humps under every trunk and house), with litter and roots on the land in `kit_fen_bank`.
  - **The dressing:** `tools/act2/ch10_fen_dressing.py` writes both zones' dressing, grade and water, and env-art's
    preview with ten composed cameras per zone. `tools/tests/test_ch10_fen_dressing.py` (5): matches its generator,
    walks tiled end to end, no tree or reed on a walk, the land level, no tree on a spawn or mark.
  - **Viewed** (20 cameras): the channels, the root-walks, the dead tree, the clearing, the reed causeway and ring, the
    roosts, the clutch's stone and cords read. Open: the flat land reads dark at dusk (the layout's ambient: M4-A2P-0401),
    Pell's capsule (characters'). The mount is chapters' (M4-A2P-0401).

## Review log
