---
id: M2-CHR-11
title: "Heroes and villagers opt into M1-CHR-14's host snaps (their Blender builds differ on an AVX2 host)"
role: character
status: done
owner_session: "characters (new account, branch claude/characters)"
reviewer: pc-gpu
depends_on: [M1-CHR-14]
milestone: M2
request-from: "rendering (PC GPU gate runner)"
---
## Goal
Every Blender job reproduces byte-identically on any host. M1-CHR-14 made Asha's build host-independent, but
heroes and villagers sharing that code haven't opted in yet. On the PC's gate runner (i9-12900K: AVX2, no
AVX-512) they rebuild differently from their committed assets, which were built on the Lead's AVX-512 container.

## Evidence (PC gate runner, 2026-10-24)
- `--all` on the integration head **d6a0886d**: 41 jobs, **10 DIFF**, 31 identical (742 s). On lead/gate-big7
  @ ab048d51, the 39 changed jobs gave nine of them.
- **`base_body`** (all three bodies): `base_body_{athletic,heavy,slender}.glb`, `POSITION` only. Every hero and
  villager below builds on it.
- **DIFF:** `rhen`, `toma`, `villager_neme`, `villager_osu`, `villager_child`, `villager_vendor`, `villager_reed`,
  `villager_netmender`, `villager_fisher`. That's 30 outputs: each one's `.glb` and `_lod1.glb`, and its
  `*_head_normal.png` (plus neme's head albedo and skinmask, and reed's body normal).
- **What differs in the glTFs:** `Head.POSITION`, `HairHead.POSITION` and `HairHead.NORMAL`, and on fisher's LOD1
  also `HairHead.TEXCOORD_0` and `HairHead.indices` (a decimate decision flipped).
- **Identical:** Asha (44 outputs), haluna_kit, vegetation and all 21 creatures.
- Same pinned Blender 5.0.1+dfsg-5 and numpy 2.5.3 as the container (`tools/dev/fetch_blender.py`, WSL2 Ubuntu 24.04).

## Acceptance criteria
- [x] base_body, Rhen, Toma and the villagers use Asha's host snaps where they share her code paths: `asha_textures.PRE_ROUND`
      (round the float image before 8-bit), the head's midline snap, the UV grid and `snap_shape_noise`.
- [ ] Their committed outputs are rebuilt once with the snaps, then verified identical on **both** the Lead's
      container (AVX-512) and the PC (`HYMN_BLENDER_ALL=1`, tools/dev/gate_runner.md).
- [x] blender_builds.md says new character builds opt in from the start.

## Notes
- 2026-10-24 (characters): claimed. rhen and toma are folded into M1-CHR-15, which rebuilds them anyway. base_body and the seven M2 villagers are with a worktree subagent. Both were sent this evidence: hair positions and the LOD1 decimate inputs need a position grid too, beyond Asha's four snaps. Verify is native vs `NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"` (the AVX2-only numpy paths). (A duplicate M2-CHR-11 file filed on claude/characters was removed in favour of this one.)
The PC can run the cross-host check on request: push the branch, and the Lead or the PC runs
`verify_blender_builds.py --all` on it in WSL.

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

- **2026-10-27, proven on the cloud's three numpy paths (characters, new account).** Every character-owned job is
  byte-identical to its committed outputs natively (AVX-512), with `NPY_DISABLE_CPU_FEATURES="X86_V4"` (the PC's
  AVX2 path) and with `"X86_V3 X86_V4"` (baseline): asha 44, rhen 31, toma 38 (M1-CHR-15's rebuild with the snaps;
  rhen again after M2-CHR-513's hook bones), the nine villager jobs, base_body, props_wick, sefir 32, ysolde 37 and
  the 27 creature jobs: 43 jobs.
  - **Found on the way:** the villager jobs failed to *build* in verify's sandbox once M1-CHR-15 landed (they import
    hero_clips, which reads game/data/characters/helper_bones.json, and the sandbox held only assets_src). Fixed:
    `copy_into_sandbox` gains `game/data/characters`, and the villager jobs list the file as a source. The PC gate
    would have hit the same failure.
  - **Left for the PC:** the second criterion's hardware half. Run `verify_blender_builds.py --all` (or
    `HYMN_BLENDER_ALL=1`) in WSL at this branch's head.
  - blender_builds.md has the opt-in rule for new character builds.

## Review log
- 2026-10-27 (pc-gpu, via the Lead): VERIFIED on the PC's AVX2 i9-12900K. claude/characters @ 3723f3eb: base_body, rhen, toma and the 9 villagers rebuild identical to the committed assets (12/12). Done; merges with big12.
