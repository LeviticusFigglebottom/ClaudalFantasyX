---
id: M3-CHR-516
title: "The Haluna smith (Ch2 Haluna, a capsule stand-in)"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Haluna smith is a CapsuleMesh stand-in in `game/levels/ch02/haluna/haluna.tscn` (`NPCs/Town/Smith/StandIn`). A
villager-path build (`assets_src/characters/villagers/`, the M1/M2 villager pipeline), dressed for the trade, with the
field idle and talk clips the town uses.

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] Idle, talk and a trade gesture clip (the villager clip set).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

## Review log
