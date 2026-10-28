---
id: M3-ENV-711
title: "Prologue: swap the City's primitives for M3-ENV-710's iskarra_city.tscn"
role: architect
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M3-ENV-710]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
For slice-polish, which owns `game/levels/prologue/**`. M3-ENV-710 built Iskarra's kit and a drop-in scene,
`res://assets/environments/zones/iskarra/iskarra_city.tscn`, that places each piece where a primitive stands now.

## Acceptance criteria
- [x] In `prologue.tscn`, delete `City/Terrace`, `City/Rise`, `City/Towers`, `City/Arches`, `City/LampColumns` (and
      their now-unused Box/Cylinder sub-resources) and instance `iskarra_city.tscn` under `City`. Keep `City/Water`,
      `City/Vigils` and `RhenLantern` as they are.
- [x] Vigils still stand on the paving: the paving top is y 0.4 as before; the rise top is y 1.0 as before.
- [x] Add a shot for P01 to `shots.json` (none exists yet) and post a render request; env-art views it.

- **env-art, 2026-10-27:** after viewing the PC's first Iskarra renders (gpu/render-env-art-8770a06):
  - **Water.** The towers read as floating over the dusk haze, because a flat StandardMaterial plane can't reflect
    them. The preview now uses the project's `WaterSurface`, with `haluna_water_material.tres` and `lagoon_waves.tres`
    as Haluna does, and fog from 70 m at 0.2. When you swap the city into `prologue.tscn`, replace its `City/Water`
    plane the same way.
  - **Paving.** The inlay is now a narrow channel along every fourth row instead of a checkerboard.
  - **The corner.** The plaza's fallen corner is pulled back, clear of Kerrid's vigil at (9.5, −5.5) (M2-FP-103).
