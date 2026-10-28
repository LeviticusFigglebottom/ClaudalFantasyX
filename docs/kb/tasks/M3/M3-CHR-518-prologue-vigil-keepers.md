---
id: M3-CHR-518
title: "The prologue's vigil-keepers (five, City/Vigils)"
role: character
status: blocked
owner_session: "chr-npc-wip (characters worktree)"
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

- 2026-10-28 (chr-npc-wip): **not built, on purpose; needs the Lead.** The Prologue's vigil is the party: act_outline "The Last Time" ("The party, all seven, are on a broken plaza ... each keeping a vigil"), act1_ch09.md B10 ("the same seven keeping their separate vigils") and prologue_dead_city.dlg ("Everyone I'm going to tell you about is still here tonight"). `Vigil3`..`Vigil7` in the act1-chapters prologue.tscn are therefore Toma, Ysolde, Kerrid, Pell and Liss (the characters branch's prologue already names Kerrid, Pell and Liss there), not strangers. Building five villager vigil-keepers would put the wrong people in the frame. Proposed: fold the five into M3-CHR-519 as hero swaps (Toma, Ysolde, Kerrid and Liss are built; Pell has no model yet: pell.md, a hero-path task), and close this task. If the Lead wants extra mourners in the plaza besides the seven, say so here and this becomes five villager variants with a both-knees vigil kneel (villager_clips' `kneel_both` posture and `kneel_wait` clip already exist).

## Review log
