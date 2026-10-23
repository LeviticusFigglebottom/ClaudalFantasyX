---
id: M1-RND-14
title: Shader-test mesh build fails on Blender 5.0.1
role: rendering
status: todo
owner_session: ""
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
- [ ] The script runs on Blender 5.0.1, and two runs are byte-identical.
- [ ] The rebuilt `.glb` files match the committed ones, or are recommitted with the shader-test shots re-approved after a look (`char_*` shots).
- [ ] `python3 tools/dev/verify_blender_builds.py --job shader_test` passes, then remove the job's `expected_failure` from `tools/dev/blender_builds.json`.

## Notes
-

## Review log
