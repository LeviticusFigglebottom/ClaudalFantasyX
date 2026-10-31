---
id: M5-A3P-1203
title: "Request (slice-polish; ui for the credits' next_scene): the Ending's last stops at Haluna and Oruvel (E5-E7)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1015]
reviewer: narrative
milestone: M5
request-from: cinematics
---
## Goal
The Ending's flow (M5-A3P-1015, `game/data/flow/chapters/ending.json`) plays E1–E4 aboard the Kite. When Liss has
brought the Kite down and nothing comes, it sets `ending_landed` and goes to `ch02/haluna` at `DockNight`. The last
three beats sit in zones and data that aren't act1-chapters':
- **E5 `ending_the_dark_sea`** (`ch02/haluna`, slice-polish's zone and flow): an arrival row, when `ending_landed` is
  set and `credits_seen` isn't, that plays it at the dock at night and then opens the credits
  (`res://game/ui/credits/credits_roll.tscn`, a `scene` step).
- **E6 `ending_beach_rite`**: the credits' `beach_rite` vignette (`game/data/ui/credits.json` `vignettes[0].scene`,
  empty today). It needs Cinematics' in-engine scene for the rite at Haluna's beach.
- **E7 `ending_first_lamp`** (`ch01/oruvel`, after the credits): the credits' `next_scene` (UI's
  `credits.json`, empty today, so the title opens). It needs a post-credits route into Oruvel that plays the scene.
  For example, a small scene that sets a flag and travels to `ch01/oruvel`, plus an Oruvel arrival row on
  `credits_seen` (slice-polish's flow).

## Acceptance criteria
- [ ] From `ending_landed`, the game plays E5, the credits with the beach rite, then E7 in Oruvel, and ends on the title.

## Review log
