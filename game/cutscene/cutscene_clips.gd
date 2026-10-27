class_name CutsceneClips
extends RefCounted
## Which clip a cutscene @anim actually plays (M2-FP-103), out of CutsceneSequencer (gdlint's file cap).


## `clip`, or the built clip `config` clip_stand_ins names for "<id>/<clip>" while the actor's rig lacks it
## (a requested clip on Character's list); the real clip plays once it is built.
static func built(config: Dictionary, id: StringName, actor: Node3D, clip: StringName) -> StringName:
	var stand_in := str((config.get("clip_stand_ins", {}) as Dictionary).get("%s/%s" % [id, clip], ""))
	if stand_in == "" or has_clip(actor, clip):
		return clip
	return StringName(stand_in)


## True when the actor's hero body (its AnimationTree) or its AnimationPlayer carries `clip`.
static func has_clip(actor: Node3D, clip: StringName) -> bool:
	var body := HeroMotion.body_of(actor)
	var tree := body.get(&"tree") as AnimationMixer if body != null else null
	if tree != null:
		return tree.has_animation(clip)
	var ap := HeroMotion.player_of(actor)
	return ap != null and ap.has_animation(clip)
