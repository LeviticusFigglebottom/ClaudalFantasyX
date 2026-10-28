# 0193 — Steep stairs are walked on a marked path

- **Status:** proposed
- **Date:** 2026-10-27
- **Roles affected:** architect, environment (env-art kits), cinematics (act1-chapters, slice-polish), character
  (creatures' NPCs)
- **Author role:** combat (hero-integration)

## Context
The field controller walks floors up to 45° and has no step-up (ADR 0200 turns Act I's stairs into ramps). Ch5
Ashcrown's kit climbs by a 48° flying stair and descends by 60° vein stairs (ashcrown.md §0.1, §2.1), and its swap
(M3-C05-1215) is blocked on a way across them. M3-ARC-1216 listed three options:
1. a traversal interact (Climb / Descend);
2. re-cutting the flights under 40°;
3. a per-zone floor-angle override.

The Lead asked for a stair mode in locomotion itself, for heroes, followers and NPCs: snap to the steps along a
marked path, eased, at a slowed pace, with no sliding (SPEC §1 pillar 3, the pilgrimage, walked rather than
cut).

## Options
1. A traversal interact: a short scripted climb, then placement at the other end. The player gives up control on
   every flight, and followers teleport.
2. Re-cut the flights under 40°. This changes the temple's massing and its silhouette from Pemakar.
3. Raise the controller's floor angle per zone. A 48° walk at field speed reads wrong, 60° doesn't work at all, and
   there are still no steps.
4. **A marked flight walked on its profile.** A HeroStairFlight marks the flight (foot, run, rise, width).
   HeroStairs takes the player along it with his own stick, at a slope speed, on a stepped and eased height profile,
   clamped inside the flight's width. Followers and NPCs read the same profile.

## Decision
Option 4.
- `HeroStairFlight` (node, or a zone layout `"stairs"` row) and `HeroStairs` (on the field player, added by
  HeroFieldActor.attach), tuned by game/data/hero_motion/stairs.json.
- Walking on a flight:
  - the root follows the profile: each step's rise eased over riser_share of its run, then flat tread;
  - speed along the slope is at most slope_speed_mps;
  - no gravity, no sliding; sideways stays inside the edges;
  - the player is taken on within enter_m of an end walking in, and let go onto the landing past it.
- A body is only on a flight within height_tolerance_m of its profile, so walking under a flying stair is safe.
- The flight's own blocking collision stays: the controller never walks it.
- Followers use the profile's height and pace. NPCs and cutscene walks get `HeroStairs.height_at` and
  `speed_cap_at`.

## Consequences
- Kits can keep steep, real stairs; zone owners mark each flight once (a node or a layout row) and give each end a
  landing floor.
- The player keeps control on stairs, and the party climbs with him, step by step.
- FieldNpc and the CutsceneSequencer's `@mark` walks must call `height_at` to stand on a flight; until they do, an NPC
  or a scripted walk across a flight follows its own line. Requests were filed to their owners.
- The guards (ADR 0192) cover stairs: test_hero_stairs runs the climb, the descent and the followers through
  HeroMotionGuard.
