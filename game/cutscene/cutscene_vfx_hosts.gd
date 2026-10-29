class_name CutsceneVfxHosts
extends RefCounted
## The stage VFX hosts an `@vfx` cue is offered to first (M3-ARC-1326, env-art-b's request for Ch9's Ebbing): every
## node in GROUP with a METHOD(effect: String, at_id: StringName, kwargs: Dictionary) -> bool. The first that takes
## the cue (returns true) plays it, and the sequencer spawns no CutsceneMotes placeholder; when none does, the
## placeholder draws as before. EbbingMotes (game/vfx/ebbing) is one: it takes a `glimmer_held` cue whose mark has a
## field row. The cue's kwargs reach the host whole, among them cues.json's `follow` (an attractor on that actor) and
## `anchors` (grief anchors on an actor group), which hosts read and the placeholder ignores.

const GROUP := &"cutscene_vfx_hosts"
const METHOD := &"play_vfx"


## Offers the cue to `tree`'s hosts; true when one took it.
static func offer(tree: SceneTree, effect: String, at_id: StringName, kwargs: Dictionary) -> bool:
	if tree == null:
		return false
	for host in tree.get_nodes_in_group(GROUP):
		if host.has_method(METHOD) and bool(host.call(METHOD, effect, at_id, kwargs)):
			return true
	return false
