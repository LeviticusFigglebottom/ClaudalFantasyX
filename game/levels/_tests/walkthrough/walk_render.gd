extends Node3D
## env-art's walk-through renderer (the Lead's Prologue–Ch4 walk pass): stages one level as the slice's shot rig does
## (fresh state, `flags`, the party at `spawn`), then for each point of a walk stands a camera at the player's eye over
## the ground under it (a ray down onto the level's collision) looking along the walk, and saves a frame per point.
## Never a test or a baseline: env-art views the frames. Run with godot-render (it needs a window):
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://game/levels/_tests/walkthrough/walk_render.tscn -- --walk=<walk.json> --out=<dir>
## walk.json: {"level_path", "spawn", "flags": [], "eye_m"?, "fov"?, "settle_frames"?, "first_settle_frames"?,
##             "points": [{"id", "at": [x, z] | [x, y, z], "look": [x, z] | [x, y, z]}]}
## An "at" with y is the eye itself (no ray); a "look" without y looks level at eye height.
## "auto_targets": true adds a still of every Interactable in the level and of each of "pois" ([{"id", "at": [x, z]}],
## the zone map's): the eye stands STAND_M off the target, on the first of eight sides with ground under it and a clear
## line to the target (the Lead's 10-30 POI and interactable pass).

const RESOLUTION := Vector2i(960, 540)
const DEFAULT_EYE_M := 1.6
const DEFAULT_FOV := 60.0
const RAY_FROM_M := 60.0
const RAY_DEPTH_M := 160.0
const STAND_M: Array[float] = [3.0, 4.5, 2.2]
const SIDES := 8
const TARGET_UP_M := 1.0
const STAND_STEP_M := 1.5
const CLEAR_SLACK_M := 0.6
const FLOOR_LAYERS := 6
const FLOOR_STEP_M := 0.3

var _shot: SliceCutsceneShot
var _camera: Camera3D


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := {}
	for a: String in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		if kv.size() == 2:
			args[kv[0]] = kv[1]
	var walk: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(str(args.get("walk", ""))))
	var out_dir := str(args.get("out", "user://walk"))
	DirAccess.make_dir_recursive_absolute(out_dir)
	get_window().size = RESOLUTION
	_shot = SliceCutsceneShot.new()
	_shot.level_path = str(walk["level_path"])
	_shot.spawn = StringName(str(walk.get("spawn", "")))
	_shot.flags = walk.get("flags", [])
	add_child(_shot)
	_shot.start()
	_camera = Camera3D.new()
	_camera.fov = float(walk.get("fov", DEFAULT_FOV))
	_camera.near = 0.05
	_camera.far = 4000.0
	add_child(_camera)
	var eye := float(walk.get("eye_m", DEFAULT_EYE_M))
	var settle := int(walk.get("settle_frames", 20))
	await _frames(int(walk.get("first_settle_frames", 90)))
	var points: Array = walk.get("points", []).duplicate()
	if bool(walk.get("auto_targets", false)):
		points += _target_points(walk.get("pois", []), eye)
	for p: Dictionary in points:
		var at := _eye(p["at"], eye)
		var look := _eye(p["look"], at.y, true)
		_camera.global_position = at
		_camera.look_at(look, Vector3.UP)
		_camera.make_current()
		await _frames(settle)
		_camera.make_current()
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		image.save_png(out_dir.path_join("%s.png" % str(p["id"])))
		print("WALK %s at %s" % [p["id"], at])
	get_tree().quit()


## The eye over [x, z] (the ground under it by ray, plus `up`), or [x, y, z] as given; `level` keeps a look's y.
func _eye(v: Array, up: float, level := false) -> Vector3:
	if v.size() == 3:
		return Vector3(float(v[0]), float(v[1]), float(v[2]))
	var x := float(v[0])
	var z := float(v[1])
	if level:
		return Vector3(x, up, z)
	var space := get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(Vector3(x, RAY_FROM_M, z), Vector3(x, RAY_FROM_M - RAY_DEPTH_M, z))
	var hit := space.intersect_ray(q)
	var ground := float(hit["position"].y) if not hit.is_empty() else 0.0
	return Vector3(x, ground + up, z)


## A still per Interactable and per POI: [{"id", "at": [eye x, y, z], "look": [x, y, z]}].
func _target_points(pois: Array, eye: float) -> Array:
	var targets: Array[Dictionary] = []
	for n: Node in _shot.find_children("*", "Interactable", true, false):
		var area := n as Interactable
		if area.is_visible_in_tree():
			targets.append({"id": "int_%s" % area.name, "pos": area.global_position + Vector3.UP * TARGET_UP_M})
	var party := _shot.find_children("*", "FieldController", true, false)
	var ref_y := (party[0] as Node3D).global_position.y if not party.is_empty() else 0.0
	for poi: Dictionary in pois:
		var at: Array = poi["at"]
		var ground := _floor_near(float(at[0]), float(at[1]), ref_y)
		var y := (ground if not is_nan(ground) else 0.0) + TARGET_UP_M
		targets.append({"id": "poi_%s" % poi["id"], "pos": Vector3(float(at[0]), y, float(at[1]))})
	var out: Array = []
	for t: Dictionary in targets:
		var pos: Vector3 = t["pos"]
		var stand := _stand(pos, eye)
		out.append({"id": t["id"], "at": [stand.x, stand.y, stand.z], "look": [pos.x, pos.y, pos.z]})
	return out


## The first eye STAND_M off `target`, over ground near its level, with nothing solid between it and the target.
func _stand(target: Vector3, eye: float) -> Vector3:
	var space := get_world_3d().direct_space_state
	for dist: float in STAND_M:
		for k in SIDES:
			var a := TAU * k / SIDES
			var x := target.x + cos(a) * dist
			var z := target.z + sin(a) * dist
			var ground := _ground(x, z, target.y + STAND_STEP_M)
			if is_nan(ground) or absf(ground + TARGET_UP_M - target.y) > STAND_STEP_M:
				continue
			var from := Vector3(x, ground + eye, z)
			var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(from, target))
			if hit.is_empty() or from.distance_to(hit["position"]) > from.distance_to(target) - CLEAR_SLACK_M:
				return from
	return target + Vector3(0.0, eye - TARGET_UP_M, STAND_M[0])


## Of every floor under [x, z] (a roof, the deck, the sea floor), the one nearest `ref_y` (the party's level), or NAN.
func _floor_near(x: float, z: float, ref_y: float) -> float:
	var best := NAN
	var from_y := RAY_FROM_M
	for i in FLOOR_LAYERS:
		var y := _ground(x, z, from_y)
		if is_nan(y):
			break
		if is_nan(best) or absf(y - ref_y) < absf(best - ref_y):
			best = y
		from_y = y - FLOOR_STEP_M
	return best


## The level's collision under [x, z] from `from_y` down (under a roof: start below it), or NAN.
func _ground(x: float, z: float, from_y := RAY_FROM_M) -> float:
	var space := get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(Vector3(x, from_y, z), Vector3(x, from_y - RAY_DEPTH_M, z))
	var hit := space.intersect_ray(q)
	return float(hit["position"].y) if not hit.is_empty() else NAN


func _frames(n: int) -> void:
	for i in n:
		_camera.make_current()
		await get_tree().process_frame
