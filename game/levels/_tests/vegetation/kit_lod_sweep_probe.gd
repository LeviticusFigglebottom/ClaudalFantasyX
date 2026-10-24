extends SceneTree
## M1-ENV-10 GPU check: which LOD of a real Haluna kit piece Godot draws at each camera distance,
## dressed two ways: by HalunaDresser.instance_piece (the layout's switch) and by the import rules
## alone (the imported .glb as it is, game/data/import/haluna_kit.json). Every mesh gets an unshaded
## override (LOD0 red, LOD1 green), and the probe counts red and green pixels in the frame: from a
## still camera (a new instance per distance), then sweeping in and sweeping out. Each row must draw
## exactly one LOD. lod_sweep_probe.gd does the same for VegetationPlant. Run it with a renderer:
##   godot-render --path . --rendering-driver vulkan -s res://game/levels/_tests/vegetation/kit_lod_sweep_probe.gd
## It prints one row per distance and `KIT_LOD_SWEEP PASS` or `KIT_LOD_SWEEP FAIL <n>`, and exits 0 or 1.

const PIECE := "dock_haluna"
## The mood layout (its later home on the Haluna zone branch is the second path).
const LAYOUTS: Array[String] = [
	"res://game/levels/_tests/haluna_mood/haluna_layout.json",
	"res://game/levels/ch02/haluna/haluna_layout.json",
]
const KIND := "haluna_kit"
const COLORS: Array[Color] = [Color(1, 0, 0), Color(0, 1, 0)]
## Half-width of the band swept around each switch (m), and the step.
const BAND_HALF_M := 6.0
const STEP_M := 0.5
const FOV_DEG := 12.0
## A pixel whose channel is above this (and the other channels below 1 - this) counts for that LOD.
const CHANNEL := 0.5
const SETTLE_FRAMES := 4
const STEP_FRAMES := 3

var _cam: Camera3D
var _fails := 0
var _dresser: HalunaDresser


func _init() -> void:
	root.size = Vector2i(320, 180)
	_cam = Camera3D.new()
	_cam.fov = FOV_DEG
	_cam.far = 1000.0
	root.add_child(_cam)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color.BLACK
	env.environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	root.add_child(env)
	_dresser = HalunaDresser.new()
	for path in LAYOUTS:
		if FileAccess.file_exists(path):
			_dresser.layout = HalunaDresser._load_json(path)
			break
	await process_frame
	var rules := AssetImportRules.load_rules(KIND)
	var modes := {
		"DRESSER": float(_dresser.layout.get("lod1_from_m", 0.0)),
		"IMPORT": float((rules["lods"]["end_m"] as Array)[0]),
	}
	for mode: String in modes:
		var switch_m: float = modes[mode]
		var dists: Array[float] = []
		var x := switch_m - BAND_HALF_M
		while x <= switch_m + BAND_HALF_M + 0.001:
			dists.append(x)
			x += STEP_M
		print("%s (switch at %.1f m) STILL (a new piece per distance)" % [mode, switch_m])
		for d in dists:
			var p := _make(mode, d)
			for f in SETTLE_FRAMES:
				await process_frame
			_report(d)
			p.free()
		for history: String in ["IN", "OUT"]:
			print("%s SWEEP %s" % [mode, history])
			var seq := dists.duplicate()
			if history == "IN":
				seq.reverse()
			var p := _make(mode, seq[0])
			for d: float in seq:
				p.position = Vector3(0.0, 0.0, -d)
				for f in STEP_FRAMES:
					await process_frame
				_report(d)
			p.free()
	_dresser.free()
	print("KIT_LOD_SWEEP PASS" if _fails == 0 else "KIT_LOD_SWEEP FAIL %d" % _fails)
	quit(0 if _fails == 0 else 1)


## The piece at `d` m straight ahead, its meshes coloured by LOD.
func _make(mode: String, d: float) -> Node3D:
	var node: Node3D
	if mode == "DRESSER":
		node = _dresser.instance_piece(PIECE)
	else:
		var packed := load(String(_dresser.layout.get("kit_dir", "")) + PIECE + ".glb") as PackedScene
		node = packed.instantiate() as Node3D
	for child: Node in node.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		var m := StandardMaterial3D.new()
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.albedo_color = COLORS[1 if String(mi.name).ends_with(LodChain.SUFFIX + "1") else 0]
		m.cull_mode = BaseMaterial3D.CULL_DISABLED
		mi.material_override = m
	node.position = Vector3(0.0, 0.0, -d)
	root.add_child(node)
	return node


func _report(d: float) -> void:
	var img := root.get_texture().get_image()
	var counts: Array[int] = [0, 0]
	for y in img.get_height():
		for x in img.get_width():
			var c := img.get_pixel(x, y)
			if c.r > CHANNEL and c.g < 1.0 - CHANNEL:
				counts[0] += 1
			elif c.g > CHANNEL and c.r < 1.0 - CHANNEL:
				counts[1] += 1
	var drawn := (1 if counts[0] > 0 else 0) + (1 if counts[1] > 0 else 0)
	var ok := drawn == 1
	if not ok:
		_fails += 1
	print("  d=%6.1f  lod0 px %5d  lod1 px %5d%s" % [d, counts[0], counts[1], "" if ok else "   <- FAIL"])
