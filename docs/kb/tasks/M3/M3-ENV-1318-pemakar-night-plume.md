---
id: M3-ENV-1318
title: Pemakar's night plume reads as smoke, not a dark blob (the Lead's gate note on ch05_pemakar_harbour)
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: [M3-ENV-1301]
milestone: M3
reviewer: art-direction
---
## Notes (2026-10-28, env-art-b)
- `tools/act1/ch05_pemakar_dressing.py` writes `game/levels/ch05/pemakar/pemakar_plume_night.tres` (env-art's
  `env_ash_plume` shader: softer, thinner edges and the crater's ember up its underside), and the plume row takes it by
  slot. `--filter=pemakar` 10/0. Self-rendered ch05_pemakar_harbour and ch05_pemakar_crown.
- The Lead's other two gate notes (the Reach's greybox backdrop, Ch9's white bar) were integration's older state.
  This branch's arena mapping and Ch9 dressing already resolve them (rendered after merging big13).

## Review log
