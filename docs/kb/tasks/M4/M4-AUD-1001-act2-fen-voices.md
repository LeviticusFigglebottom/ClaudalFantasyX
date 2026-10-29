---
id: M4-AUD-1001
title: "Request (act1-chapters): creature voices for Ch10's tannin archer, root crab and fen leech"
role: audio
status: blocked
blocked-by: ADR 0041
owner_session: ""
depends_on: [M4-C10-03]
milestone: M4
request-from: cinematics
---
## Goal
M4-C10-03 added three Act II foes (`tannin_archer`, `root_crab`, `fen_leech`; act2_roster.md Ch10). They are "silent"
in `game/data/audio/creature_voices.json` so validate_data stays green; give them voice rows (the root crab can borrow
the reef crab's family, the leech the sail leech's).
