---
id: M3-ENV-711
title: "Prologue: swap the City's primitives for M3-ENV-710's iskarra_city.tscn"
role: architect
status: todo
owner_session: ""
depends_on: [M3-ENV-710]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
For slice-polish, which owns `game/levels/prologue/**`. M3-ENV-710 built Iskarra's kit and a drop-in scene,
`res://assets/environments/zones/iskarra/iskarra_city.tscn`, that places each piece where a primitive stands now.

## Acceptance criteria
- [ ] In `prologue.tscn`, delete `City/Terrace`, `City/Rise`, `City/Towers`, `City/Arches`, `City/LampColumns` (and
      their now-unused Box/Cylinder sub-resources) and instance `iskarra_city.tscn` under `City`. Keep `City/Water`,
      `City/Vigils` and `RhenLantern` as they are.
- [ ] Vigils still stand on the paving: the paving top is y 0.4 as before; the rise top is y 1.0 as before.
- [ ] Add a shot for P01 to `shots.json` (none exists yet) and post a render request; env-art views it.
