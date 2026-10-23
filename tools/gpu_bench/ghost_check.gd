class_name GhostCheck
extends Node
## Temporal ghosting check for the Undertow body (M1-RND-10 follow-up). Needs a real GPU and window:
##   godot --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/ghost_check.tscn -- \
##     --config=final|static --mode=moving|converged --out=C:/abs/dir
## A deterministic sequence on undertow_test.tscn (Horizon camera, High preset, 2560x1440): the camera
## pans at --pan-deg-s while an opaque ship-sized box near the camera sweeps across the storm, the
## storm runs at its fastest API settings (rotation_rad_s and time_scale at their undertow.json maxima)
## and a lightning flash is forced at --flash-frame. Every quantity advances by a fixed step per frame;
## the weather (water) clock is frozen so only the storm and the silhouette move.
##   --mode=moving     render the sequence after --history frames at the start pose; save the frames in
##                     --save (indices into the sequence) plus rois.json (the box's screen rect per frame)
##   --mode=converged  for each saved index, hold that frame's pose for --converge frames (TAA and the
##                     step jitter settle) and save it: the reference the moving frame should match
##   --config=final    undertow.json as shipped (High: 32 steps, curl_reuse 2, temporal_jitter)
##   --config=static   the same with the M1-RND-10 temporal levers off (44 steps, curl_reuse 1, no jitter)
##   --config=reference  48 steps, curl_reuse 1, jitter on; run with --mode=converged --converge=128 as
##                     the common ground truth for both configs
## Compare with: python tools/gpu_bench/ghost_stats.py <moving_dir> <converged_dir>

const SCENE := "res://game/levels/_tests/undertow/undertow_test.tscn"
const RES := Vector2i(2560, 1440)
const FPS := 60.0
const STATIC_HIGH := {"march_steps": 44, "curl_reuse": 1, "temporal_jitter": false}
## A common ground truth: the High variant's step cap, a fresh curl warp per step, jitter integrated.
const REFERENCE_HIGH := {"march_steps": 48, "curl_reuse": 1, "temporal_jitter": true}
## The ship: a dark opaque box this far in front of the start view, this far right of centre, this size.
const SHIP_DISTANCE_M := 450.0
const SHIP_OFFSET_M := 140.0
const SHIP_SIZE := Vector3(110.0, 70.0, 20.0)
const SHIP_HEIGHT_M := 75.0
const SHIP_COLOR := Color(0.03, 0.035, 0.04)
const FLASH_SITE := 0

var _opts: Dictionary = {}
var _rig: UndertowTestRig
var _storm: UndertowStorm
var _cam: Camera3D
var _ship: MeshInstance3D
var _start_basis: Basis
var _t0: float = 0.0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	if DisplayServer.get_name() == "headless" or out == "":
		printerr("GHOST needs a real window and --out=<abs dir>")
		get_tree().quit(2)
		return
	DirAccess.make_dir_recursive_absolute(out)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	win.size = RES
	_rig = (load(SCENE) as PackedScene).instantiate() as UndertowTestRig
	_rig.frame_step_s = 0.0
	add_child(_rig)
	_storm = _rig.storm
	_storm.playing = false
	_cam = _rig.horizon_camera
	_cam.make_current()
	for i in 3:
		await get_tree().process_frame
	var gs := GraphicsSettings.new()
	gs.set_preset("high")
	gs.apply_current(get_viewport(), _rig.world_environment.environment)
	var high := _storm.state.config["quality"]["high"] as Dictionary
	match str(_opts.get("config", "final")):
		"static":
			high.merge(STATIC_HIGH, true)
		"reference":
			high.merge(REFERENCE_HIGH, true)
	_storm.set_quality("high")
	var api := _storm.state.config["state"] as Dictionary
	_storm.rotation_rad_s = float((api["rotation_rad_s"] as Dictionary)["max"])
	_storm.time_scale = float((api["time_scale"] as Dictionary)["max"])
	_t0 = _storm.get_time()
	_start_basis = _cam.global_transform.basis
	_ship = _make_ship()
	add_child(_ship)
	var saves: Array[int] = []
	for s in str(_opts.get("save", "8,16,24,32,40,47")).split(",", false):
		saves.append(int(s))
	if str(_opts.get("mode", "moving")) == "converged":
		await _converged(saves, out)
	else:
		await _moving(saves, out)
	print("GHOST done: %s %s -> %s" % [_opts.get("config", "final"), _opts.get("mode", "moving"), out])
	get_tree().quit()


func _moving(saves: Array[int], out: String) -> void:
	var rois := {}
	_pose(0)
	for i in int(_opts.get("history", 90)):
		await _frame()
	var frames := int(_opts.get("frames", 48))
	for i in frames:
		_pose(i)
		await _frame()
		if saves.has(i):
			_save(out, i)
			rois[str(i)] = _ship_rect()
	var f := FileAccess.open(out.path_join("rois.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify(rois, "  "))


func _converged(saves: Array[int], out: String) -> void:
	for i in saves:
		_pose(i)
		for k in int(_opts.get("converge", 64)):
			await _frame()
		_save(out, i)


## Sequence frame i: camera yaw, storm clock and the forced flash, all a pure function of i.
func _pose(i: int) -> void:
	var yaw := deg_to_rad(float(_opts.get("pan-deg-s", 30.0)) / FPS * i)
	_cam.global_transform.basis = Basis(Vector3.UP, -yaw) * _start_basis
	_storm.state.clear_forced_flashes()
	var flash_frame := int(_opts.get("flash-frame", 20))
	var dt := _storm.time_scale / FPS
	if i >= flash_frame:
		_storm.force_flash(FLASH_SITE, _t0 + flash_frame * dt)
	_storm.set_time(_t0 + i * dt)


## One rendered frame; the step jitter advances (UndertowState.frame) as if the storm were playing.
func _frame() -> void:
	await RenderingServer.frame_post_draw
	_storm.state.frame += 1


func _make_ship() -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = SHIP_SIZE
	mi.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = SHIP_COLOR
	mat.roughness = 1.0
	mi.material_override = mat
	var fwd := -_start_basis.z
	fwd.y = 0.0
	fwd = fwd.normalized()
	var right := fwd.cross(Vector3.UP).normalized()
	mi.position = Vector3(_cam.global_position.x, SHIP_HEIGHT_M, _cam.global_position.z)
	mi.position += fwd * SHIP_DISTANCE_M + right * SHIP_OFFSET_M
	# Long side across the view (the node is not in the tree yet, so no look_at).
	mi.basis = Basis(fwd, Vector3.UP, -right)
	return mi


## Screen rect (x, y, w, h in pixels) of the ship's bounding box corners.
func _ship_rect() -> Array:
	var aabb := _ship.global_transform * _ship.get_aabb()
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for c in 8:
		var p := _cam.unproject_position(aabb.get_endpoint(c))
		lo = lo.min(p)
		hi = hi.max(p)
	return [lo.x, lo.y, hi.x - lo.x, hi.y - lo.y]


func _save(out: String, i: int) -> void:
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	img.save_png(out.path_join("f%02d.png" % i))


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
