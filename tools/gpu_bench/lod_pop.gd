class_name LodPopBench
extends Node
## LOD pop at a palm's switch distance (M1-ENV-03). Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 res://tools/gpu_bench/lod_pop.tscn -- \
##     --out=C:/abs/dir [--plant=Plants/PalmA --from=35 --to=60 --step=0.25 --settle=8 --preset=high]
## Puts a camera 1.6 m up, looking at the plant's crown against the sky, and backs it away from
## --from to --to metres in --step steps, letting each position settle (TAA) for --settle frames.
## Writes pop.csv: distance, mean absolute luminance change from the previous step over the frame.
## A hard LOD switch shows as one step far above its neighbours; a cross-fade spreads it out.
## --sweep=switch holds the camera at --at metres and moves the plant's LOD0 switch distance from
## --from to --to instead, so the only change between steps is the LOD (camera motion would mask it).

const SCENE := "res://game/levels/_tests/vegetation/vegetation_test.tscn"
const EYE_HEIGHT_M := 1.6
const CROWN_HEIGHT_M := 7.0
const REC709 := Vector3(0.2126, 0.7152, 0.0722)

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
	win.size = Vector2i(1280, 720)
	var scene := (load(SCENE) as PackedScene).instantiate()
	add_child(scene)
	var plant := scene.get_node(NodePath(str(_opts.get("plant", "Plants/PalmA")))) as Node3D
	var cam := Camera3D.new()
	cam.fov = 40.0
	scene.add_child(cam)
	cam.make_current()
	await get_tree().process_frame
	var gs := GraphicsSettings.new()
	gs.set_preset(str(_opts.get("preset", "high")))
	var envs := scene.find_children("*", "WorldEnvironment", true, false)
	gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
	var base := plant.global_position
	var away := Vector3(0.3, 0.0, 1.0).normalized()
	var d := float(_opts.get("from", 35.0))
	var to := float(_opts.get("to", 60.0))
	var step := float(_opts.get("step", 0.25))
	var settle := int(_opts.get("settle", 8))
	var prev := PackedFloat32Array()
	var f := FileAccess.open(out.path_join("pop.csv"), FileAccess.WRITE)
	f.store_line("distance_m,mean_abs_dlum")
	var sweep_switch := str(_opts.get("sweep", "")) == "switch"
	var lods := plant.get("lod_end_m") as PackedFloat32Array
	while d <= to + 1e-4:
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
		if _opts.has("png") and (prev.is_empty() or d + step > to + 1e-4):
			img.save_png(out.path_join("at_%.1f.png" % d))
		var lum := _luminance(img)
		if prev.size() == lum.size():
			var acc := 0.0
			for i in lum.size():
				acc += absf(lum[i] - prev[i])
			f.store_line("%.2f,%.6f" % [d, acc / lum.size()])
		prev = lum
		d += step
	f.close()
	print("LOD_POP wrote %s" % out.path_join("pop.csv"))
	get_tree().quit()


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
