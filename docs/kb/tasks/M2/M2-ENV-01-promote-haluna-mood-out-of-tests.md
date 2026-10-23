---
id: M2-ENV-01
title: Promote the Haluna mood scene's shared content out of _tests/ before content lock
role: environment
status: todo
owner_session: ""
depends_on: [M2-FP-04]
milestone: M2
request-from: "qa"
---
## Goal
The playable zone `ch02/haluna` (game/levels/ch02/haluna/haluna.tscn) instances
`game/levels/_tests/haluna_mood/haluna_mood.tscn`, so its dressing, its sea (the `hymn_water_level`
publisher), its shrine (`haluna_shrine`) and its `WeatheringTide` live in a test folder. A change made
for a mood shot can then break the shipped zone without anyone noticing (M1-ENV-06 review-sweep-L nit,
carried by M1-NIT-02; docs/kb/tech/architecture.md "Location registry").

## Acceptance criteria
- [ ] The shared content moves to `game/levels/ch02/haluna/` (for example `haluna_dressing.tscn` and its scripts), and `haluna.tscn` instances that, not anything under `_tests/`.
- [ ] `haluna_mood.tscn` stays as a thin test wrapper (the shot cameras and capture setup) around the promoted scene.
- [ ] The five `haluna_*` shots re-render byte-identical, or any difference is explained and accepted by Rendering.
- [ ] locations.json, `SaveShrine` ids, ownership.md globs and PROVENANCE paths follow the move. `validate_data`, `--filter=haluna` and `--filter=world_return` pass.
- [ ] Done before content lock.

## Review log
