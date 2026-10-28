---
id: M3-ENV-1301
title: Ch5 Pemakar takes env-art's harbour pieces (M3-ENV-1214): the quay, the weir at the quay's east end, the wake-wall, the crown bell, the day grade
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: [M3-ENV-1214]
milestone: M3
reviewer: cinematics
---
## Goal
The zone kept three greybox stand-ins (WakeWall, SeaCutWeir, CrownBell) and a quay of terrace modules. Place
env-art's pieces and its day grade.

## Acceptance criteria
- [x] The preview's `harbour_quay` replaces the module quay; `wake_wall`, `sea_cut_weir`, `crown_bell` follow their
  blocks; no greybox kept.
- [x] The weir: env-art's preview sets it at the bottom channel's outlet (x -39), but B05's weir folk stand at the
  quay's east end, so the weir comes to them: its west cheek against the quay's east end, cheek tops flush with the
  deck (crest 0.7 m over the sea). `--weir-relayout` (once) moved the weir folk 4.6 m east with P11/P12/P02D.
- [x] A lamp pillar at the quay's east end and the spill's fire light (night only: they follow the Lamps block).
- [x] The dawn variant (`ch05_kahre_bound`) takes `pemakar_day_environment.tres` and env-art's day sun (24° / 252°).
- [x] `--filter=ch05`, `pemakar`, the cutscene-walk audit green; shots `ch05_pemakar_weir`, `ch05_pemakar_harbour_day`
  self-rendered and viewed.

## Review log
