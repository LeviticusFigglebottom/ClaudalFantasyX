---
id: M2-CHR-11
title: Host-independent builds for base_body, Rhen, Toma and the villagers (M1-CHR-14's snaps)
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: lead
depends_on: [M1-CHR-14]
milestone: M2
request-from: lead
priority: top
---
## Goal
The PC's Blender gate showed 10 diffs on its AVX2 host for base_body, rhen, toma and the villager jobs. Asha is already host-independent (M1-CHR-14). Opt every other character job into the same snaps and rebuild once:
- MIDLINE_SNAP on head coordinates;
- snap_shape_noise (shape deltas on a 1 µm grid);
- quantize_uvs (UVs on a 2^-16 grid);
- asha_textures.PRE_ROUND in the texture runs.

## Acceptance criteria
- [ ] rhen and toma opted in (carried by M1-CHR-15, which rebuilds them anyway).
- [x] base_body and the seven M2 villagers opted in. Tavi and Kell already are, through their params.
- [ ] `verify_blender_builds.py` identical for every character job, both natively and with NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4" (the AVX2-only numpy paths).
- [ ] Changed shots viewed. The changes should be invisible, at RMSE ~1e-4.

## Notes
**2026-10-24, base_body and the villagers (character-18; rhen and toma are still pending in M1-CHR-15).**
- **Reproduced first.** This host has AVX-512. With the sources at b932d0fe, every in-scope job verified identical natively
  but differed under `NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"`. base_body differed in POSITION on all three bodies.
  The villagers differed in Head.POSITION and HairHead.POSITION/NORMAL, fisher's LOD1 also in HairHead TEXCOORD_0 and
  indices, reed also in Body.POSITION, plus `*_head_normal.png`, neme's head albedo and skinmask, and reed's body
  normal. This matches the PC gate. **Tavi and Kell, already on `host_snaps`, differed too** (Head.POSITION:
  one midline coordinate at 1.5e-9 or 3.4e-9, above build_asha's 1e-9 snap; HairHead moved by up to 80 um), so the
  four Asha snaps were not enough.
- **Cause.** The donor fit's last bits differ between numpy's SIMD paths. In base_body, about 19k coordinates differ by
  ~1e-15 m, and one near-midline coordinate (2.8e-9) flips in float32. In the villagers the same noise reaches the
  hair through the BVH scalp (`head_surface`) and moves whole cards. A hair drape grid was not needed: identical scalp
  input gives identical cards.
- **Fix.** `host_snaps` (build_villager) now also rounds the donor skin `V` to `POS_GRID = 1e-6` m right after
  `bb_donor.generate` (head, body, scalp, coverage and normals all follow), and the hair cards to the same grid before
  the HairHead object is built, so LOD1's decimate sees the same input. This is build_sefir's 1 um grid. The seven M2 params
  set `_build.host_snaps: true`. test_villagers now requires `host_snaps` on all nine villagers; `garment_fit` stays
  off the M2 seven. base_body/build.py rounds positions to 1 um and the donor UVs to 2^-16. It has no shape keys or
  textures, so there is no shape snap or PRE_ROUND. Tavi and Kell were rebuilt with the stronger snaps.
- **Verify** (`HYMN_BLENDER_BASE=b932d0fe`, the 8 in-scope jobs plus villager_tavi and villager_kell): **all 10 identical**
  natively, with `X86_V3 X86_V4` disabled (numpy's X86_V2 baseline) and with only `X86_V4` disabled (the AVX2 path an
  i9-12900K takes). HairHead and the LOD1 indices match on all three paths.
- **Shots** (39: `base_body_*` and every `villager_*`): all pass against the baselines. base_body is at 6e-5..1.2e-3.
  Tavi and Kell are at 1.9e-4..3.2e-3. The M2 seven are at 3.9e-4..6.3e-3, but that is mostly old drift:
  the pre-change neme and vendor assets render at 0.00628 and 0.00602 against the same baselines. The change on its own,
  new render against old render, is 4.1e-4 (neme_front) and 3.2e-4 (vendor_front). The viewed diffs show only the
  costume and hairline outlines (sub-pixel hair moves). Head UVs are repacked by quantize_uvs and the textures are
  re-baked to match, with no seams. Baselines were not updated.
- **Gates:** validate_data, taskboard --check, `unittest test_villagers test_blender_builds test_base_body` (59 OK),
  test_rig_integrity (71 OK, 14 skipped), Godot `--filter=post_import` (19 run, 0 failed).

## Review log
