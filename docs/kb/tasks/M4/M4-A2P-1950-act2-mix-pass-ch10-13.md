---
id: M4-A2P-1950
title: "Act II mix pass as played, Ch10-Ch13: cutscene -> field -> battle -> victory -> field"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: []
reviewer: lead
milestone: M4
---
## Goal
The Lead's 10-30 18:04 item: an Act II mix pass as played on Ch10-Ch13, through cutscene -> field -> battle ->
victory -> field, looking for silences, loudness jumps and doubled starts.

## Acceptance criteria
- [x] Every hand-over's loudness step measured (`tools/audio/act1_mix_pass.py --act 2 --chapters ch10,ch11,ch12,ch13`,
  report `docs/kb/audio/act2_mix_pass.md`): 40 hand-overs, 0 over 3 LU.
- [x] Silences: none (`act1_playthrough.py --act 2 --holds docs/kb/audio/act2_direction_holds.json`).
- [x] Doubled starts: none that restart a cue. The cutscene -> battle seams carry the same cue on.
- [x] The victory -> field seam: the sting is measured at its own rule; the field's cue fades in under it.

## Notes
- The tool gained `--act` and `--chapters` and the victory -> field pair. Its test covers Act II
  (`tools/tests/test_act1_mix_pass.py`).
- The bosses sit about 2 LU under the field loops (row volume_db, as Act I's): intended, the fight's own weight.
