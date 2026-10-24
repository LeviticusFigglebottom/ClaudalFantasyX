---
id: M2-ARC-02
title: A shipped owner for the weather clock (hymn_wind_time, hymn_wind) so zone and battle water moves
role: architect
status: review
reviewer: lead
owner_session: "worktree-agent-a4071bcb36cd4fdae"
depends_on: []
milestone: M2
request-from: "lead"
---
## Goal
The PC's M2-RND-04 work found that no shipped scene advances the weather clock (`hymn_wind_time`) or sets `hymn_wind`. Only test rigs and the Drownbell flood rig drive it. So the water in Haluna, the beach and every ordinary battle stands still in play, even though every water and vegetation shot (whose capture setup pins the globals) looks right.

## Acceptance criteria
- [x] One runtime owner, an autoload or a system SceneRouter installs the way `ShaderGlobals.install` is, advances `hymn_wind_time` every frame through `ShaderGlobals.set_value`. The owner pauses with the tree and keeps its value across scene swaps.
- [x] `hymn_wind` (direction and strength) comes from zone data (a per-zone JSON or zone-script export), with a project default when a zone sets none.
- [x] The Drownbell flood rig's own clock defers to the owner, so there's one writer; document how it gets its time.
- [x] Screenshot capture stays deterministic. Capture setup's pinned globals must win over the owner, either by disabling the owner under capture or by having capture override it last. No baseline changes.
- [x] Tests: the clock advances, pauses, and survives a swap; zone wind is applied and reset; capture pinning wins.
- [x] docs/kb/tech/water.md and architecture.md describe the owner.

## Notes
- Source: the PC GPU session's RND-04 report (2026-10-24).
- Respect the ShaderGlobals listener API (M1-ENV-09) and the zone-global reset on `scene_swapping` (M1-RND-23). Decide whether the wind belongs in ZONE_GLOBALS; the clock itself must not reset.

## Notes (architect, worktree-agent-a4071bcb36cd4fdae)
- Owner: `WeatherClock` (game/core/weather_clock.gd), the SceneRouter child that `WeatherClock.install(self)` adds. It is PROCESS_MODE_PAUSABLE and never resets.
- Wind: comes from game/data/world/zone_weather.json, keyed by scene path, with a `default` row. It is written on `scene_swapping`. It is not a ZONE_GLOBAL, because the owner rewrites it on every swap and so stays independent of handler order.
- The clock is in the new `ShaderGlobals.FRAME_GLOBALS`, so listeners are not called every frame.
- Capture: tests/screenshots/capture.gd holds the owner for the whole run, so baselines don't move.
- Flood rig: its clock is removed. It reads the shared global.
- Handoff: docs/kb/handoffs/2026-10-24-architect-19.md.

## Review log
- 2026-10-24 architect (worktree-agent-a4071bcb36cd4fdae): ready for review (reviewer **lead**).
