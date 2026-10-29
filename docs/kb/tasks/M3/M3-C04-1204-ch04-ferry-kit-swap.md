---
id: M3-C04-1204
title: Ch4 greybox to final, the Brightwater ferry and the Seventh Terrace dress ch04/brightwater_ferry (ADR 0200)
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-ENV-08, M3-ENV-08B, M3-C04-02, M3-C06-1200]
milestone: M3
reviewer: qa
request-from: ""
---
## Goal
Swap Ch4's greybox ferry, derelict and islet for env-art's ferry kit (M3-ENV-08) and the Seventh Terrace (M3-ENV-08B).

## Acceptance criteria
- [x] `tools/act1/ch04_ferry_dressing.py`: the ferry at (0, 0, 10), the derelict at `bf_terrace.DERELICT_IN_FERRY` from
      her (never joined, ADR 0017 (d)), the dressing (both ships, the sails and name-board states on their blocks,
      the alongside gear, the preview's lanterns, bundles and drowned hulks) and the collision (decks in slices inside
      the bulwarks, the starboard gangway open, poop ladders as ramps, hatches, the deckhouse with its door, masts,
      cargo, the derelict's galley with its door, the islet and the gangplank).
- [x] The story points moved once onto the kit (`--relayout`), with the kit's anchors for the purser, the shrine
      (the Order niche inside the deckhouse), the ferrymaster at the tiller, the rail, the gangway; the islet turned
      to lie off the starboard gangway (the kit boards midships); `SternGate` now closes that gangway.
- [x] The night: the moon low in the east (#9DB4D9 at 0.28), the preview's `ch04` grade and the night sea's glow.
- [x] `test_ch04_thread` 11/0; `test_ch04_validate` reads the collision file's ids.
- [x] Shots `ch04_ferry_deck`, `ch04_ferry_derelict` rendered on the PC, viewed and approved. Baselines approved by the Lead's gates (big13 1fa92b81 / a4410fd9; tracks never write baselines, TRACK-RULES).

## Notes
- The derelict's daylight sub-frame (C4-11 to C4-14, `ch04_derelict`) is Rendering's; Ch04Zone has no light rows,
  so for now the whole zone is the pre-dawn crossing.
- `haluna_wake` (the wake night on Haluna) is next: it is a stand-in for Haluna's night variant (M3-C04-03).

## Review log
- 2026-10-29 act1-chapters: to review (every criterion met; the stand-ins listed in Notes wait on their own requests).
