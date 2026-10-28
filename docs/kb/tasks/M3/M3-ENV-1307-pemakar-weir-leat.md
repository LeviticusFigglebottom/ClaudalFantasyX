---
id: M3-ENV-1307
title: Pemakar's weir gets the leat that feeds it (a stepped channel from tier 0's culvert down the flank)
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: [M3-ENV-1301]
milestone: M3
reviewer: art-direction
---
## Goal
The weir moved to the quay's east end (M3-ENV-1301), and nothing fed its cut: by day it read as a pale stone slab.

## Notes (2026-10-28, env-art-b)
- New Pemakar kit piece `weir_leat` (`b_leat.py`): twelve 2 m stepped beds between cheek walls with water and spill
  sheets, from a culvert mouth in tier 0's wall to the cut's back. The kit was rebuilt `--all`: older pieces are
  byte-identical. Placed by `ch05_pemakar_dressing.py` (LEAT_AT), following the SeaCutWeir block. It has no collision
  (only the road is walkable on the flank).
- `--filter=pemakar` 10/0. Self-rendered ch05_pemakar_harbour_day (the leat climbs to tier 0) and ch05_pemakar_weir
  (unchanged).

## Review log
