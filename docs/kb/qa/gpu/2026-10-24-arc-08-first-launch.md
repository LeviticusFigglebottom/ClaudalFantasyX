# M2-ARC-08 first-launch re-measure on hardware (2026-10-24)

**Base.** The integration branch at e1d4f3e1, batch 4: M2-ARC-05's frame clock and M2-ARC-08's progress-based boot
wait and first-run cue.

**Build.** A baked Windows release (`Windows Perf`, shader baker on). Exported with a window, because a headless
export doesn't bake.

**Machine.** RX 9070 XT, 2560×1440.

**Method.** Before each first launch: `pipeline_warm.cfg`, the project's `shader_cache` and `vulkan` folders, **and
the AMD driver's Vulkan shader cache** (`%LOCALAPPDATA%\AMD\VkCache`, 1.4 GB; it rebuilds itself) are cleared.
M1-RND-29 left that last one alone, so this is the truly cold case. Then the slice sweep runs
`launch,title,haluna_beach`, a first launch followed by a second.

## Results

| | Low, first launch | Low, second | High, first | High, second |
|---|---|---|---|---|
| `reveal_wait_end` | **done** | **done** | **done** | **done** |
| `reveal_wait_ms` | 32,214 | 3,500 | 26,647 | 2,524 |
| `reveal_wait_max_frame_ms` | **1,570** | 389 | **2,890** | 304 |
| `reveal_wait_frames` | 168 | 33 | 165 | 30 |
| Launch's visible worst (sweep, the 60 frames after the lift) | **825 ms** | 0.6 | 0.7 | 0.6 |
| Haluna entry: hidden worst / total | **1,719** / 4,369 ms | 319 / 2,108 | **1,607** / 3,767 | 269 / 1,801 |

- **The wait ends on its own (done) in every run,** never at the cap. Without the driver cache, a cold first launch
  waits 27–32 s.
- **The cue shows:** "Preparing the graphics for first use. This happens only once.", with a thin progress bar,
  6 s into a cold first launch (`arc08/first_run_cue.png`, the editor binary). It fades in after
  `cue.delay_ms` (1.5 s), as designed.
- **What breaks ADR 0029, on the truly cold first launch only:**
  1. The launch's worst hidden frame: 1.57 s (Low) and 2.89 s (High), against ≤ 1 s. It's under the card.
  2. On Low, one **visible** 825 ms frame in the 60 frames after the card lifts, against ≤ 50 ms. The router's own
     `max_visible_frame_ms` reads 17.6, so it falls just after the router's window. Something still compiles after
     the reveal.
  3. Haluna's first entry has a 1.6–1.7 s hidden frame, and takes 4.4 s on Low against ≤ 3 s. The first-run warm-up
     doesn't cover all of Haluna's driver pipelines when the driver's cache is empty.
- The second launch is within budget everywhere. The visible worst is under 1 ms, but Haluna's entry is 1.8–2.1 s
  (better than M1-RND-29's 2.4–3.25 s).

## Exit-time leaks (the RND-29 residual)
Every run of the release build logs, at exit:
- **"1 RID of type Compute" and "1 RID of type Shader" leaked.** That's the warm compute pipeline, which M2-RND-11
  frees (it's in batch gpu6, not on this base yet).
- **"130 resources still in use at exit"**, plus 4 MaterialStorage shader RIDs, in every run, second launches
  included. That's the same family as RND-29's residual (scripts and preloaded shaders still referenced when the
  sweep quits). It's 130 here, against 94 under `--quit-after` before. On a windowed editor boot with a settled
  marker it was 0 in 2 runs today. So it tracks how the process quits (the sweep's `quit()` mid-scene), not the
  warm-up. Not fixed here.

## For the Lead
- ARC-08's progress-based wait works: always `done`, never the cap, and the cue shows.
- A cold driver cache is a much harder first launch than RND-29 measured. To get Low's 825 ms post-reveal frame and
  Haluna's first-entry frames under ADR 0029, the first-run warm-up needs to cover the driver pipelines Haluna and
  the title draw. That's for rendering (me) or ARC, whoever you route it to.

## Correction (M2-RND-15, 2026-10-24)
The "825 ms visible frame just after the lift" on cold Low was **not visible**. The sweep's launch wait timed out at
its 30 s transition timeout while the cold card held for 30–36 s, so its "visible" 60 frames were still under the
card (the first-run stage was drawing in them). The router's own window, which starts at the card's open, measured
the real visible worst: 17.6 ms. The sweep now waits up to 300 s and warns `SLICE_TIMEOUT` (M2-RND-15). With that,
the cold launch's visible worst is 1.5 ms. Haluna's cold first entry is fixed in M2-RND-15 (637 ms / 2.3 s on Low).
