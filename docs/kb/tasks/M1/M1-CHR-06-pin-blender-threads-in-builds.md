---
id: M1-CHR-06
title: Pin Blender's thread count in the base_body and Asha build scripts
role: character
status: todo
owner_session: ""
depends_on: [M1-QA-06]
milestone: M1
request-from: "qa"
---
## Goal
M1-QA-06 pinned Blender's thread count in the rebuild gate (tools/dev/blender_builds.json), because two character builds depend on it:
- **base_body** exports tangents, and Blender's threaded tangent export races. At 4 threads the rebuild hash changed from run to run (athletic `cbcee8…` or `4523ba…`, heavy `58142e…` or `06cf15…`). At `--threads 1` it was byte-stable. The gate runs it at `--threads 1`.
- **Asha's** body bakes (`asha_body_normal`, `_orm`, `_skinmask`) are stable at a fixed thread count, but differ at 1 thread compared with 4. The committed textures match 4 (this sandbox's CPU count), so the gate runs Asha at `--threads 4`.

`assets_src/characters/base_body/build_all.sh` and `assets_src/characters/asha/build.sh` still use Blender's default (the host's CPU count). A rebuild on a machine with another core count, or one that loses the tangent race, commits files the gate then rejects.

## Acceptance criteria
- [ ] base_body's build script passes `--threads 1` to Blender (or stops exporting tangents and regenerates), and M1-CHR-05's rebuild uses it.
- [ ] Asha's build.sh passes `--threads 4` (or the gate's `default_threads` changes with a regenerate, in one commit).
- [ ] `python3 tools/dev/verify_blender_builds.py --job asha --job base_body` agrees with the committed files, apart from base_body's tracked M1-CHR-05 mismatch until that lands.

## Notes
- Do not change these from QA; `assets_src/characters/asha` is being rebuilt in another worktree (M1-CHR-03/04 line). Fold this in there.

## Review log
