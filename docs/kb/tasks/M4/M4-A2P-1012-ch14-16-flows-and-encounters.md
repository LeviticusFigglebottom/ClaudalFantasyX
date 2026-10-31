---
id: M4-A2P-1012
title: "Request: the Ch14–Ch16 flows play no scene, and four of their fights have no encounter"
role: cinematics
status: review
owner_session: "act1-chapters"
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

## Done (act1-chapters, 2026-10-30)
- **1, 4 (Ch14):** done earlier under M4-A2P-1200: the vows → water-steps chain, the first ripple → Venn, left standing, and the escape gated on `ch14_complete`.
- **1, 2, 4 (Ch15):** the arrival plays `ch15_unlamped` (B01), with the deck talks as interacts until the fin (B02). The bow's "Wait for the dawn" first plays `ch15_the_fin` → `ch15_wakefin` (B03–B04; new flag `ch15_wakefin_felled`). The return plays `ch15_the_shoal` (B06–B08). Then the bow plays `ch15_current_song` and goes on to Hollowmere (B09). The first Hollowmere arrive plays `ch15_the_dock_master` (B10). A `jetty` touch at the bier plays `ch15_let_me_carry_him` → `ch15_pyre_raft` (B12–B13). `supper` is an interact for `ch15_two_daces` (B14). The ship waits on `ch15_pyre_raft`, then plays `ch15_the_ship` and goes on to the Rim (B15). Hollowmere's people, side errands and camp are wired too.
- **1, 4 (Ch16):** the arrival plays `ch16_ship_waits`. The wade's six barks are overheard across the white, and the cairns hold the wader, the one turning back, the counting stone, the fallen cairn and the last night's camp. In the Choir, the first arrival plays `ch16_the_choir` (B03–B07) → `ch16_abiding_guard` (`ch16_guard_beaten`). The return runs `ch16_storm_wakes` (`ch16_line_held`), and the next return plays `ch16_swept_away` (B10–B11). **The act break after it** (B11's vigil at `prologue/iskarra_dusk`, B12's act card) **isn't wired.** Act III's opening is open (ADR 0207), so this is a LEAD-ASK.
- **3:** all four encounters exist. `ch16_storm_wakes` is the sheet's §5b in ADR 0100's schema: the line (ward, quota 3, `scripted_escape`), the storm wall (a tide that summons a storm crawler or glass skate every 2nd turn, cap 3, and charges `the_wall_comes`), and Kerrid locked in. **Two departures from the sheet, combat's call:**
  - Kerrid's Hold the Line is lent as a skill, not his `attack_override`. As an override every policy covered, and naive matched role_answer.
  - The grip on the line comes from a set-piece-only `storm_crawler` (the rim crawler's model, lore and voice): the sim's ward guard reads foes' threats, not a tide entry's.
  - The sheet's lighter `storm_dark` is left out: field rules ride an enemy phase.

  Suite `ch16_storm_wakes` at 500 seeds: naive 24.0%, role_answer 91.8%, smart 100%, p90 32 turns, no timeouts. Audio has no music row for `ch16_storm_wakes` (the sheet asks for `abiding_guard` stem 2); that's a request to audio.
- **5:** Pell is staged and voiced by the scenes' casts, as in Ch10–13. He gets no party row until his kit lands (M3-C09-07).
- Tests: test_ch14_16_thread plays every beat above; qa_threads is green.

## Review log
