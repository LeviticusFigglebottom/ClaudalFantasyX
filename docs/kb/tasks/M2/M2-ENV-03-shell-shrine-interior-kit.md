---
id: M2-ENV-03
title: Shell Shrine interior kit to replace the trial's greybox (haluna.md §3.2)
role: environment
status: doing
owner_session: "env-art"
depends_on: [M2-FP-16]
milestone: M2
request-from: cinematics
---
## Goal
Request from the m2-slice track. The Shell Shrine trial (M2-FP-16) plays in a greybox built at runtime by `ShellShrineLevel` from `game/data/trials/shell_shrine.json` `layout` and `greybox`. The slice needs the room at final quality: the fan-shell roof and oculus, the curved walls and whorl columns, the carved channels with nacre inlay, the three rotatable shell-basins (each with three spouts, a 90° turn over 1.2 s), the octagonal inner pool, the shell-valve door that sinks as the pool rises, the side pool, the net-float charm (salt-glass, 6 cm), and the west-facing exterior steps with leaf-boats (S01).

## Acceptance criteria
- [ ] Kit pieces in `assets_src/environments/kits/` (reproducible, with PROVENANCE rows) and a dressed `ch03/shell_shrine` scene. The trial's moving parts are separate nodes the level can drive: each basin's turning part, the pool water, the door, the side-pool water and the charm. The level then swaps its greybox for them, keeping the same JSON positions or moving those.
- [ ] Channel water uses flowmap water (SPEC §8.2.1) where Rendering has it; otherwise a documented stand-in. A lit channel shimmers (no glimmer).
- [ ] LightmapGI baked per state (pre-flood and post-flood), as haluna.md's GI note recommends, or a measured alternative. Five shots S01–S05 at the brief's lenses, with lavapipe baselines.

## Review log
