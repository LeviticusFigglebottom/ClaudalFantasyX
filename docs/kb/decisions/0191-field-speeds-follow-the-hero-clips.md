# 0191 — Field walk and run speeds follow the hero locomotion clips

- **Status:** proposed
- **Date:** 2026-10-24
- **Roles affected:** architect (field movement), cinematics (sequencer walk speeds), audio (footsteps), character (clips)
- **Author role:** architect (hero-integration track, M2-HER-1107)

## Context
The human's playtest asked for heroes that move naturally in the field (ADR 0190). The field speeds
(`game/data/world/field_movement.json`) were set for a capsule: walk 2.4 m/s, run 4.6 m/s. The real heroes' in-place
cycles plant their feet at much lower speeds. M2-CHR-12's rebuilt clips (`game/data/characters/locomotion.json`) run
at walk 0.88–1.04 m/s and run 2.59–3.00 m/s. Playing them at the old speeds needs a 1.5–1.8× run playback (a sprint
cadence on a jog stride) or leaves 15–35% foot slide. M2-HER-1101 already lowered the walk to 1.5 m/s, but at that
speed the blend mixes 25–35% of the run cycle into the walk.

## Options
1. Keep the gameplay speeds and speed the clips up (raise `max_playback_scale`): fast, but the feet whirl.
2. Ask for faster clips: longer strides read as lunging at this scale (characters chose the strides per persona).
3. Bring the field speeds to the clips: walk 1.0 m/s, run 3.6 m/s, with the run playing at 1.20–1.39× so every hero
   plants.

## Decision
Option 3. `field_movement.json`: `walk_speed_mps` 1.0, `run_speed_mps` 3.6. Acceleration (9) and deceleration
(12) stay for responsiveness. 3.6 rather than 3.4 keeps audio's `run_above_m_s` (3.5) classing it as a run. The
rationale and the foot-slide numbers per hero are in M2-HER-1107.

## Consequences
- **Feet plant.** Measured slide at a run drops from 23–34% to under 8% for each hero.
- **The field is slower, about 22% at a run.** Zone traversal times and FieldEncounters' distance pacing get longer
  in time. Encounter distance (metres walked) is unchanged.
- **Followers** keep their 5.4 m/s catch-up cap.
- **Other owners:**
  - The sequencer's `walk_mps` (1.3) reads cleaner at ~1.0 (m2-slice's call).
  - footsteps.json step spacing should follow the clips' `foot_l_down` / `foot_r_down` markers (audio).
- If playtests find the run too slow, the next lever is a longer run stride from characters, not a higher playback
  scale.
