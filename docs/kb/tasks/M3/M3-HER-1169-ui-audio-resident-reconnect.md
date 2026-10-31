---
id: M3-HER-1169
title: "Request (audio): UiAudio re-connects a resident zone's nodes after a fight (\"Signal 'used' is already connected\")"
role: audio
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: tech
---
## Goal
SceneRouter keeps the field zone resident through a random fight and re-attaches the same instance (the battle-return
fix, ADR 0205). When it re-enters the tree, `node_added` fires again for every node. `AudioDirector._on_node_added`
then calls `UiAudio.watch` on nodes UiAudio dropped from `watched` when they left, and `watch()` connects the same bound
`request` callable a second time. Each watched node (an interactable's `used`) logs:

    ERROR: Signal 'used' is already connected to given callable 'Node(UiAudio)::request' in that object.
       [0] watch (res://game/audio/ui_audio.gd:90)  [1] _call_if_alive (res://game/audio/audio_director.gd:614)

Repro: `godot --headless --path . res://game/core/debug/scene_swap_probe.tscn -- --encounter=ch03_causeway_shore
--return=res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn`, which logs 6 of these.

## Proposed fix (tested by hero-integration, not committed: game/audio/** is audio's)
Skip a connection that's already there. With it, the repro logs 0, and `--filter=audio` passes 185/0.

```diff
-		if argc >= 0:
-			node.connect(StringName(sig), play.unbind(argc) if argc > 0 else play)
-	if hook.has("on_exit"):
-		node.tree_exiting.connect(request.bind(StringName(str(hook["on_exit"]))))
+		var call := play.unbind(argc) if argc > 0 else play
+		if argc >= 0 and not node.is_connected(StringName(sig), call):
+			node.connect(StringName(sig), call)
+	var leave := request.bind(StringName(str(hook.get("on_exit", ""))))
+	if hook.has("on_exit") and not node.tree_exiting.is_connected(leave):
+		node.tree_exiting.connect(leave)
```

## Acceptance criteria
- [ ] The repro above logs no "already connected" error.
- [ ] A re-attached node's UI sounds still play once per use (not twice).
- [ ] `--filter=audio` stays green.

## Review log
