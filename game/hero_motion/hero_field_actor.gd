class_name HeroFieldActor
extends Node3D
## A hero's visible body in the field (M2-HER-1101, ADR 0190): the real model on top of a gameplay node
## (the FieldController, a CutsceneStage actor root, or a follower's anchor), moving like a body.
##
## The node it follows (`source`) keeps moving and turning the way it always did; the body copies its
## position each frame (feet on the node's origin, plus field.ground_offset_m) and turns on its own
## through HeroLocomotion: toward its travel while it moves, toward the node's facing while still, at
## most turn.max_rate_deg_per_sec, eased in and out. Only a teleport (a jump over gait.teleport_m in
## one frame) or snap() puts it on the node's yaw at once. The body is top_level, so the node's instant
## rotation never shows. The speed comes from the node's per-frame position delta, so cutscene moves
## (which set global_position) blend the gait too.
##
## Its AnimationTree (built in code, advanced manually by advance()):
##   loco    BlendSpace1D on the filtered ground speed: idle at 0, walk at walk_clip_mps, run at run_clip_mps
##   scale   TimeScale: HeroLocomotion.playback_scale (the run speeds up past its clip speed)
##   act_a / act_b  the one-shot or looping clip play_clip() asked for (two slots so clips cross-fade)
##   mode    Transition between scale, act_a and act_b
## play_clip(name, blend) is the cutscene entry point: a locomotion clip name (field.locomotion_clips)
## returns to the speed blend; any other clip plays over it, a one-shot returning to locomotion when it
## ends (unless `hold`), a loop staying until the next call. Clips started on the model's own
## AnimationPlayer (the sequencer's current path) are routed through play_clip too.
##
## Attach: HeroFieldActor.attach(controller) (one line in FieldController._ready) puts the party
## leader's body on the player, the bodies on the zone's CutsceneStage hero capsules and the followers
## (HeroFieldParty). Tuning: game/data/hero_motion/hero_motion.json "field".

const NAME := &"HeroBody"
const LOCO := &"scale"
const SLOT_A := &"act_a"
const SLOT_B := &"act_b"
const P_BLEND := &"parameters/loco/blend_position"
const P_SCALE := &"parameters/scale/scale"
const P_MODE := &"parameters/mode/transition_request"

static var _data_cache: Dictionary = {}

var hero_id: StringName = &""
## The gameplay node the body follows (never moved by the body).
var source: Node3D
var loco: HeroLocomotion
var model: Node3D
var anim: AnimationPlayer
var tree: AnimationTree
## The capsule visuals this body hid on its source.
var hidden_stand_ins: Array[Node3D] = []
## The clip play_clip() is showing (&"" while on locomotion).
var action: StringName = &""

var _field: Dictionary = {}
var _yaw_offset := 0.0
var _ground_offset := 0.0
var _last_pos := Vector3.ZERO
var _travel_yaw := 0.0
var _has_travel := false
var _slot: StringName = SLOT_B
var _action_left := 0.0
var _action_hold := false
var _transition: AnimationNodeTransition


## The hero_motion.json dictionary (read once).
static func data() -> Dictionary:
	if _data_cache.is_empty():
		_data_cache = HeroLocomotion.load_data()
	return _data_cache


static func field_data() -> Dictionary:
	return data().get("field", {}) as Dictionary


## The model scene for a hero id, or "" when the hero has no field body.
static func scene_path(id: StringName) -> String:
	var row := (field_data().get("heroes", {}) as Dictionary).get(String(id), {}) as Dictionary
	var path := str(row.get("scene", ""))
	return path if path != "" and ResourceLoader.exists(path) else ""


## The party leader's id: the first joined hero with a field body, else field.leader_default.
static func leader_id() -> StringName:
	for id: StringName in Game.state.party_ids:
		if scene_path(id) != "":
			return id
	return StringName(str(field_data().get("leader_default", "")))


## Puts the leader's body on `controller` (hiding its capsule), the bodies on the zone's stage hero
## capsules, and the followers. Idempotent; returns the body, or null when the model cannot load.
static func attach(controller: FieldController) -> HeroFieldActor:
	var body := controller.get_node_or_null(NodePath(String(NAME))) as HeroFieldActor
	if body == null:
		body = create(leader_id())
		if body == null:
			return null
		controller.add_child(body)
		body.bind(controller)
	if controller.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) == null:
		var party := HeroFieldParty.new()
		party.controller = controller
		party.leader = body
		controller.add_child(party)
	if controller.get_parent() != null:
		for stage in HeroFieldParty.find_scripted(controller.get_parent(), &"CutsceneStage"):
			attach_stage(stage as CutsceneStage)
	return body


## Gives every hero actor under `stage`/Actors that is still a capsule (no model of its own) a body.
static func attach_stage(stage: CutsceneStage) -> Array[HeroFieldActor]:
	var out: Array[HeroFieldActor] = []
	var folder := stage.get_node_or_null(CutsceneStage.ACTORS)
	if folder == null:
		return out
	for child in folder.get_children():
		var a := child as Node3D
		if a != null and not a is FieldController:
			var b := attach_actor(a, StringName(a.name))
			if b != null:
				out.append(b)
	return out


## A body on a cutscene actor root `actor` for hero `id`, or null when the hero has no body or the
## actor already shows a real model (an AnimationPlayer or a Skeleton3D under it). Idempotent.
static func attach_actor(actor: Node3D, id: StringName) -> HeroFieldActor:
	var existing := actor.get_node_or_null(NodePath(String(NAME))) as HeroFieldActor
	if existing != null:
		return existing
	if scene_path(id) == "":
		return null
	if not actor.find_children("*", "AnimationPlayer", true, false).is_empty():
		return null
	if not actor.find_children("*", "Skeleton3D", true, false).is_empty():
		return null
	var body := create(id)
	if body == null:
		return null
	actor.add_child(body)
	body.bind(actor)
	return body


## A body for hero `id` (not yet in the tree or bound), or null when its model cannot load.
static func create(id: StringName) -> HeroFieldActor:
	var path := scene_path(id)
	if path == "":
		return null
	var ps := load(path) as PackedScene
	if ps == null:
		return null
	var m := ps.instantiate() as Node3D
	if m == null:
		return null
	var body := HeroFieldActor.new()
	body.name = NAME
	body.hero_id = id
	body._setup(m)
	return body


func _setup(m: Node3D) -> void:
	_field = field_data()
	var d := data().duplicate(true)
	var gait := (d.get("gait", {}) as Dictionary).duplicate()
	var row := (_field.get("heroes", {}) as Dictionary).get(String(hero_id), {}) as Dictionary
	for k: String in ["walk_clip_mps", "run_clip_mps"]:
		if row.has(k):
			gait[k] = row[k]
	d["gait"] = gait
	loco = HeroLocomotion.new(d)
	_yaw_offset = deg_to_rad(float(_field.get("model_yaw_offset_deg", 0.0)))
	_ground_offset = float(_field.get("ground_offset_m", 0.0))
	top_level = true
	model = m
	model.name = &"Model"
	add_child(model)
	anim = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if anim != null:
		anim.stop()
		anim.active = false  # the tree animates; plays started on it are routed through play_clip
		_build_tree()
	HeroMotion.add_micro_motion(model, hero_id)  # M2-HER-1104: breathing, weight shift, the head leads turns


func _build_tree() -> void:
	var clips := _field.get("locomotion_clips", {}) as Dictionary
	var bs := AnimationNodeBlendSpace1D.new()
	bs.min_space = 0.0
	bs.max_space = maxf(loco.run_clip_mps, loco.walk_clip_mps)
	bs.add_blend_point(_clip_node(StringName(str(clips.get("idle", "")))), 0.0)
	bs.add_blend_point(_clip_node(StringName(str(clips.get("walk", "")))), loco.walk_clip_mps)
	bs.add_blend_point(_clip_node(StringName(str(clips.get("run", "")))), loco.run_clip_mps)
	var bt := AnimationNodeBlendTree.new()
	bt.add_node(&"loco", bs)
	bt.add_node(LOCO, AnimationNodeTimeScale.new())
	bt.connect_node(LOCO, 0, &"loco")
	bt.add_node(SLOT_A, AnimationNodeAnimation.new())
	bt.add_node(SLOT_B, AnimationNodeAnimation.new())
	_transition = AnimationNodeTransition.new()
	_transition.input_count = 3
	_transition.set_input_name(0, String(LOCO))
	_transition.set_input_name(1, String(SLOT_A))
	_transition.set_input_name(2, String(SLOT_B))
	_transition.xfade_time = float(_field.get("clip_blend_sec", 0.0))
	bt.add_node(&"mode", _transition)
	bt.connect_node(&"mode", 0, LOCO)
	bt.connect_node(&"mode", 1, SLOT_A)
	bt.connect_node(&"mode", 2, SLOT_B)
	bt.connect_node(&"output", 0, &"mode")
	tree = AnimationTree.new()
	tree.name = &"AnimationTree"
	for lib in anim.get_animation_library_list():
		tree.add_animation_library(lib, anim.get_animation_library(lib))
	tree.tree_root = bt
	tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	model.add_child(tree)
	tree.active = true


static func _clip_node(clip: StringName) -> AnimationNodeAnimation:
	var n := AnimationNodeAnimation.new()
	n.animation = clip
	return n


## Follows `node` from now on: hides its capsule visuals (field.standin_names, direct children) and
## puts the body on it at once.
func bind(node: Node3D) -> void:
	source = node
	var names: Array = _field.get("standin_names", [])
	for child in node.get_children():
		var vis := child as GeometryInstance3D
		if vis != null and vis.visible and String(vis.name) in names:
			vis.visible = false
			hidden_stand_ins.append(vis)
	snap()


## Puts the body on its source's position and facing with no turn or gait left (spawns, teleports).
func snap() -> void:
	if source == null or not is_instance_valid(source):
		return
	_last_pos = source.global_position if source.is_inside_tree() else source.position
	loco.reset_yaw(source_facing())
	loco.reset_speed(0.0)
	_has_travel = false
	_place(_last_pos)
	if tree != null:
		tree.set(P_BLEND, 0.0)
		tree.set(P_SCALE, 1.0)


## The source's facing yaw (FieldMotor convention: Basis(UP, yaw) * FORWARD).
func source_facing() -> float:
	if source is FieldController and (source as FieldController).motor != null:
		return (source as FieldController).motor.facing_yaw
	var b := source.global_basis if source.is_inside_tree() else source.basis
	return FieldMotor.yaw_of_basis(b)


## The yaw the body shows (FieldMotor convention).
func visible_yaw() -> float:
	return loco.yaw


func _process(delta: float) -> void:
	advance(delta)


## One frame: measure the source's travel, step the gait and the turn, place the body, run the tree.
func advance(delta: float) -> void:
	if source == null or not is_instance_valid(source) or delta <= 0.0:
		return
	var p := source.global_position if source.is_inside_tree() else source.position
	var step := p - _last_pos
	if loco.is_teleport(step.length()):
		snap()
		p = _last_pos
	else:
		var flat := Vector3(step.x, 0.0, step.z)
		loco.step_speed(flat.length() / delta, delta)
		if flat.length_squared() > 0.0:
			_travel_yaw = HeroLocomotion.yaw_of(flat)
			_has_travel = true
		var moving := _has_travel and loco.is_moving(loco.speed)
		loco.step_yaw(_travel_yaw if moving else source_facing(), delta)
		_last_pos = p
	HeroMotion.set_locomotion_speed(model, loco.speed)  # the micro-motion fades out while walking
	_place(p)
	_route_player_clip()
	if tree != null:
		tree.set(P_BLEND, loco.blend_position())
		tree.set(P_SCALE, loco.playback_scale(loco.speed))
		if action != &"" and not _action_hold and _action_left > 0.0:
			_action_left -= delta
			if _action_left <= 0.0:
				_to_locomotion(float(_field.get("clip_blend_sec", 0.0)))
		tree.advance(delta)


func _place(p: Vector3) -> void:
	var t := Transform3D(Basis(Vector3.UP, loco.yaw + _yaw_offset), p + Vector3.UP * _ground_offset)
	if is_inside_tree():
		global_transform = t
	else:
		transform = t


## Plays clip `clip_name` over the locomotion with a `blend` second cross-fade (negative: the data's
## clip_blend_sec). A locomotion clip returns to the speed blend. A one-shot returns to locomotion when
## it ends unless `hold` (it then keeps its last pose until the next call); a loop stays. Returns false
## when the model has no such clip.
func play_clip(clip_name: StringName, blend: float = -1.0, hold: bool = false) -> bool:
	if tree == null:
		return false
	var fade := blend if blend >= 0.0 else float(_field.get("clip_blend_sec", 0.0))
	if String(clip_name) in (_field.get("locomotion_clips", {}) as Dictionary).values():
		_to_locomotion(fade)
		return true
	if not tree.has_animation(clip_name):
		return false
	var an := tree.get_animation(clip_name)
	_slot = SLOT_A if _slot == SLOT_B else SLOT_B
	((tree.tree_root as AnimationNodeBlendTree).get_node(_slot) as AnimationNodeAnimation).animation = clip_name
	_transition.xfade_time = fade
	tree.set(P_MODE, String(_slot))
	action = clip_name
	_action_hold = hold or an.loop_mode != Animation.LOOP_NONE
	_action_left = an.length
	return true


func _to_locomotion(fade: float) -> void:
	action = &""
	_action_left = 0.0
	if _transition != null:
		_transition.xfade_time = fade
		tree.set(P_MODE, String(LOCO))


## The sequencer still plays clips on the first AnimationPlayer under an actor; route those through
## play_clip so the tree (not a second mixer) shows them.
func _route_player_clip() -> void:
	if anim == null or not anim.is_playing():
		return
	var clip := StringName(anim.current_animation)
	anim.stop()
	if clip != &"":
		play_clip(clip)


## The locomotion weights the tree is blending now (idle, walk, run), for tests and debugging.
func gait_weights() -> PackedFloat32Array:
	return loco.weights(loco.blend_position())
