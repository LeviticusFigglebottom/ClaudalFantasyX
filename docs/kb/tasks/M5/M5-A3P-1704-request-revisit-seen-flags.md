---
id: M5-A3P-1704
title: "Request (flow): set ch18_revisit_<town> when each Ch18 revisit side scene plays, for the Kite's log"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice)"
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
- [x] Each revisit side scene sets its flag when it plays. This could be a `<<set $ch18_revisit_<town> = true>>`
      at its end, or the flow's trigger setting it as part of the Ch18 staging (M5-A3P-1004).
- [x] Haluna's flag is set on the visit itself, whether or not the optional lifting ("Backs to the Water",
      `ch18_haluna_lifted`) is played.

## Done (slice-polish, 2026-11-03)
- The seven revisit scenes (`ch18_revisit_{ansedra,corrow,hollowmere,oruvel,pemakar,quellan,tamsule}.dlg`, one node
  each, no jumps) end with `<<set $ch18_revisit_<town> = true>>`.
- Haluna: HalunaStory's arrival sets `revisit_seen_flag` (`ch18_revisit_haluna`) whenever `revisit_open_flag`
  (`ch18_world_open`) is set (first_playable.json `haluna`). It counts the visit itself; the lifting stays optional.
- Note: nothing plays `ch18_backs_to_the_water` (the lifting) in Haluna yet. That belongs to the Ch18 staging and flow
  (M5-A3P-1004).
- Tests: test_ch18_revisit_flags 3/0; haluna 67/0. dlgc and validate_data clean.

## Review log
