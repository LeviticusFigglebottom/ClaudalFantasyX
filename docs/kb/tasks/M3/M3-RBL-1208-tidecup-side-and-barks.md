---
id: M3-RBL-1208
title: Tidecup opening round, the story's opponent (Sorrin, not Pemakar) and the match's barks
role: combat
status: todo
owner_session: ""
depends_on: [M3-RBL-01, M3-C07-1206]
milestone: M3
request-from: cinematics
---
## Goal
act1_ch07.md §5.2: the away side is **Sorrin**, an atoll side from the Low Reaches (captain Ione Sabe; quick
swimmers), and explicitly not Tamsule. `game/data/reefball/matches.json` `tidecup_opening` plays Oruvel against
`pemakar`. Also §5.2: Rhen plays in Pio's place with four Oruvel names, and §5.3 lists the match's neutral barks
(kick-off, a float up, Sorrin scores, Rhen's first score, the final whistle). TidecupMatch (M3-C07-1206) only frames
the match, so these are the engine's data.

## Acceptance criteria
- [ ] A `sorrin` side in sides.json and `tidecup_opening` against it (the sim's bands re-run).
- [ ] The §5.3 barks fired on the engine's events (the HUD shows them), none naming a score.

## Review log
