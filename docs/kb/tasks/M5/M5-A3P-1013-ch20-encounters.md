---
id: M5-A3P-1013
title: "Request (combat): Ch20's seven fights (six Vowbound, the Cage), their fight lines, and the release flags"
role: combat
status: todo
owner_session: ""
depends_on: [M5-A3P-1010, M5-A3P-1009]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
The Ch20 scripts start seven encounters that don't exist yet: `ch20_ilun`, `ch20_kahre`, `ch20_virel`, `ch20_hesk`,
`ch20_nhoa`, `ch20_ethren` and `ch20_the_cage`. The Cage's victory flag is `ch20_cage_broken`. Brief: act3_ch20.md §5;
vowbound.md (each Vowbound's final fight).

## Fight lines
`ch20_bark_vowbound_fights.dlg` has one node per trigger and needs M5-A3P-1009's mid-battle hook:
- Kahre's "It doesn't hurt, son." (verbatim; with the `ch20_bark_kahre_kerrid` and `_garo` variants);
- Nhoa's echo;
- the Cage's seat and Lamptongue nodes.

## Release flags
Each `ch20_<vowbound>_release` scene sets `ch20_<vowbound>_released`. After it:
- the Vowbound leaves the summon menu (vowbound data's released flag, owned by combat/progression);
- the codex marks the release.

## Acceptance criteria
- [ ] The seven encounters exist, and each fight line plays at its trigger.
- [ ] A released Vowbound can't be called.

## Review log
