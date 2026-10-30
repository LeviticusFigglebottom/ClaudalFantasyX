---
id: M3-CIN-1250
title: "Request (creatures, the crowd's VillagerLayer): crowd routines start in step (Tamsule's fisher and boatman haul at 0.0 together)"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
`tests/unit/test_zone_cast.gd::test_a_cast_actor_shows_its_model_and_idles_out_of_step` is red on the integration branch
(merged into claude/act1-chapters @ f9074e913). In ch07/tamsule the crowd layer (M3-CRE-657 mounted it; M3-CRE-659's
routines) gives the cast fisher and boatman the routine `haul`, both at clip position **0.0**. Two people hauling in
lockstep read as robotic; ZoneCast had given each actor its own phase (`HeroIdleMicro.share(id, ...)`), as FieldNpc does.

## Acceptance criteria
- [ ] Each crowd body's routine starts at its own phase (a hash of its id, as ZoneCast and FieldNpc do).
- [ ] `--filter=zone_cast` green. act1-chapters already relaxed the test's clip-name check (a routine is fine); the
      out-of-step check stays.

## Review log
