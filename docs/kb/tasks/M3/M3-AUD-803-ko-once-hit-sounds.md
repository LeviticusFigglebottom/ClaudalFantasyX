---
id: M3-AUD-803
title: Battle hit and KO sounds matched to battle-presentation's KO-once fix (M2-BPR-11)
role: audio
status: doing
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
M2-BPR-11 makes a felled foe's KO play once, then fade out and hide. Audio's KO layers (BattleAudio ko_release, ChoreoAudio ko_collapse, CreatureAudio death) must also play exactly once, in step.

## Acceptance criteria
- [ ] Each KO is heard once, timed to the KO clip, with a fade sound if the fade wants one; tests against the M2-BPR-11 contract.

## Notes

## Review log
