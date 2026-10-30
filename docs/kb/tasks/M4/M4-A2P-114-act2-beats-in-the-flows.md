---
id: M4-A2P-114
title: "Request: play the Act II scenes from the Ch10–Ch16 flows (the setters for the beat-level objective rows)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To act1-chapters, who own the Ch10–Ch16 greybox flows (M4-C10-02 … M4-C14-02). This comes from the Lead's FAST-TRACK on
big23's test_qa_threads red.

The greybox flows play no Act II scene, so no chapter thread raises the story flags the scenes set. test_qa_threads
requires every main objective's `requires` and `until` in a chapter's zones to be raised by that chapter's thread.
Story's beat-level objective rows for Ch10–Ch13 therefore failed on 19 flags.

**Update (2026-10-30, the Lead):** story has written the 10 cut rows back in, unchanged (the Ch10–Ch14 block is as
at 089c254d4). Each flag the threads can't raise yet is listed in `tests/integration/qa_known.json` `"unraised"`, with
the scene that sets it and this task, so test_qa_threads reports it instead of failing. An objective's `until` gates no
beat, so none of them is a softlock.

**For act1-chapters:** as each flow step lands (a `play` of the scene, or a battle's `victory_flag`), delete that
flag's `unraised` row in the same commit. The guard then holds it for good. The rows in `objectives.json` need no
change.

## What to wire (the scene that sets each flag, and the row that waits on it)
| Flag | Set by (scene or battle) | Rows that wait on it |
|---|---|---|
| ch10_farewell_tide_seen | `ch10_farewell_tide` | r_shore `until`; r_gate |
| ch10_complete | `ch10_dawn_gate` | r_gate `until` |
| ch11_nhoa_bound | `ch11_nhoa` | l_down `until`; l_out |
| ch11_complete | `ch11_held_by_you` | l_out `until` |
| ch12_ram_felled | **the Avalanche Ram's battle: a `victory_flag` in ch12.json** (only the side scene `ch12_herd_cord` sets it now) | k_wall `until`; k_to_quellan |
| ch12_hesk_bound | `ch12_hesk` | c_dais `until`; q_inn |
| ch12_ysolde_confessed | `ch12_forty_seven_voices` | q_inn `until`; q_on |
| ch12_complete | `ch12_down_the_other_side` | q_on `until` |
| ch13_ethren_bound | `ch13_ethren` | a_sanctum and s_ledge `until`; a_archive `requires` |
| ch13_read_ledgers | `ch13_archive_ledgers` | la_ledgers `until`; la_roll |
| ch13_read_cantor_roll | `ch13_archive_roll` | la_roll `until` |
| ch13_archive_read | `ch13_archive_hands` | a_archive `until`; a_moorings |
| ch13_pact_of_silence, ch13_complete | `ch13_the_pact` | a_moorings, a_rest |
| ch14_vows_spoken, ch14_declared_heretics | `ch14_the_vows` | lc_vows (`requires` ch14_started, `until` ch14_vows_spoken); lc_steps |
| ch14_steps_held | the water-steps set piece's scripted escape (and `ch14_first_ripple`, which now sets it as it opens) | lc_steps `until`; lc_gate |
| ch14_complete | `ch14_left_standing` | lc_gate `until` |

The scenes' running order and the flags they set are in each `act2_chNN.md` §1, and their staging is in
`act2_chNN_direction.md`.

**The Lacquer Court's rows are Ch14's but sit in a `ch13/` zone**, so Ch13's thread is the one that checks them (see
M3-UI-1242). Their five flags (ch14_started and the four beat flags) stay in `unraised` until either the guard reads a
row's `"chapter"` or Ch13's thread plays into Ch14.

**Ch15** (`ch15_the_dock_master` must play when the party reaches Hollowmere, after `ch15_current_song` at sea) and
**Ch16** have no thread that checks their rows yet, so their rows are unchanged.

## Acceptance criteria
- [x] The beat-level rows are back in `objectives.json` (story, 2026-10-30).
- [ ] Each Ch10–Ch14 flow plays its scenes and battles in §1's order.
- [ ] `qa_known.json` `"unraised"` is empty again, and test_qa_threads stays green.

## Review log
