---
id: M2-FP-114
title: "FAST-TRACK: the final causeway's random fights keep the greybox's pacing (two or three, not six to eight)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-108, M2-FP-28]
reviewer: combat
milestone: M2
request-from: lead
---
## Goal
Queue item 4 (encounter pacing). M2-FP-108 moved B06 from the greybox (about 70 m from the harrier to the islet) to
the final route (about 215 m), but kept the greybox's 25–45 m encounter gaps. That would mean six to eight random
fights back to back, which is the playtest's old complaint (M2-FP-28).

## Acceptance criteria
- [x] `tools/causeway/build_causeway_gameplay.py` scales the gaps to the walk left after the harrier (0.32–0.45 of
  it: 67.6–95.1 m), so the route meets two or three fights, plus the 12 m post-battle grace.
- [x] test_causeway_route `test_the_route_after_the_harrier_meets_two_or_three_fights`; causeway 13, fp_thread 2 and
  zone_story 15, all 0 failed.
- First-battle clarity is M2-FP-105: the tideline opens on the timeline prompt and prompts the commands on Rhen's
  first turn.

## Review log
