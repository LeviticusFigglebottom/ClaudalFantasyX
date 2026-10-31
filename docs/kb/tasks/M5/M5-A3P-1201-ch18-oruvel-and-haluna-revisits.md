---
id: M5-A3P-1201
title: "Request: Ch18's revisits to Oruvel and Haluna (the Ch1-Ch3 zones' Act III rows) and Haluna's heirloom"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1004]
reviewer: narrative
milestone: M5
request-from: cinematics
---
## Goal
To slice-polish (the Ch1-Ch3 zones and `first_playable.json`'s Haluna story are yours), from act1-chapters' Ch18
flow. The Kite (`ch18/kite`, `chapters/ch18.json`) sets a course to each revisited town. Every town has an Act III
arrive row in its own chapter file, gated on `ch18_world_open` and a seen flag: it plays the town's revisit once,
then goes back aboard (`ch18/kite` Deck) or offers an `a3_to_kite` interact. Pemakar, Tamsule, Corrow, Quellan,
Hollowmere and Reedhollow are done. Two towns aren't in my lane:
- **Oruvel** (`ch01/oruvel`, `chapters/ch01.json`): `ch18_revisit_oruvel` (reads `ch07_told_tavi`).
- **Haluna** (`ch02/haluna`, HalunaStory and `first_playable.json`): `ch18_backs_to_the_water` (optional and
  flagged; sets `ch18_haluna_lifted`), and Asha's heirloom (Imra's lantern-staff), a node of `ch18_heirloom_rhen.dlg`
  until M5-A3P-1200 splits it.

## Ask
The rows in your zones, as in `chapters/ch05.json`'s first `ch05/pemakar` arrive row. Then I add their courses to
the Kite (`tools/act3/ch18_greybox.py` `COURSES`, the loc rows `FIELD_PROMPT_CH18_COURSE_*`) and beats to
`ch18.json`. Name the spawn the Kite lands at.

## Acceptance criteria
- [ ] Oruvel's and Haluna's revisits play once from a Kite landing and hand back aboard; their threads stay green.

## Review log
