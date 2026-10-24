---
id: M3-BPR-01
title: Act I battle arenas and their presentation (encounter arena ids, greybox fallbacks, per-arena staging)
role: combat
status: review
owner_session: battle-presentation (claude/battle-presentation)
reviewer: lead
depends_on: [M2-BPR-07]
milestone: M3
request-from: lead
---
## Goal
Every Act I fight gets an arena (the M2-BPR-07 / M2-ENV-11 contract: docs/kb/tech/battle_presentation.md "Arenas",
docs/kb/tech/battle_arenas.md). The encounters are m2-slice's (game/data/battle/encounters.json on claude/m2-slice:
ch01_*, ch03_causeway_*, ch04_*, ch05_*). Proposed arenas, graded from the color script, each from env-art's zone
kit for that place:

| Arena id | Encounters | Place and grade (color_script.md) | Env-art kit |
|---|---|---|---|
| `oruvel_raft_morning` | ch01_scuttlers, ch01_hullgnaw (wickfry and oil_slug moved to underway_tower, see Notes) | Oruvel raft-town deck, Ch1 10:30 (sun 58°, key #FFEFE1 3.0, exposure 0.65) | M3-ENV-05 / raft-town |
| `underway_tower` | ch01_wickfry, ch01_oil_slug, ch01_shaft_limpet, ch01_underway_shoals, ch01_underway_limpet | the drowned tower, underwater: only Rhen's oil lamp and held cyan motes (Ch1 note; underwater.md) | M3-ENV-05 lamp-diver seafloor |
| `causeway_route_afternoon` | ch03_causeway_shore, ch03_causeway_harrier | the Saltgrass Causeway route at 14:30 (lut_ch02_noon, haluna.md) | M2-ENV-10 causeway route |
| `derelict_deck_night` | ch04_sail_leeches, ch04_bottle_hermit, ch04_spar_wraith, ch04_derelict_* | a derelict's deck under the Ch4 night sky (key #FFB16E lamp 1.2, sea-glow, exposure 1.10) | M3-ENV-02 Brine Shoals |
| `ash_terrace_lanternfall` | ch05_stair_*, ch05_cinder_matron | Terraces of Ash, Ch5 festival night (key #FFA757 1.6, fog #5A3A2E, exposure 1.05) | M3-ENV-03 Terraces of Ash |

## Acceptance criteria
- [x] Arena ids agreed with env-art (request M3-ENV-06) and m2-slice (the encounter rows' `arena` fields)
- [x] Greybox fallbacks graded from the color script until each kit lands; arenas.json rows; shots viewed
- [x] Per-arena staging where the place asks for it (underwater: shorter runs, slower falls; a deck: no run past its rail)
- [x] Tests (the arena data test covers every arena; the loader keeps capture fixtures on the sandbox)

## Notes
- Lead queue 2026-10-24 item 4. Starts when big7 (with m2-slice's Act I encounters) lands on the integration branch.

- 2026-10-24 15:28: env-art took M3-ENV-06 (claude/env-art 78916415), keeping the five ids. Building causeway_route_afternoon, derelict_deck_night and ash_terrace_lanternfall now; underway_tower after the M3-ENV-05 sea-floor kit (look agreed with Rendering); oruvel_raft_morning from the Haluna waterfront pieces unless a raft-town zone comes first.

- 2026-10-24 (battle-presentation worktree): the five greybox arenas are in `game/battle/arenas/` (hand-written
  primitive meshes, StandardMaterial3D, ProceduralSkyMaterial or a flat underwater colour; grades from color_script.md
  and haluna.md, every number in each scene's header comment), with `arenas.json` rows and the `arena` field on every
  ch01/ch03_causeway/ch04/ch05 encounter row. **Mapping change:** `ch01_wickfry` and `ch01_oil_slug` are the
  Underway's scripted fights (act1_ch01.md C1-04 wickfry drawn by the open shutter, C1-06 the slug in the gauge
  room), so they fight in `underway_tower`; the raft keeps the scuttlers and Hullgnaw (C1-13/C1-14, the net-pen
  hull). The raft greybox shows the storm wall low on the horizon under the 10:30 sky (O18: "the sky is still blue
  above it"); the full `lut_ch01_storm` variant is env-art's. Shots `battle_arena_raft|underway|route|derelict|terrace`
  rendered, viewed and baselined; tests/unit/test_battle_arena.gd checks every arena's contract (Sea only where
  there is open water: not underway_tower or ash_terrace_lanternfall), the Act I mapping, and an arena with no Sea.
- **Open (for Lead / Art / env-art):** two grades are the chapter's frame rather than the fight's hour. The derelict
  is boarded at 07:40 and the Spar-Wraith fought at 08:10 (act1_ch04.md C4-12/C4-13, morning on the strait), and the
  stair fights and the Cinder Matron are day 2, 11:30-13:40 at Ashcrown (act1_ch05.md B07-B09), not Lanternfall
  night. The ids and night grades follow this task's table and env-art's M3-ENV-06 agreement; a `ch04_ferry_morning`
  and an Ashcrown-day sub-frame (color script) would let env-art re-grade the kits without an id change.
- **Not done here:** criterion 3 (per-arena staging: underwater shorter runs and slower falls, no run past a deck's
  rail) needs choreo data, not scenes; left for a follow-up (the criterion stays open).

- 2026-10-24 (track lead): merged the agent's five greybox arenas; underway_tower lifted (ambient 0.6, key 0.45) so the foes read (pillar 4), re-approved after viewing. Staging: arenas.json `staging` (underway: travel 0.6, tempo 0.8; derelict deck: travel 0.85), read by BattleChoreo. BattleArena clears moved nodes' owner (no "inconsistent owner" warnings). Open: the derelict and Ashcrown fights are morning/day in the beats, graded night here as agreed with env-art; Art may add sub-frames.

## Review log
