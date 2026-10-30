---
id: M5-A3P-1009
title: "Request (combat): the Ch19 Wardens' encounter (ch19_abiding_wardens) and a mid-battle line hook for Act III's fight lines"
role: combat
status: todo
owner_session: ""
depends_on: [M5-A3P-1006]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
`ch19_the_signatures` ends on `<<event start_battle ch19_abiding_wardens>>`, and no such encounter exists yet. Brief:
act3_ch19.md §5 (Wardens Hesper Oan and Ilsabet Rue, two of the Abiding held alive by bound light, fought openly as
revenants for the first time). The victory flag is `ch19_abiding_beaten`.

The fight lines in `ch19_bark_abiding_wardens.dlg` are one node per trigger:
- the opening;
- Hesper at 50% HP (`ch19_bark_wardens_half`);
- once, if Kerrid is in the active party (`ch19_bark_wardens_kerrid`);
- the end (`ch19_bark_wardens_end`).

The game plays lead-in barks only (`battle_transition.json`). The same hook serves the Ch20 Vowbound fights and the
Ch21 phases (drafts README decision 13), so one general hook is worth more than a per-fight one: play a dialogue
node on an HP threshold, a party-member condition, or the battle's end.

## Acceptance criteria
- [ ] The `ch19_abiding_wardens` encounter exists, with `victory_flag: ch19_abiding_beaten`.
- [ ] Each node plays at its trigger, without pausing the timeline longer than a bark.

## Review log
