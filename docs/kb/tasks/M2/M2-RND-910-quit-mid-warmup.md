---
id: M2-RND-910
title: "Quitting during a first run's warm-up hangs on exit (RND-15/18's worker-thread scene loads)"
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: architect
depends_on: [M2-RND-15, M2-RND-18]
milestone: M2
request-from: "lead"
---
## Goal
The Lead's big8 merge found it: the `boot_title` capture rendered (rmse 0) but its process never exited (killed at
600 s). A player who quits during a first launch would hit the same thing.

## Root cause
Reproduced on Windows (RX 9070 XT, the editor binary) as well as lavapipe: exit 124 after 180 s. Prints around the
waits showed predelete blocked in `WorkerThreadPool.wait_for_task_completion` on the **M2-RND-18 harvest load**: a
raw `load()` of a first_run_scenes entry (Haluna) on a WorkerThreadPool task. The live-scene tasks (M2-RND-15)
hadn't started. A `load()` on a worker can sit in the loader while the main thread, waiting on that worker in
predelete, never gets back to the loader's main-thread work.

## Fix (`game/core/shader_prewarm.gd`, `prewarm_harvest.gd`)
- The harvest loads through `ResourceLoader.load_threaded_request` and is polled each frame
  (`load_threaded_get_status`). There's no worker task.
- Live scenes load the same way. Only once a scene is loaded does a worker instance it:
  `PrewarmHarvest.instance_live` now takes the PackedScene and never loads.
- Predelete waits on no load. A request in flight stays with ResourceLoader. An instancing worker, which no longer
  loads, is still waited for and its instance freed.

## Checks
- `boot_title` capture on a first run (marker deleted): exits in **5 s, 3/3**. Before: hung until killed.
- New test `test_quitting_mid_first_run_never_waits_on_its_scene_loads`: a first run loading Haluna (harvest and
  live) is freed mid-load in under 500 ms. On the old code the prewarm suite **hangs** there (killed at 300 s, exit
  124), so the test catches the bug (the gate's step timeout fails it).
- Prewarm tests 22/0 (the RND-15 live-scene and RND-18 spread-harvest tests included). gdlint clean, and
  shader_prewarm.gd stays under 1000 lines (998) after trimming comments.

## Review log
