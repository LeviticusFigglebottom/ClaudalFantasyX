extends SceneTree
## M1-ENV-08/09 GPU check: which VegetationPlant LODs Godot really draws at each camera distance.
## Three unshaded quads (LOD0 red, LOD1 green, LOD2 blue) sit at the same distance in three
## directions, and the probe reads their pixels back: from a still camera (a new plant per distance,
## so no LOD has a history), then sweeping in and sweeping out. Each row must draw exactly one LOD
## opaque, or crossfade the faded last LOD in over the LOD below within lod_margin_m of that switch.
## The unit test's model of Godot's range check (tests/unit/test_vegetation_plant.gd) is checked
## against this. Run it with a renderer (the headless dummy draws nothing):
##   godot-render --path . --rendering-driver vulkan -s res://game/levels/_tests/vegetation/lod_sweep_probe.gd
## It prints one row per distance and `LOD_SWEEP PASS` or `LOD_SWEEP FAIL <n>`, and exits 0 or 1.

const ANGLES_DEG: Array[float] = [-12.0, 0.0, 12.0]
const COLORS: Array[Color] = [Color(1, 0, 0), Color(0, 1, 0), Color(0, 0, 1)]
const BANDS_M: Array[Vector2] = [Vector2(40.0, 50.0), Vector2(114.0, 126.0), Vector2(390.0, 410.0)]
const STEP_M := 0.5
## Screen-space size of each quad, as a fraction of its distance.
const QUAD_SCALE := 0.12
## A channel above OPAQUE reads as drawn opaque; above DRAWN as drawn at all (a fading instance).
const OPAQUE := 0.97
const DRAWN := 0.03
const SETTLE_FRAMES := 4
const STEP_FRAMES := 3

var _cam: Camera3D
var _fails := 0


func _init() -> void:
	root.size = Vector2i(320, 180)
	_cam = Camera3D.new()
	_cam.fov = 60.0
	_cam.far = 1000.0
	root.add_child(_cam)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color.BLACK
	env.environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	root.add_child(env)
	await process_frame
	var dists: Array[float] = []
	for band: Vector2 in BANDS_M:
		var x := band.x
		while x <= band.y + 0.001:
			dists.append(x)
			x += STEP_M
	print("STILL (a new plant per distance)")
	for d in dists:
		var p := _make_plant(d)
		root.add_child(p)
		for f in SETTLE_FRAMES:
			await process_frame
		_report(p, d)
		p.free()
	for history: String in ["IN", "OUT"]:
		print("SWEEP %s" % history)
		var seq := dists.duplicate()
		if history == "IN":
			seq.reverse()
		var p := _make_plant(seq[0])
		root.add_child(p)
		for d: float in seq:
			_place(p, d)
			for f in STEP_FRAMES:
				await process_frame
			_report(p, d)
		p.free()
	print("LOD_SWEEP PASS" if _fails == 0 else "LOD_SWEEP FAIL %d" % _fails)
	quit(0 if _fails == 0 else 1)


func _make_plant(d: float) -> VegetationPlant:
	var plant := VegetationPlant.new()
	plant.shelter = VegetationPlant.Shelter.OPEN
	for i in COLORS.size():
		var mi := MeshInstance3D.new()
		mi.name = "probe-lod%d" % i
		mi.mesh = QuadMesh.new()
		var m := StandardMaterial3D.new()
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.albedo_color = COLORS[i]
		m.cull_mode = BaseMaterial3D.CULL_DISABLED
		mi.material_override = m
		plant.add_child(mi)
	_place(plant, d)
	return plant


func _dir(i: int) -> Vector3:
	var a := deg_to_rad(ANGLES_DEG[i])
	return Vector3(sin(a), 0.0, -cos(a))


func _place(plant: VegetationPlant, d: float) -> void:
	for i in COLORS.size():
		var mi := plant.get_child(i) as MeshInstance3D
		mi.position = _dir(i) * d
		mi.scale = Vector3.ONE * d * QUAD_SCALE


func _report(plant: VegetationPlant, d: float) -> void:
	var img := root.get_texture().get_image()
	var cells: Array[String] = []
	var opaque := 0
	var fading: Array[int] = []
	for i in COLORS.size():
		var c := img.get_pixelv(Vector2i(_cam.unproject_position(_dir(i) * 10.0)))
		var v := maxf(c.r, maxf(c.g, c.b))
		if v > OPAQUE:
			opaque += 1
			cells.append("%d     " % i)
		elif v > DRAWN:
			fading.append(i)
			cells.append("%d(%.2f)" % [i, v])
		else:
			cells.append(".     ")
	var ends := plant.lod_end_m
	var last := ends.size() - 1
	var crossfade := absf(d - ends[last - 1]) <= plant.lod_margin_m and plant.lod_fade_m > 0.0
	var past_end := d >= ends[last] - plant.lod_fade_m
	var ok := false
	if past_end:
		ok = opaque <= 1 and fading.size() <= 1 and (fading.is_empty() or fading[0] == last)
	elif crossfade:
		ok = opaque >= 1 and opaque + fading.size() <= 2
	else:
		ok = opaque == 1 and fading.is_empty()
	if not ok:
		_fails += 1
	print("  d=%6.1f  %s%s" % [d, " ".join(cells), "" if ok else "   <- FAIL"])
