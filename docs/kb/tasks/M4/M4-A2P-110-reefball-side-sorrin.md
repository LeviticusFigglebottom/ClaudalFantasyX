---
id: M4-A2P-110
title: "Rename the Reefball side id `pemakar` to `sorrin` (Ch7's opponent is Sorrin)"
role: progression
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
Ch7's Tidecup opening match is Oruvel against **Sorrin**:
- act1_ch07.md §203;
- `DLG_CH07_BARK_BOARD_001` ("Oruvel against Sorrin");
- `DLG_CH07_BARK_MARKET_001`.

The Act I proofread (2026-10-30, FAST-TRACK) changed the display strings to Sorrin: `RBL_SIDE_PEMAKAR`, and
`RBL_DIVER_PEM_*`, which shows "Sorrin lifter" and the rest. The data still names the side `pemakar`, in
`game/data/reefball/sides.json` and in `matches.json` `tidecup_opening.sides`. Renaming the id (and the loc keys, if you
want them to match) is the reefball data owner's call. The Lead routed it here (2026-10-30).

## Acceptance criteria
- [ ] `sides.json` id and `matches.json` reference renamed (or left, with a note that the id is internal).
- [ ] If the loc keys are renamed too, rename them in strings.csv in the same commit.
- [ ] Godot `--filter=reefball` green.

## Review log
