---
id: M5-A3P-1203
title: "Request (slice-polish; ui for the credits' next_scene): the Ending's last stops at Haluna and Oruvel (E5-E7)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice)"
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
- [x] From `ending_landed`, the game plays E5, the credits with the beach rite, then E7 in Oruvel, and ends on the title.

## Done (slice-polish, 2026-11-03)
- E5 at Haluna: an arrival on `ending_landed` with `ending_dark_sea_seen` unset gives Haluna at night with the sea's
  glow at 0 and only Asha on the dock, plays `ending_the_dark_sea` on E11 (`grade: ending_dock`; her turn is
  `@anim asha look_at haluna` toward the staged `haluna` mark), sets `ending_dark_sea_seen` and opens the credits.
- The credits: the beach-rite vignette and next_scene (see M5-A3P-1701).
- E7 in Oruvel: on `credits_seen`, the storm comes down and `ending_first_lamp` plays on E13 (`grade: post_credits`,
  the blue hour). Kell's-wick oil lamp is a light-only practical (`game/data/cutscene/ch01/oil_lamp.tscn`), and the
  title follows.
- Staging: `game/data/cutscene/ch02/haluna.json` (E11, E12, the marks) and `ch01/oruvel.json` (E13, the lamp).
  HalunaZone gained `location_id` so CutsceneStaging applies.
- Fixed: CutsceneGrade never found a GreyboxZone's environment (a code-built stage has no owner). No other scene
  used a built grade row, so nothing else changes.
- Tests: test_ending_last_stops 4/0, cutscene_grade 4/0, credits 6/0, haluna 67/0, ch01 20/0.
- Viewed (lavapipe): E12 (Toma, backs to the sea) and E13 (the blue hour, the lamp's warm light on the stall). E11
  reads very dark under ending_dock on lavapipe (PC-QUEUE).
- Open: the rite's `@anim crowd turn_back sea` has no `crowd` actor (the villagers' routine is creatures'); E12 is
  daylight, with no dawn grade yet (env-art).

## Review log
