---
id: M5-A3P-1013
title: "Request (combat): Ch20's seven fights (six Vowbound, the Cage), their fight lines, and the release flags"
role: combat
status: review
owner_session: "act1-chapters"
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

## Notes (act1-chapters, the chapters combat seat, 2026-10-31)
- The seven encounters exist (encounters.json, all scripted):
  - `ch20_<v>`: one `<v>_held` each; a "release" phase at 20%; answered by the hero vowbound.md names (Ilun/Nhoa/Ethren
    Ysolde, Kahre Kerrid, Virel/Hesk Toma).
  - `ch20_the_cage`: four founder seats (`cage_orin/halde/isse/cael`; each seat's phase `when_down` its neighbour
    grows it stronger); Toma locked active (HUD_SWAP_CH20_TOMA_LINE). Victory flag `ch20_cage_broken` stays the flow's.
- Bands (500 seeds, tools/balance/targets.json):
  - the six held fights are in the Act III regular band (role 89.0-99.4, naive <= 8.4, smart 100);
  - the Cage is in the Act III boss band (role 70.0, naive 0, smart 100 at 34 mean turns >= 30).
- Released flags: the six vowbound.json rows carry `released_flag: ch20_<v>_released` (the HUD and the status menu
  already drop a released Vowbound, M5-A3P-1705).
- **Open:** the fight lines (`ch20_bark_vowbound_fights.dlg`) wait on M5-A3P-1009's mid-battle line hook
  (battle-presentation); there is no hook to wire them to yet. Toma's primed Swell after `ch14_toma_refused` is a flow
  primer the Ch20 zone (M5-A3P-1011) sets.
- No models yet: the held shapes M5-A3P-1809, the Cage M5-A3P-1851 (qa_known capsules).

## Review log
