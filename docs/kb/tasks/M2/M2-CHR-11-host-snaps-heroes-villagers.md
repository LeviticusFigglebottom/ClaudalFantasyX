---
id: M2-CHR-11
title: "Heroes and villagers opt into M1-CHR-14's host snaps (their Blender builds differ on an AVX2 host)"
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: qa
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
- [ ] base_body, Rhen, Toma and the villagers use Asha's host snaps where they share her code paths: `asha_textures.PRE_ROUND`
      (round the float image before 8-bit), the head's midline snap, the UV grid and `snap_shape_noise`.
- [ ] Their committed outputs are rebuilt once with the snaps, then verified identical on **both** the Lead's
      container (AVX-512) and the PC (`HYMN_BLENDER_ALL=1`, tools/dev/gate_runner.md).
- [ ] blender_builds.md says new character builds opt in from the start.

## Notes
- 2026-10-24 (characters): claimed. rhen and toma are folded into M1-CHR-15, which rebuilds them anyway. base_body and the seven M2 villagers are with a worktree subagent. Both were sent this evidence: hair positions and the LOD1 decimate inputs need a position grid too, beyond Asha's four snaps. Verify is native vs `NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"` (the AVX2-only numpy paths). (A duplicate M2-CHR-11 file filed on claude/characters was removed in favour of this one.)
The PC can run the cross-host check on request: push the branch, and the Lead or the PC runs
`verify_blender_builds.py --all` on it in WSL.

## Review log
