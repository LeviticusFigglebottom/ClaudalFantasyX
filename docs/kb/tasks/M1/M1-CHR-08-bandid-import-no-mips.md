---
id: M1-CHR-08
title: Import the cloth band-id map without mipmaps
role: character
status: done
owner_session: "worktree-agent-af72bd4d8af383b91"
reviewer: rendering
depends_on: [M1-RND-09]
milestone: M1
request-from: "rendering"
---
## Goal
`assets/characters/shader_test/sleeve_bandid.png.import` has `mipmaps/generate=true`. Since M1-RND-09 the cloth shader samples `tex_band_id` with `filter_nearest` (no mipmap filtering), so the mips are never read: there is no bleed any more, only wasted VRAM. The contract now exempts id maps from the "mipmaps on" rule (docs/kb/tech/character_shading.md, "Every map" and the `asha_sleeve_bandid` row).

## Acceptance criteria
- [x] `sleeve_bandid.png.import`: `mipmaps/generate=false` (and the same for the production `asha_sleeve_bandid` when it lands)
- [x] The texture build script writes id maps with each band region at least 2 texels wide (contract row)

## Notes
Owner of `assets/characters/**` is Character, so Rendering did not edit the import. Expect `char_cloth_gold` to stay within its threshold (the shader already ignores the mips).

## Work notes (2026-10-23, worktree-agent-af72bd4d8af383b91)
- Both band-id imports now have `mipmaps/generate=false`: the shader-test `sleeve_bandid.png.import` and the production `asha_sleeve_bandid.png.import` (it had landed with CHR-02). Nothing else in either import changed: still lossless (`compress/mode=0`).
- Both texture builders (`build_shader_test_textures.py`, `asha_textures.py`) call `check_id_map` before writing an id map, and the build stops if any label's region is under `ID_MAP_MIN_RUN` = 2 texels along a row or a column. The committed maps measure 50/16 (shader test) and 99/16 (Asha) texels at their narrowest, so the outputs are unchanged.
- Tests:
  - `tools/tests/test_character_id_maps.py` (new, 6 tests): id maps import with mips off and lossless, every other character map keeps mips on, values are whole labels 0..7, every region is at least 2 texels wide, and `check_id_map` rejects a 1-texel region.
  - `test_asha.py`: the "mipmapped imports" check now exempts `*_bandid`.
  - `tests/unit/test_character_shading.gd::test_band_id_maps_import_without_mipmaps`: the engine loads both maps with no mip levels.
- Reproducibility:
  - `verify_blender_builds.py --job asha` (HYMN_BLENDER_BASE=a504072) gave 44 identical.
  - A scratch rebuild of the shader-test textures is byte-identical for all 17 PNGs.
- Shots, on lavapipe against the current baselines; none re-approved:

  | Shot | RMSE |
  |---|---|
  | `char_cloth_gold` | 0.00080 |
  | `char_low_compare` | 0.00001 |
  | `asha_sleeve_s0` | 0.00010 |
  | `asha_sleeve_s4` | 0.00010 |
  | `asha_front` | 0.00052 |
  | `asha_q34` | 0.00033 |
  | `asha_profile` | 0.00057 |

## Review log
- 2026-10-24 review-sweep-P (rendering): **approve.** Both criteria hold in the files, not only in the notes. `asha_sleeve_bandid.png.import` and `shader_test/sleeve_bandid.png.import` have `mipmaps/generate=false` and are still lossless (`compress/mode=0`), and no other character map lost its mips. Both builders call `check_id_map` on the id map before writing it (asha_textures.py:1478, build_shader_test_textures.py:563). The 2-texel minimum is pinned by `test_character_id_maps.py` (6 OK, re-run here) and by the engine-side `test_band_id_maps_import_without_mipmaps` (the character_shading filter is 16/0 here). The shot RMSEs are all at noise level, so no baseline needed re-approval. Nit, no task: `id_map_min_run` and `check_id_map` are copied in two builders. If a third character needs an id map, move them into a shared helper under `assets_src/characters/`.
