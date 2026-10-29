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
##   mode    Transition between scale, act_a and act_b (each slot through its own TimeScale, ts_a / ts_b)
## Gait clips (M2-HER-1107, HeroGaitClips): when the model has M2-CHR-12's walk/run starts and stops, turns
## in place and idle variant (and game/data/characters/locomotion.json has their root curves), they play in
## the action slots over the blend: starts and stops by the ground covered, turns driving the visible yaw.
## The gait speeds then come from locomotion.json too (gait_speeds()). Without them nothing changes.
## play_clip(name, blend) is the cutscene entry point: a locomotion clip name (field.locomotion_clips)
## returns to the speed blend; any other clip plays over it, a one-shot returning to locomotion when it
## ends (unless `hold`), a loop staying until the next call. Clips started on the model's own
## AnimationPlayer (the sequencer's current path) are routed through play_clip too.
##
## Attach: HeroFieldActor.attach(controller) (one line in FieldController._ready) puts the party
## leader's body on the player, the bodies on the zone's CutsceneStage hero capsules and the followers
## (HeroFieldParty). Tuning: game/data/hero_motion/hero_motion.json "field".

## A foot touched down in the clip the body shows (&"l" / &"r"), from the clips' footfall markers; `run` when the
## clip is a run (field.foot_contacts.run_clips). Audio's footsteps listen to it (M3-AUD-810).
signal foot_contact(foot: StringName, run: bool)

const NAME := &"HeroBody"
const LOCO := &"scale"
const SLOT_A := &"act_a"
const SLOT_B := &"act_b"
const P_BLEND := &"parameters/loco/blend_position"
const P_SCALE := &"parameters/scale/scale"
const P_MODE := &"parameters/mode/transition_request"
const SCALE_A := &"ts_a"
const SCALE_B := &"ts_b"

static var _data_cache: Dictionary = {}
static var _loco_cache: Dictionary = {}
static var _loco_read := false

var hero_id: StringName = &""
## The gameplay node the body follows (never moved by the body).
var source: Node3D
var loco: HeroLocomotion
var model: Node3D
var anim: AnimationPlayer
var tree: AnimationTree
## The capsule visuals this body hid on its source.
var hidden_stand_ins: Array[Node3D] = []
## The source's props this body carries on a bone (field.heroes.<id>.carry), e.g. Haluna's LanternLight.
var carried: Array[Node3D] = []
## The clip play_clip() is showing (&"" while on locomotion).
var action: StringName = &""
## The starts, stops, turns and idle variant (null when the model has no AnimationPlayer).
var gait: HeroGaitClips
## Footfall tracking for foot_contact.
var contacts: HeroFootContacts

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


## The characters track's locomotion.json (M2-CHR-12; field.gait_clips.locomotion_data), or {} while it
## is not in this tree. Read once.
static func locomotion_data() -> Dictionary:
	if not _loco_read:
		var cfg := field_data().get("gait_clips", {}) as Dictionary
		_loco_cache = HeroGaitClips.load_locomotion(str(cfg.get("locomotion_data", "")))
		_loco_read = true
	return _loco_cache


## Hero `id`'s table in locomotion.json ({} when there is none).
static func locomotion_of(id: StringName) -> Dictionary:
	return (locomotion_data().get("heroes", {}) as Dictionary).get(String(id), {}) as Dictionary


## The ground speeds (m/s) at which hero `id`'s walk and run plant their feet: locomotion.json's
## speed_mps when it has them (source "locomotion"), else hero_motion.json field.heroes (source
## "hero_motion", measured from the clips before M2-CHR-12). {walk_clip_mps, run_clip_mps, source}.
static func gait_speeds(id: StringName) -> Dictionary:
	return gait_speeds_from(id, locomotion_of(id))


## gait_speeds() for hero `id` with `loco_row` as its locomotion.json table (tests inject one).
static func gait_speeds_from(id: StringName, loco_row: Dictionary) -> Dictionary:
	var row := (field_data().get("heroes", {}) as Dictionary).get(String(id), {}) as Dictionary
	var gait := data().get("gait", {}) as Dictionary
	var out := {
		"walk_clip_mps": float(row.get("walk_clip_mps", gait.get("walk_clip_mps", 0.0))),
		"run_clip_mps": float(row.get("run_clip_mps", gait.get("run_clip_mps", 0.0))),
		"source": "hero_motion",
	}
	var walk := float((loco_row.get("walk", {}) as Dictionary).get("speed_mps", 0.0))
	var run := float((loco_row.get("run", {}) as Dictionary).get("speed_mps", 0.0))
	if walk > 0.0 and run > walk:
		out["walk_clip_mps"] = walk
		out["run_clip_mps"] = run
		out["source"] = "locomotion"
	return out


## HeroClipGait's measure settings for the clips gait_speeds() describes: field.gait_measure, with its
## `planted_ball` block over it for M2-CHR-12's clips (they pivot the planted foot on its ball, so the
## ball, not the ankle, holds still on the ground).
static func measure_config(id: StringName) -> Dictionary:
	var cfg := (field_data().get("gait_measure", {}) as Dictionary).duplicate()
	if str(gait_speeds(id)["source"]) == "locomotion":
		cfg.merge(cfg.get("planted_ball", {}) as Dictionary, true)
	return cfg


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
	if controller.get_node_or_null(NodePath(String(HeroStairs.NAME))) == null:  # M3-ARC-1216: steep flights
		var stairs := HeroStairs.new()
		stairs.controller = controller
		controller.add_child(stairs)
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
			var b := attach_actor(a, hero_of(StringName(a.name)))
			if b != null:
				out.append(b)
	return out


## The hero a stage actor plays: its node name when that is a hero id, else field.actor_aliases[name], else the name
## with a field.actor_prefixes prefix stripped (vigil_asha -> asha). &"" when it plays no hero.
static func hero_of(actor_name: StringName) -> StringName:
	var name := String(actor_name)
	if (field_data().get("heroes", {}) as Dictionary).has(name):
		return actor_name
	var alias := str((field_data().get("actor_aliases", {}) as Dictionary).get(name, ""))
	if alias != "":
		return StringName(alias)
	for prefix: Variant in field_data().get("actor_prefixes", []):
		if name.begins_with(str(prefix)):
			return StringName(name.trim_prefix(str(prefix)))
	return actor_name


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
	var gait_row := (d.get("gait", {}) as Dictionary).duplicate()
	var speeds := gait_speeds(hero_id)
	for k: String in ["walk_clip_mps", "run_clip_mps"]:
		gait_row[k] = speeds[k]
	d["gait"] = gait_row
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
		gait = HeroGaitClips.new(
			_field.get("gait_clips", {}) as Dictionary,
			locomotion_of(hero_id),
			tree.has_animation,
			float(locomotion_data().get("fps", 0.0)),
			loco.walk_clip_mps,
			loco.run_clip_mps,
			hero_id
		)
		contacts = HeroFootContacts.new(_field.get("foot_contacts", {}) as Dictionary)
	HeroMotion.add_micro_motion(model, hero_id)  # M2-HER-1104: breathing, weight shift, the head leads turns
	HeroMotion.add_foot_ik(model)  # M2-HER-1116: feet on slopes and steps, after the micro-motion


## The clips this body's locomotion plays for idle, walk and run: field.locomotion_clips, under the hero row's own
## `clips` (Sefir's walk and run are his walk_glide: he has no stepping walk, M3-HER-1225).
func locomotion_clips() -> Dictionary:
	return HeroFieldActor.clips_of(hero_id)


## locomotion_clips() for hero `id`, without a body (the clip-speed tests measure what the body will play).
static func clips_of(id: StringName) -> Dictionary:
	var f := field_data()
	var clips := (f.get("locomotion_clips", {}) as Dictionary).duplicate()
	var row := (f.get("heroes", {}) as Dictionary).get(String(id), {}) as Dictionary
	clips.merge(row.get("clips", {}) as Dictionary, true)
	return clips


func _build_tree() -> void:
	var clips := locomotion_clips()
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
	bt.add_node(SCALE_A, AnimationNodeTimeScale.new())
	bt.add_node(SCALE_B, AnimationNodeTimeScale.new())
	bt.connect_node(SCALE_A, 0, SLOT_A)
	bt.connect_node(SCALE_B, 0, SLOT_B)
	_transition = AnimationNodeTransition.new()
	_transition.input_count = 3
	_transition.set_input_name(0, String(LOCO))
	_transition.set_input_name(1, String(SLOT_A))
	_transition.set_input_name(2, String(SLOT_B))
	_transition.xfade_time = float(_field.get("clip_blend_sec", 0.0))
	bt.add_node(&"mode", _transition)
	bt.connect_node(&"mode", 0, LOCO)
	bt.connect_node(&"mode", 1, SCALE_A)
	bt.connect_node(&"mode", 2, SCALE_B)
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
	var ik := HeroMotion.foot_ik_of(model) if model != null else null
	if ik != null and node is CollisionObject3D:
		ik.exclude = [(node as CollisionObject3D).get_rid()] as Array[RID]  # its own capsule is not the floor
	var names: Array = _field.get("standin_names", [])
	for child in node.get_children():
		var vis := child as GeometryInstance3D
		if vis != null and vis.visible and String(vis.name) in names:
			vis.visible = false
			hidden_stand_ins.append(vis)
	_carry.call_deferred()
	snap()


## Moves the source's props named in field.heroes.<id>.carry onto the model: each hangs from `bone` at
## the model-space point `at_model` (where the prop sits on the hero, e.g. Rhen's lantern glass), so it
## turns with the eased body instead of the node's instant yaw. Missing props or bones are skipped.
func _carry() -> void:
	if source == null or not is_instance_valid(source) or model == null:
		return
	var skel := HeroMotion.skeleton_of(model)
	var row := (_field.get("heroes", {}) as Dictionary).get(String(hero_id), {}) as Dictionary
	for spec: Dictionary in row.get("carry", []):
		var prop := source.get_node_or_null(NodePath(str(spec.get("name", "")))) as Node3D
		var bone := skel.find_bone(str(spec.get("bone", ""))) if skel != null else -1
		if prop == null or bone < 0:
			continue
		var at: Array = spec.get("at_model", [0.0, 0.0, 0.0])
		var hook := BoneAttachment3D.new()
		hook.name = "Carry_%s" % prop.name
		hook.bone_name = skel.get_bone_name(bone)
		skel.add_child(hook)
		prop.reparent(hook, false)
		var point := Vector3(float(at[0]), float(at[1]), float(at[2]))
		prop.transform = Transform3D(Basis.IDENTITY, skel.get_bone_global_rest(bone).affine_inverse() * point)
		carried.append(prop)


## Puts the body on its source's position and facing with no turn or gait left (spawns, teleports).
func snap() -> void:
	if source == null or not is_instance_valid(source):
		return
	_last_pos = source.global_position if source.is_inside_tree() else source.position
	loco.reset_yaw(source_facing())
	loco.reset_speed(0.0)
	_has_travel = false
	if gait != null:
		if gait.clip != &"" and action == &"":
			_to_locomotion(0.0)
		gait.reset()
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
		if gait != null:
			_step_gait(flat.length(), delta)
		if gait != null and gait.phase == HeroGaitClips.Phase.TURN:
			_turn_toward(gait.turn_yaw(), delta)
		else:
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
		_emit_contacts()


## Steps the gait clips from this frame's travel and shows what they pick (a cutscene clip holds them).
func _step_gait(dist: float, delta: float) -> void:
	if action != &"" or tree == null:
		gait.reset(loco.speed)
		return
	var shown := gait.clip
	var heading := angle_difference(loco.yaw, _travel_yaw) if _has_travel else 0.0
	var facing := angle_difference(loco.yaw, source_facing())
	gait.step(loco.yaw, loco.speed, dist, heading, facing, _intent_mps(), _stop_dist_m(), delta)
	if gait.clip != shown:
		if gait.clip != &"":
			_show_slot(gait.clip, gait.blend_sec)
		else:
			_to_locomotion(gait.blend_sec)
	if gait.clip != &"":
		tree.set(_scale_param(_slot), gait.time_scale)


## One capped step of the visible yaw toward `want` (a turn clip's curve): never over max_rate.
func _turn_toward(want: float, delta: float) -> void:
	var cap := loco.max_rate_rad * delta
	var d := clampf(angle_difference(loco.yaw, want), -cap, cap)
	loco.yaw = wrapf(loco.yaw + d, -PI, PI)
	loco.yaw_rate = d / delta


## The speed the source is heading for (m/s): a FieldController's stick (as FieldMotor.step reads it),
## 0 while it coasts to a stop, -1 when the source cannot tell (followers, cutscene roots, a scripted move).
func _intent_mps() -> float:
	var c := source as FieldController
	if c == null or c.motor == null:
		return -1.0
	var stick := c.current_stick()
	var mag := minf(stick.length(), 1.0)
	if mag <= c.motor.deadzone:
		return 0.0 if c.motor.velocity.length_squared() > 0.0 else -1.0
	var walk := c.walk_override or mag < c.motor.walk_run_threshold
	walk = walk or (c.accepts_input and Input.is_action_pressed(FieldInput.WALK))
	return c.motor.walk_speed if walk else c.motor.run_speed


## The distance a FieldController needs to stop from its speed at its deceleration, or -1.
func _stop_dist_m() -> float:
	var c := source as FieldController
	if c == null or c.motor == null or c.motor.deceleration <= 0.0:
		return -1.0
	var v := Vector2(c.motor.velocity.x, c.motor.velocity.z).length()
	return v * v / (2.0 * c.motor.deceleration)


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
	if String(clip_name) in locomotion_clips().values():
		if action == &"" and gait != null and gait.clip != &"":
			return true  # a start, stop or turn is the locomotion already: let it finish
		_to_locomotion(fade)
		return true
	if not tree.has_animation(clip_name):
		return false
	var an := tree.get_animation(clip_name)
	if gait != null:
		gait.reset(loco.speed)
	_show_slot(clip_name, fade)
	tree.set(_scale_param(_slot), 1.0)
	action = clip_name
	_action_hold = hold or an.loop_mode != Animation.LOOP_NONE
	_action_left = an.length
	return true


## Shows `clip_name` in the free action slot with a `fade` second cross-fade.
func _show_slot(clip_name: StringName, fade: float) -> void:
	_slot = SLOT_A if _slot == SLOT_B else SLOT_B
	((tree.tree_root as AnimationNodeBlendTree).get_node(_slot) as AnimationNodeAnimation).animation = clip_name
	_transition.xfade_time = fade
	tree.set(P_MODE, String(_slot))


static func _scale_param(slot: StringName) -> StringName:
	return StringName("parameters/%s/scale" % (SCALE_A if slot == SLOT_A else SCALE_B))


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


## Emits foot_contact for every footfall marker the live clip crossed this frame: the action slot when one shows,
## else the locomotion point with the most weight.
func _emit_contacts() -> void:
	if contacts == null:
		return
	var state := StringName(str(tree.get(&"parameters/mode/current_state")))
	var clip := &""
	var node := &""
	if state == SLOT_A or state == SLOT_B:
		node = state
		clip = ((tree.tree_root as AnimationNodeBlendTree).get_node(state) as AnimationNodeAnimation).animation
	else:
		var w := gait_weights()
		var idx := 0
		for i in w.size():
			if w[i] > w[idx]:
				idx = i
		var names := [&"idle", &"walk", &"run"]
		clip = StringName(str(locomotion_clips().get(String(names[idx]), "")))
		node = StringName("loco/%d" % idx)
	if clip == &"" or not tree.has_animation(clip):
		return
	var pos := float(tree.get(StringName("parameters/%s/current_position" % node)))
	for foot in contacts.step(clip, tree.get_animation(clip), pos):
		foot_contact.emit(foot, contacts.is_run(clip))


## The locomotion weights the tree is blending now (idle, walk, run), for tests and debugging.
func gait_weights() -> PackedFloat32Array:
	return loco.weights(loco.blend_position())
