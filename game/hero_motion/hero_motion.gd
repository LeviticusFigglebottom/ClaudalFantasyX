class_name HeroMotion
extends RefCounted
## The cutscene side of the hero motion layer (M2-HER-1104, ADR 0190; docs/kb/tech/hero_motion.md): one
## static entry point the CutsceneSequencer (or any host) calls on a stage actor, whatever body it has.
##
## The sequencer keeps the motion maths (CutsceneMotion: the eased turn and the walk's ramps) and moves
## and turns the actor ROOT. This layer only reaches the body under it:
##   play(actor, clip, blend)          a body with play_clip(clip, blend) -> bool (HeroFieldActor's
##                                     AnimationTree) plays it; else the actor's AnimationPlayer
##                                     cross-fades to it. False when nobody has the clip.
##   set_locomotion_speed(actor, mps)  forwards the root's ground speed to a body with
##                                     set_locomotion_speed (a speed-driven gait blend follows the walk's
##                                     ramps) and fades the idle micro-motion out while it moves.
##   add_micro_motion(actor, id)       breathing, a weight shift and a head that leads the body's turns
##                                     (HeroIdleMicro), under the actor's Skeleton3D. Null without one.
## Everything is duck-typed (has_method), so no body class is required.

const BODY_PLAY := &"play_clip"
const BODY_SPEED := &"set_locomotion_speed"
const MICRO_NAME := &"HeroIdleMicro"
const PLAYER_NAME := &"AnimationPlayer"
## How deep under the actor a body node is looked for (actor -> body -> its own children).
const BODY_SEARCH_DEPTH := 2


## The node that plays clips for `actor`: the actor itself or a descendant (two levels down) with
## play_clip(clip, blend). Null when the actor has no such body.
static func body_of(actor: Node) -> Node:
	if actor == null or not is_instance_valid(actor):
		return null
	return _find_method(actor, BODY_PLAY, BODY_SEARCH_DEPTH)


static func _find_method(node: Node, method: StringName, depth: int) -> Node:
	if node.has_method(method):
		return node
	if depth <= 0:
		return null
	for child: Node in node.get_children():
		var found := _find_method(child, method, depth - 1)
		if found != null:
			return found
	return null


## Plays `clip` on the actor's body, cross-fading over `blend_sec` (< 0: the player's default blend).
## `restart` false leaves a clip that is already playing alone (the fallback path; a body decides for
## itself). Returns false when neither a body nor an AnimationPlayer has the clip.
static func play(actor: Node3D, clip: StringName, blend_sec: float = -1.0, restart: bool = true) -> bool:
	if actor == null or not is_instance_valid(actor) or clip == &"":
		return false
	var body := body_of(actor)
	if body != null:
		return bool(body.call(BODY_PLAY, clip, blend_sec))
	var ap := player_of(actor)
	if ap == null or not ap.has_animation(clip):
		return false
	if not restart and ap.current_animation == clip and ap.is_playing():
		return true
	ap.play(clip, blend_sec)
	return true


## The first AnimationPlayer under the actor (the hero glTF import rule puts one at the asset root).
static func player_of(actor: Node) -> AnimationPlayer:
	if actor == null or not is_instance_valid(actor):
		return null
	return actor.find_child(PLAYER_NAME, true, false) as AnimationPlayer


## Tells the body how fast its root moves over the ground (m/s): a body with set_locomotion_speed
## blends its gait by it, and the idle micro-motion fades out while it moves.
static func set_locomotion_speed(actor: Node3D, mps: float) -> void:
	if actor == null or not is_instance_valid(actor):
		return
	var body := _find_method(actor, BODY_SPEED, BODY_SEARCH_DEPTH)
	if body != null:
		body.call(BODY_SPEED, mps)
	var micro := micro_of(actor)
	if micro != null:
		micro.amount = 0.0 if mps > float(micro.data.get("still_below_mps", 0.0)) else 1.0


## Sets the idle micro-motion's target strength (1 standing, 0 walking); it eases there by itself.
static func set_idle_amount(actor: Node3D, amount: float) -> void:
	var micro := micro_of(actor)
	if micro != null:
		micro.amount = clampf(amount, 0.0, 1.0)


## The first Skeleton3D under the actor, or null.
static func skeleton_of(actor: Node) -> Skeleton3D:
	if actor == null or not is_instance_valid(actor):
		return null
	if actor is Skeleton3D:
		return actor as Skeleton3D
	var found := actor.find_children("*", "Skeleton3D", true, false)
	return null if found.is_empty() else found[0] as Skeleton3D


## The actor's idle micro-motion modifier, or null.
static func micro_of(actor: Node) -> HeroIdleMicro:
	var skel := skeleton_of(actor)
	return null if skel == null else skel.get_node_or_null(NodePath(String(MICRO_NAME))) as HeroIdleMicro


## Adds breathing, the weight shift and the head lead to the actor's skeleton (once; a second call
## returns the same modifier). `actor_id` seeds its phases (default: the actor's node name). Returns
## null, changing nothing, when the actor has no Skeleton3D (a capsule stand-in).
static func add_micro_motion(actor: Node3D, actor_id: StringName = &"") -> HeroIdleMicro:
	var skel := skeleton_of(actor)
	if skel == null:
		return null
	var existing := micro_of(actor)
	if existing != null:
		return existing
	var micro := HeroIdleMicro.new(actor_id if actor_id != &"" else StringName(actor.name))
	micro.name = MICRO_NAME
	skel.add_child(micro)
	return micro
