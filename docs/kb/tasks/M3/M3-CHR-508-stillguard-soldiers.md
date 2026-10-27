---
id: M3-CHR-508
title: "Stillguard soldiers (six variants) for the Ch6 raid"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-01, M1-CHR-14, M3-CHR-507]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ch6's Stillguard are capsules in `brine_shoals_layout.json` `actors` (M3-C06-06 #4: six variants if the set is short).
The Order's soldiers: red-lacquered shell armour, round shields, spears (`shield_up`, `level_spear` proposals). Built
as one kit on the base body (Moll's armour language, M3-CHR-507) with six variants by build, face, helm and
weathering.

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] The Ch6 proposals they perform: `stand_watch_seaward`, `shield_up`, `level_spear` (the spear gripped).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

## Review log
