class_name FieldController
extends CharacterBody3D
## The player in the field (SPEC §6.6, M1-ARC-01): camera-relative movement through FieldMotor,
## gravity and floor snapping, interaction with Interactables, and touch triggers.
##
## Camera-relative input follows the director's live camera; when the director changes shot
## while the stick is held, FieldMotor latches the old reference until the stick is released.
## Tuning: game/data/world/field_movement.json. Actions: game/data/world/field_input.json
## (added at runtime when project.godot lacks them).
##
## Tests and cutscenes drive it without devices: set `input_override` (stick in Input.get_vector
## convention) and call step(delta), or call `interact()` directly.

signal interacted(target: Interactable)

## Slide iterations for the off-physics-frame fallback (same default as CharacterBody3D).
const MAX_SLIDES := 6

@export var director_path: NodePath
## Disable to freeze the player (cutscenes, menus); the director keeps tracking.
@export var accepts_input := true

var motor: FieldMotor
var director: FieldCameraDirector
var data: Dictionary = {}
## When set (not NAN), used instead of the device stick. Vector2(NAN, NAN) = read devices.
var input_override := Vector2(NAN, NAN)
var walk_override := false
## Walkable ground at the water's edge: no step off a dock into the sea (FieldShore, field_movement.json "shore").
var shore: FieldShore

var _gravity := 0.0
var _max_fall := 0.0
var _reach := 0.0
var _touching: Dictionary = {}
var _grounded := false


func _ready() -> void:
	FieldInput.ensure_actions()
	data = FieldInput.load_json(FieldMotor.DATA_PATH)
	motor = FieldMotor.new(data)
	_gravity = float(data.get("gravity_mps2", 0.0))
	_max_fall = float(data.get("max_fall_speed_mps", 0.0))
	_reach = float(data.get("interact_reach_m", 0.0))
	floor_snap_length = float(data.get("floor_snap_m", floor_snap_length))
	shore = FieldShore.new(data)
	motor.facing_yaw = rotation.y
	director = get_node_or_null(director_path) as FieldCameraDirector
	if director != null:
		director.shot_changed.connect(_on_shot_changed)
		director.snapped.connect(_on_snapped)
	var services := TownServices.new()  # M2-UI-06: {"shop": id} / {"inn": id} payloads open a town menu
	services.name = &"TownServices"
	add_child(services)
	var shrines := ShrineServices.new()  # M3-C07-05: {"save_shrine": id} payloads rest, save and offer the road
	shrines.name = &"ShrineServices"
	add_child(shrines)
	FieldHud.attach(self)  # M2-UI-17/19/20: the objective line, the destination cue, the interaction prompt
	HeroFieldActor.attach(self)  # M2-HER-1101/1102: the real hero body, the stage heroes and the followers


func _physics_process(delta: float) -> void:
	step(delta)


func _unhandled_input(event: InputEvent) -> void:
	if accepts_input and screen_clear() and event.is_action_pressed(FieldInput.INTERACT):
		if interact() != null:
			get_viewport().set_input_as_handled()
	elif accepts_input and event.is_action_pressed(FieldMenu.OPEN_ACTION):  # M2-UI-04: the field menu
		FieldMenu.open_in(self)
		get_viewport().set_input_as_handled()


## One movement step: stick -> FieldMotor -> move_and_slide, then touch triggers.
## Inside a physics frame this is plain move_and_slide. Outside one (tests, scripted moves) the
## physics delta is 0, so it slides with move_and_collide over `delta` instead.
func step(delta: float) -> void:
	var stick := current_stick()
	var yaw := director.camera_yaw() if director != null else 0.0
	var walk := walk_override or (accepts_input and Input.is_action_pressed(FieldInput.WALK))
	var horizontal := motor.step(stick, yaw, delta, walk)
	velocity.x = horizontal.x
	velocity.z = horizontal.z
	if grounded():
		velocity.y = 0.0
	else:
		velocity.y = maxf(velocity.y - _gravity * delta, -_max_fall)
	var from := global_position
	var was_grounded := _grounded
	if Engine.is_in_physics_frame():
		move_and_slide()
		_grounded = is_on_floor()
	else:
		_slide(velocity * delta)
	if shore.enabled() and shore.refuses(self, from, global_position):
		global_position = from  # the water's edge holds him as a wall would
		velocity = Vector3.ZERO
		_grounded = was_grounded
	elif shore.enabled():
		shore.settle(self, _grounded)
	rotation.y = motor.facing_yaw
	_check_touch()


## On the floor after the last step (either movement path).
func grounded() -> bool:
	return _grounded


func _slide(motion: Vector3) -> void:
	var remaining := motion
	for i in MAX_SLIDES:
		var hit := move_and_collide(remaining)
		if hit == null:
			break
		remaining = hit.get_remainder().slide(hit.get_normal())
		if remaining.is_zero_approx():
			break
	_grounded = test_move(global_transform, Vector3.DOWN * floor_snap_length)
	if _grounded:
		var snap := move_and_collide(Vector3.DOWN * floor_snap_length, true)
		if snap != null:
			global_position += snap.get_travel()


func current_stick() -> Vector2:
	if not is_nan(input_override.x):
		return input_override
	return FieldInput.move_vector() if accepts_input and screen_clear() else Vector2.ZERO


## False while SceneRouter's fade still covers the screen (a scene change, the way back from a fight): the player
## gets the stick and the interact button when he can see (the human's playtest: the hero moved ~0.3 s before the
## fade cleared). Tests and cutscenes (input_override, interact()) are not gated.
func screen_clear() -> bool:
	var router := get_node_or_null(^"/root/SceneRouter")
	return router == null or not router.has_method(&"fade_alpha") or float(router.call(&"fade_alpha")) <= 0.0


## The available interact-mode Interactable nearest the player within reach, or null.
func nearest_interactable() -> Interactable:
	var best: Interactable = null
	var best_d := INF
	for n in get_tree().get_nodes_in_group(Interactable.GROUP):
		var it := n as Interactable
		if it == null or it.activation != Interactable.Activation.INTERACT or not it.is_available():
			continue
		var d := global_position.distance_to(it.global_position)
		var reachable := it.contains_point(global_position) or d <= _reach
		if reachable and d < best_d:
			best = it
			best_d = d
	return best


## Uses the nearest interactable. Returns it, or null when nothing fired.
func interact() -> Interactable:
	var it := nearest_interactable()
	if it != null and it.try_interact():
		interacted.emit(it)
		return it
	return null


func _check_touch() -> void:
	for n in get_tree().get_nodes_in_group(Interactable.GROUP):
		var it := n as Interactable
		if it == null or it.activation != Interactable.Activation.TOUCH:
			continue
		var inside := it.contains_point(global_position)
		if inside and not _touching.has(it):
			_touching[it] = true
			it.on_touched()
		elif not inside:
			_touching.erase(it)


func _on_shot_changed(_shot: CameraShot, hard_cut: bool, _blend_sec: float) -> void:
	motor.on_camera_change(hard_cut)


## A snap shows a new camera at once: re-read it rather than keep a latch to the old one.
func _on_snapped(_shot: CameraShot) -> void:
	motor.relatch(director.camera_yaw())
