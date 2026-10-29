---
id: M3-HER-1151
title: "WeatherClock writes hymn_wind_time while the router instantiates a zone on a thread: 'Attempting to initialize the wrong RID'"
role: architect
status: review
owner_session: "integration-qa (hero-integration track, architect role per the Lead 2026-10-28)"
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The human hit "Trying to cast a freed object" entering a fight. While integration-qa's real-frame battle entry probe
(`tools/dev/battle_entry_probe.tscn -- --chapters=3`) was looking for that, it logged this once on the router's swap
back from `ch03_causeway_shore` into `ch03/saltgrass_causeway`. That swap reported `"instantiated_on_thread": true`
and a hidden frame of 3.3 s.

```
ERROR: Attempting to initialize the wrong RID   (rid_owner.h:250 get_or_null)
ERROR: Parameter "mem" is null.                 (rid_owner.h:294 initialize_rid)
  [0] ShaderGlobals.set_value (game/core/shader_globals.gd:44)   RenderingServer.global_shader_parameter_set
  [1] WeatherClock.advance (game/core/weather_clock.gd:114)
  [2] WeatherClock._process (game/core/weather_clock.gd:103)
```

The likeliest cause is a race in the RenderingServer's RID owner. The main thread's `_process` writes a global
uniform while the router's worker thread is creating the zone's materials and other RIDs. The same family of fault
(an object or RID touched while another thread or the swap owns it) would explain an intermittent freed-object
error on a fight entry.

## Acceptance criteria
- [x] Find the cause: either hold the WeatherClock (and every other per-frame ShaderGlobals writer) while the
      router instantiates on a thread, or show that the write is safe and the race lies elsewhere.
- [x] The probe's ch03 run logs no RID error in three runs in a row (0, 0, 0 on big15 merged; before the fix, 1 in 2
      runs). The runs' other errors are all M3-HER-1158 (the result panel's freed casts).

## Notes
Owners: Systems Architect (`game/core/**`; SceneRouter, ShaderGlobals, WeatherClock). It reproduced once in two
ch1–3 runs, so it's intermittent. Filed rather than fixed because the files belong to another track.

## Done (integration-qa, holding the architect role)
- `ShaderGlobals.hold_writes()` / `release_writes()`: while held, set_value() and reset() keep the CPU copy current
  but hold the RenderingServer write. The last value per global is sent when the last hold ends.
- `SceneRouter._instantiate` holds them around the WorkerThreadPool task, so no global write walks the material list
  while the thread is creating the zone's materials. That covers WeatherClock and every other per-frame writer
  (water level, still actors, glimmer).
- tests/unit/test_shader_globals_hold.gd (3): held writes wait and the copy doesn't; holds nest; the router holds
  around its thread (source order). weather_clock 11/0, scene_router 15/0, haluna_weather 3/0.

## Review log
