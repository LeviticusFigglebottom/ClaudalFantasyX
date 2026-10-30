---
id: M3-AUD-803
title: Battle hit and KO sounds matched to battle-presentation's KO-once fix (M2-BPR-11)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
M2-BPR-11 makes a felled foe's KO play once, then fade out and hide. Audio's KO layers (BattleAudio ko_release, ChoreoAudio ko_collapse, CreatureAudio death) must also play exactly once, in step.

## Acceptance criteria
- [x] Each KO is heard once, timed to the KO clip, with a fade sound if the fade wants one; tests against the M2-BPR-11 contract.

## Notes
- 2026-10-24 audio (claude/audio):
  - **The bug wasn't audio's.** M2-BPR-11's bug replayed the creature's KO *clip*. None of audio's KO layers listen
    to that clip: BattleAudio's `ko_release` follows the VFX effect, ChoreoAudio's `ko_collapse` follows the
    choreography's `kos` for the felling action, and CreatureAudio's death plays once per fall (`_dead`, cleared on a
    revive). CreatureAudio's clip map holds only attack and cast.
  - **Test:** `test_a_ko_is_heard_once_through_later_actions` (tests/integration/test_battle_audio_live.gd) fells a
    foe, then runs `refresh_ko` and three later actions; the collapse, the death cry and the release are each heard
    once. It passes on claude/audio and on a scratch merge with origin/claude/battle-presentation (M2-BPR-11's code);
    test_battle_ko_once is 6/0 there too.
  - **Also found:** with battle-presentation merged, `battle_stinger` fires before the bark, so the bark test now
    expects the tide line at most once and before the line, rather than an exact list. That test would otherwise
    have broken at that merge.
  - **The fade (foe_ko_alpha 0):** no extra sound. The release and the collapse already cover the moment, and a
    sound on the fade would double them.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
