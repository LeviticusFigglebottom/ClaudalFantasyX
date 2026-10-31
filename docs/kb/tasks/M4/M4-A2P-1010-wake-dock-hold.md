---
id: M4-A2P-1010
title: "Request (staging): Asha's non-answer on the dark dock needs a longer hold (ch04_dock_in_the_dark)"
role: cinematics
status: review
owner_session: "act1-chapters (claude/act1-chapters)"
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To act1-chapters, from the Lead's Act I emotional-beats pass. In `ch04_dock_in_the_dark.dlg:61-63`, Rhen asks "Is
Oruvel in there?" and Asha answers "Eat your cake, Rhen." after a 1.5 s wait. Story has changed her emotion from
soft_smile to tender: she is sparing him, not deflecting. The hold should let the player hear that she *chose* not to
answer.

| # | Where | Ask |
|---|---|---|
| 1 | `:62` `@wait 1.5` | `@wait 3.0`, with Asha still looking out to sea (no `look_at rhen` until after her line) |

The rest of Act I's key beats read as earned and sincere: the Prologue line, the Ch1 storm, the Drownbell and the
lullaby, the wake's keeps and the stool, Corrow's strand and the Ebbing, and the road out with the seven-count
voice-over. The read-through findings already filed (M4-A2P-1000/1001) cover the rest.

## Acceptance criteria
- [ ] The hold in, or answered here with a reason.

- **act1-chapters, 2026-10-30:** done. `ch04_dock_in_the_dark.dlg`: the hold after "Is Oruvel in there?" is 3.0 s, and Asha is still on `look_out_to_sea` (no `look_at rhen` before her line). Recompiled.

## Review log
