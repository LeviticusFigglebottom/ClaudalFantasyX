class_name FootstepAudio
extends Node
## Footsteps for one walker in the field (M2-AUD-05; ADR 0031; docs/kb/tech/audio_runtime.md), by listening: the
## director attaches one when a FieldController enters the tree. Once a frame it reads the walker's position (and
## grounded(), when it has one) and never writes the walker's state. The horizontal distance covered fills a stride
## accumulator; each full stride plays the surface's footstep row at the walker's feet. A walking pace takes
## `walk_step_m` strides and a run `run_step_m` (game/data/audio/footsteps.json); the surface is the scene's (its
## `scenes` row, else `default`). A jump in position longer than `teleport_m` (a spawn or a warp) is not walked.
## A paused walker (the field menu pauses the tree) covers no distance, so it takes no steps.

## Plays a row at a position: (id: StringName, at: Vector3, opts: Dictionary) -> void.
var player: Callable = Callable()
## The walker (a FieldController in the game, any Node3D in tests).
var walker: Node3D
## footsteps.json.
var data: Dictionary = {}
## The surface the steps sound on (a key of data.surfaces).
var surface: StringName = &""
## Distance walked since the last step (m), and the last position read.
var stride := 0.0
var steps := 0
## The walker's smoothed horizontal speed (m/s).
var speed := 0.0
var _last := Vector3.ZERO
var _has_last := false
var _moving := false
var _still_sec := 0.0


func _init(table: Dictionary = {}) -> void:
	data = table


## Starts listening to `node`; `scene_path` picks the surface.
func attach(node: Node3D, scene_path: String) -> void:
	walker = node
	surface = surface_for(data, scene_path)
	_has_last = false


## The surface for `scene_path`: its scenes row, else the default.
static func surface_for(table: Dictionary, scene_path: String) -> StringName:
	var scenes := table.get("scenes", {}) as Dictionary
	return StringName(str(scenes.get(scene_path, table.get("default", ""))))


## The stride length at `speed` (m/s): a walk's below run_above_m_s, a run's at or above it.
static func step_length(table: Dictionary, speed: float) -> float:
	var run := speed >= float(table.get("run_above_m_s", 0.0))
	return float(table.get("run_step_m" if run else "walk_step_m", 1.0))


## Reads the walker once and plays the steps it took. AudioDirector.advance calls it; tests call it directly.
func advance(delta: float) -> void:
	if not is_instance_valid(walker) or not walker.is_inside_tree():
		return
	var at := walker.global_position
	if not _has_last:
		_last = at
		_has_last = true
		return
	var moved := Vector2(at.x - _last.x, at.z - _last.z).length()
	_last = at
	if moved > float(data.get("teleport_m", 3.0)) or not _on_ground():
		return
	# Render frames between physics ticks read no movement: only a pause longer than stop_sec ends a walk, and
	# the pace is a smoothed speed.
	var k := clampf(delta / maxf(float(data.get("speed_smooth_sec", 0.15)), 1e-4), 0.0, 1.0)
	speed = lerpf(speed, moved / maxf(delta, 1e-4), k)
	if moved <= float(data.get("still_m", 0.0)):
		_still_sec += delta
		if _still_sec >= float(data.get("stop_sec", 0.2)):
			_moving = false
			speed = 0.0
		return
	_still_sec = 0.0
	if not _moving:
		_moving = true
		stride = step_length(data, 0.0) * float(data.get("first_step", 0.5))
	stride += moved
	var length := step_length(data, speed)
	if stride >= length:
		stride = fmod(stride, length)
		_play(at, speed)


func _on_ground() -> bool:
	return not walker.has_method(&"grounded") or bool(walker.call(&"grounded"))


func _play(at: Vector3, pace: float) -> void:
	var row := StringName(str((data.get("surfaces", {}) as Dictionary).get(String(surface), "")))
	if row == &"":
		return
	steps += 1
	var run := pace >= float(data.get("run_above_m_s", 0.0))
	var opts := {"volume_db": float(data.get("run_db" if run else "walk_db", 0.0))}
	if player.is_valid():
		player.call(row, at, opts)
