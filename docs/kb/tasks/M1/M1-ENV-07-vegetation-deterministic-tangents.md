---
id: M1-ENV-07
title: Vegetation builds with deterministic tangents (single-threaded, or no exported tangents)
role: environment
status: doing
owner_session: "worktree-agent-a361fe4924e35dfcf"
depends_on: [M1-QA-06]
milestone: M1
request-from: "qa"
---
## Goal
M1-QA-06 found that Blender's threaded tangent export races. At 4 threads, base_body's rebuild hash changed from run to run, and at `--threads 1` it was byte-stable. Another agent's full gate run failed `vegetation` on palm_coconut_b.glb TANGENT data with no asset change, which fits the same race. The gate now rebuilds vegetation at `--threads 1` (blender_builds.json `"threads": 1`), and the committed files match that build. But `assets_src/environments/vegetation/build.py`, run by hand, still uses Blender's default thread count, so a future rebuild can commit a variant the gate rejects.

## Acceptance criteria
- [ ] The vegetation build is deterministic whoever runs it. Either document and use `blender --threads 1` for it (a header line in build.py and the PROVENANCE build column), or stop exporting tangents (`export_tangents=False` in veg_common.py, as kit_common.py does; Godot's `ensure_tangents` import setting already generates them), then regenerate and re-approve the affected screenshots.
- [ ] `python3 tools/dev/verify_blender_builds.py --job vegetation`, run three times at once, reports `7 identical` every time.
- [ ] If tangents are no longer exported, the job's `"threads": 1` in tools/dev/blender_builds.json may go back to the default (the unit test in tools/tests/test_blender_builds.py only requires 1 thread for jobs that export tangents).

## Notes
- Measured in M1-QA-06 (docs/kb/qa/blender_builds.md, "Threads are pinned"). 38 default-thread vegetation rebuilds were all identical here, so the race is rare for these meshes, but base_body shows it is real.

## Review log
