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
## M3-CRE-613 routines on top (all optional, from data or the VillagerLayer):
##   attention a NpcLook modifier turns the head: to the player while talking, a glance at a party that
##             comes near, the sky in a storm, the chat partner, the work in its hands, and now and then
##             a look around;
##   chat      two villagers with `chat_with` face each other and take turns talking;
##   work      `work.clip` replaces idle at rest (and at route points marked `activity = work`), the head
##             down on the work;
##   storm     set_storm(true) (or FieldNpc.set_storm_all): after a per-villager delay it hurries to its
##             shelter point (if it has one), braces, and keeps glancing at the sky; set_storm(false)
##             walks it home.
## Ground: the route's own Y (linear between points); villagers have no physics body.
## Tuning: game/data/world/npc/npc.json (defaults plus per-villager overrides). Deterministic: no
## randomness, and the state only advances by tick(delta).

signal talk_started(player: Node3D)
signal talk_ended
signal point_reached(index: int)

enum Mode { REST, WALK, PAUSE, TALK, AFTER_TALK, GO }

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
const CLIP_WORK := &"work"
const CLIP_STORM := &"storm"
## Every FieldNpc joins this group (set_storm_all).
const GROUP := &"field_npc"
## A route Marker3D's metadata: `activity = "work"` plays the work clip while it pauses there.
const META_ACTIVITY := &"activity"
const ACTIVITY_WORK := "work"
const LOOK_NAME := &"NpcLook"

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
## Per route point (with route_points): its pause (seconds; 0 or missing: the data's) and its activity.
@export var route_pauses: PackedFloat32Array = PackedFloat32Array()
@export var route_activities: PackedStringArray = PackedStringArray()
## False: nothing advances unless the owner calls tick(delta) (tests, cutscenes).
@export var auto_process := true
## Another FieldNpc to chat with while both rest (M3-CRE-613).
@export var chat_with: NodePath
## A Node3D its head looks at while it works. Empty: the data's `work.look_at` (node space).
@export var work_target_path: NodePath
## A Node3D it hurries to in a storm. Empty: it braces where it stands.
@export var shelter_path: NodePath
## M3-CRE-659: this person's colours on a shared body (NpcTints: cloth_a, cloth_b, cloth_c, hair -> a colour),
## applied to the actor's materials as per-instance overrides.
@export var tints: Dictionary = {}
## M3-CRE-659: merged over its npc.json tuning (a crowd person's work clip and focus, a child's pace).
@export var tuning_over: Dictionary = {}
## M3-HER-1142: when opaque, the body is drawn as one glowing silhouette in this colour (NpcSilhouette).
@export var silhouette := Color(0.0, 0.0, 0.0, 0.0)

var tuning: Dictionary = {}
var loco: HeroLocomotion
var actor: Node3D
## Every override material put on the actor (its tints, its silhouette), held here as well as on the meshes (PC row
## 85), so they free after the meshes and their render instances (the children go first), never while an instance
## still draws with them.
var override_materials: Array[Material] = []
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
## Its own idle and work playback rate (npc.json `idle_playback` [lo, hi], drawn from its id): two villagers of one
## body breathe and shift at different paces, not only out of phase.
var idle_rate := 1.0
## The filtered ground speed this frame (m/s).
var ground_speed := 0.0
## The head (null on a rig without a skeleton).
var look: NpcLook
var partner: FieldNpc
var storm := false
## Seconds the current talk has run, and whether the player was held (a dialogue) during it.
var talk_sec := 0.0
## Where it came from (parent space), so a storm's run to shelter can walk home again.
var home := Vector3.ZERO
var work_target: Node3D
var shelter: Node3D
var activities := PackedStringArray()

var _direction := 1
var _timer := 0.0
var _resume_mode := Mode.REST
var _talk_yaw := 0.0
var _face_hold := 0.0
var _face_yaw := 0.0
var _player_searched := false
var _go_target := Vector3.ZERO
var _go_yaw := 0.0
var _go_then := Mode.REST
var _storm_wait := -1.0
var _storm_on := false
var _talk_held := false
var _glance_until := -1.0
var _glance_next := 0.0
var _glance_count := 0
var _was_near := false
var _look_index := 0
var _look_next := 0.0
var _look_until := -1.0
var _look_yaw := 0.0
var _chat_slot := -1
var _chat_slot_end := 0.0
var _chat_speaker: StringName = &""
var _bout := -1
var _bout_end := 0.0
var _bout_on := false


func _ready() -> void:
	if npc_id == &"":
		npc_id = StringName(String(name).to_snake_case())
	tuning = merged(tuning_for(npc_id), tuning_over)
	loco = HeroLocomotion.new(merged(HeroLocomotion.load_data(), tuning.get("locomotion", {}) as Dictionary))
	rest_yaw = rotation.y
	home = position
	loco.reset_yaw(rest_yaw)
	loco.reset_speed(0.0)
	add_to_group(GROUP)
	_attach_actor()
	_read_route()
	if not chat_with.is_empty():
		partner = get_node_or_null(chat_with) as FieldNpc
	if not work_target_path.is_empty():
		work_target = get_node_or_null(work_target_path) as Node3D
	if not shelter_path.is_empty():
		shelter = get_node_or_null(shelter_path) as Node3D
	_look_next = _share_range("look_around", "every_sec", 0)
	if route.size() >= 2:
		mode = Mode.WALK
	listen_to(get_node_or_null(interactable_path) as Interactable)
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


func _section(key: String) -> Dictionary:
	return tuning.get(key, {}) as Dictionary


func _sub(section: String, key: String) -> float:
	return float(_section(section).get(key, 0.0))


## A deterministic value in [section.key[0], section.key[1]] (or the number itself) for the `index`th draw.
## A top-level tuning value: a number, or [lo, hi] drawn from the villager's id (1.0 when unset).
func _share_value(key: String) -> float:
	var v: Variant = tuning.get(key, 1.0)
	if v is Array and (v as Array).size() == 2:
		return lerpf(float(v[0]), float(v[1]), HeroIdleMicro.share(npc_id, key))
	return float(v)


func _share_range(section: String, key: String, index: int) -> float:
	var v: Variant = _section(section).get(key, 0.0)
	if v is Array and (v as Array).size() == 2:
		var u := HeroIdleMicro.share(npc_id, "%s/%s/%d" % [section, key, index])
		return lerpf(float(v[0]), float(v[1]), u)
	return float(v)


## Starts the talk when `inter` is used (several can be connected; the VillagerLayer passes the zone's).
func listen_to(inter: Interactable) -> void:
	if inter != null and not inter.used.is_connected(_on_used):
		inter.used.connect(_on_used)


func _attach_actor() -> void:
	actor = get_node_or_null(actor_path) as Node3D
	if actor == null and actor_scene != null:
		actor = actor_scene.instantiate() as Node3D
		actor.name = ACTOR_NAME
		add_child(actor)
	if actor == null:
		push_warning("FieldNpc %s: no actor" % npc_id)
		return
	NpcTints.apply(actor, tints)
	if silhouette.a > 0.0:
		# Nothing swaps these back on leaving the tree (PC row 85: the pass-3 clear in _exit_tree put the body's own
		# materials back on its surfaces mid-teardown while the silhouette's were freed).
		NpcSilhouette.apply(actor, silhouette)
	override_materials = NpcSilhouette.overrides_of(actor)
	anim = HeroMotion.player_of(actor)
	HeroMotion.add_micro_motion(actor, npc_id)
	var skel := HeroMotion.skeleton_of(actor)
	if skel != null:
		look = skel.get_node_or_null(NodePath(String(LOOK_NAME))) as NpcLook
		if look == null:
			look = NpcLook.new(_section("look"))
			look.name = LOOK_NAME
			skel.add_child(look)
	if anim != null and anim.has_animation(_clip(CLIP_IDLE)):
		var length := anim.get_animation(_clip(CLIP_IDLE)).length
		idle_offset_sec = HeroIdleMicro.share(npc_id, SALT_IDLE) * length
	idle_rate = _share_value("idle_playback")


func _read_route() -> void:
	route = PackedVector3Array()
	pauses = PackedFloat32Array()
	activities = PackedStringArray()
	var holder := get_node_or_null(route_path)
	if holder != null:
		for c: Node in holder.get_children():
			if c is Marker3D:
				route.append(_to_parent((c as Marker3D).global_position))
				pauses.append(float(c.get_meta(META_PAUSE, _num("pause_sec"))))
				activities.append(str(c.get_meta(META_ACTIVITY, "")))
	if route.is_empty():
		route = route_points.duplicate()
		for i in route.size():
			var own := route_pauses[i] if i < route_pauses.size() else 0.0
			pauses.append(own if own > 0.0 else _num("pause_sec"))
			activities.append(route_activities[i] if i < route_activities.size() else "")
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
	if mode == Mode.GO:
		_resume_mode = Mode.GO
	elif mode != Mode.AFTER_TALK:
		_resume_mode = Mode.WALK if route.size() >= 2 and not _storm_on else Mode.REST
	mode = Mode.TALK
	talk_sec = 0.0
	_talk_held = false
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
	if loco == null or delta <= 0.0 or not is_inside_tree():
		return
	clock += delta
	_step_storm(delta)
	var off := player_offset()
	var dist := off.length() if off != Vector3.INF else INF
	var target_yaw := _rest_heading()
	var want_speed := 0.0
	match mode:
		Mode.TALK:
			talk_sec += delta
			if dist != INF and dist > 0.0:
				_talk_yaw = HeroLocomotion.yaw_of(off)
			target_yaw = _talk_yaw
			if dist != INF and dist > _num("release_radius_m"):
				end_talk()
			elif _player_free_again():
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
		Mode.WALK, Mode.GO:
			target_yaw = yaw()
			if dist > _num("stop_radius_m") or (mode == Mode.GO and _storm_on):
				var plan := _walk_plan()
				target_yaw = plan.x
				want_speed = plan.y
	if mode != Mode.TALK and mode != Mode.AFTER_TALK:
		target_yaw = _face_player(target_yaw, off, dist, delta)
	rotation.y = loco.step_yaw(target_yaw, delta)
	ground_speed = loco.step_speed(want_speed, delta)
	_move(delta)
	_step_chat()
	_attend(delta, off, dist)
	_update_clip()


## (heading, speed) toward the current route point; arriving there starts the pause.
func _walk_plan() -> Vector2:
	var to := _goal() - position
	var flat := Vector3(to.x, 0.0, to.z)
	if flat.length() <= _num("arrive_m"):
		if mode == Mode.GO:
			mode = _go_then
			rest_yaw = _go_yaw
			return Vector2(yaw(), 0.0)
		mode = Mode.PAUSE
		_timer = pauses[target_index]
		point_reached.emit(target_index)
		return Vector2(yaw(), 0.0)
	var heading := HeroLocomotion.yaw_of(flat)
	var err := absf(angle_difference(yaw(), heading))
	var tolerance := deg_to_rad(_num("walk_heading_tolerance_deg"))
	# Turn first at a corner: no ground speed until it roughly faces the next point, then ease in.
	var speed := 0.0 if err >= tolerance else _walk_speed() * cos(err / tolerance * PI * 0.5)
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
	if ground_speed <= 0.0 or (route.is_empty() and mode != Mode.GO):
		return
	var to := _goal() - position
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
	elif mode == Mode.TALK or (_chat_speaker == npc_id and chatting()):
		kind = CLIP_TALK
	elif _storm_on and _has_clip(CLIP_STORM):
		kind = CLIP_STORM
	elif working() and _has_clip(CLIP_WORK):
		kind = CLIP_WORK
	if kind == CLIP_WALK:
		var rate := ground_speed / loco.walk_clip_mps if loco.walk_clip_mps > 0.0 else 1.0
		anim.speed_scale = clampf(rate, _num("walk_playback_min"), _num("walk_playback_max"))
	elif _storm_on:
		anim.speed_scale = _sub("storm", "idle_playback")
	elif kind == CLIP_IDLE or kind == CLIP_WORK:
		anim.speed_scale = idle_rate
	else:
		anim.speed_scale = 1.0
	var clip := _clip(kind)
	if clip == current_clip and not force:
		return
	var blend := (
		0.0 if force else _num("%s_blend_sec" % (kind if kind != CLIP_WORK and kind != CLIP_STORM else CLIP_IDLE))
	)
	if not HeroMotion.play(actor, clip, blend):
		push_warning("FieldNpc %s: no clip %s" % [npc_id, clip])
	current_clip = clip
	if kind == CLIP_IDLE:
		anim.seek(idle_phase(), false)
	elif kind == CLIP_WORK or kind == CLIP_STORM:
		anim.seek(loop_phase(clip), false)


## Where in the idle loop it is now: its offset plus the clock, wrapped (the idle never restarts at 0).
func idle_phase() -> float:
	if anim == null or not anim.has_animation(_clip(CLIP_IDLE)):
		return 0.0
	return fposmod(idle_offset_sec + clock * idle_rate, anim.get_animation(_clip(CLIP_IDLE)).length)


## Where in a resting loop (a work or storm clip) it is now: a share of the loop of its own, plus the clock, so two
## villagers at the same work never haul or brace in step (big17: Tamsule's crowd fisher and boatman hauled together).
func loop_phase(clip: StringName) -> float:
	if anim == null or not anim.has_animation(clip):
		return 0.0
	var length := anim.get_animation(clip).length
	return fposmod(HeroIdleMicro.share(npc_id, String(clip)) * length + clock * idle_rate, length)


## True when the data names a clip for `kind` and the actor has it (work and storm clips are optional).
func _has_clip(kind: StringName) -> bool:
	return anim != null and _section("clips").has(String(kind)) and anim.has_animation(_clip(kind))


## The point it walks toward: the run's goal (GO) or the current route point.
func _goal() -> Vector3:
	return _go_target if mode == Mode.GO else route[target_index]


func _walk_speed() -> float:
	return _sub("storm", "walk_speed_mps") if _storm_on else _num("walk_speed_mps")


## The heading it rests on: toward its chat partner while they chat, else its resting heading.
func _rest_heading() -> float:
	if chatting():
		var d := partner_offset()
		return HeroLocomotion.yaw_of(Vector3(d.x, 0.0, d.z))
	return rest_yaw


## True when the talk should end because the player has control again: a dialogue held them and let go,
## or nothing held them for talk_unheld_sec (a bark that never takes control).
func _player_free_again() -> bool:
	if player == null or not is_instance_valid(player) or not &"accepts_input" in player:
		return false
	var free := bool(player.get(&"accepts_input"))
	if not free:
		_talk_held = true
		return false
	if _talk_held:
		return true
	return talk_sec >= _num("talk_unheld_sec")


## The partner's offset from this node in this node's parent space (the partner may sit under another parent: a
## villager inside a cutscene actor), planar.
func partner_offset() -> Vector3:
	var d := _to_parent(partner.global_position) - position
	return Vector3(d.x, 0.0, d.z)


# --- chat pairs ---------------------------------------------------------------------------------------


## True while this villager speaks its turn of a chat (read by audio's LifeAudio, M3-AUD-815).
func chat_speaking() -> bool:
	return _chat_speaker == npc_id and chatting()


## True while it rests near its partner and both are free to chat (no talk with the player, no storm).
func chatting() -> bool:
	if partner == null or not is_instance_valid(partner) or _storm_on or partner._storm_on:
		return false
	if mode != Mode.REST or partner.mode != Mode.REST:
		return false
	var d := partner_offset()
	if Vector2(d.x, d.z).length() > _sub("chat", "max_distance_m"):
		return false
	return _bout_on if _chat_lead() else partner._bout_on


## Advances the lead's bouts: chat.bout_sec of chatting, then chat.quiet_sec back at their own business.
func _step_bouts() -> void:
	if not is_instance_valid(partner) or not _chat_lead():
		return
	if not _section("chat").has("bout_sec"):
		_bout_on = true
		return
	while clock >= _bout_end:
		_bout += 1
		_bout_on = _bout % 2 == 0
		_bout_end += _share_range("chat", "bout_sec" if _bout_on else "quiet_sec", _bout)


## The pair's lead: the partner whose id sorts first runs the turn schedule; the other reads it.
func _chat_lead() -> bool:
	return is_instance_valid(partner) and String(npc_id) < String(partner.npc_id)


## Who speaks now (&"" in a pause): turns of chat.turn_sec, alternating, with a pause now and then.
func _step_chat() -> void:
	_step_bouts()
	if not chatting():
		_chat_speaker = &""
		return
	if not _chat_lead():
		_chat_speaker = partner._chat_speaker
		return
	while clock >= _chat_slot_end:
		_chat_slot += 1
		# A chat that resumes after a break starts its next turn now, not in the past.
		_chat_slot_end = maxf(_chat_slot_end, clock) + _share_range("chat", "turn_sec", _chat_slot)
		var pause := HeroIdleMicro.share(npc_id, "chat/pause/%d" % _chat_slot) < _sub("chat", "pause_share")
		if pause:
			_chat_speaker = &""
		else:
			_chat_speaker = npc_id if _chat_slot % 2 == 0 else partner.npc_id


# --- work -----------------------------------------------------------------------------------------------


## True while it rests (or pauses at a work point) with work to do and nothing else to attend to.
func working() -> bool:
	if _storm_on or chatting() or _section("work").is_empty():
		return false
	if mode == Mode.REST:
		return true
	return mode == Mode.PAUSE and target_index < activities.size() and activities[target_index] == ACTIVITY_WORK


## The work's focus in world space: work_target, else `work.look_at` in node space.
func work_point() -> Vector3:
	if work_target != null and is_instance_valid(work_target):
		return work_target.global_position
	var at: Variant = _section("work").get("look_at", [])
	if at is Array and (at as Array).size() == 3:
		return to_global(Vector3(float(at[0]), float(at[1]), float(at[2])))
	return to_global(Vector3(0.0, 0.0, -1.0))


# --- storm ----------------------------------------------------------------------------------------------


## Every FieldNpc in the tree braces for (or comes out of) the storm.
static func set_storm_all(tree: SceneTree, on: bool) -> void:
	if tree == null:
		return
	for n: Node in tree.get_nodes_in_group(GROUP):
		(n as FieldNpc).set_storm(on)


## The storm begins or ends; each villager reacts after its own delay (storm.react_sec).
func set_storm(on: bool) -> void:
	if on == storm:
		return
	storm = on
	_storm_wait = _share_range("storm", "react_sec", 0 if on else 1)


func _step_storm(delta: float) -> void:
	if _storm_wait < 0.0:
		return
	_storm_wait -= delta
	if _storm_wait > 0.0:
		return
	_storm_wait = -1.0
	_storm_on = storm
	if mode == Mode.TALK or mode == Mode.AFTER_TALK:
		_resume_mode = Mode.REST
	if storm and shelter != null and is_instance_valid(shelter):
		_go(_to_parent(shelter.global_position), shelter.global_rotation.y)
	elif not storm and position.distance_to(home) > _num("arrive_m"):
		_go(home, _home_yaw())
	elif storm and (mode == Mode.WALK or mode == Mode.PAUSE):
		mode = Mode.REST
	elif not storm and mode == Mode.REST and route.size() >= 2:
		mode = Mode.WALK


func _home_yaw() -> float:
	return float(get_meta(&"home_yaw", rest_yaw))


## Walks to `point` (parent space), then rests there facing `yaw_at`; a route resumes after a walk home.
func _go(point: Vector3, yaw_at: float) -> void:
	if not has_meta(&"home_yaw"):
		set_meta(&"home_yaw", rest_yaw)
	_go_target = point
	_go_yaw = yaw_at
	_go_then = Mode.WALK if not storm and route.size() >= 2 else Mode.REST
	if mode == Mode.TALK or mode == Mode.AFTER_TALK:
		_resume_mode = Mode.GO
	else:
		mode = Mode.GO


# --- attention (the head) -------------------------------------------------------------------------------


## Picks where the head looks this frame, in priority order, and eases it there.
func _attend(delta: float, off: Vector3, dist: float) -> void:
	if look == null:
		return
	var aim := _attention(off, dist)
	if aim == Vector2.INF:
		look.look_ahead()
	else:
		look.look(aim.x, aim.y)
	look.advance(delta)


## (relative yaw, pitch) in radians, or Vector2.INF for straight ahead.
func _attention(off: Vector3, dist: float) -> Vector2:
	var near := dist <= _sub("glance", "radius_m") and dist > 0.0
	if mode == Mode.TALK or mode == Mode.AFTER_TALK:
		return _aim_at_player(off)
	# A glance: when the party comes near, then again every glance.rest_sec while it stays.
	if near and (not _was_near or clock >= _glance_next):
		_glance_until = clock + _share_range("glance", "hold_sec", _glance_count)
		_glance_count += 1
		_glance_next = _glance_until + _share_range("glance", "rest_sec", _glance_count)
	_was_near = near
	if near and clock < _glance_until:
		var aim := _aim_at_player(off)
		if aim != Vector2.INF and look.can_reach(aim.x):
			return aim
	if _storm_on:
		return _storm_aim()
	if chatting():
		return _aim_at(partner.global_position + Vector3.UP * _sub("look", "head_height_m"))
	if working():
		return _work_aim()
	return _look_around()


## Toward a world point from the head (the node plus look.head_height_m).
func _aim_at(world_point: Vector3) -> Vector2:
	var head := global_position + Vector3.UP * _sub("look", "head_height_m")
	var d := world_point - head
	var flat := Vector2(d.x, d.z).length()
	if flat < 0.001:
		return Vector2.INF
	var rel := angle_difference(global_rotation.y, HeroLocomotion.yaw_of(Vector3(d.x, 0.0, d.z)))
	return Vector2(rel, atan2(d.y, flat))


func _aim_at_player(off: Vector3) -> Vector2:
	if off == Vector3.INF or player == null or not is_instance_valid(player):
		return Vector2.INF
	return _aim_at(player.global_position + Vector3.UP * _sub("look", "player_eye_height_m"))


## Down at the work, looking up now and then (work.look_up_every_sec, work.look_up_sec).
func _work_aim() -> Vector2:
	var aim := _aim_at(work_point())
	var cycle := _share_range("work", "look_up_every_sec", 0)
	if cycle > 0.0 and fposmod(clock + idle_offset_sec, cycle) < _sub("work", "look_up_sec"):
		var k := floori((clock + idle_offset_sec) / cycle)
		var side := HeroIdleMicro.share(npc_id, "work/side/%d" % k) * 2.0 - 1.0
		return Vector2(side * deg_to_rad(_sub("work", "look_up_yaw_deg")), 0.0)
	return aim


## Braced (head down against the wind), with a look up at the sky every storm.sky_every_sec.
func _storm_aim() -> Vector2:
	var cycle := _share_range("storm", "sky_every_sec", 0)
	var rel := 0.0
	var az: Variant = _section("storm").get("look_azimuth_deg", null)
	if az != null:
		# Azimuth clockwise from north (-Z), as zone_weather.json; yaw is counter-clockwise from -Z.
		rel = angle_difference(global_rotation.y, -deg_to_rad(float(az)))
	if cycle > 0.0 and fposmod(clock + idle_offset_sec, cycle) < _sub("storm", "sky_look_sec"):
		return Vector2(rel, deg_to_rad(_sub("storm", "sky_pitch_deg")))
	return Vector2(rel * _sub("storm", "brace_yaw_share"), -deg_to_rad(_sub("storm", "brace_pitch_deg")))


## Now and then a slow look to one side and back (look_around.every_sec, hold_sec, yaw_deg).
func _look_around() -> Vector2:
	if _section("look_around").is_empty():
		return Vector2.INF
	if clock >= _look_next:
		_look_until = clock + _share_range("look_around", "hold_sec", _look_index)
		var u := HeroIdleMicro.share(npc_id, "look_around/yaw/%d" % _look_index) * 2.0 - 1.0
		_look_yaw = u * deg_to_rad(_sub("look_around", "yaw_deg"))
		_look_index += 1
		_look_next = _look_until + _share_range("look_around", "every_sec", _look_index)
	if clock < _look_until:
		return Vector2(_look_yaw, 0.0)
	return Vector2.INF
