# M1-RND-24 criterion 2: the unshadowed cavity-bounce pass on the GPU (2026-10-24)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/m1-rnd-24-gpu-check`, cut from the integration branch at a514c06
(RND-24 merged). Tool: `tools/gpu_bench/mouth_bounce_probe.tscn` (new).

## Rig

`asha_face_grief` (camera `Cameras/Face`, 960×540 for the metrics), with the preset applied as capture_preset does.
The stage's directional `KeyLight` is either kept (`dir`) or replaced by a **positional key along the same
direction**, 2 m from the mouth:
- a `spot` (20°, range 6 m) or an `omni` (range 6 m);
- the key's colour and shadow blur, and its energy scaled so the mouth gets the directional key's irradiance
  (`energy × d^attenuation / range window`).

Each key is captured with its shadow on, and with it off (the control). There are four variants:
- `pass`: as shipped. CharacterShaderTiers attaches the bounce pass.
- `fallback`: the pass is removed and `cavity_bounce_pass` is cleared. This is the pre-RND-24 bounce, which
  includes the shadow.
- `nobounce`: `cavity_bounce` is 0. This is the pre-RND-21 interior.
- `mask`: the mouth family is painted unshaded green.

**Each frame comes from its own process.** A fresh run repeats exactly (RMSE 0.0). Frames captured later in the same
process drift by about 0.004, so they can't be compared with each other.

**Which pixels count.** "Interior" uses RND-21's definition: pixels of the mouth crop that are darker than 0.02
linear luminance without the bounce (681 px at High, 624 at Low). RND-21 had 566 and 542, because the head has
changed since. "Mask" is the mouth family's own pixels (about 770). The figures are linear luminance.

## Result: grief interior

| Preset | Key | Key shadow | No bounce | Fallback (pre-RND-24) | **Pass** | Share < 0.01: fallback → pass |
|---|---|---|---:|---:|---:|---|
| High | spot | on | 0.0127 | 0.0145 | **0.0194** | 0.16 → **0.10** |
| High | spot | off (control) | 0.0140 | 0.0194 | 0.0205 | 0.09 → 0.09 |
| High | omni | on | 0.0140 | 0.0194 | 0.0208 | 0.09 → 0.09 |
| High | dir | on (shipped stage) | 0.0106 | 0.0165 | 0.0161 | 0.24 → 0.23 |
| Low | spot | on | 0.0127 | 0.0144 | **0.0185** | 0.19 → **0.07** |
| Low | spot | off (control) | 0.0133 | 0.0196 | 0.0197 | 0.05 → 0.05 |
| Low | omni | on | 0.0134 | 0.0197 | 0.0197 | 0.05 → 0.05 |
| Low | dir | on (shipped stage) | 0.0111 | 0.0169 | 0.0169 | 0.17 → 0.17 |

The luminance columns are medians over the interior pixels. Over the mouth family's own pixels (the mask) the
medians are: shadowed spot at High, fallback 0.0230 → pass 0.0291; at Low, 0.0219 → 0.0282. Means and the full
table come from the scratch `metrics.py`, whose output is reproduced in the task notes.

**What it shows:**
- **A shadowed spot key.** The pass gives back the bounce the shadow took. At High the interior median rises
  0.0145 → 0.0194 (+34 %), and the share below 0.01 falls 0.16 → 0.10. At Low it's 0.0144 → 0.0185, and
  0.19 → 0.07.
- **The pass is about as good as removing the shadow.** With the key shadow off, the median is 0.0194–0.0205 at
  High and 0.0196–0.0197 at Low, whichever variant runs.
- **A shadowed omni key.** Here the pass changes nothing, because the omni's cube shadow (soft, biased, 2 m away)
  doesn't put the interior in the lips' shadow. A tighter omni would behave like the spot.
- **Directional keys (every shipped Asha shot).**
  - At Low, the pass and the fallback are pixel-identical (RMSE 0.0), as designed.
  - At High they differ a little; see the FSR2 finding below.
- **Against RND-21's numbers** (directional stage, High, median 0.0121 → 0.0174): the same rig measures
  0.0106 → 0.0161–0.0165 over today's pixel set. The bounce is intact, and RND-24 didn't regress it.

## Closed mouths are unchanged

RMSE between pass and fallback, linear:

| Shot | High, dir | High, spot | Low, dir | Low, spot |
|---|---:|---:|---:|---:|
| `asha_face_smile` | 0.00008 | 0.00010 | 0.0 | 0.00002 |
| `asha_face_neutral` | 0.00004 | 0.00007 | 0.0 | 0.00001 |

## QA-08 fault A doesn't change

See `rnd24/crop_grief_keys_variants.png` (High, 3×). The top row is the dir key, the bottom row the spot key. The
columns are no bounce, fallback, pass, and pass with the key shadow off.
- The hard dark band on the inner lip is the same in the fallback and pass columns.
- It goes away only when the key's shadow is off (the control).
- This confirms the RND-24 diagnosis: the band is the lips' shadow on `skin_head`, which no bounce reaches. It's
  M1-RND-25's to fix.

## Cost (2560×1440, grief close-up, the face fills the frame; GPU median and p99 over 400 frames, 2 runs each)

| Preset | Key | Fallback | Pass | Δ median |
|---|---|---|---|---:|
| High | spot (shadowed) | 1.468 / 1.468 ms | 1.465 / 1.469 ms | ≤ ±0.003 ms |
| High | omni (shadowed) | 1.493 / 1.499 ms | 1.494 / 1.499 ms | ≤ +0.001 ms |
| High | dir | 1.450 / 1.458 ms | 1.453 / 1.457 ms | ≤ ±0.003 ms |
| Low | spot (shadowed) | 0.801 / 0.802 ms | 0.805 / 0.804 ms | ≤ +0.004 ms |
| Low | omni (shadowed) | 0.804 / 0.807 ms | 0.805 / 0.807 ms | ≤ +0.001 ms |
| Low | dir | 0.789 / 0.791 ms | 0.785 / 0.791 ms | ≤ ±0.004 ms |

**The pass costs nothing measurable** (under 0.005 ms, inside run-to-run noise), even in the worst framing.
Single-frame p99 spikes (up to 1.7 ms) appear in both variants and don't repeat across runs.

## Finding: under FSR2 (the High preset), the pass softens the mouth's edges even when it adds nothing

- **The symptom.** With only directional lights, the pass's `light()` adds nothing. At Low the frames are
  identical, but at High they aren't:
  - full-frame RMSE is 0.0005 (key shadow on) and 0.0012 (off);
  - the changed pixels lie on the mouth family only, up to 80/255 on the teeth edges;
  - the mean luminance over the changed pixels rises 0.004.
- **The cause is the FSR2 upscaler.** Per-option overrides on High: with `scaling_mode=bilinear` the pass and the
  fallback are identical (RMSE 0.0); turning off `gi_mode`, `ssil_quality` or `aa` changes nothing. FSR2 treats the
  pixels under a transparent (`blend_add`) draw differently from opaque ones, even when the draw adds zero. So the
  teeth and interior edges resolve slightly softer (`rnd24/crop_fsr2_pass_drift.png`: fallback, pass and the
  difference ×8, then the shadowed spot's fallback and pass).
- **The impact.** It's small and needs a 4× crop to see. It affects every mouth-family surface at High, the default
  preset, under any lighting: a GPU capture of `asha_face_grief` at High is no longer identical to pre-RND-24.
  - Lavapipe baselines use the capture rig's scene defaults, not FSR2, so no lavapipe shot drifts from this.
  - Ultra uses bilinear scaling and Medium uses FSR 1, so neither is affected.
- **Filed** M1-RND-26 (rendering, reviewer character). It asks for the pass to be attached or drawn only when a
  positional light can reach the mouth, or for the side effect to be accepted and documented.

## Checks

- **Run:**
  - gdlint and gdformat on the probe.
  - Godot tests filtered to `character_shading`.
  - validate_data and `taskboard --check`.
  - The probe at High and Low.
- **Skipped:** the tools unittests (nothing under `tools/` except the new probe, which they don't cover) and lavapipe
  shots (no shipped file changed).
