---
id: M1-RND-14
title: Shader-test mesh build fails on Blender 5.0.1
role: rendering
status: review
owner_session: "worktree-agent-a361fe4924e35dfcf"
depends_on: [M1-QA-02]
milestone: M1
request-from: "qa"
---
## Goal
The Blender rebuild gate (M1-QA-02, `docs/kb/qa/blender_builds.md`) can't rebuild `assets/characters/shader_test/shader_test_{bust,cloth}.glb`. `assets_src/characters/shader_test/build_shader_test_meshes.py` stops in `new_object` (line 50) on the pinned Blender 5.0.1:

```
bm.faces.sort(key=lambda f: tuple(sorted(v.index for v in f.verts)))
ValueError: the value returned by the 'key' function is not a number
```

BMesh's `sort(key=...)` needs a number, not a tuple. One deterministic fix is to rank the faces first: compute the sorted tuple keys, then sort by the rank of each face's key.

## Acceptance criteria
- [x] The script runs on Blender 5.0.1, and two runs are byte-identical.
- [x] The rebuilt `.glb` files match the committed ones, or are recommitted with the shader-test shots re-approved after a look (`char_*` shots).
- [x] `python3 tools/dev/verify_blender_builds.py --job shader_test` passes, then remove the job's `expected_failure` from `tools/dev/blender_builds.json`.

## Notes
- 2026-10-23 (worktree-agent-a361fe4924e35dfcf):
  - **Fix** (`new_object`): compute each face's sorted vertex-index tuple, rank the faces by that tuple, and `bm.faces.sort(key=rank)`. It gives the same order the tuple key meant, as an int.
  - **The committed files came from an unsorted build.** Their triangle order is not sorted by the key. A build with the sort line removed matches `shader_test_cloth.glb` byte for byte, but it differs from the committed `shader_test_bust.glb` in Head/Eye/Cornea/Collar indices. That is the pointer-hash order the script's comment warns about, so it can't be reproduced. The sort stays, and both files are **recommitted**.
  - **What changed** (old vs rebuild, all 13 meshes): POSITION, UV and COLOR are equal, with the same vertex count and order. The triangle *sets* are equal and only their order differs. NORMAL differs by ≤ 4e-4 (accumulation order). The bust also shares two index accessors between L/R eyes (43 accessors instead of 45; −54 KB), because the exporter dedups identical index buffers once both sides sort the same way.
  - Determinism: 4 rebuilds, 3 of them concurrent, gave identical `shader_test_bust` `1e42da…` and `shader_test_cloth` `f6c185…`. The marker is removed, and the job reports `2 identical`.
  - Shots: `char_skin_eye_closeup` 0.00004, `char_hair_backlit` 0.00001, `char_cloth_gold` 0.00080, `char_low_compare` 0.00001 (limit 0.008): **pass, no re-approval**.
  - Review: character (SPEC §12.3, Rendering ↔ Character).

## Review log
- 2026-10-23 character (review-sweep-L, fresh reviewer): **approve.** No blockers.
  - **Checks:** `python3 tools/dev/verify_blender_builds.py --job shader_test`: **`2 identical`**, rc 0, on Blender 5.0.1. The rank-based `bm.faces.sort(key=rank)` gives the order the tuple key intended, as an int. The recommit is justified: the old bust came from an unsorted, pointer-order build that can't be reproduced. The four `char_*` shots were within their limits at ≤ 0.0008, per the notes. I did not re-render, because the Lead's gate covers it.
  - **Nit:** the bust now shares the L and R eye index accessors (43 accessors where there were 45). That's fine for Godot, but note it in character_shading.md in case a tool ever edits one eye's indices in place.
