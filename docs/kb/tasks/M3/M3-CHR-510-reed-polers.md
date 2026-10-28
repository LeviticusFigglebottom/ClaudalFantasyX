---
id: M3-CHR-510
title: "Four Reeds (the Ch6 barge polers)"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-01, M1-CHR-14, M2-CHR-515]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ch6's four Reed polers are capsules (M3-C06-06 #4). `villager_reed` exists: these are four variants of it (build,
face, wrap, weathering) with the `pole_barge` clip (the pole gripped by the M2-CHR-515 prop grip).

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] `pole_barge` and `bow_from_barge` clips.

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

## Review log
