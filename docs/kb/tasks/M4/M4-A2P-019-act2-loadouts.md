---
id: M4-A2P-019
title: "Act II loadouts (Ch10–Ch16) and every Act II suite re-run on its own chapter's loadout"
role: combat
status: review
owner_session: "act1-chapters"
depends_on: [M4-A2P-030, M4-A2P-031]
reviewer: progression
milestone: M4
request-from: lead
---
## Goal
Every Act II suite runs on `ch08_seawall` today. Add a loadout per chapter (`ch10_fen` … `ch16_rim`): the party the story gives (seven, Pell in), the Lattice progress of a player who spent every point (balance_targets.md), and the chapter's gear tier. Re-run the ten regular suites and add the boss and set-piece suites as the chapters land.

## Acceptance criteria
- [ ] Loadouts in `tools/balance/targets.json`; all Act II suites `--check` clean on the Act II curve.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.7.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters, 2026-10-31:** six loadouts in `game/data/battle/sim_policies.json`: `ch10_fen`, `ch11_vey`,
  `ch12_pass`, `ch14_court`, `ch15_sea` and `ch16_rim`. Each carries Act I's best gear (no Act II gear exists),
  Kerrid's and Liss's own kit, the Act I flags, and the Vowbound bound by then: Nhoa from Ch12, Hesk from Ch13,
  Ethren from Ch14 (Nhoa is bound only after the Lamp Engine, so Ch11 has none). Each chapter's consumables follow
  its shop's stock. Every Act II suite in `targets.json` now names its chapter's loadout.
  - **Left out:** Pell, who has no battle kit (M3-C09-07), and the Lattice: the sim has no party-progress hook yet
    (balance_targets.md: "to be scripted with `run_one(..., party_modifier)`"). Both want their own rows when they
    land.
  - **500 seeds, every Act II suite:** all in band (89 OK rows) except `ch15_wakefin`'s report-only `naive_swell`,
    whose losses run p90 91 against the cap of 80. That's the call rule re-calling Ilun; it's filed as
    M4-A2P-1202 (a policy change that also moves Act I). No encounter needed a retune: the new loadouts moved
    nothing out of band (the 200-seed `ch10_fen_archers` smart 96.5 and `ch12_pass_scree` naive 60.5 read 97.0 and
    59.8 at 500).

## Review log
