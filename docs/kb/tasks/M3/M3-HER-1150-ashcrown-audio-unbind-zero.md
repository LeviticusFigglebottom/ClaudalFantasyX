---
id: M3-HER-1150
title: "AshcrownAudio._connect calls unbind(0) (an engine error on every Ashcrown entry); FootstepAudio casts a freed mesh before checking it"
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

## Also: FootstepAudio.mesh_surface_at casts before it checks (the human's "Trying to cast a freed object")
`game/audio/footstep_audio.gd:590`: `var mi := c[0] as MeshInstance3D` comes before `is_instance_valid(mi)`. A
surface candidate freed while it's still listed (a zone torn down by the router's swap into a fight, a despawned
prop) is a script error on the cast. Check `c[0]` first: `if not is_instance_valid(c[0]): continue`, then cast.
`tools/freed_cast_lint.py` lists this hit under this task. Drop its KNOWN row when it's fixed.

- [ ] footstep_audio.gd checks `c[0]` before the cast, and freed_cast_lint's KNOWN row for it is removed.

## Notes
Owner: Audio (`game/audio/**`, ownership.md). Filed rather than fixed because the file belongs to another track.

## Review log
