---
id: M5-A3P-1851
title: "The Cage (Ch20 boss): the frame, its four founders' seats and chains, at final quality"
role: character
status: review
owner_session: "creatures-b (claude/creatures-b)"
reviewer: combat
depends_on: [M3-CRE-648]
milestone: M5
---
## Goal
The Ch20 boss (act3_ch20.md U07; docs/kb/art/creatures/act3/the_cage.md). The roster's reconciliation (act3_roster.md
"Reconciled with the Act III beat sheets", item 1) asks for the sheet's amendment first: four seats of bound light round
a well, each founder chained into one; break a seat's chains and that founder stops fighting and thanks you. The
founders' figures are the characters track's; the frame, seats, chains, rig, clips and its own VFX are creatures-b's.

## Acceptance criteria
- [ ] The sheet amended (seats and chains), agreed with creatures (its author) and Combat.
- [ ] The frame built, rigged and clipped at final quality, reproducible, with PROVENANCE rows; viewed in its arena.

## Progress
- 2026-10-31: built from the roster's amendment, written up in docs/kb/art/creatures/act3/the_cage_seats.md
  (creatures-b's note beside creatures' unchanged sheet; M5-A3P-1854 was unanswered, so this follows the default
  logged on 2026-10-30).
  - assets_src/creatures/the_cage/build_the_cage.py writes the GLB: four seats on the arc, each chained at the
    wrists and ankles. It is 47 bones and 17.4k triangles, and reproduces byte for byte.
  - Each quarter is `Q<n>Whole` (lit bars and crown, the clasp's spawn_wound seam) and `Q<n>Broken` (dark and
    cracked, the clasp split, the rings open, the chains parted).
  - Clips: idle, attack (the drag), cast (the tightening), hit, break_q1..q4 (4.0 s; the founder's cue at 0.5 s),
    and ko (the empty frame lets go).
  - The creatures row has four cumulative `break_q<n>` phases (hide/show/hide_after), stand_in yaw 45 and height 4.3,
    and `vfx_core` on the row of clasps. The scene holds `FounderQ1..Q4` placeholders at the seats.
  - Also: materials, the Blender job `creature_the_cage`, a portrait, PROVENANCE rows and tools/tests/test_the_cage.py.
  - Viewed: the portrait, the clip sheet, and a scratch render with q1 and q2 broken (dark and cracked) beside a
    lit q3 and q4.
  - **For Combat (review):** the enemy row, the phase thresholds (break_q4 just above 0 HP), `travel: none` for its
    skills, and its arena mark.
  - **For characters:** the founders, seated (the_cage_seats.md "For the characters track").

## Review log
