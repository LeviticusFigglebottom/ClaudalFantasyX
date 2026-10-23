extends Node
## Reads the swatch card back (M1-ART-04): renders swatch_card.tscn, averages the centre of every patch, and
## writes the measured on-screen sRGB to JSON. Needs a real renderer (ADR 0009), not --headless:
##   ~/.cache/hymn/godot-4.6.3+ds-2/godot-render --path . --audio-driver Dummy --fixed-fps 60 \
##     res://game/levels/_tests/swatches/swatch_measure.tscn -- --out=/abs/path.json [--exposure=1.0]
##     [--saturation=1.0]
## Without overrides the grade is the card's reference grade (AgX, white 12, exposure 1, no adjustment).
## The palette's `onscreen` fields come from this output (docs/kb/art/README.md).

const CARD_SCENE := "res://game/levels/_tests/swatches/swatch_card.tscn"
const SIZE := Vector2i(1280, 720)
const SETTLE_FRAMES := 8
## Half-size of the averaged box at each patch centre, in px (patches are 64 x 40 px).
const SAMPLE_HALF := Vector2i(12, 8)


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var opts := _parse_args()
	get_window().size = SIZE
	var card := (load(CARD_SCENE) as PackedScene).instantiate() as SwatchCard
	add_child(card)
	var env := (card.get_node("WorldEnvironment") as WorldEnvironment).environment
	env.tonemap_exposure = float(opts.get("exposure", env.tonemap_exposure))
	if opts.has("camera_multiplier"):
		# ADR 0014: with physical light units off, CameraAttributesPractical.exposure_multiplier is a plain
		# multiplier on top of tonemap_exposure (the cinematic trim). This checks it.
		var attrs := CameraAttributesPractical.new()
		attrs.exposure_multiplier = float(opts["camera_multiplier"])
		(card.get_node("WorldEnvironment") as WorldEnvironment).camera_attributes = attrs
	if opts.has("saturation"):
		env.adjustment_enabled = true
		env.adjustment_saturation = float(opts["saturation"])
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	image.convert(Image.FORMAT_RGB8)
	if image.get_size() != SIZE:
		push_error("swatch measure: captured %s, wanted %s" % [image.get_size(), SIZE])
		get_tree().quit(1)
		return
	# Orthographic, keep-height camera centred on the card: metres map to pixels linearly.
	var ppm := float(SIZE.y) / SwatchCard.CAMERA_HEIGHT_M
	var ladder: Array = []
	var swatches := {}
	for cell in card.cells:
		var pos := cell["pos"] as Vector3
		var px := Vector2(SIZE.x * 0.5 + pos.x * ppm, SIZE.y * 0.5 - pos.y * ppm)
		var c := _average(image, Vector2i(px.round()))
		var entry := {"level": cell["level"], "hex": "#" + c.to_html(false).to_upper(), "srgb": [c.r, c.g, c.b]}
		if cell["kind"] == "ladder":
			entry["lin"] = (cell["lin"] as Vector3).x
			ladder.append(entry)
		else:
			if not swatches.has(cell["name"]):
				swatches[cell["name"]] = {}
			(swatches[cell["name"]] as Dictionary)[str(cell["level"])] = entry["hex"]
	var out := {
		"grade":
		{
			"tonemap": "agx",
			"agx_white": env.tonemap_agx_white,
			"agx_contrast": env.tonemap_agx_contrast,
			"exposure": env.tonemap_exposure,
			"saturation": env.adjustment_saturation if env.adjustment_enabled else 1.0,
		},
		"renderer": RenderingServer.get_video_adapter_name(),
		"ladder": ladder,
		"swatches": swatches,
	}
	var path := str(opts.get("out", "user://swatch_measure.json"))
	FileAccess.open(path, FileAccess.WRITE).store_string(JSON.stringify(out, " ", false))
	print("SWATCH MEASURE wrote %s (%d patches)" % [path, card.cells.size()])
	get_tree().quit(0)


func _average(image: Image, centre: Vector2i) -> Color:
	var sum := Vector3.ZERO
	var n := 0
	for y in range(centre.y - SAMPLE_HALF.y, centre.y + SAMPLE_HALF.y + 1):
		for x in range(centre.x - SAMPLE_HALF.x, centre.x + SAMPLE_HALF.x + 1):
			var p := image.get_pixel(clampi(x, 0, image.get_width() - 1), clampi(y, 0, image.get_height() - 1))
			sum += Vector3(p.r, p.g, p.b)
			n += 1
	sum /= float(n)
	return Color(sum.x, sum.y, sum.z)


func _parse_args() -> Dictionary:
	var opts := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--") and arg.contains("="):
			var kv := arg.trim_prefix("--").split("=", true, 1)
			opts[kv[0]] = kv[1]
	return opts
