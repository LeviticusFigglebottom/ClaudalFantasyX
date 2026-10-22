class_name FieldMotor
extends RefCounted
## Pure field-movement logic (M1-ARC-01): stick + camera yaw -> horizontal velocity and facing.
## No Nodes, deterministic, so tests drive it directly. FieldController owns one.
##
## Camera-relative input with a latch (genre convention for fixed cameras): when the shot changes
## while the stick is held, the reference yaw of the PREVIOUS camera is kept, so "up" keeps
## meaning the same world direction across the cut. The latch releases when the stick returns
## inside the deadzone, or when it turns more than release_on_turn_deg away from where it pointed
## at the change (0 disables that). Tuning: game/data/world/field_movement.json.

const DATA_PATH := "res://game/data/world/field_movement.json"

var walk_speed := 0.0
var run_speed := 0.0
var acceleration := 0.0
var deceleration := 0.0
var turn_speed_rad := 0.0
var deadzone := 0.0
var walk_run_threshold := 0.0
var latch_on_cut := true
var latch_on_blend := true
var release_on_turn_rad := 0.0

## Yaw (radians, around +Y) that stick-up currently maps to. Read it for debugging and tests.
var reference_yaw := 0.0
var latched := false
var velocity := Vector3.ZERO
## Facing yaw of the character (radians): forward is -Z rotated by this.
var facing_yaw := 0.0

var _latched_stick := Vector2.ZERO
var _stick_active := false


func _init(data: Dictionary = {}) -> void:
	configure(data if not data.is_empty() else FieldInput.load_json(DATA_PATH))


func configure(d: Dictionary) -> void:
	walk_speed = float(d.get("walk_speed_mps", 0.0))
	run_speed = float(d.get("run_speed_mps", 0.0))
	acceleration = float(d.get("acceleration_mps2", 0.0))
	deceleration = float(d.get("deceleration_mps2", 0.0))
	turn_speed_rad = deg_to_rad(float(d.get("turn_speed_deg_per_sec", 0.0)))
	deadzone = float(d.get("stick_deadzone", 0.0))
	walk_run_threshold = float(d.get("walk_run_threshold", 0.0))
	var latch := d.get("input_latch", {}) as Dictionary
	latch_on_cut = bool(latch.get("latch_on_cut", true))
	latch_on_blend = bool(latch.get("latch_on_blend", true))
	release_on_turn_rad = deg_to_rad(float(latch.get("release_on_turn_deg", 0.0)))


## Called by the controller when the director changes shot. Latches only while the stick is held.
func on_camera_change(hard_cut: bool) -> void:
	if not _stick_active:
		return
	if (hard_cut and latch_on_cut) or (not hard_cut and latch_on_blend):
		latched = true


## Advances one step. `stick` uses Input.get_vector's convention (x right, y back/down);
## `camera_yaw` is the live camera's yaw. Returns the new horizontal velocity.
func step(stick: Vector2, camera_yaw: float, delta: float, walk: bool = false) -> Vector3:
	var magnitude := minf(stick.length(), 1.0)
	var active := magnitude > deadzone
	if not active:
		latched = false
		_latched_stick = Vector2.ZERO
		reference_yaw = camera_yaw
	elif not latched:
		reference_yaw = camera_yaw
		_latched_stick = stick
	elif release_on_turn_rad > 0.0 and absf(_latched_stick.angle_to(stick)) > release_on_turn_rad:
		latched = false
		reference_yaw = camera_yaw
		_latched_stick = stick
	_stick_active = active
	var target := Vector3.ZERO
	if active:
		var dir := world_direction(stick, reference_yaw)
		var speed := walk_speed if (walk or magnitude < walk_run_threshold) else run_speed
		target = dir * speed
		facing_yaw = rotate_toward(facing_yaw, yaw_of(dir), turn_speed_rad * delta)
	var rate := acceleration if active else deceleration
	velocity = velocity.move_toward(target, rate * delta)
	return velocity


## Stick -> unit world direction on XZ for a camera with yaw `yaw` (stick up = camera forward).
static func world_direction(stick: Vector2, yaw: float) -> Vector3:
	var basis := Basis(Vector3.UP, yaw)
	var forward := basis * Vector3.FORWARD
	var right := basis * Vector3.RIGHT
	var dir := right * stick.x - forward * stick.y
	dir.y = 0.0
	return dir.normalized() if dir.length_squared() > 0.0 else Vector3.ZERO


## Yaw of a basis around +Y, measured so that Basis(UP, yaw) * FORWARD faces the same way on XZ.
static func yaw_of_basis(basis: Basis) -> float:
	var forward := -basis.z
	forward.y = 0.0
	if forward.length_squared() == 0.0:
		forward = basis.y
		forward.y = 0.0
	return yaw_of(forward)


static func yaw_of(dir: Vector3) -> float:
	return atan2(-dir.x, -dir.z)


static func rotate_toward(from: float, to: float, max_step: float) -> float:
	var diff := angle_difference(from, to)
	if absf(diff) <= max_step:
		return to
	return from + signf(diff) * max_step
