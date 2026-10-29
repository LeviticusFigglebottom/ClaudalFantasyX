---
id: M3-ARC-1326
title: "Request: the sequencer offers `@vfx` cues to stage VFX hosts first (Ch9's Ebbing), and the cue vocabulary for following and anchors"
role: architect
status: todo
owner_session: ""
depends_on: [M3-C09-03]
milestone: M3
request-from: rendering (env-art-b), for M3-C09-03 (act1_ch09.md §9 item 9)
---
## Goal
M3-C09-03's real Ebbing is `EbbingMotes` (`game/vfx/ebbing/ebbing_motes.gd`, data `game/data/vfx/ebbing.json`, docs
`docs/kb/tech/ebbing.md`). `ch09/corrow_night`'s dressing places it, in the group `cutscene_vfx_hosts`. Today
`CutsceneSequencer._cue_vfx` always spawns the CutsceneMotes placeholder, so the chapter's eight `@vfx glimmer_held
at=<mark>` cues never reach the real fields. `game/cutscene/**` is Systems' and the Architect's, and integration-qa
holds that seat now, so this is a request.

### 1. The hook (the one change needed for the cues to play the real thing)
At the top of `_cue_vfx`, before the placeholder:

```gdscript
for host in get_tree().get_nodes_in_group(&"cutscene_vfx_hosts"):
	if host.has_method(&"play_vfx") and host.play_vfx(effect, at_id, step.kwargs):
		return
```

`EbbingMotes.play_vfx(effect: String, at_id: StringName, kwargs: Dictionary) -> bool` takes a `glimmer_held` cue
whose mark has a field row and returns true. It returns false for anything else, so every other zone and cue keeps
the placeholder. No `.dlg` changes are needed. The fields' rows already say which follow the staff and which hold to
the mourners, so the current cues play the full Ebbing as they stand.

### 2. The vocabulary (item 9: a joint answer with Cinematics)
EbbingMotes already passes `kwargs` through. Two kwargs would let other scenes say what the Ebbing's rows say:
- `follow=<actor>_staff` (or `follow=<actor>`): one attractor on that body, for a held or released field.
- `anchors=<actor group>` (for example `anchors=mourners`): grief anchors that let go as the follow-host passes.

Proposal: accept both in `cues.json`'s `vfx` kwargs (the dlgc validator). Hosts read them; the placeholder ignores
them. Until then, EbbingMotes's data rows answer for Ch9.

## Acceptance criteria
- [ ] The hook in `_cue_vfx`, with a unit test: a host that takes a cue means no CutsceneMotes is spawned; a host that
      declines means the placeholder still draws.
- [ ] `tests/integration/test_ch09_thread.gd` stays green.
- [ ] The vocabulary decision is written in this file (accept, amend or decline).

## Review log
