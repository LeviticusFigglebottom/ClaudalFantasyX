---
id: M3-ENV-706
title: "Ch6's battle arenas at final quality from the Brine Shoals kit (brine_shoals_afternoon, salvage_camp_burning)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-02, M3-BPR-03]
milestone: M3
request-from: combat
reviewer: rendering
---
## Goal
The last two Act I encounter arenas were still M3-BPR-03's greybox. Build them on the M2-ENV-11 contract from the
Brine Shoals kit and swap them in.

## Acceptance criteria
- [x] Kit grounds `arena_shoals_ground` and `arena_camp_ground` (`bs_arenas.py`, job `brine_shoals_kit`, every
      other piece byte-identical); arena tables in `arena_scenes.py` (ch06 light, `silted_flats` sea, the LUT
      copied to each arena's folder); `arenas.json` repointed.
- [x] The camp's fire lights keep M3-BPR-03's contract (`Arena/FireLight0`, no fog energy): `--filter=arena` 18/0.
- [x] `test_arenas`, `test_fog_lamps`, `test_brine_shoals_kit` OK; every other arena regenerates identically.
- [ ] PC renders of `battle_arena_shoals`, `battle_arena_camp`, `battle_boss_intro_inquisitor`; view, re-approve.
