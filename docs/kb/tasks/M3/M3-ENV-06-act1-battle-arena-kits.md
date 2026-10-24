---
id: M3-ENV-06
title: Act I battle arenas from the zone kits (five arenas on the M2-ENV-11 contract)
role: environment
status: review
owner_session: "env-art"
depends_on: [M3-BPR-01, M2-ENV-11]
milestone: M3
request-from: combat
reviewer: rendering
---
## Goal
Build the Act I battle arenas proposed in M3-BPR-01 (oruvel_raft_morning, underway_tower, causeway_route_afternoon,
derelict_deck_night, ash_terrace_lanternfall) as `assets/environments/arenas/<id>/<id>.tscn` on the M2-ENV-11
contract (docs/kb/tech/battle_arenas.md), each from its zone kit and graded from the color script. Rename or regroup
ids freely; tell battle-presentation in your live log, and it updates the encounter rows and arenas.json.

## Acceptance criteria
- [x] Five arenas on the contract (WorldEnvironment, Sun, Sea or none, dressing, CameraHints; flat clear floor
      under the sandbox slots; nothing between the battle camera and the fighters)
- [ ] The underwater arena agreed with Rendering (underwater.md) for its look under the battle camera (proposal
      built; open in M3-RND-25)
- [x] Preview shots viewed and approved (five baselines on lavapipe, one per arena)

## Notes
- Request from the battle-presentation track (M3-BPR-01).
- **Plan (env-art, 2026-10-24):**
  - **Now, from merged kits:** `causeway_route_afternoon` (M2-ENV-10), `derelict_deck_night` (M3-ENV-02 Brine Shoals)
    and `ash_terrace_lanternfall` (M3-ENV-03 Pemakar).
  - **Next:** `underway_tower`, once M3-ENV-05's sea-floor kit merges. It also needs Rendering's agreement on the
    underwater look under the battle camera.
  - `oruvel_raft_morning` has no raft-town kit yet. It will be built from the Haluna waterfront and village pieces
    (deck planks, stilts) unless a raft-town zone task comes first.
  - The ids are kept as proposed.
- **Built (env-art, 2026-10-24): three of five.** On the M2-ENV-11 contract, each with a lavapipe baseline
  (viewed; dark fighters read in all three):
  - `causeway_route_afternoon` (`ch03_causeway`, 14:30): a shell-and-sand bar on the low-tide flats, the kit's
    causeway slabs and marker posts on their bed past the enemy line and away to the Shell Shrine's islet, saltgrass,
    coral heads, the lagoon; the zone's cumulus sky and `lut_ch02_noon`. New ground `arena_causeway_route_ground`
    (haluna_kit job).
  - `derelict_deck_night` (`ch04`): a great trader's main deck, aground on the shoals; the camera stands over the
    deck, bulwarks beside the fight at x ±7.2, the hatch and mast stump forward, a raised foredeck; oil-lamp key
    (rail lanterns, a hatch lamp, Rhen's lantern behind the party), the moon as the directional (0.28 ≤ 2.5 × 0.12),
    sea-glow 0.12 on a `night_sea` copy, other wrecks out in the glowing sea. New ground `arena_derelict_deck`
    (brine_shoals_kit job); new grade `lut_ch04_wake`.
  - `ash_terrace_lanternfall` (`ch05`): Pemakar's tier 7 widened into a flat ash tread; the tier 8 grave wall behind
    the enemy line with mourners' lamps at its foot, tiers 8 and 9 (graves, lamps, boats, trees) from the kit
    preview's town layout, the main stair and gate on frame right, the massif, Ashcrown, the plume and the far
    lights. New ground `arena_ash_tread` (pemakar_kit job); new grade `lut_ch05_lanternfall`.
  - Tests: all five ids in `tests/unit/test_battle_arenas.gd` (flat clear floor, nothing between camera and
    fighters, every arena's own Sea publishing only while visible); the three grounds, the night grades and rule 3
    in `tools/tests/test_arenas.py`.
- **Swap-in note for battle-presentation:** scenes at `BattleArenaRoot.path_for(id)`:
  `assets/environments/arenas/causeway_route_afternoon/causeway_route_afternoon.tscn`,
  `assets/environments/arenas/derelict_deck_night/derelict_deck_night.tscn`,
  `assets/environments/arenas/ash_terrace_lanternfall/ash_terrace_lanternfall.tscn`. Same loader rules as the first
  two (WorldEnvironment and Sun to the battle root, the rest under `Arena`, `Sea` an `ArenaSea`). No `BossAnchor` or
  `FloodAnchor` in any of the three. CameraHints: route `wide_high`, `party_side`, `foe_side`, `from_the_causeway`;
  deck `wide_high`, `party_side`, `foe_side`, `from_the_foredeck`; terrace `wide_high`, `party_side`, `foe_side`,
  `lanternfall_low`. Add the ids to `arenas.json` and the encounter rows (that track's files).
- **Known:** the terrace's default frame cannot show the plume or Ashcrown (the camera's top edge is 8° up, the
  crown 23°+ from any tier); they are in the arena for the hints. ~70 unshadowed omnis on the terrace, 7 on the deck:
  to measure on the GPU tier.
- **Remaining (status stays doing):** `underway_tower` (after M3-ENV-05's sea-floor kit, with Rendering's
  underwater agreement) and `oruvel_raft_morning` (Haluna waterfront and village pieces).
- **Built (env-art, 2026-10-24, second worker): the last two; all five exist, status → review (rendering).** Each with
  one lavapipe baseline, viewed and iterated (the fighters read in both):
  - `oruvel_raft_morning` (`ch01`, 10:30): one of Oruvel's working decks. New ground `arena_raft_deck` (haluna_kit
    job, `arenas.py`): planks fore and aft at y 0 over four lashed hulls (painted bows out past the open north end),
    rope rails and float logs beyond the slots at x ±6.3, a dive ladder; a plank bridge to the chandler's cabin raft;
    the town's other rafts on hulls with bridges between them; single hulls moored round. The town on it is Haluna's
    pieces (cabin houses, a storehouse, a net shed, a carved gull on every ridge, a stall and awning, nets, outriggers)
    and two Brine Shoals salvage pieces; the open sea east. New grade `lut_ch01_raft` (`zone_lut.py --grade
    ch01_raft`; a `band_sat` pass lifts the cyans and oranges 8%), shared with the Underway.
  - `underway_tower` (`ch01_underway_int`): the lamp gallery's breach end, 22 m down. No new geometry: the kit
    preview's tower and terrace (`ou_preview_layout.py`, read-only) turned a quarter so the camera looks east down the
    gallery to the breach; the kit's F9 slabs are the floor; the fight's bay's columns are left out (props within 4 m
    of a slot). Rhen's lantern (the rig's) at his lantern hand on slot 0 keys the fight; the breach's sunlit patches
    and the terrace beyond are behind the fighters; held motes sink beyond the enemy line. The look is the existing
    `UnderwaterRig` through `ArenaUnderwater` (an in-scatter `light_scale` 0.33, new in `game/world/arenas/`), the sun
    and ambient baked tinted for 21 m of water (downwelling stand-in). **Not agreed with Rendering yet:** request
    filed, M3-RND-25 (what the arena needs from the rig under the battle camera; extends M3-RND-24).
  - Contract: the Godot floor rays now start at the fighters' head-room (5.5 m), so the gallery's ceiling is not
    "on the floor"; the tools test exempts the floor's own tiles and lets structure (walls, piers) stand 2 m off the
    slots (props still 4 m). Tests: both ids in `tests/unit/test_battle_arenas.gd` (all seven arenas) plus the
    underwater arena's rig, lantern and motes, and ArenaUnderwater's scale; `tools/tests/test_arenas.py` adds the raft
    deck's and the gallery slabs' floors, the downwelling tint, the gallery's columns and `lut_ch01_raft`.
- **Swap-in note for battle-presentation (the last two):** `assets/environments/arenas/oruvel_raft_morning/oruvel_raft_morning.tscn`
  and `assets/environments/arenas/underway_tower/underway_tower.tscn` (`BattleArenaRoot.path_for(id)`). Same loader
  rules. No `BossAnchor` or `FloodAnchor`. CameraHints: raft `wide_high`, `party_side`, `foe_side`,
  `from_the_bridge`; Underway `wide_high`, `party_side`, `foe_side`, `to_the_low_lights`. **The Underway's extra
  children** go under `Arena` with the rest: `Underwater` (ArenaUnderwater: it must be added after the moved
  WorldEnvironment and Sun, which the loader's child order already gives), `Lantern` (re-target
  `Arena/Underwater.lantern_target` to Rhen's lamp node once his fighter carries one) and `HeldMotes`. Keep camera
  hints 2.5 m or more off the lantern (the halo hazes the frame nearer). Add both ids to `arenas.json` and the Ch1
  encounter rows (C1-04/C1-06 Underway fights; a raft-town fight).

## Review log
