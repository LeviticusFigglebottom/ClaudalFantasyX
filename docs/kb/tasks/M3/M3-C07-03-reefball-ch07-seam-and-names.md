---
id: M3-C07-03
title: "Reefball: replace Ch7's stand-in match at the seam, and reconcile the match's names"
role: lead
status: todo
owner_session: ""
depends_on: [M3-C07-02]
milestone: M3
request-from: cinematics
---
## Goal
M3-C07-02 built Ch7's story around the Reefball match (M3-RBL-01, the Reefball Lead agent's) with a data-driven stand-in where the match goes. Swap the stand-in for the real match, and bring the match's provisional names in line with act1_ch07.md.

## Acceptance criteria
- [ ] **The seam.** In `game/data/flow/chapters/ch07.json`, zone `ch07/tamsule_bell_galleries`, replace the steps of the beat `reefball_match` (and nothing else) with the hand-off to the match scene. Today those steps are `{"set": "ch07_tidecup_played"}` then `{"go": {"location": "ch07/tamsule_bell_galleries", "spawn": "CatchPool"}}`. The naming beat already runs this beat through `{"if_event": "start_reefball", ...}` once `ch07_naming.dlg` reports `<<event start_reefball tidecup_opening>>`. A `scene` step to the match, or a new step kind (ADR 0035 says how), both work.
- [ ] **The match's return** (act1_ch07.md §5.4):
  - always set `ch07_tidecup_played`;
  - set `ch07_tidecup_won` on a win only (a reward, never read by the story);
  - give the rewards (the Oruvel Float and lume on a win, lume on a loss);
  - go to `ch07/tamsule_bell_galleries` at spawn `CatchPool`, where the arrival row plays B07.
  - No retry prompt.
- [ ] **Names.** Rename the provisional loc rows:
  - the opponent is the atoll side **Sorrin** (captain Ione Sabe), not "Pemakar Terraces";
  - Rhen dives **in Pio's place**, Oruvel's missing youngest;
  - Oruvel's divers are the sheet's proposed four: Brann Ollo, Mae Ketter, Dovic Saan and Tull Arro. They replace "Noa" and "Old Ama", whose names now belong to nobody.
  - Ch7's moorings scene names the Ketters, Ollo, Dovic's brothers and Old Arro, so please keep those four.
- [ ] **The barks.** Fire `game/data/dialogue/ch07/ch07_reefball_barks.dlg`'s nodes on the match's own events, if wanted: the first node (kick-off), `oruvel_scores`, `sorrin_scores`, `rhen_first_score` (once), and `final_whistle`.
- [ ] **The flag check.** If a `.dlg` gives the win reward, add it to `REWARD_SCRIPTS` in `tests/integration/test_ch07_thread.gd`. That is the only place a script may read `ch07_tidecup_won`.
- [ ] **One event.** `start_reefball` is declared in `game/data/dialogue/events.json` by M3-C07-02 (arg `match`, an id). If your branch declares it too, keep one row.
- [ ] Update `tests/integration/test_ch07_thread.gd`'s `_naming_and_match` for the real hand-off, and keep `test_after_the_bell_is_the_same_win_or_lose` green.

## Notes
- The match id is `tidecup_opening`, not act1_ch07.md's `ch07_tidecup_oruvel_sorrin` (the Lead's call, 2026-10-24).
- The story's half of the Bell is the greybox stand-in zone `ch07/tamsule_bell_galleries`: the galleries, the pool and rim, and the moorings. The arena itself, `ch07/tamsule_bell`, is env-art's and yours. Whether the story beats move into it later is M3-C07-04's call.
- See `docs/kb/tech/chapter_flow.md`, "Ch7".

## Review log
