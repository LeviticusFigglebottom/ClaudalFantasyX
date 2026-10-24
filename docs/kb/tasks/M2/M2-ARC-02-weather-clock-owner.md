---
id: M2-ARC-02
title: A shipped owner for the weather clock (hymn_wind_time, hymn_wind) so zone and battle water moves
role: architect
status: doing
owner_session: "worktree-agent-a4071bcb36cd4fdae"
depends_on: []
milestone: M2
request-from: "lead"
---
## Goal
The PC's M2-RND-04 work found that no shipped scene advances the weather clock (`hymn_wind_time`) or sets `hymn_wind`. Only test rigs and the Drownbell flood rig drive it. So the water in Haluna, the beach and every ordinary battle stands still in play, even though every water and vegetation shot (whose capture setup pins the globals) looks right.

## Acceptance criteria
- [ ] One runtime owner, an autoload or a system SceneRouter installs the way `ShaderGlobals.install` is, advances `hymn_wind_time` every frame through `ShaderGlobals.set_value`. The owner pauses with the tree and keeps its value across scene swaps.
- [ ] `hymn_wind` (direction and strength) comes from zone data (a per-zone JSON or zone-script export), with a project default when a zone sets none.
- [ ] The Drownbell flood rig's own clock defers to the owner, so there's one writer; document how it gets its time.
- [ ] Screenshot capture stays deterministic. Capture setup's pinned globals must win over the owner, either by disabling the owner under capture or by having capture override it last. No baseline changes.
- [ ] Tests: the clock advances, pauses, and survives a swap; zone wind is applied and reset; capture pinning wins.
- [ ] docs/kb/tech/water.md and architecture.md describe the owner.

## Notes
- Source: the PC GPU session's RND-04 report (2026-10-24).
- Respect the ShaderGlobals listener API (M1-ENV-09) and the zone-global reset on `scene_swapping` (M1-RND-23). Decide whether the wind belongs in ZONE_GLOBALS; the clock itself must not reset.

## Review log
