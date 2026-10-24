# Shell Shrine load + GI bake on hardware: hang probe (2026-10-24, measure only)

**Why.** In the Lead's batch-5 gate, a lavapipe capture of `shrine_s01_approach` deadlocked twice after
"GI baked (2 states)". The main thread was in a cond-wait, and the four WorkerThreads were blocked on a mutex. A
Lead QA agent is root-causing it on lavapipe. This checks whether it hangs on a real GPU. Nothing was fixed here.

**Setup.** RX 9070 XT, Godot 4.6.3, `claude/m2-slice` @ 511aff82 in a throwaway worktree (removed afterwards).

## Results
- **The capture, 20 times:** `tests/screenshots/capture.tscn -- --shots=shrine_s01_approach`, each with a 180 s
  timeout. **20/20 completed and saved the frame in 7–10 s. No hang.** "GI baked (2 states)" took 3521–3848 ms.
- **The game path, 5 times:** the slice sweep's `launch,shell_shrine` at High, 2560×1440. All 5 completed, so no hang.
- **But it's over budget:**

| Run | GI bake | Shell Shrine hidden worst frame | entry total | visible worst |
|---|---:|---:|---:|---:|
| 1 | 3712 ms | **5643 ms** | 6491 ms | 7.9 |
| 2 | 3601 | **4182** | 4882 | 4.5 |
| 3 | 3662 | **4252** | 4953 | 3.5 |
| 4 | 3628 | **4220** | 4914 | 3.4 |
| 5 | 3606 | **4198** | 4893 | 4.6 |

  The VoxelGI bake (`ShellShrineLevel`, two lighting states at load) runs in one main-thread frame. That breaks
  ADR 0029 on a fast GPU: hidden frames ≤ 1 s and zone entry ≤ 3 s. On the integration branch before this bake, the
  shrine's entry was about 0.5 s with a worst hidden frame of 0.15–0.2 s (M1-RND-29). On a min-spec GPU it will be
  longer still.

## For the Lead
- No hang on the GPU in 25 loads. The lavapipe deadlock looks specific to the software rasteriser's threading
  (llvmpipe/lavapipe worker threads).
- The bake's cost is a separate issue for m2-slice/Environment. Ideas: spread the two states over frames (one per
  frame, under the fade); bake only the opening state at load and the other one when the door opens; or ship
  baked VoxelGI data. Measure-only here; nothing changed.
