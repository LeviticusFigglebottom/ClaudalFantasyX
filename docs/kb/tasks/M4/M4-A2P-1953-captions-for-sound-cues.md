---
id: M4-A2P-1953
title: "Captions for important non-dialogue sound cues (a setting and where they show)"
role: ui
status: todo
request-from: audio
owner_session: ""
depends_on: [M4-A2P-1952]
reviewer: audio
milestone: M4
---
## Goal
The Lead's 10-30 21:25 accessibility item asked for captions for any important non-dialogue sound cue, if the game has a captions setting. It has none. Dialogue, narration and voice-over are subtitled (SubtitleStyle), but a sound that carries meaning on its own reaches a deaf or hard-of-hearing player only if it is also seen. This needs a captions setting (off by default, on the Accessibility page) and a place to show a short bracketed line ("[a bell tolls, far off]"). Audio will then add an event per cue and its loc keys.

## Cues that carry meaning (audio's list)
- **Battle tells:** a telegraphed skill's wind-up (skills.json `charge`; seven in Act I, four in Act II). The timeline already shows the intent, so a caption here is only "[the Drownbell gathers]" for a player watching the arena, not the timeline.
- **Off-screen story sounds in cutscenes:** an `@sfx` that a line or a beat answers (a sound the party reacts to before the camera shows its source). Audio will list these by marking their cutscene sfx rows `story: true` once the setting exists.

## Acceptance criteria
- [ ] A `captions` bool in accessibility.json (default off) and a caption line that never covers the dialogue box.
- [ ] Audio emits the caption with a loc key, and adds the keys.

## Review log
