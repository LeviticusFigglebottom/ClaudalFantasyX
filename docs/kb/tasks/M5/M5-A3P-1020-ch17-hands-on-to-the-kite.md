---
id: M5-A3P-1020
title: "Request (act1-chapters, Ch17 flow): Ch17's boarding hands on to Ch18's maiden flight on the Kite"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1001, M5-A3P-1004]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
Ch17 ends when the party boards Dace's hull (`aboard`, which sets `ch17_complete`), and Ch18 opens on the maiden flight
aboard the Kite (K01, `ch18/kite`, spawn `Deck`; act3_ch18.md §2). At big36 nothing links them: the `aboard` beat sets
the flag and the party stays on the hull at Hollowmere, so Ch18 can't be reached in play.

act1-chapters own `game/data/flow/chapters/ch17.json` (the Lead, 2026-10-31; ADR 0207). act2-plan has not edited it.

## The patch (one step, appended to the `aboard` beat's steps)
```json
"aboard": {"when": {"set": ["ch17_verse_begun"], "unset": ["ch17_complete"]},
           "steps": [{"set": "ch17_complete"}, {"go": {"location": "ch18/kite", "spawn": "Deck"}}]}
```
`ch18.json`'s Kite block then plays K01 on arrival (`ch18_started`, chapter 18). test_ch17_thread can assert the
hand-off as test_ch11_thread does (`[ZoneStory.KIND_GO, {"location": "ch18/kite", "spawn": "Deck"}]`).

## Acceptance criteria
- Boarding the hull in Ch17 takes the party to the Kite's deck, and K01 plays.
- test_ch17_thread asserts the hand-off; test_ch18_thread stays green.

## Review log
