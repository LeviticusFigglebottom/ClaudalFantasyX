---
id: M4-A2P-1951
title: "Act II mix pass as played, Ch14-Ch16: cutscene -> field -> battle -> victory -> field"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: []
reviewer: lead
milestone: M4
---
## Goal
The Ch14-Ch16 half of the Lead's 10-30 18:04 item (an Act II mix pass as played), through cutscene -> field -> battle ->
victory -> field, looking for silences, loudness jumps and doubled starts.

## Acceptance criteria
- [x] Every hand-over's loudness step measured (`tools/audio/act1_mix_pass.py --act 2 --chapters ch14,ch15,ch16`,
  report `docs/kb/audio/act2_mix_pass.md`): 22 hand-overs, 0 over 3 LU (62 across Ch10-Ch16).
- [x] Silences: none (`act1_playthrough.py --act 2 --holds docs/kb/audio/act2_direction_holds.json`).
- [x] Doubled starts: none that restart a cue.
- [x] Cutscene -> battle: three Ch14-Ch16 fights would have played the generic `battle_standard_v2` instead of their
  delivered cues: `ch14_malcor_venn` (malcor_venn), `ch14_water_steps` (court_steps) and `ch16_abiding_guard`
  (abiding_guard). Combat hasn't written those encounters yet, so music.json `battle.pending_encounters` now holds them
  and `data_check` accepts them until encounters.json has them (then it asks for them to come off). Each fight scores
  itself the moment it exists. The Wakefin's seam carries its own cue.
- [x] The victory -> field seam: the sting is measured at its own rule; the field's cue fades in under it.

## Notes
- The chapter plan (ch14.md) calls the steps set piece `ch14_hold_the_steps`; the script starts `ch14_water_steps`.
  Both ids name court_steps until combat settles it (a LEAD-ASK in the live log).
- The tool gained `--act` and `--chapters` and the victory -> field pair. Its test covers Act II
  (`tools/tests/test_act1_mix_pass.py`).
- The bosses sit about 2 LU under the field loops (row volume_db, as Act I's): intended, the fight's own weight.
