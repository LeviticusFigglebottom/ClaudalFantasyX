---
id: M3-CIN-1234
title: "Request (slice-polish, Ch1): the dive rolls 4–5 random fights; widen ch01/oruvel_underway's gaps to about 3"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
act1-chapters' flow and pacing pass (the Lead's brief, 2026-10-29; the Lead asked for this proposal) on
lead/gate-big18. `ch01/oruvel_underway`'s encounter block is `min_m` 18, `max_m` 34 (grace 12 m, the default). The
critical route Drop → BellRoom1 → Gallery → GalleryAfter → GaugeRoom → ShaftFoot is 130 m in straight lines.
Simulated over 2,000 seeds (uniform gaps, grace after each fight), with the shutter open:

| walked (detour) | fights now (mean, max) | min 32 / max 52 | min 40 / max 60 |
|---|---|---|---|
| 156 m (x1.2) | 3.98, 5 | 2.75 | 2.04 |
| 195 m (x1.5) | 5.0, 6 | 3.25 | 2.99 |

That's on top of the dive's scripted fights. For the game's opening (Pillar 4, and the slice's own two or three
causeway fights, M2-FP-114) it reads dense. The lantern shutter's `encounter_rate_mult` halves it only for a player who
uses it.

## Acceptance criteria
- [ ] `min_m` 32, `max_m` 52 (about 3 random fights on the dive), or slice-polish's own tuning with its numbers.
- [ ] `tools/balance/sim.py --suite ch01_underway_shoals --suite ch01_underway_limpet` still in band (the fights
      themselves don't change).

## Review log
