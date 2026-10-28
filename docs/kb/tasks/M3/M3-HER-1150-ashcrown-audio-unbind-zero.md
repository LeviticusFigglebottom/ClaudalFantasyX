---
id: M3-HER-1150
title: "AshcrownAudio._connect calls unbind(0) for a three-argument signal (an engine error on every Ashcrown entry)"
role: audio
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
integration-qa's real-frame battle entry probe (`tools/dev/battle_entry_probe.tscn -- --chapters=5`) logs
`ERROR: Amount of unbind() arguments must be 1 or greater. (callable.cpp:148)` each time the router enters
`ch05/ashcrown`, with the backtrace `_connect (game/audio/ashcrown_audio.gd:49)` ← `attach (:33)` ←
`AudioDirector.attach_ashcrown (audio_director.gd:583)`.

For a signal with exactly three arguments, the `_:` branch runs `.unbind(maxi(argc - 3, 0))`, which is `unbind(0)`.
Godot logs that as an error and returns the callable unchanged, so the sound still plays, but it's an engine error
on a normal zone entry, and the QA guards fail on engine errors. The sibling helpers already guard this
(`ui_audio.gd:90`, `choreo_audio.gd:165`, `reefball_audio.gd:172`: `x.unbind(n) if n > 0 else x`).

## Acceptance criteria
- [ ] `ashcrown_audio.gd` unbinds only when `argc > 3`.
- [ ] Entering Ashcrown logs no unbind error (the probe's ch05 line is clean).

## Notes
Owner: Audio (`game/audio/**`, ownership.md). Filed rather than fixed because the file belongs to another track.
