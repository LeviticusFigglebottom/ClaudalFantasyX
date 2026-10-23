class_name SwatchCard
extends Node3D
## The palette swatch card (M1-ART-04): every material-input swatch of docs/kb/art/palette.json drawn as a
## flat unshaded patch through the project tonemap, so the on-screen value of each palette entry can be
## measured (docs/kb/art/README.md, "Two kinds of colour value").
## Layout, top to bottom (17 columns, 1280x720 under an orthographic camera at 40 px per metre):
## - rows 0-1: a neutral ladder, linear 2^-8 to 2^4.375 in 3/8-stop steps (the tonemap curve itself);
## - rows 2-5, 6-9, 10-13: the swatches at scene-referred level 0.5, 1.0 and 2.0 (-1, 0, +1 stop),
##   in palette.json order. UI swatches are skipped: UI is drawn after the tonemap, so its hex IS on screen.
## The WorldEnvironment is the reference grade: AgX, white 12, contrast 1.25 (engine default), exposure 1,
## no adjustment, no glow, no fog, no LUT. swatch_measure.tscn reads the patches back.

const PALETTE_PATH := "res://docs/kb/art/palette.json"
const SHADER_PATH := "res://game/levels/_tests/swatches/swatch_flat.gdshader"
## Swatch families that are post-tonemap already (2D UI) and therefore not on the card.
const SKIP_FAMILIES: Array[String] = ["ui"]
## Scene-referred levels of the three swatch bands (stops -1, 0, +1 around the unit level).
const LEVELS: Array[float] = [0.5, 1.0, 2.0]
const COLUMNS := 17
const LADDER_ROWS := 2
const ROWS_PER_BAND := 4
const LADDER_MIN_STOP := -8.0
const LADDER_STEP_STOPS := 0.375
## Geometry in metres (40 px per metre at the 1280x720 shot resolution).
const CELL_SIZE := Vector2(1.6, 1.0)
const CELL_PITCH := Vector2(1.85, 1.25)
const CAMERA_HEIGHT_M := 18.0
const CAMERA_DISTANCE_M := 10.0

## One entry per patch: {"kind": "ladder" | "swatch", "name", "level", "lin": Vector3, "pos": Vector3}.
var cells: Array[Dictionary] = []
var camera: Camera3D


func _ready() -> void:
	camera = get_node_or_null("ShotCamera") as Camera3D
	if camera != null:
		camera.projection = Camera3D.PROJECTION_ORTHOGONAL
		camera.size = CAMERA_HEIGHT_M
		camera.position = Vector3(0.0, 0.0, CAMERA_DISTANCE_M)
	cells = build_cells(load_swatches())
	var shader := load(SHADER_PATH) as Shader
	var quad := QuadMesh.new()
	quad.size = CELL_SIZE
	for cell in cells:
		var mat := ShaderMaterial.new()
		mat.shader = shader
		mat.set_shader_parameter(&"lin", cell["lin"])
		mat.set_shader_parameter(&"level", cell["level"])
		var mi := MeshInstance3D.new()
		mi.mesh = quad
		mi.material_override = mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.position = cell["pos"]
		mi.name = "%s_%s" % [cell["name"], str(cell["level"]).replace(".", "_")]
		add_child(mi)


## Material-input swatches in palette order: [{"name", "lin": Vector3}].
static func load_swatches() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(PALETTE_PATH))
	if not data is Dictionary:
		push_error("swatch card: cannot parse %s" % PALETTE_PATH)
		return out
	var swatches: Dictionary = (data as Dictionary).get("swatches", {})
	for swatch_name: String in swatches:
		var s: Dictionary = swatches[swatch_name]
		if SKIP_FAMILIES.has(str(s.get("family", ""))):
			continue
		var l: Array = s["linear"]
		out.append({"name": swatch_name, "lin": Vector3(float(l[0]), float(l[1]), float(l[2]))})
	return out


static func build_cells(swatches: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for i in LADDER_ROWS * COLUMNS:
		var v := pow(2.0, LADDER_MIN_STOP + LADDER_STEP_STOPS * i)
		out.append(
			{"kind": "ladder", "name": "grey_%02d" % i, "level": 1.0, "lin": Vector3(v, v, v), "pos": cell_pos(i)}
		)
	for band in LEVELS.size():
		for i in swatches.size():
			var slot := LADDER_ROWS * COLUMNS + band * ROWS_PER_BAND * COLUMNS + i
			var s := swatches[i]
			out.append(
				{"kind": "swatch", "name": s["name"], "level": LEVELS[band], "lin": s["lin"], "pos": cell_pos(slot)}
			)
	return out


## World position of patch slot n (row-major, 17 columns, rows from the top).
static func cell_pos(slot: int) -> Vector3:
	var rows := LADDER_ROWS + LEVELS.size() * ROWS_PER_BAND
	var row := slot / COLUMNS
	var col := slot % COLUMNS
	var x := (col - (COLUMNS - 1) * 0.5) * CELL_PITCH.x
	var y := ((rows - 1) * 0.5 - row) * CELL_PITCH.y
	return Vector3(x, y, 0.0)
