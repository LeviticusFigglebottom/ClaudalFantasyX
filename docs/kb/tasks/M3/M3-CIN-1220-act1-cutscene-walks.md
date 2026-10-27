---
id: M3-CIN-1220
title: Act I cutscene walks stay on the floor (the quality bar on the kit zones): waypoints, marks, off-screen places
role: cinematics
status: doing
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-CIN-1221]
milestone: M3
request-from: ""
---
## Goal
The sequencer's `@mark` walks an actor to a mark in a straight line with its height lerped. On the kit zones' heights
(ADR 0200) and on the greybox zones' houses, tables and rails, 66 Act I walks leave the floor or pass through
something (a rail on the mole, the Fisher Stair walked as a slope through the air, Pemakar's harbour to its crown,
the galleries' platforms, Tamsule's decks over the water). `tests/integration/test_act1_cutscene_walks.gd` replays
the Act I chapter threads and checks every seen walk from where the actor really stands; the walks still to fix are
in `tests/integration/act1_cutscene_walks_known.json` (the test fails on any other, and on a listed one that's clean).

## Fixes, by kind
- **A path:** `via=` marks round the obstacle or down the stair (needs M3-CIN-1221's sequencer patch).
- **A mark in the wrong place:** move it.
- **A walk nobody should see** (from one end of a zone to the other between beats): the zone's states / variants /
  `stand` put the actor at the start before the scene, or the script fades.

## Acceptance criteria
- [ ] The known list is empty; the test stays in the suite.

## Review log
