---
id: M3-CHR-509
title: "The Order clerk (Ch6, speaker `clerk`)"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ch6's Order clerk is a capsule (M3-C06-06 #4, act1_ch06.md §9 #27: speaker `clerk`, CHAR_CLERK). A villager-path
build (the villager pipeline, `assets_src/characters/villagers/`), in the Order's colours without armour.

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] Clips for the scripts' `hand_over` proposal and talk/idle.

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

## Review log
