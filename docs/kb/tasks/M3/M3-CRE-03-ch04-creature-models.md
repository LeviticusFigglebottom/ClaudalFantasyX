---
id: M3-CRE-03
title: "Ch4 creature models: Spar-Wraith, bottle hermit, sail leech"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M3-CRE-01]
milestone: M3
request-from: lead
---
## Goal
The three Ch4 creatures from docs/kb/art/creatures/act1/ through the creature pipeline (docs/kb/art/creatures/pipeline.md):
build, materials, battle scene, creatures.json row, job, provenance, a review shot. `"model"` goes on their enemies.json
rows once m2-slice adds them (M3-C04-02).

## Acceptance criteria
- [x] spar_wraith (first pass: 4.6k triangles, 11 bones; a segmented spawn body hanging in a rigging web between two broken spars it grips; three glowing knots; review shot creature_spar_wraith)
- [x] bottle_hermit (first pass: 3.4k triangles, 16 bones, the five clips; review shot creature_bottle_hermit)
- [x] sail_leech (first pass: 5.7k triangles, 11 bones, the five clips; origin is its hover point; review shot creature_sail_leech)

## Notes
- 2026-10-24: all three have first passes, rows, identical jobs, PROVENANCE and approved review shots. No enemies.json rows yet (m2-slice, M3-C04-02); add `model` with them. Heights: Spar-Wraith 3.6 m (spar tips), bottle hermit 0.45 m, sail leech built around its hover point (spec hover about 1.4 m).

- 2026-10-24: m2-slice's two-phase spar_wraith (`hauled_down`): a `Shroud` mesh (hidden by the phase), a `Sheath` water skin (`show_after`, a new phase key), the drop and deck strikes (phase `clips`). The kit gained `pose_of`/`in_pose`, shared with the Reach (its build is byte-identical). Shot re-approved after viewing (0.03089).

## Review log
