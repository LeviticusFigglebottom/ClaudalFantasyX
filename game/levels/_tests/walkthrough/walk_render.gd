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

const RESOLUTION := Vector2i(960, 540)
const DEFAULT_EYE_M := 1.6
const DEFAULT_FOV := 60.0
const RAY_FROM_M := 60.0
const RAY_DEPTH_M := 160.0

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
	for p: Dictionary in walk["points"]:
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


func _frames(n: int) -> void:
	for i in n:
		_camera.make_current()
		await get_tree().process_frame
