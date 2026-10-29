---
id: M3-AUD-101
title: "Request (slice-polish): LifeAudio.advance casts a freed villager before checking it (a script error per scene exit)"
role: audio
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
reviewer: cinematics
---
## Goal
Self-rendering the slice (TRACK-RULES 01:00), every Haluna and Ch1 capture logs `SCRIPT ERROR: Trying to cast a freed
object. at: LifeAudio.advance (res://game/audio/life_audio.gd:124)` as the process exits. The shots affected are
the beach pair, dock night, the Oruvel shots and the Underway. The line is `var node := w["node"] as Node3D`, which
casts before line 125's `is_instance_valid(node)` check, so a villager freed while it is still watched (zone teardown,
or any despawn) errors on the cast. Players never see it, but ADR 0041 asks for clean logs, and the capture gate
reads them.

## Acceptance criteria
- [ ] Check the raw value first, for example `var raw: Variant = w["node"]` and
      `if not is_instance_valid(raw) or not (raw as Node3D).is_inside_tree():`, and cast after that.
- [ ] A unit test: watch a FieldNpc, free it, call `advance()`, and no error is logged and the row is dropped.

## Review log
