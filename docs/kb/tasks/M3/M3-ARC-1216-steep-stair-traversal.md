---
id: M3-ARC-1216
title: A steep-stair traversal for the field (Ashcrown's 48° flying stair and 60° vein stairs)
role: architect
reviewer: cinematics
status: review
owner_session: "hero-integration (session_01PzF7Jc4XVQdTWcaYUyCjPB), reassigned by the Lead 2026-10-27"
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
env-art's Ashcrown kit (ashcrown.md §0.1, §2.1) climbs the temple by a 48° flying stair and descends the trial by
60° vein stairs. The field controller has no step-up and walks floors up to 45°, so Act I's kit zones turn stairs
into ramps (ADR 0200), which can't stand in for these flights. Ch5's Ashcrown swap (M3-C05-1215) is blocked on a way
across them. Options (act1-chapters' preference first):
1. **A traversal interact**: a trigger at a flight's foot and head ("Climb" / "Descend") that plays a short climb
   (HeroMotion along the flight's line, camera on a rail) and places the party at the other end; the flight itself
   keeps a box collider so nobody walks it. Data: `traversals: [{id, from, to, path: [points], prompt_key}]` in the
   zone layout.
2. env-art re-cuts the flights under 40° (changes the temple's massing and its far silhouette from Pemakar).
3. A per-zone floor angle override for the controller (a 48° walk reads wrong at field speed; 60° doesn't work).

## Acceptance criteria
- [x] A decision: ADR 0193. The Lead asked for a walkable stair mode instead of option 1's traversal interact
      (heroes, followers and NPCs walk the flight).
- [x] The traversal in the field, with tests (tests/unit/test_hero_stairs.gd, 7):
      - a 48° climb and a 60° descent, each step by step with no snaps;
      - the speed along the slope stays at slope_speed_mps;
      - standing still on a 60° flight doesn't slide;
      - pushing sideways stays inside the flight;
      - walking under a flying stair doesn't climb it;
      - Asha and Toma follow up the steps.
- [x] Ashcrown's flights are placed and checked in play. env-art's M3-ENV-1303 did it (not act1-chapters'
      M3-C05-1215): 24 HeroStairs rows in ashcrown_collision.json (KitCollision merges them), and
      test_ch05_ashcrown_walkable walks them, 5/0 (2026-10-29).

## Notes
### 2026-10-27 (hero-integration): how a zone gets a walkable steep flight
- **Mark it**, either way:
  - a `HeroStairFlight` node (game/hero_motion/hero_stair_flight.gd). Its origin is the centre of the foot on the
    lower floor; it climbs along the node's -Z (forward); exports `run_m`, `rise_m`, `width_m`, `step_rise_m`
    (0 = stairs.json's 0.18);
  - or a row in the zone layout's `"stairs"` list:
    `{"id": "FlyingStair", "foot": [x, y, z], "head": [x, y, z], "width_m": 2.0, "step_rise_m": 0.18}`.
    HeroStairs (on the player) builds a HeroStairFlight for each row when the zone loads.
- **Collision:** keep the flight's own blocking collision (a box or ramp the controller can't walk). The flight takes
  the player before he reaches it: within `enter_m` (0.35 m) of either end, walking in.
- **Landings:** each end needs a floor at its height for the controller to walk on after it lets go.
- **Followers** take the steps from the flight on their own.
- **NPCs and cutscene walks:** `HeroStairs.height_at(node, point)` gives the step height (NAN off a flight), and
  `HeroStairs.speed_cap_at(node, point)` the pace. Creatures' FieldNpc and the sequencer's `@mark` walks can adopt
  them (requests filed).
- **Tuning:** game/data/hero_motion/stairs.json:
  - slope_speed_mps 1.0;
  - riser_share 0.8: the root steps up tread by tread, eased;
  - height_tolerance_m 0.6: nobody walking under a flying stair is put on it.

## Review log
