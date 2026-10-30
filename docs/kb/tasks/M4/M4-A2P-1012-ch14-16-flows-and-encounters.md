---
id: M4-A2P-1012
title: "Request: the Ch14–Ch16 flows play no scene, and four of their fights have no encounter"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To act1-chapters (the flows and encounters), from the Lead's Act II read-through of Ch14–Ch16 on paper. The scripts and
beat sheets agree with each other; story fixed its own findings (commit on claude/act2-plan). This row is the mounting.

| # | Where | Problem | Ask |
|---|---|---|---|
| 1 | `game/data/flow/chapters/ch14.json`, `ch15.json`, `ch16.json` | No scene is played. Ch14 has only the arrive and the escape `go`; Ch15 and Ch16 are greybox walks | Wire each sheet's §1 in order, as M4-A2P-114 does for Ch10–13 (its table covers Ch14's setters) |
| 2 | ch15.json (hollowmere arrive) | `ch15_the_dock_master` (B10) must play on arrival at Hollowmere, after `ch15_current_song` at sea (act2_ch15_direction §0) | Play it in the first `ch17/hollowmere` arrive row |
| 3 | `game/data/battle/encounters.json` | `ch14_water_steps`, `ch14_malcor_venn`, `ch16_abiding_guard` and `ch16_storm_wakes` have no rows, though the scripts' `<<event start_battle>>` calls them. Only `ch15_wakefin` exists | The four encounters (combat seat; see M4-A2P-1008 for their tutorials) |
| 4 | ch14–ch16 flows | `ch14_left_standing` and `ch16_swept_away` follow battles the flows don't chain | Chain the battle returns to the after-scenes |
| 5 | ch14.json party | No Pell (he's present in every Ch14–16 scene; no battle kit yet) | Keep him as a follower/actor, as Ch10–13 do |

## Acceptance criteria
- [ ] Ch14 → Ch16 plays through by flow, each sheet's §1 in order.

## Review log
