---
id: M3-CRE-644
title: "Ethren, the Level Saint (Glimmer, bound Ch13): the Vowbound model (design sheet done; build next)"
role: character
status: doing
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-638]
milestone: M3
request-from: creatures
---
## Goal
Build ethren per its design sheet, docs/kb/art/creatures/vowbound/ethren.md (proposed, 2026-10-27), the way Ilun was built
(M3-CRE-638) and Kahre and Virel are being built (M3-CRE-640/641): the model and clips, the creatures.json
`"vowbound": true` row, a review shot, a portrait manifest row, and the tests, including the summon path.

## Notes
- ethren has no game/data/battle/vowbound.json row yet. The model doesn't need stats, but its clip map (which skill plays
  which clip) waits on Combat's skill ids; until then use the stand-in set.
- The sheet's open questions are for Combat and the Lead, not the human.

## Review log
