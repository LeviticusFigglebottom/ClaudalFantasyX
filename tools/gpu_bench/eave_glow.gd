class_name EaveGlowBench
extends Node
## Plants glowing under an eave (M1-ENV-03). Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 res://tools/gpu_bench/eave_glow.tscn -- --out=C:/abs/dir
##     [--camera=Cameras/Backlit --kind=palm]  (the floor shows when the leaves are backlit)
## In vegetation_test.tscn (camera FrangipaniClose) a 6 x 0.3 x 6 m roof with collision is placed on
## the sun ray 1 m above the crown of the frangipani nearest the camera's view, so the plant sits in the roof's
## shadow. Renders three frames: no roof; roof with the plant's shelter forced to 0 (the old
## behaviour: the leaves' through-shadow floor still lights them); roof with shelter AUTO (the probe
## sees the roof). Prints the mean linear luminance in a 240 px box around the plant for each.

const SCENE := "res://game/levels/_tests/vegetation/vegetation_test.tscn"
const ROOF_SIZE := Vector3(6.0, 0.3, 6.0)
## The roof sits this far above the plant's crown, on the sun ray (an eave over the whole plant).
const ROOF_ABOVE_CROWN_M := 1.0
const BOX_PX := 120
const SETTLE := 30

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
	var cam := scene.get_node(NodePath(str(_opts.get("camera", "Cameras/FrangipaniClose")))) as Camera3D
	cam.make_current()
	var plant := _nearest_plant(scene, cam)
	await _frames(SETTLE)
	var sun := scene.find_children("*", "DirectionalLight3D", true, false)[0] as DirectionalLight3D
	var sun_dir := sun.global_basis.z.normalized()
	var results := {"no_roof": _measure(cam, plant)}
	_save(out, "no_roof")
	var roof := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = ROOF_SIZE
	shape.shape = box
	roof.add_child(shape)
	var mesh := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = ROOF_SIZE
	mesh.mesh = bm
	roof.add_child(mesh)
	scene.add_child(roof)
	var above := float(plant.call("crown_height")) + ROOF_ABOVE_CROWN_M
	roof.global_position = plant.global_position + sun_dir * (above / maxf(sun_dir.y, 0.2))
	plant.set("shelter", 0.0)
	plant.call("set_shelter", 0.0)
	await _frames(SETTLE)
	results["roof_shelter_0"] = _measure(cam, plant)
	_save(out, "roof_shelter_0")
	await get_tree().physics_frame
	var sheltered := bool(plant.call("is_sheltered"))
	plant.call("set_shelter", 1.0 if sheltered else 0.0)
	await _frames(SETTLE)
	results["roof_auto"] = _measure(cam, plant)
	results["auto_detected"] = sheltered
	_save(out, "roof_auto")
	print("EAVE_GLOW %s" % JSON.stringify(results))
	get_tree().quit()


func _save(out: String, tag: String) -> void:
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	img.save_png(out.path_join(tag + ".png"))


func _nearest_plant(scene: Node, cam: Camera3D) -> Node3D:
	var best: Node3D = null
	var best_d := INF
	var fwd := -cam.global_basis.z
	for n in scene.find_children("*", "Node3D", true, false):
		if not n.has_method("set_shelter") or not str(n.scene_file_path).contains(str(_opts.get("kind", "frangipani"))):
			continue
		var to := (n as Node3D).global_position - cam.global_position
		var off := to.length() * (1.0 - fwd.dot(to.normalized()))
		if off < best_d:
			best_d = off
			best = n as Node3D
	return best


func _measure(cam: Camera3D, plant: Node3D) -> float:
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	var c := cam.unproject_position(plant.global_position + Vector3.UP * 1.5)
	var acc := 0.0
	var n := 0
	for y in range(int(c.y) - BOX_PX, int(c.y) + BOX_PX, 2):
		for x in range(int(c.x) - BOX_PX, int(c.x) + BOX_PX, 2):
			if x < 0 or y < 0 or x >= img.get_width() or y >= img.get_height():
				continue
			var p := img.get_pixel(x, y).srgb_to_linear()
			acc += p.r * 0.2126 + p.g * 0.7152 + p.b * 0.0722
			n += 1
	return acc / maxf(1.0, float(n))


func _frames(n: int) -> void:
	for i in n:
		await RenderingServer.frame_post_draw


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
