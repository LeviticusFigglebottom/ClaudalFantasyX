---
id: M3-AUD-800
title: Switch the battle hooks live: ChoreoAudio on the real BattleChoreo, CreatureAudio on CreatureActor, the stings
role: audio
status: doing
owner_session: "audio (claude/audio; worktree agent)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
big7 brought claude/battle-presentation's BattleChoreo and claude/creatures' CreatureActor onto the integration branch. choreo_sfx.json's hook is still pending, and M3-AUD-13/14/18 were only tested against stand-ins.

## Acceptance criteria
- [ ] Pending flags off; validate_data checks the real names; tests drive a real battle with the real choreography and creature models and hear each layer once (no doubled contacts, a retry leaves one listener).

## Notes

## Review log
