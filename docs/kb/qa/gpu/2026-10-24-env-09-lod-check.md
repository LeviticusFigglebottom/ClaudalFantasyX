# M1-ENV-09 GPU check: the vegetation LOD chain and the 118–122 m crossfade (2026-10-24)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/m1-env-09-lod-check`, cut from the integration branch at 54425e2.
This checks 8569fe3: the LODs are chained by `visibility_parent`, and the shelter is re-probed on a new sun. The scene
is `vegetation_test.tscn`, PalmA, at `lod_end_m` 45/120/400, `lod_margin_m` 2 and `lod_fade_m` 6.

**Verdict: pass.** There are no pops, no holes, and no double draw outside the designed band. The band costs about
2–2.6 µs per crossfading palm at 1440p.

## 1. The colour-probe sweep on the GPU

`lod_sweep_probe.gd` was written for lavapipe; here it ran on Vulkan on the RX 9070 XT. It prints **`LOD_SWEEP PASS`**
for the still camera, sweeping in and sweeping out, at 40–50, 114–126 and 390–410 m. At 120 m all three passes give
the same rows:
- LOD1 is opaque from 116 to 122.0 m.
- LOD2 fades in at 118.5 m (0.22), then 0.43, 0.60, 0.73, 0.84 and 0.93, and is opaque from 121.5 m.
- Above 122.5 m only LOD2 draws.

So there's no hysteresis state left at this switch, and the 118–120 m hole and 120–122 m double draw that the task
describes are gone.

## 2. The real palm: `tools/gpu_bench/lod_pop.tscn`, stepped

This is PalmA alone (`--solo`: the other plants and the grass are hidden), at 0.25 m steps with 8 settle frames, over
110–130 m in both directions. The tool now records the viewport's objects and draw calls for each step.
- **Objects.** Outside the band there are 4: the sand, the sea and one LOD's two meshes. Inside 118.5–122.0 m there
  are 6 (LOD1 plus the fading LOD2). Sweeping in and out give the same counts at the same distances, and the count
  never drops below 4, so there's no hole.
- **Pops.** The mean luminance change between steps is flat: 0.0015–0.0017, with no step at 118 or 122 m. The
  largest values in the run (0.0021–0.0024) are at 129–130 m and come from the camera's own motion.

## 3. A moving camera (5 m/s, 60 fps, 1920×1080)

The camera moves 0.0833 m per frame with one frame per position, over 108–132 m in both directions: 288 frames each.
Every metre is saved, and `env09/band_strip_in_out.png` crops 116–124 m (top row moving in, bottom row moving out).
- **No visible pop.** The mean per-frame change is 0.0009. The band's edges are no larger than the frames around
  them; the largest value is the first frame after the camera is placed.
- **No translucent trunk.** The trunk stays opaque through the band (LOD1 is drawn under the fade), and the crown
  changes smoothly.
- **Draw counts.**
  - Moving out: 4 → 6 at 118.33 m, and 6 → 4 at 122.33 m.
  - Moving in: 4 → 6 at 122.17 m, and 6 → 4 at 118.25 m.
- **One transient.** Moving in, the single frame where LOD1 enters (122.25 m) counts 8 objects. Hiding each LOD in
  turn (`--hide-lod`) shows that LOD1's two meshes are counted twice on that frame. Hiding LOD0 changes nothing, so
  LOD0 doesn't appear.
  - That frame shows no luminance change (0.00085 against 0.00075–0.00090 around it).
  - So it's a one-frame overlap while Godot hands LOD1 in during the parent's fade, not a visible double image.
  - The same transient shows on the first frame after a camera teleport. **It isn't a defect**, and nothing needs to
    be done.

## 4. The crossfade band's cost

`--bench`: 40 copies of PalmA on an arc filling the view, all at the bench distance (`env09/bench_40_palms_120_vs_116.png`
shows 120 m on top and 116 m below). GPU median over 300 frames, 2560×1440, two runs each (they agree within
0.01 ms).

| Preset | 116 m (LOD1) | 119 m (band) | 120 m (band) | 121 m (30 of 40 in band) | 124 m (LOD2) | Band cost, 40 palms (119 m vs 116 m) |
|---|---:|---:|---:|---:|---:|---:|
| Low | 0.769 ms | 0.840 ms | 0.837 ms | 0.806 ms | 0.719 ms | **+0.071 ms** (1.8 µs per palm) |
| High | 1.315 ms | 1.402 ms | 1.394 ms | 1.354 ms | 1.255 ms | **+0.087 ms** (2.2 µs per palm) |
| Ultra | 1.604 ms | 1.711 ms | 1.687 ms | 1.620 ms | 1.482 ms | **+0.107 ms** (2.7 µs per palm) |

- **What the cost is.** It's the faded LOD2 drawn as a transparent pass over LOD1, which is twice as many objects
  (82 → 162).
- **In context.** A palm spends 4 m of its distance in the band, so even a dense grove has only a few palms there at
  once. Forty in the band together, which no shot does, costs 0.09 ms at High.

## Checks

- **Run:**
  - gdlint and gdformat on `lod_pop.gd`.
  - validate_data and `taskboard --check`.
  - Godot tests filtered to `vegetation` (the tool isn't loaded by any test).
- **Skipped:** lavapipe shots, the tools unittests and the full suite. No shipped file changed; only the
  `tools/gpu_bench` probe and docs.
- **Not covered:** the task's AUTO shelter check against the first-playable Haluna collision. That criterion is
  Environment's (it waits on that branch) and isn't part of this GPU check.
