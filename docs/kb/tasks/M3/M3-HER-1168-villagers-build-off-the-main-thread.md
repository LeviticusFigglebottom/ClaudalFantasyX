---
id: M3-HER-1168
title: "Request (creatures, VillagerLayer): build the villagers' actors off the main thread under the fade; Haluna's held reveal is ~3 s on every fresh entry (the Drownbell's return, the human's black-screen report)"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The last piece of the human's black-screen report: the Drownbell's return (Shell Shrine → Haluna DockNight, a different
zone, so not the resident field) still holds about 5 s of black. Traced headless on big28 (c646c3a8) with cloud-qa's
return_probe, logging SceneRouter's fade and its reveal holders every 100 ms from the victory panel's Return:

| from Return | what |
|---|---|
| 0–0.4 s | the fade going down |
| 0.4–1.9 s | Haluna loading and instantiating (behind the fade, prewarmed by ui's 95f51b98 during the panel) |
| **1.9–5.0 s** | **Haluna in the tree; the reveal held by `villager_layer.gd`** (`_build_spread`: 18 rows at ~120–250 ms a frame) |
| 5.0–5.3 s | the fade lifting |

During a real change each villager row costs ~180 ms headless (its actor scene instantiated and readied, or a model
adopted under a FieldNpc). A time budget per frame was tried (as many rows a frame as fit 40 ms) and changes nothing,
because each row alone is over it. Every fresh Haluna entry pays this, not only the Drownbell.

## Ask
Take the per-villager cost off the hidden frames the way SceneRouter takes the zone's: instantiate each villager's
actor scene on a WorkerThreadPool task (`PackedScene.instantiate()` off the tree is thread-safe; ShaderGlobals.hold_writes
around it, as SceneRouter does), then add the ready instances a few a frame. Or build the layer during the zone's own
threaded instantiate, before the zone enters the tree. Keep the held reveal only for what is left.

## Acceptance criteria
- [ ] The Drownbell return (`return_probe -- --cases=drownbell`): Haluna's reveal held ≤ 0.5 s headless after the zone
      is in (now 3.1 s), and no visible frame over 50 ms when the fade lifts.
- [ ] integration-qa re-measures and logs the timeline.

## Review log
