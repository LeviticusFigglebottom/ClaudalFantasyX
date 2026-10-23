---
id: M1-ARC-05
title: Camera director cutscene control and debug overlay input fixes (review-sweep-A)
role: architect
status: done
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
- 2026-10-23 cinematics (review-sweep-C): **approve with fixes**. The `play_shot`/`release` contract works for an `@camera`-driven sequencer as written. Repeated `play_shot` chains shots, explicit `blend=0` cuts, volume selection is suspended, the return shot is remembered outside volumes, `snap()` stays on the held shot, and the debug-overlay and F6 fixes look right (the full suite passes). The gaps are on the authoring side: what a cutscene can say in `.dlg`, and how the sequencer knows a move landed.
  - should-fix: `game/world/field_camera_director.gd:164-189` (`release`). It "always blends… ignoring `hard_cut` and `force_hard_cut`". `force_hard_cut` exists for setups where a blend would sweep the camera through geometry, or reverse the screen axis (a camera behind a wall, a 180° side-on dolly). Ending a cutscene inside such a volume will drag the lens through the set. Fix: honour `v.force_hard_cut` on release, so only a shot's soft `hard_cut` is overridden. Or let the cue choose (see the next item).
  - should-fix: `game/data/dialogue/cues.json` `camera`. There is no authored release: the sequencer "calls `release()` when the cutscene ends" with an implicit blend, so a writer can't control the hand-back, or hand the camera back mid-scene for walk-and-talk. `@camera` also can't pass the `ease` that `play_shot` takes. Fix: add `@camera release [blend=] [ease=]` and an `ease=` kwarg on `@camera`, with the cue doc in dialogue_format.md.
  - should-fix: field_camera.md:69 ("Wait for `blend_finished(shot)`") against `_activate` (field_camera_director.gd:413-436). A cut or a no-move `play_shot` never emits `blend_finished`, so a sequencer that waits on it after every `@camera` (to hold the next line until the move lands) hangs on every `blend=0.0` cue. Both slice scenes use `blend=0.0` almost exclusively. Fix: emit `blend_finished` for cuts and no-ops too, or give the sequencer one `shot_settled` signal it can always await.
  - nit: field_camera_director.gd:300-315. `aim_node` is a NodePath resolved against the rail root, but sequencer-spawned actors have runtime paths, and a miss silently frames the **player** (it warns once). In a cutscene that frames the wrong person. Offer `play_shot(..., aim: Node3D = null)` (or `@camera H06 aim=asha`) so the shot sub-resource isn't mutated, and treat a miss as an error while `is_scripted()`.
  - nit: field_camera_director.gd:203-204. `update()` returns at once when `target == null`, so a scripted shot is never applied in a cutscene staged without the player node (an intro, or a remote location). Allow scripted evaluation without a target.
- 2026-10-23 lead: closing on review-sweep-C approve-with-fixes; sequencer-contract fixes are in M1-ARC-07.
