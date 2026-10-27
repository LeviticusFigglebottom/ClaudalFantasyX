class_name FieldNpc
extends Node3D
## A villager alive in the field (M3-CRE-610; docs/kb/tech/field_npc.md). Put one in a zone with the
## villager's actor scene as its child `Actor` (or set `actor_scene`), an optional `Interactable` child it
## listens to, and an optional `Route` child of Marker3D points. It then:
##   idles     `idle` loops from a per-villager phase (a hash of npc_id), so two villagers never move in
##             step, with HeroIdleMicro's breathing, weight shift and head lead on top;
##   talks     when its Interactable is used or begin_talk(player) is called: it turns to the player with
##             HeroLocomotion.step_yaw (eased, rate-capped, never snapping) and cross-fades to `talk`;
##             end_talk() (or a DialogueRunner's `finished`, see follow_dialogue, or the player walking
##             off past release_radius_m) returns it to idle and, after return_delay_sec, eases it back
##             to its resting heading or on along its route;
##   walks     a route of points at a slow pace: HeroLocomotion.step_speed filters the ground speed and
##             its gait weights pick idle or walk (cross-faded, the walk's playback following the speed
##             so the feet keep planting), eased turns at the corners, a pause at each point, loop or
##             ping-pong. It stops when the player comes within stop_radius_m or talks to it.
## The node itself moves and turns (its Interactable comes along); the actor faces the node's -Z.
## Ground: the route's own Y (linear between points); villagers have no physics body.
## Tuning: game/data/world/npc/npc.json (defaults plus per-villager overrides). Deterministic: no
## randomness, and the state only advances by tick(delta).

signal talk_started(player: Node3D)
signal talk_ended
signal point_reached(index: int)

enum Mode { REST, WALK, PAUSE, TALK, AFTER_TALK }

const DATA_PATH := "res://game/data/world/npc/npc.json"
const ACTOR_NAME := &"Actor"
const ROUTE_LOOP := "loop"
const ROUTE_PING_PONG := "ping_pong"
## A Marker3D in the route can carry its own pause (seconds) as this metadata.
const META_PAUSE := &"pause_sec"
## Hash salt for the idle clip's phase (HeroIdleMicro.share).
const SALT_IDLE := "idle_clip"
const CLIP_IDLE := &"idle"
const CLIP_TALK := &"talk"
const CLIP_WALK := &"walk"

## Which villager this is (its tuning row and its phases). Empty: the node name in snake_case.
@export var npc_id: StringName = &""
## Instanced as the `Actor` child when the node has none.
@export var actor_scene: PackedScene
@export var actor_path: NodePath = ^"Actor"
@export var interactable_path: NodePath = ^"Interactable"
## The player. Empty: the first FieldController in the current scene (looked up once).
@export var player_path: NodePath
## A Node3D whose Marker3D children are the route (read once at _ready, in world space).
@export var route_path: NodePath = ^"Route"
## The route in the parent's space, used when there is no Route node.
@export var route_points: PackedVector3Array = PackedVector3Array()
## False: nothing advances unless the owner calls tick(delta) (tests, cutscenes).
@export var auto_process := true

var tuning: Dictionary = {}
var loco: HeroLocomotion
var actor: Node3D
var anim: AnimationPlayer
var player: Node3D
var mode := Mode.REST
## The heading it rests on and returns to (radians, the node's yaw at _ready).
var rest_yaw := 0.0
## The route (parent space) and each point's pause.
var route := PackedVector3Array()
var pauses := PackedFloat32Array()
var target_index := 0
## Seconds since _ready (tick moves it); the idle phase runs on it.
var clock := 0.0
var current_clip: StringName = &""
## Where in the idle loop this villager starts (seconds).
var idle_offset_sec := 0.0
## The filtered ground speed this frame (m/s).
var ground_speed := 0.0

var _direction := 1
var _timer := 0.0
var _resume_mode := Mode.REST
var _talk_yaw := 0.0
var _face_hold := 0.0
var _face_yaw := 0.0
var _player_searched := false


func _ready() -> void:
	if npc_id == &"":
		npc_id = StringName(String(name).to_snake_case())
	tuning = tuning_for(npc_id)
	loco = HeroLocomotion.new(merged(HeroLocomotion.load_data(), tuning.get("locomotion", {}) as Dictionary))
	rest_yaw = rotation.y
	loco.reset_yaw(rest_yaw)
	loco.reset_speed(0.0)
	_attach_actor()
	_read_route()
	if route.size() >= 2:
		mode = Mode.WALK
	var inter := get_node_or_null(interactable_path) as Interactable
	if inter != null:
		inter.used.connect(_on_used)
	if not player_path.is_empty():
		player = get_node_or_null(player_path) as Node3D
		_player_searched = true
	_update_clip(true)
	set_process(auto_process)


func _process(delta: float) -> void:
	tick(delta)


## The merged tuning for a villager: defaults with its `villagers.<id>` row over them.
static func tuning_for(id: StringName, data: Dictionary = {}) -> Dictionary:
	var d := data if not data.is_empty() else load_data()
	var rows := d.get("villagers", {}) as Dictionary
	return merged(d.get("defaults", {}) as Dictionary, rows.get(String(id), {}) as Dictionary)


static func load_data() -> Dictionary:
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f == null:
		push_error("FieldNpc: cannot read %s" % DATA_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


## `over` on top of `base`; nested dictionaries merge, everything else replaces.
static func merged(base: Dictionary, over: Dictionary) -> Dictionary:
	var out := base.duplicate(true)
	for k: Variant in over:
		if out.get(k) is Dictionary and over[k] is Dictionary:
			out[k] = merged(out[k] as Dictionary, over[k] as Dictionary)
		else:
			out[k] = over[k]
	return out


func _num(key: String) -> float:
	return float(tuning.get(key, 0.0))


func _clip(kind: StringName) -> StringName:
	var clips := tuning.get("clips", {}) as Dictionary
	return StringName(str(clips.get(String(kind), String(kind))))


func _attach_actor() -> void:
	actor = get_node_or_null(actor_path) as Node3D
	if actor == null and actor_scene != null:
		actor = actor_scene.instantiate() as Node3D
		actor.name = ACTOR_NAME
		add_child(actor)
	if actor == null:
		push_warning("FieldNpc %s: no actor" % npc_id)
		return
	anim = HeroMotion.player_of(actor)
	HeroMotion.add_micro_motion(actor, npc_id)
	if anim != null and anim.has_animation(_clip(CLIP_IDLE)):
		var length := anim.get_animation(_clip(CLIP_IDLE)).length
		idle_offset_sec = HeroIdleMicro.share(npc_id, SALT_IDLE) * length


func _read_route() -> void:
	route = PackedVector3Array()
	pauses = PackedFloat32Array()
	var holder := get_node_or_null(route_path)
	if holder != null:
		for c: Node in holder.get_children():
			if c is Marker3D:
				route.append(_to_parent((c as Marker3D).global_position))
				pauses.append(float(c.get_meta(META_PAUSE, _num("pause_sec"))))
	if route.is_empty():
		route = route_points.duplicate()
		for i in route.size():
			pauses.append(_num("pause_sec"))
	target_index = 0
	_direction = 1


func _to_parent(global_point: Vector3) -> Vector3:
	var par := get_parent_node_3d()
	return par.to_local(global_point) if par != null else global_point


## The player's offset from this node, in the parent's space (planar: y = 0). Vector3.INF without one.
func player_offset() -> Vector3:
	if player == null and not _player_searched:
		_player_searched = true
		player = _find_player()
	if player == null or not is_instance_valid(player) or not player.is_inside_tree():
		return Vector3.INF
	var d := _to_parent(player.global_position) - position
	return Vector3(d.x, 0.0, d.z)


func _find_player() -> Node3D:
	var tree := get_tree()
	var scope: Node = tree.current_scene if tree != null and tree.current_scene != null else null
	if scope == null:
		return null
	var found := scope.find_children("*", "FieldController", true, false)
	return null if found.is_empty() else found[0] as Node3D


## The node's current heading (radians).
func yaw() -> float:
	return loco.yaw if loco != null else rotation.y


func is_talking() -> bool:
	return mode == Mode.TALK


## Starts a conversation: it stops, turns toward `with_player` (or the known player) and talks.
func begin_talk(with_player: Node3D = null) -> void:
	if with_player != null:
		player = with_player
		_player_searched = true
	if mode == Mode.TALK:
		return
	if mode != Mode.AFTER_TALK:
		_resume_mode = Mode.WALK if route.size() >= 2 else Mode.REST
	mode = Mode.TALK
	_talk_yaw = yaw()
	var off := player_offset()
	if off != Vector3.INF and off.length() > 0.0:
		_talk_yaw = HeroLocomotion.yaw_of(off)
	_update_clip()
	talk_started.emit(player)


## Ends the conversation: back to idle at once, and after return_delay_sec back to its heading or route.
func end_talk() -> void:
	if mode != Mode.TALK:
		return
	mode = Mode.AFTER_TALK
	_timer = _num("return_delay_sec")
	_update_clip()
	talk_ended.emit()


## Ends the talk when `runner` (a DialogueRunner, or anything with a `finished` signal) finishes.
func follow_dialogue(runner: Object) -> void:
	if runner != null and runner.has_signal(&"finished") and not runner.is_connected(&"finished", end_talk):
		runner.connect(&"finished", end_talk, CONNECT_ONE_SHOT)


func _on_used(_interactable: Interactable) -> void:
	begin_talk()


## One frame of behaviour: what it wants (heading, speed), then the eased turn, the filtered gait, the
## move along the route and the clip.
func tick(delta: float) -> void:
	if loco == null or delta <= 0.0:
		return
	clock += delta
	var off := player_offset()
	var dist := off.length() if off != Vector3.INF else INF
	var target_yaw := rest_yaw
	var want_speed := 0.0
	match mode:
		Mode.TALK:
			if dist != INF and dist > 0.0:
				_talk_yaw = HeroLocomotion.yaw_of(off)
			target_yaw = _talk_yaw
			if dist != INF and dist > _num("release_radius_m"):
				end_talk()
		Mode.AFTER_TALK:
			target_yaw = _talk_yaw
			_timer -= delta
			if _timer <= 0.0:
				mode = _resume_mode
		Mode.PAUSE:
			target_yaw = yaw()
			_timer -= delta
			if _timer <= 0.0:
				_next_target()
				mode = Mode.WALK
		Mode.WALK:
			target_yaw = yaw()
			if dist > _num("stop_radius_m"):
				var plan := _walk_plan()
				target_yaw = plan.x
				want_speed = plan.y
	if mode != Mode.TALK and mode != Mode.AFTER_TALK:
		target_yaw = _face_player(target_yaw, off, dist, delta)
	rotation.y = loco.step_yaw(target_yaw, delta)
	ground_speed = loco.step_speed(want_speed, delta)
	_move(delta)
	_update_clip()


## (heading, speed) toward the current route point; arriving there starts the pause.
func _walk_plan() -> Vector2:
	var to := route[target_index] - position
	var flat := Vector3(to.x, 0.0, to.z)
	if flat.length() <= _num("arrive_m"):
		mode = Mode.PAUSE
		_timer = pauses[target_index]
		point_reached.emit(target_index)
		return Vector2(yaw(), 0.0)
	var heading := HeroLocomotion.yaw_of(flat)
	var err := absf(angle_difference(yaw(), heading))
	var tolerance := deg_to_rad(_num("walk_heading_tolerance_deg"))
	# Turn first at a corner: no ground speed until it roughly faces the next point, then ease in.
	var speed := 0.0 if err >= tolerance else _num("walk_speed_mps") * cos(err / tolerance * PI * 0.5)
	# Slow into the point over the last arrive_ease_m so the gait rolls down to idle as it lands.
	var ease_m := _num("arrive_ease_m")
	if ease_m > 0.0:
		speed *= clampf(flat.length() / ease_m, _num("arrive_min_speed_share"), 1.0)
	return Vector2(heading, speed)


func _next_target() -> void:
	if route.size() < 2:
		return
	if str(tuning.get("route_mode", ROUTE_PING_PONG)) == ROUTE_LOOP:
		target_index = (target_index + 1) % route.size()
		return
	if target_index + _direction < 0 or target_index + _direction >= route.size():
		_direction = -_direction
	target_index += _direction


## A villager the player stands close to turns to them; it keeps that heading return_delay_sec after
## they leave, then eases back to `fallback`.
func _face_player(fallback: float, off: Vector3, dist: float, delta: float) -> float:
	if dist <= _num("face_radius_m") and dist > 0.0:
		_face_yaw = HeroLocomotion.yaw_of(off)
		_face_hold = _num("return_delay_sec")
		return _face_yaw
	if _face_hold > 0.0:
		_face_hold -= delta
		return _face_yaw
	return fallback


func _move(delta: float) -> void:
	if ground_speed <= 0.0 or route.is_empty():
		return
	var to := route[target_index] - position
	var step := minf(ground_speed * delta, to.length())
	if step > 0.0:
		position += to.normalized() * step


## Picks the clip for this frame: walk while the gait says so, else talk or idle; cross-fades on change.
func _update_clip(force: bool = false) -> void:
	HeroMotion.set_locomotion_speed(actor, ground_speed)
	if anim == null:
		return
	var walk_weight := loco.weights(ground_speed)[HeroLocomotion.WALK]
	var kind := CLIP_IDLE
	if walk_weight >= _num("gait_switch_weight"):
		kind = CLIP_WALK
	elif mode == Mode.TALK:
		kind = CLIP_TALK
	if kind == CLIP_WALK:
		var rate := ground_speed / loco.walk_clip_mps if loco.walk_clip_mps > 0.0 else 1.0
		anim.speed_scale = clampf(rate, _num("walk_playback_min"), _num("walk_playback_max"))
	else:
		anim.speed_scale = 1.0
	var clip := _clip(kind)
	if clip == current_clip and not force:
		return
	var blend := 0.0 if force else _num("%s_blend_sec" % kind)
	if not HeroMotion.play(actor, clip, blend):
		push_warning("FieldNpc %s: no clip %s" % [npc_id, clip])
	current_clip = clip
	if kind == CLIP_IDLE:
		anim.seek(idle_phase(), false)


## Where in the idle loop it is now: its offset plus the clock, wrapped (the idle never restarts at 0).
func idle_phase() -> float:
	if anim == null or not anim.has_animation(_clip(CLIP_IDLE)):
		return 0.0
	return fposmod(idle_offset_sec + clock, anim.get_animation(_clip(CLIP_IDLE)).length)
