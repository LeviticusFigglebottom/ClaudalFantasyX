extends SceneTree
## M1-ARC-15 / RND-12 S2 probe: does the Incremental radiance cubemap follow a turning sun?
## Usage (software or GPU; one process, ~10 min on lavapipe at 480x270):
##   godot --path . --rendering-driver vulkan --fixed-fps 60 -s res://tools/gpu_bench/sky_sun_probe.gd
## Renders haluna_mood (H01) with a mirror sphere (roughness 0: shows the radiance cubemap) and a rough
## metal sphere in view, turns the sun 120 deg about Y and diffs the sphere pixels over the following
## frames against a reference made by forcing a full radiance re-render (dirtying the sky material).
## Runs twice: with the sun's authored sky_mode, then with SKY_MODE_LIGHT_AND_SKY.
## Reading it: "mirror vs before" rising and "mirror vs ref" falling to the noise floor (the authored
## Light Only case shows the floor) means the radiance followed the sun. Results:
## docs/kb/tech/graphics_settings.md, "Sky radiance and a turning sun".

const MOOD := "res://game/levels/_tests/haluna_mood/haluna_mood.tscn"
const SETTLE := 40
const CHECKS: Array[int] = [1, 4, 16, 64]

var mood: Node3D
var sun: DirectionalLight3D
var env: Environment
var mirror: MeshInstance3D
var rough: MeshInstance3D
var cam: Camera3D
var sun_basis0: Basis


func _initialize() -> void:
	_run.call_deferred()


func _frames(n: int) -> void:
	for i in n:
		await process_frame
	await RenderingServer.frame_post_draw


func _img() -> Image:
	var img := root.get_texture().get_image()
	img.convert(Image.FORMAT_RGBF)
	return img


func _region_mean(img: Image, center: Vector2i, r: int) -> Color:
	var acc := Color(0, 0, 0)
	var n := 0
	for y in range(center.y - r, center.y + r):
		for x in range(center.x - r, center.x + r):
			acc += img.get_pixel(x, y)
			n += 1
	return acc / float(n)


func _diff(a: Image, b: Image, center: Vector2i, r: int) -> float:
	var d := 0.0
	var n := 0
	for y in range(center.y - r, center.y + r):
		for x in range(center.x - r, center.x + r):
			var p := a.get_pixel(x, y) - b.get_pixel(x, y)
			d += absf(p.r) + absf(p.g) + absf(p.b)
			n += 1
	return d / float(n * 3)


func _sphere(metallic: float, roughness: float, at: Vector3) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	var s := SphereMesh.new()
	s.radius = 1.5
	s.height = 3.0
	m.mesh = s
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(1, 1, 1)
	mat.metallic = metallic
	mat.roughness = roughness
	m.material_override = mat
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mood.add_child(m)
	m.global_position = at
	return m


func _run() -> void:
	root.size = Vector2i(480, 270)
	mood = (load(MOOD) as PackedScene).instantiate() as Node3D
	root.add_child(mood)
	await _frames(1)
	cam = mood.get_node(^"Cameras/H01") as Camera3D
	cam.make_current()
	sun = mood.get_node(^"Sun") as DirectionalLight3D
	sun_basis0 = sun.global_basis
	env = (mood.get_node(^"WorldEnvironment") as WorldEnvironment).environment
	var vis := root.get_visible_rect().size
	print("PROBE visible rect %s root.size %s" % [vis, root.size])
	mirror = _sphere(1.0, 0.0, cam.project_position(Vector2(vis.x * 0.35, vis.y * 0.6), 12.0))
	rough = _sphere(1.0, 0.7, cam.project_position(Vector2(vis.x * 0.65, vis.y * 0.6), 12.0))
	print("PROBE sky process_mode=%d sun sky_mode=%d" % [env.sky.process_mode, sun.sky_mode])
	for mode: int in [sun.sky_mode, DirectionalLight3D.SKY_MODE_LIGHT_AND_SKY]:
		await _case(mode)
	quit()


func _case(mode: int) -> void:
	sun.sky_mode = mode as DirectionalLight3D.SkyMode
	sun.global_basis = sun_basis0
	await _frames(SETTLE)
	var before := _img()
	var w := before.get_width()
	var h := before.get_height()
	var c_s := Vector2i(w / 2, h / 8)
	var pm := Vector2i(int(w * 0.35), int(h * 0.6))
	var pr := Vector2i(int(w * 0.65), int(h * 0.6))
	var r := 4
	print("PROBE image %dx%d" % [w, h])
	sun.global_rotate(Vector3.UP, deg_to_rad(120.0))
	var shots := {}
	var done := 0
	for k in CHECKS:
		await _frames(k - done)
		done = k
		shots[k] = _img()
	# Reference: force a full radiance re-render (a sky material change dirties it) and settle.
	var mat := env.sky.sky_material as ShaderMaterial
	var v: Variant = mat.get_shader_parameter(&"horizon_curve")
	mat.set_shader_parameter(&"horizon_curve", float(v) + 0.0001)
	await _frames(2)
	mat.set_shader_parameter(&"horizon_curve", v)
	await _frames(SETTLE)
	var ref := _img()
	print("PROBE sky_mode=%d sky_px before->after(1f) diff=%.4f" % [mode, _diff(before, shots[1] as Image, c_s, r)])
	print("PROBE sky_mode=%d mirror before->ref=%.4f rough before->ref=%.4f" % [mode, _diff(before, ref, pm, r), _diff(before, ref, pr, r)])
	for k in CHECKS:
		var img := shots[k] as Image
		print("PROBE sky_mode=%d frame+%d  mirror vs ref=%.4f  rough vs ref=%.4f  mirror vs before=%.4f" % [mode, k, _diff(img, ref, pm, r), _diff(img, ref, pr, r), _diff(img, before, pm, r)])
	print("PROBE sky_mode=%d mirror mean before %s ref %s" % [mode, _region_mean(before, pm, r), _region_mean(ref, pm, r)])
