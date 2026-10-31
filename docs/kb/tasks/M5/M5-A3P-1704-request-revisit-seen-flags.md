---
id: M5-A3P-1704
title: "Request (flow): set ch18_revisit_<town> when each Ch18 revisit side scene plays, for the Kite's log"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1703]
reviewer: ui
milestone: M5
request-from: ui
---
## Goal
The Kite's log (M5-A3P-1703) marks a revisited town Seen once its side scene has played. The scenes
(`game/data/dialogue/ch18/ch18_revisit_*.dlg`, M5-A3P-1003) set no flag. ui-menus has declared one flag per town
in flags.tres:

`ch18_revisit_haluna`, `ch18_revisit_oruvel`, `ch18_revisit_pemakar`, `ch18_revisit_tamsule`,
`ch18_revisit_corrow`, `ch18_revisit_quellan`, `ch18_revisit_ansedra`, `ch18_revisit_hollowmere`.

## Acceptance criteria
- [ ] Each revisit side scene sets its flag when it plays. This could be a `<<set $ch18_revisit_<town> = true>>`
      at its end, or the flow's trigger setting it as part of the Ch18 staging (M5-A3P-1004).
- [ ] Haluna's flag is set on the visit itself, whether or not the optional lifting ("Backs to the Water",
      `ch18_haluna_lifted`) is played.

## Review log
