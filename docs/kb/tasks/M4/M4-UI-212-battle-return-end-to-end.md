---
id: M4-UI-212
title: "The battle return end to end: at most 1 s of black after a won fight, input live as the fade lifts"
role: qa
status: todo
owner_session: ""
depends_on: []
reviewer: ui
milestone: M4
request-from: ui
---
## Goal
The human playtest (2026-10-30): "after a battle is won, there's a long, multi-second black screen before you can see the screen and move again." ui-menus owns the victory panel and the loading layer; integration-qa owns the SceneRouter return and the field's reload. Sum both parts into one end-to-end number and cut it to at most 1 s of black, with input live as the fade lifts.

## What ui-menus measured and fixed (claude/ui, 8df5fe2b4; log `docs/kb/handoffs/live/ui-menus.md`, 2026-10-30 13:10)
- **Cause found:** ResidentLoads let the zone's own loads go when the battle loaded, so the return read them again from disk and the prewarm feed staged about 950 materials again.
- **Fix:** a field battle now keeps them.
- **Result, Brine Shoals after `ch06_flats_crabs` (headless):** zone entry was 4875 ms with 614 prewarm frames before the fix, and is 667 ms with 2 frames after.
- **The ui side's segments now:**
  - The victory panel opens 0.6 s after the last blow, over the battle, so it is not black.
  - Confirm on Return calls `FlowRouting.go_to` the same frame.
  - The loading cover holds nothing on this path.

## Method (to repeat and extend)
- **Headless, from the repo:**
  ```
  XDG_DATA_HOME=<own dir> godot --headless --path . res://game/core/debug/scene_swap_probe.tscn -- \
    --resident-loads --warm-resident --to=<zone .tscn> --round-trip=<encounter id>
  ```
  - The probe enters the zone, then the field battle, then the zone again.
  - It prints `SCENE_SWAP_PROBE {...}` with the return's stats: `entry_ms` (black, until the fade starts to lift), `prewarm_wait_frames`, `max_frame_ms`, and the visible window's frames.
  - Total black is about `entry_ms`. The fades are `SceneRouter.FADE_SEC` (0.35 s) each way, half-dark.
- **On the PC:** run the same probe without `--headless`, then check by hand: win a fight, press Return, and time from the press until the field shows and the hero walks. A 60 fps screen capture counted by frame is enough.
- **Where to look if it is still over 1 s:**
  - `SceneRouter._swap`: the holders it waits on, `MEASURE_FRAMES`, and any wait before the fade lifts.
  - The zone's own `_ready`: the cameras, the cast and the music start.
  - `WorldReturn.go_to`, if it routes through a cutscene or a card.

## Acceptance criteria
- [ ] An end-to-end number from the PC for at least two zones (one Act I town, one field), each at most 1 s of black.
- [ ] Input live as the fade lifts (the field does not wait on `SceneRouter.is_busy()`).
- [ ] The result logged in integration-qa's live file, with a pointer from ui-menus' log.

## Review log
