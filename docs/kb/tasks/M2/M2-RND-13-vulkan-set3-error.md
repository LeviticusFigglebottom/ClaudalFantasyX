---
id: M2-RND-13
title: "The 'Uniforms supplied for set (3)' Vulkan error with the compute storm body: root cause and fix"
role: rendering
status: done
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M2-RND-12]
milestone: M2
request-from: "lead"
---
## Goal
Twice a run, `gpu_bench` on `undertow_test.tscn` logged "Uniforms supplied for set (3) ... are not the same format
as required by the pipeline shader", followed by two "Attempted to free invalid ID". It's on the integration branch
already (found in M2-RND-10, queued by the Lead).

## Acceptance criteria
- [x] Root cause.
- [x] Fix, and no such errors on High, Medium or Ultra, including a resize.

## Notes (PC GPU, 2026-10-24)
**Isolated.** The error appears only with the compute body: none with `half_res_compute=false`, none with the storms
hidden, none on Low (shells). It shows every time the render size changes, which `gpu_bench` does when it sizes its
window. A game boot rarely does this, but a window resize or a render-scale change would.

**Root cause.**
- `UndertowBodyEffect._ensure_targets` recreates its render targets on a size change. It freed the old
  textures at once, on the render thread.
- But the `Texture2DRD`s that the composite and the water sample only get the new RIDs through `set_deferred` (the
  main thread; assigning on the render thread keeps the placeholder).
- So for a frame those materials' uniform sets still referenced freed textures. Godot drew them with a set that
  lacked the texture bindings: the composite's 16-byte set against its pipeline's 32 bytes and two textures, and
  likewise a 464-byte set against 832. That's the set-3 error.
- Then Godot tried to free those uniform sets' stale texture references: "Attempted to free invalid ID".

**Fix.**
1. Replaced targets are retired, not freed: they're freed `RETIRE_FRAMES` (3) dispatches later, once the main
   thread has handed the new RIDs over. Retired ones are also freed with the effect.
2. The composite gets the effect's textures, and is shown, only once their RD textures exist. Before the first
   dispatch they're invalid too.

**Verified.** `gpu_bench` on `undertow_test.tscn`, Day camera, at 1280×720 then 2560×1440 (a resize), on High,
Medium and Ultra: **0 error lines**, against 2 set-3 errors plus 2 invalid frees before. The undertow tests pass
(53/0, GPU and headless), and a capture is unchanged (RMSE 0.0003).

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **The diagnosis holds against the code:** `UndertowBodyEffect` no longer frees resized targets on the render
    thread while the `Texture2DRD`s still hold them. Retired targets wait in `_retired` and are freed a frame
    later (lines 69–72).
  - **Checks:** `--filter=undertow` 53/0. The resize run on High, Medium and Ultra is the PC's measurement. Done.
