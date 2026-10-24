# M1-RND-29: a fresh install's first launch (2026-10-24)

Machine: RX 9070 XT, Godot 4.6.3. A baked Windows release build (`Windows Perf`), 2560×1440. Branch
`gpu/m1-rnd-29-first-launch` (integration at cd4e425, with M2-ARC-03's boot card, plus the sweep's `launch`
segment). "Fresh install" means this project's `shader_cache`, `vulkan` and `pipeline_warm.cfg` are cleared. The AMD
driver's own shader cache isn't cleared: it's shared with other apps. So a truly first install is somewhat
slower, most of all on Low and Ultra, which had run less often on this PC.

## Changes

1. **The first-run warm-up.** `ShaderPrewarm.first_run`: a boot run with no marker for this engine, GPU, driver and
   preset (`first_run_key`, `user://pipeline_warm.cfg`).
   - It stages every registry entry the preset wants, not only the resident ones, and harvests the registry's
     `first_run_scenes`: Haluna, Shell Shrine, the field battle, the First Verse and the prologue. That's 163–165
     draws.
   - It's time-sliced, behind M2-ARC-03's boot card, which waits for it. The marker is written when it finishes,
     so the second launch runs only the resident warm-up (17–19 draws).
2. **Prewarm frames are wall time.** Godot 4.6.3 (and 4.7.2) caps the process `delta` at about 140–150 ms: a
   500 ms stall reports 135–147 ms. ShaderPrewarm's `max_frame_ms`, and its batch halving, ran on `delta`, so they
   under-reported every long frame and never halved on them. They now use `Time.get_ticks_usec`.
   - BootCard does the same, which feeds the launch's `reveal_wait_max_frame_ms`. That's filed as **M2-ARC-05**.
   - The router's own swap and reveal loops already use wall time.

## Results (ms; hidden worst / whole entry; visible worst)

| | Low, first launch | Low, second | High, first | High, second | Ultra, first | Ultra, second |
|---|---|---|---|---|---|---|
| Launch, behind the card | **1348** / 9498 | 369 / 2354 | 542 / 5242 | 226 / 1907 | 525 / 5515 | 326 / 2264 |
| Haluna Beach | 200 / **1332**; 2.6 | 324 / 3249; 5.3 | 143 / 1257; 4.4 | 272 / 2430; 4.1 | 206 / 1301; 7.4 | 373 / 2792; 7.2 |
| Tideline battle | 126 / 549; 6.6 | 107 / 645; 7.0 | 123 / 553; 23.3 | 105 / 658; 7.3 | 130 / 587; 7.1 | 103 / 672; 6.9 |
| Shell Shrine | 149 / 509; 1.0 | 143 / 502; 1.1 | 146 / 507; 1.4 | 141 / 501; 1.2 | 146 / 507; 1.2 | 133 / 492; 1.1 |
| Drownbell battle | 221 / 588; 5.1 | 442 / 1060; 5.7 | 82 / 456; 4.8 | 300 / 935; 4.9 | 215 / 581; 5.4 | 495 / 1174; 10.1 |

**Before this change** (the same build, fresh install): Haluna's entry was 2.5 s (High), 4.3 s (Low) and 3.6 s
(Ultra), with worst hidden frames of 0.28–0.82 s.

**After the first-run warm-up, every zone entry passes ADR 0029:**
- entries take 0.46–1.33 s;
- hidden frames are at most 221 ms;
- visible frames are at most 23 ms.

**One frame still fails, once per install:** the first launch's worst hidden frame on Low is **1.35 s** (High
0.54, Ultra 0.53). It's the process's first 3D frame, the renderer's own first-use pipelines on a cold cache, under
the boot card. RND-27 already draws that frame plain, and it can't be split from the project side; Godot's driver
pipeline compile is synchronous. It's hidden, on the first launch only, and it's on the PC's cold Low path.

**The second launch** keeps Haluna's 2.4–3.25 s entry, which is its instancing and prebuild (M2-ENV-05, with
m2-slice), not pipelines: Low's 3.25 s is over 3 s for that reason.

## Checks

- **Run:**
  - gdlint and gdformat.
  - The Godot `prewarm` filter (14/0) and the full suite (1449/0).
  - validate_data and `taskboard --check`.
  - The GPU runs above (the perf build re-exported, and project.godot reverted after the export).
