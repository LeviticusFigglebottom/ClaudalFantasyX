---
id: M3-CHR-518
title: "The prologue's vigil-keepers (five, City/Vigils)"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`game/levels/prologue/prologue.tscn` `City/Vigils/Vigil3`..`Vigil7` are capsules (Mesh_25). Five vigil-keepers
built as villager variants, kneeling or standing at the vigil (Rhen and Asha in the same group are heroes, M3-CHR-519).

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] A vigil kneel and a standing-vigil idle (story-clip specs).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

## Review log
