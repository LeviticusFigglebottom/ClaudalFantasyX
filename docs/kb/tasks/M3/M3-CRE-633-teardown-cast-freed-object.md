---
id: M3-CRE-633
title: "Gate fix: 'Trying to cast a freed object' at capture shutdown (LifeAudio.advance; VillagerLayer's latent same)"
role: audio
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: creatures
---
## Goal
The big11 PC gate (lead/gate-big11 @ 23ea8c6f) ends both capture shards with exit 1 on "SCRIPT ERROR: Trying to
cast a freed object". Reproduced headless on that tree with capture.gd's lifecycle (instance, 20 frames,
queue_free, next shot): **64 errors, every one at `LifeAudio.advance` (game/audio/life_audio.gd:86 on big11; line
124 on claude/audio's M3-AUD-826)**. They start in the shot after a zone with villagers or wildlife is freed.
`var node := w["node"] as Node3D` casts a freed object before the `is_instance_valid` check on the next line.

## The fix (audio's file): check as a Variant first, then cast
```gdscript
	for i in range(watched.size() - 1, -1, -1):
		var w := watched[i]
		var raw: Variant = w["node"]
		if not is_instance_valid(raw) or not (raw as Node).is_inside_tree():
			var steps: Variant = w.get("steps")
			if is_instance_valid(steps):
				(steps as Node).queue_free()
			watched.remove_at(i)
			continue
		var node := raw as Node3D
```
(On claude/audio, `(w["steps"] as Node).queue_free()` casts too: the footstep node is the villager's child and is
freed with it.) Do the same for any other `as` cast on a node held across frames (`birds`, `crabs`: the
`(birds as Array)[b] as Object` lines are fine only while the layer lives).

## Acceptance criteria
- [ ] LifeAudio checks every held node as a Variant before casting
- [ ] A unit test that watches a FieldNpc (or any hooked Node3D), frees it, then calls `advance`; tests/run_tests.gd
      fails a test on any script error (tests/error_counter.gd), so it is red before the fix
- [ ] The PC re-runs the capture shards with exit 0

## Done on the creatures side (commit 'M3-CRE-633: VillagerLayer and FieldNpc survive ...')
VillagerLayer had the same latent pattern (a typed loop over freed keys); fixed, with a test that is red on the old
code with exactly this error.
