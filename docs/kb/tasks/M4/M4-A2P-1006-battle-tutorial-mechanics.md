---
id: M4-A2P-1006
title: "Request: Act I battle tutorials: the hound's guard isn't built; Swap, the timeline and Poison are taught late"
role: progression
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To act1-chapters' combat seat (`game/data/battle/encounters.json` turn prompts, `enemies.json`). This comes from the
Lead's Act I tutorial clarity pass (pillar 4). Story has rewritten 13 `TUT_*` lines to match the mechanics as built
(commit on claude/act2-plan). These rows need data, not words.

| # | Sev | Where | Problem | Suggested fix |
|---|---|---|---|---|
| T5 | med | `enemies.json` `raid_hound` (its note: the intercept is M3-C06-05) | The beat sheet's hound "guards the Inquisitor", but no intercept exists: it Pounces on the lowest-HP hero every third turn and Bites at random otherwise. **Story's interim tip** now says what it does: "The hound harries the weakest. Toma's Challenge draws its bites onto him." | Build the guard (M3-C06-05) and tell story, which will restore "draw it off" |
| T6 | med | `encounters.json` `ch02_tideline` | Swap is first taught in Ch4 (`TUT_CH04_SWAP`), but Toma is in reserve from the Tideline on, and the reef crab's role answer is Toma | A Tideline turn prompt: "Toma is in reserve. Swap him in on any hero's turn. It costs no time." (story can add the loc row) |
| T7 | med | `encounters.json` `ch01_wickfry` | The timeline is first taught at Hullgnaw (Ch1's fifth fight), but the wickfry are already faster than Rhen. `TUT_TIDELINE_TIMELINE` exists and is true, but nothing references it | Use `TUT_TIDELINE_TIMELINE` as the wickfry's prompt for Rhen |
| T16 | low | `encounters.json` `ch02_tideline` | The first Poison (the reef crab's Brine Spit, 40%) lasts until cured and has no tip | A prompt such as "Poison bites each turn until cured. Bitterleaf, under Items, clears it." |
| T9 | low | `enemies.json` `gull_harrier` (evasion 30) | The beat sheet's lesson is "fliers dodge most blows". At evasion 30 they dodge about a quarter, so story's tip now says "more than most" | Optional: raise the evasion if the lesson should stand |

## Acceptance criteria
- [ ] Each row done, or answered here with a reason.

## Review log
