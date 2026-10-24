# M1-RND-21 mouth-interior fill (2026-10-23)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/rnd-21-mouth-fill`, cut from `claude/new-session-mj8c3c`.
The problem is QA-05c fault 2: in grief, the mouth interior goes near-black.

## Change

- **New shader family** `mouth` (`game/shaders/character/character_mouth{,_medium,_low}.gdshader`, body
  `character_mouth_body.gdshaderinc`). It's in character_shader_tiers.json and prewarm_materials.json (scoped to the
  Asha stage).
- **Cavity bounce:** each light adds an unshadowed bounce:
  `col_cavity_bounce × cavity_bounce × mix(1, ao, cavity_occlusion) × (0.5 + 0.5·L·V) × LIGHT_COLOR / π`.
  For positional lights it's also multiplied by `ATTENUATION`.
  - Defaults: #C79A8C, 0.4 and 0.5.
  - The bounce is on every tier. Low drops only the specular lobe.
- **Asha:** `write_materials.py` moves teeth, tongue and mouth from StandardMaterial3D to the family, with the same
  values (`roughness_from_orm` 0 keeps the mouth bag's flat roughness). Outputs regenerated and normalised to LF.
- **Tests:** the family's contract and compile on every tier; Asha's three materials use it; the bounce is in
  `light()` outside any tier gate, with a default above 0.
- **Tool:** `capture_preset --mat-set` now takes `#rrggbb` colours. Before, `str_to_var` returned null and silently
  reset the uniform.

## Tuning (GPU, asha_face_grief, High, `--mat-set`)

| Variant | Read |
|---|---|
| bounce 0 (= the old StandardMaterial3D, RMSE 0.0000) | interior near-black, teeth dark slabs |
| 0.3, lip red #CC7566, AO fully | interior dark red; teeth orange; the top band under the upper lip stays black (AO 0 there) |
| 0.6, lip red | teeth brown-orange, too warm |
| 0.4, #C79A8C, `cavity_occlusion` 0.5 (**chosen**) | interior a dark, readable red-brown; the top band opens up |
| 0.4–0.6, neutral #B0A8A8 | the teeth still khaki, so the tint is the teeth albedo (fault 3, M1-CHR-11), not the bounce |

## Result

Interior pixels are those of the mouth crop darker than 0.02 linear luminance before the change.

| Preset | Pixels | Median luminance, before → after | p90 after | Share < 0.01, before → after |
|---|---:|---|---:|---|
| High | 566 | 0.0121 → 0.0174 | 0.0384 | 0.30 → 0.16 |
| Low | 542 | 0.0121 → 0.0180 | 0.0403 | 0.29 → 0.14 |

Drift (GPU, High, base → branch): asha_face_grief 0.0023; asha_face_smile, asha_face_neutral and asha_q34 0.0000
(closed mouths). The lavapipe `asha_face_grief` baseline needs re-approval. The other asha_* shots should pass, but
their scenes load the changed materials, so they were captured anyway.

## Not addressed

- **Teeth colour:** khaki-brown under any bounce. This is the asset's albedo, QA-05c fault 3, which M1-CHR-11 owns.
- **The first idea, a stage fill light** (the old local stash): rejected. It lights the whole face, and a stage
  light doesn't reach the zones.

## Checks

- **Run:**
  - gdlint and gdformat on the touched files.
  - Godot tests filtered to `character_shading` (15/0) and `shader_prewarm` (9/0).
  - `tools/tests` (433; one failure, the known Windows-only `test_python_runs_use_this_interpreter`).
  - validate_data.
  - The 4 asha shots on the GPU at High, plus grief at Low.
- **Skipped:** the full suite and the other shots. No other scene uses these materials or the new shaders.
  `HYMN_SKIP_BLENDER`: `write_materials.py` is plain Python, with no Blender job.
