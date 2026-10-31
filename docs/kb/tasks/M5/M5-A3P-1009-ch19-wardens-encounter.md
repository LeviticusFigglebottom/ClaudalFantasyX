---
id: M5-A3P-1009
title: "Request (combat): the Ch19 Wardens' encounter (ch19_abiding_wardens) and a mid-battle line hook for Act III's fight lines"
role: combat
status: review
owner_session: "act1-chapters"
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

## Notes
- **act1-chapters (the chapters combat seat), 2026-10-31:** `ch19_abiding_wardens` exists: `hesper_oan` and
  `ilsabet_rue`, scripted (no Escape). The flow's battle step names the victory flag `ch19_abiding_beaten`.
  - **The watch-roll, as the engine can play it:** Ilsabet *is* the roll. Only Ysolde can break it (`answered_by`,
    as the Ch14 flat-engine). Every fourth turn she reads it back (Protect on both); between, she notes a hero down
    (a light blow). While the roll stands, Hesper takes an answering stance every third turn (a counter until her
    next turn, Stand Firm's rule). At half HP, or once the roll is broken (`when_down`), Hesper fights plainly and
    harder. Ilsabet leaves with Hesper. Neither yields: they lie still (rule 4). Kerrid answers Hesper.
  - **What the brief asks and the engine can't do yet:** recording the party's last three actions and answering the
    most frequent. That needs an engine feature; the stance and the roll's Protect stand in for it.
  - **Numbers** (provisional), suite `ch19_abiding_wardens` on a new `ch19_iskarra` loadout (Ch16's, plus Kesh),
    500 seeds: naive 0.0%, role_answer 69.8%, smart 100% (report only, with the Act II bosses' ease floor of 30
    mean turns: 40.7), p90 44, no timeouts. The probe showed that an earlier Slow on "Noted" cost the party half its
    turns, so it was dropped.
  - **The fight barks** (the second ask: a dialogue node on an HP threshold, a party member or the battle's end) are
    a battle-presentation hook. The nodes are ready in `ch19_bark_abiding_wardens.dlg`; that hook isn't mine to
    build.
  - **Bodies:** M5-A3P-1202 (character). Until then both are known in qa_known.json `capsules.battle_foes`, along
    with the Act II people already waiting (M4-A2P-051, M3-CHR-508).

## Review log
