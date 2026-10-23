# M1-CHR-04 rendering + material half: GPU measurements (2026-10-23)

Machine: RX 9070 XT, Godot 4.6.3-stable Forward+/Vulkan. Tool: `tools/gpu_bench/capture_preset.tscn` (preset High,
scale 1, plus 2× for look-dev), before = branch base, after = this branch. Branch `gpu/chr-04-materials`.

## (a) Shadow terminator on the face

Cause (M1-QA-05): Godot's directional `shadow_normal_bias` scales with the shadow texel, and at dialogue range the
coarse cheek/jaw triangles disagree with the smooth normals, so the terminator steps into bands and acne islands.

| Key/rim `shadow_normal_bias` | Face shots at 2× High |
|---:|---|
| 1.0 (old) | diagonal banding on the shadow-side cheek, blotches under the cheekbone |
| 2.0 | mostly clean, a faint residual band |
| **2.5 (chosen)** | clean; the nose's real cast shadow stays |
| 3.0 | clean |

No peter-panning at 2.5: the feet and staff contact shadows hold in `asha_q34`. Applied to KeyLight and RimLight in
`game/levels/_tests/characters/asha/asha_stage.tscn`. No skin-shader terminator offset was needed.

## (b) Vest lacquer

`cloth.tres` ran on the shader defaults (base 0.35, coat 0.06, strength 1.0) over a 100 % lacquer mask, which reads as
patent plastic. The uniforms already existed (see the correction in the QA-05 report). Candidates on `asha_q34`, 2× High:

| Variant | base / coat / strength | Read |
|---|---|---|
| A (old) | 0.35 / 0.06 / 1.0 | hard mirror highlight, patent plastic |
| B | 0.45 / 0.16 / 0.6 | lacquer sheen, softer |
| C | 0.50 / 0.24 / 0.45 | broad, soft |
| D | 0.60 / 0.30 / 0.30 | satin |
| E | 0.65 / – / 0.0 | matte leather; loses the "lacquer" in asha.md |
| **Chosen** | **0.55 / 0.16 / 0.55** | dark sky mirror kept as a broad sheen; no plastic hotspot |

## Drift against the capture (High, before → after, linear RMSE)

| Shot | RMSE | max abs (8-bit) | pixels > 8 levels |
|---|---:|---:|---:|
| asha_extreme_pose | 0.00614 | 130 | 1.9% |
| asha_face_grief | 0.01168 | 109 | 6.4% |
| asha_face_neutral | 0.01169 | 106 | 6.3% |
| asha_face_smile | 0.01178 | 114 | 6.5% |
| asha_face_stylized_compare | 0.02101 | 150 | 14.9% |
| asha_front | 0.00607 | 99 | 1.6% |
| asha_profile | 0.00442 | 122 | 0.7% |
| asha_q34 | 0.00525 | 98 | 1.2% |
| asha_sleeve_s0 | 0.00847 | 176 | 3.1% |
| asha_sleeve_s4 | 0.00849 | 165 | 3.0% |

**Lavapipe baselines that will drift (not overwritten):** all ten `asha_*` shots above; the four face shots and both
sleeve shots exceed the 0.008 threshold for certain, and the others carry the vest change. Re-approve them with the
CHR-04 mesh half (lips, hair, face density) so they move once.

Tests: `test_asha_stage_lights_clear_the_shadow_terminator`, `test_asha_vest_lacquer_is_leather_not_plastic`
(tests/unit/test_character_shading.gd).

## Follow-up after the mesh half merged (2026-10-23)

- The vest values are now in `assets_src/characters/asha/write_materials.py` (the `cloth` row), because the generator
  rewrites `cloth.tres`. A regenerated file is byte-identical to the committed one.
  - On Windows the script writes CRLF, which I normalised to LF. Nothing else differs.
- **Shadow terminator on the new head:** clean at 2× High, `asha_face_neutral`.
- **Hair under the warm key light** (2× High, `asha_face_neutral`), judged on the GPU: it reads **warm brown, not
  black**.

  | Region | Median sRGB | Hue | Saturation | Value |
  |---|---|---:|---:|---:|
  | Scalp | (70, 33, 11) | 22° | 0.84 | 0.27 |
  | Braid | (83, 58, 42) | 23° | 0.49 | 0.33 |

  The scalp catches a golden sheen along the part. The braid's crossings stay a dark warm brown.
- **Checks skipped** (gate scope): the Blender rebuild (no Blender source touched) and the screenshot manifest (the Lead
  re-approves the `asha_*` set). I ran the Godot tests filtered to `character_shading`.

