---
id: M3-CHR-511
title: "Saltwright wrights: the girl at the brazier and two children (Ch6)"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ch6's Saltwright wrights are capsules (M3-C06-06 #4): the girl at the brazier and two children, line-marks visible
on pushed-up sleeves. Villager-path builds using `liss_textures.line_marks` / `paint_marks` with their own seeds and
placements (act1_npcs.md §2.3).

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] Clips for `dig_sand`, `flatten_sand`, `set_in_hole`, `crawl_out` (the children).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

## Review log
