# M1-RND-20: the smiling mouth corner's shadow terminator, on the GPU (2026-10-23)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/rnd-20-smile-terminator`, at the integration branch with Asha rounds
3–5. Captures are `capture_preset --scale=2 --preset=high` (1920×1080).

**Diagnosis (confirms M1-CHR-10).** With the key light's shadow off, the diagonal striations at the smiling corner
vanish (QA-05c `crop_diag.png`). They are the terminator on the folded corner's facets, the same family as the
CHR-04 cheek.

## Candidates tried

| Candidate | Smile corner | Side effects |
|---|---|---|
| Normal bias 2.5 (as merged, CHR-04) | striations | – |
| Skin-shader terminator band 0.2 (fade the shadow over geometric N·L 0–0.2) + bias 3.5 | clean | **Breaks the nose's cast shadow.** The skin under the nose faces partly away from the light, so its legitimate cast shadow fades and smears orange through `shadow_scatter`. Rejected. |
| Band 0.35 | clean | The same, plus light leaks into the lip seam (an orange line). Rejected. |
| Band 0.08 or 0.1 + bias 3.5 or 4.5 | clean | The nose shadow still breaks. Rejected. |
| Bias 3.5 | stripes under the lower lip | – |
| **Bias 4.5 (key and rim)** | **clean**, with a faint trace of the fold line at 2× | The nose shadow is intact. Feet and staff contact hold in `asha_q34` (no peter-panning). |

**Change.**
- `game/levels/_tests/characters/asha/asha_stage.tscn`: KeyLight and RimLight `shadow_normal_bias` 2.5 → **4.5**.
- `test_asha_stage_lights_clear_the_shadow_terminator` now requires ≥ 4.5.
- No shader or material change. The terminator-band experiment was reverted, so Asha's materials and
  `write_materials.py` are untouched.

**For dialogue rigs (Cinematics).** Faces keyed at the Asha stage's angle want a key-light normal bias of about
4.5. Godot's normal bias scales with the shadow texel size, so a rig with a tighter shadow distance may use less.

**For Character (optional).** If the faint fold line shows in a dialogue close-up, give the corner more
subdivision; LOD0 has 1,210 triangles of headroom. That would also let rigs use less bias.

## Drift (GPU, 2× High, before → after; lavapipe baselines not overwritten)

| Shot | RMSE |
|---|---:|
| asha_face_smile / neutral / grief | 0.0060 / 0.0056 / 0.0059 |
| asha_face_stylized_compare | 0.0119 |
| asha_front / q34 / profile | 0.0064 / 0.0064 / 0.0052 |
| asha_sleeve_s0 / s4 | 0.0085 / 0.0085 |
| asha_extreme_pose | 0.0075 |

Every `asha_*` shot moves, by the bias on the stage's key and rim lights. Re-approve them together.

## Not done here

The grief mouth interior going near-black (QA-05c fault 2) is a separate cavity-fill question; the bias doesn't
change it. It's left for a follow-up, with the teeth material, which is Character's.

## Checks

- **Run:** gdlint and gdformat; the Godot tests filtered to `character_shading` (14/0); validate_data; taskboard.
- **Skipped:** the full suite and the other shots (only the Asha stage changed).
