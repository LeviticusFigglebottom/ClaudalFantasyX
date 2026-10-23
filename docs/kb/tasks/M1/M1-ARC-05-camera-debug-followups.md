---
id: M1-ARC-05
title: Camera director cutscene control and debug overlay input fixes (review-sweep-A)
role: architect
status: review
owner_session: architect-stream-5
reviewer: cinematics
depends_on: [M1-ARC-01, M1-ARC-02]
milestone: M1
request-from: "cinematics"
---
## Goal
Review-sweep-A findings on ARC-01/02.

## Acceptance criteria
- [x] FieldCameraDirector.play_shot(shot, blend)/release() that suspend volume selection until released
- [x] CameraShot.aim_node (aim at an actor/mark, not only the player)
- [x] snap() mid-blend into the active shot ends the blend; snap re-latches input to the visible camera
- [x] Debug overlay only consumes list keys on list pages (flags, teleport, Lattice); never swallows Enter/Space/Up/Down elsewhere
- [x] F6 Lattice cheat respects Facet stack caps

## Notes
- `play_shot(shot, blend_sec = -1, ease = &"")` / `release(blend_sec = -1, ease = &"") -> bool`, plus the
  signals `scripted_shot_started`, `scripted_shot_released` and `snapped`. The contract the sequencer
  drives from `@camera` is in `docs/kb/tech/field_camera.md`, under "Scripted shots".
- `release()` always blends unless it is given 0, even onto a `hard_cut` volume shot. Outside every volume
  it returns to the shot that was active before the first `play_shot`.
- `CameraShot.aim_node` + `aim_offset` work in FIXED (it looks at the node), PAN_FOLLOW, DOLLY (the node
  drives progress and aim) and ORBIT. A missing node warns once and falls back to the player.
- `snap()` ends any blend, resets the active shot's tracking, and emits `blend_finished` (if a blend was cut
  short) and then `snapped`. `FieldController` calls `FieldMotor.relatch(camera_yaw)` on `snapped`.
- List pages are data: `"list": true` in `game/data/debug/debug_overlay.json` (flags, teleport, lattice).
- F6: `DebugReadouts.grant_facets` clamps each Facet to `ItemDB.cap_of`.
- Field screenshots are unchanged: field framing behaviour without `aim_node` or scripted shots is the same.
  No re-capture was needed.

## Review log
