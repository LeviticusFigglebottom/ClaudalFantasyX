---
id: M2-CHR-515
title: "M1-QA-09 hardware findings on the heroes: props gripped, staff clear of skirt and floor, underskirt in deep kneels, Toma's beard edge"
role: character
status: todo
owner_session: "characters (new account, branch claude/characters)"
reviewer: rendering
depends_on: [M1-CHR-15, M2-CHR-513]
milestone: M2
request-from: rendering (pc-gpu, M1-QA-09 on hardware)
priority: top
---
## Goal
The PC's M1-QA-09 hardware read (gpu/m1-qa-09-heroes, docs/kb/qa/gpu/2026-10-27-m1-qa-09-heroes/README.md, at the
integration head f580e756) found these on the heroes. The ⚠ ones a player sees in normal play.

## Acceptance criteria
- [ ] ⚠ 1, 2, 7: Asha's staff and Toma's spear are gripped: the fingers close round the shaft in every clip (the
      clips key no finger today, so the hand stays open), and the prop reads as held in run, walk_cycle and turn.
      Rhen's fists close on his hooks while they are drawn (M2-CHR-513).
- [ ] ⚠ 2: in offer_hand the staff no longer stands behind her back through the braid.
- [ ] ⚠ 3: in kneel_over_rhen and laugh the staff stays out of the skirt and the floor.
- [ ] ⚠ 4: the white underskirt no longer reads as a rigid tube under the front knee in offer_hand, and the trailing
      shin stays under it.
- [ ] 5: extreme_pose's raised-knee skirt pocket (a stress stage; the two-bone panels' limit, see M1-CHR-15's notes).
- [ ] 8: Toma's beard edge at close-up (the alpha cards along the jaw).
- [ ] 6 (low): the gauze sleeve at large arm angles.

## Notes
- Item 9 (Rhen's hooks) is M2-CHR-513, done at 038d5651.

## Review log
