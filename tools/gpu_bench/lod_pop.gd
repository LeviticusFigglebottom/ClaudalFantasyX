class_name LodPopBench
extends Node
## LOD pop at a palm's switch distance (M1-ENV-03, M1-ENV-09). Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 res://tools/gpu_bench/lod_pop.tscn -- \
##     --out=C:/abs/dir [--plant=Plants/PalmA --from=35 --to=60 --step=0.25 --settle=8 --preset=high]
## Puts a camera 1.6 m up, looking at the plant's crown against the sky, and backs it away from
## --from to --to metres in --step steps, letting each position settle (TAA) for --settle frames.
## Writes pop.csv: distance, mean absolute luminance change from the previous step over the frame,
## and the objects and draw calls the viewport drew (a hole drops them, a double draw raises them).
## A hard LOD switch shows as one step far above its neighbours; a cross-fade spreads it out.
## --sweep=switch holds the camera at --at metres and moves the plant's LOD0 switch distance from
## --from to --to instead, so the only change between steps is the LOD (camera motion would mask it).
## M1-ENV-09 additions:
## - --direction=in walks from --to down to --from (default out). --solo hides every other plant and
##   the grass, so the draw counts are the one plant's. --hide-lod=N hides that LOD's meshes (diagnosis).
##   --res=WxH sizes the window (default 1280x720).
## - A moving camera: --settle=1 with --step at the speed per frame (e.g. 0.0833 = 5 m/s at 60 fps);
##   --png-every=N saves at_<d>.png every N steps.
## - --bench=116,120,124 --clones=N: N copies of the plant on an arc in view, all at each distance
##   from the camera; prints "LOD_POP_BENCH <d> median_ms p99_ms objects" over --frames frames.

const SCENE := "res://game/levels/_tests/vegetation/vegetation_test.tscn"
const EYE_HEIGHT_M := 1.6
const CROWN_HEIGHT_M := 7.0
const REC709 := Vector3(0.2126, 0.7152, 0.0722)
## The bench's arc of clones, as a share of the camera's horizontal field of view.
const ARC_FOV_SHARE := 0.8

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	var res := str(_opts.get("res", "1280x720")).split("x")
	win.size = Vector2i(int(res[0]), int(res[1]))
	var scene := (load(SCENE) as PackedScene).instantiate()
	add_child(scene)
	var plant := scene.get_node(NodePath(str(_opts.get("plant", "Plants/PalmA")))) as Node3D
	if _opts.has("solo") or _opts.has("bench"):
		for n in scene.get_node(^"Plants").get_children():
			(n as Node3D).visible = n == plant
		(scene.get_node(^"Ground") as Node3D).visible = false
	if _opts.has("hide-lod"):  # diagnosis: which LOD a draw count belongs to
		for n in plant.find_children("*", "MeshInstance3D", true, false):
			if VegetationPlant.lod_index(String(n.name)) == int(_opts["hide-lod"]):
				(n as MeshInstance3D).visible = false
	var cam := Camera3D.new()
	cam.fov = 40.0
	cam.far = 1000.0
	scene.add_child(cam)
	cam.make_current()
	await get_tree().process_frame
	var gs := GraphicsSettings.new()
	gs.set_preset(str(_opts.get("preset", "high")))
	var envs := scene.find_children("*", "WorldEnvironment", true, false)
	gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
	if _opts.has("bench"):
		await _bench(scene, plant, cam)
		get_tree().quit()
		return
	var base := plant.global_position
	var away := Vector3(0.3, 0.0, 1.0).normalized()
	var from := float(_opts.get("from", 35.0))
	var to := float(_opts.get("to", 60.0))
	var step := float(_opts.get("step", 0.25))
	var inward := str(_opts.get("direction", "out")) == "in"
	var d := to if inward else from
	var settle := int(_opts.get("settle", 8))
	var png_every := int(_opts.get("png-every", 0))
	var prev := PackedFloat32Array()
	var f := FileAccess.open(out.path_join("pop.csv"), FileAccess.WRITE)
	f.store_line("distance_m,mean_abs_dlum,objects,draw_calls")
	var sweep_switch := str(_opts.get("sweep", "")) == "switch"
	var lods := plant.get("lod_end_m") as PackedFloat32Array
	var rid := get_viewport().get_viewport_rid()
	var n := 0
	while d >= from - 1e-4 and d <= to + 1e-4:
		var cam_d := float(_opts.get("at", 45.0)) if sweep_switch else d
		cam.global_position = base + away * cam_d + Vector3(0.0, EYE_HEIGHT_M, 0.0)
		cam.look_at(base + Vector3(0.0, CROWN_HEIGHT_M, 0.0), Vector3.UP)
		if sweep_switch:
			var l := lods.duplicate()
			l[0] = d
			plant.set("lod_end_m", l)
			plant.call("apply")
		for i in settle:
			await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		var last := (d - step < from - 1e-4) if inward else (d + step > to + 1e-4)
		if (_opts.has("png") and (prev.is_empty() or last)) or (png_every > 0 and n % png_every == 0):
			img.save_png(out.path_join("at_%.2f.png" % d))
		var objects := RenderingServer.viewport_get_render_info(
			rid,
			RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,
			RenderingServer.VIEWPORT_RENDER_INFO_OBJECTS_IN_FRAME
		)
		var draws := RenderingServer.viewport_get_render_info(
			rid,
			RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,
			RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME
		)
		var lum := _luminance(img)
		if prev.size() == lum.size():
			var acc := 0.0
			for i in lum.size():
				acc += absf(lum[i] - prev[i])
			f.store_line("%.3f,%.6f,%d,%d" % [d, acc / lum.size(), objects, draws])
		prev = lum
		d += -step if inward else step
		n += 1
	f.close()
	print("LOD_POP wrote %s" % out.path_join("pop.csv"))
	get_tree().quit()


## The crossfade band's cost: --clones copies of the plant on an arc in view, each at the bench
## distance from a fixed camera, so every copy is in the same LOD state.
func _bench(scene: Node3D, plant: Node3D, cam: Camera3D) -> void:
	var clones := int(_opts.get("clones", 40))
	var copies: Array[Node3D] = [plant]
	for i in clones - 1:
		var c := plant.duplicate() as Node3D
		scene.get_node(^"Plants").add_child(c)
		copies.append(c)
	var base := plant.global_position
	var eye := base + Vector3(0.0, EYE_HEIGHT_M, 0.0)
	cam.global_position = eye
	var half := deg_to_rad(cam.fov) * 0.5 * ARC_FOV_SHARE * float(get_window().size.x) / float(get_window().size.y)
	var rid := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	for dist_s in str(_opts["bench"]).split(",", false):
		var dist := float(dist_s)
		for i in copies.size():
			var a := lerpf(-half, half, (float(i) + 0.5) / float(copies.size()))
			copies[i].global_position = base + Vector3(sin(a), 0.0, -cos(a)) * dist
		cam.look_at(eye + Vector3(0.0, (CROWN_HEIGHT_M - EYE_HEIGHT_M) / dist, -1.0) * dist, Vector3.UP)
		for i in 60:
			await RenderingServer.frame_post_draw
		var times: Array[float] = []
		for i in int(_opts.get("frames", 300)):
			await RenderingServer.frame_post_draw
			times.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
		times.sort()
		var objects := RenderingServer.viewport_get_render_info(
			rid,
			RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,
			RenderingServer.VIEWPORT_RENDER_INFO_OBJECTS_IN_FRAME
		)
		if _opts.has("png"):
			var img := get_viewport().get_texture().get_image()
			img.convert(Image.FORMAT_RGB8)
			img.save_png(str(_opts["out"]).path_join("bench_%s.png" % dist_s))
		print(
			(
				"LOD_POP_BENCH %s %.4f %.4f %d"
				% [dist_s, times[times.size() / 2], times[int(times.size() * 0.99)], objects]
			)
		)


## Luminance of every 4th pixel in each direction (enough for a mean, 16x fewer reads).
static func _luminance(img: Image) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	for y in range(0, img.get_height(), 4):
		for x in range(0, img.get_width(), 4):
			var c := img.get_pixel(x, y)
			out.append(c.r * REC709.x + c.g * REC709.y + c.b * REC709.z)
	return out


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
