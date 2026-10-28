---
id: M3-ENV-1311
title: Ch7 Tamsule's lane signboard as the kit's gilded board (the Signboard block had no piece)
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: [M3-ENV-1300]
milestone: M3
reviewer: art-direction
---
## Goal
The Lead's "props a player touches or reads" pass. Tamsule's `Signboard` block (T01: gilded signboards) was hidden
with the greybox and nothing stood in its place.

## Outcome (2026-10-28, env-art-b): nothing to add
The block was a 3 x 0.8 m fascia board 3.2 m up at the front of lane house S0 (`shophouse_b` at (-17, 12), front at
z 7). Tamsule's shophouses already hang their own gilded signboard from the front corner (`port.py`), so the hidden
block's job is done by the kit's houses. A standing `signboard_gilded` there crowded the shop front (tried and viewed
from the lane, then reverted). No piece is needed.

## Review log
