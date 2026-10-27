extends Node
## Menu portrait renderer (M2-MNU-301, ADR 0120). Renders the entries of tools/portraits/portraits.json
## to transparent PNGs. Heroes: the characters track's review stage (AshaStage: the hero glb, hero
## materials, shader tier, face pose from the emotion tag, pinned wind, the Face camera aimed at the eye
## midpoint) is instanced once per emotion into a transparent SubViewport, with the manifest's framing
## and the backdrop nodes hidden. Nothing of the stage is copied: its own _ready poses and aims.
## Creatures (M2-MNU-302): each creatures.json actor in its own small world (see _render_creature), the
## same _capture().
## Run it through tools/portraits/render.sh (the lavapipe wrapper, one process per entry); it needs a
## real renderer, never --headless.
## User args (after `--`): --only=<id>[,<id>]  --emotions=<tag>[,<tag>]  --out-dir=<absolute dir>
##   --manifest=<res:// path>
## Exit code: 0 when every wanted portrait was written, 1 when one failed, 2 on a bad setup.

const MANIFEST_PATH := "res://tools/portraits/portraits.json"
const FACE_CAMERA := ^"Cameras/Face"
const WORLD_ENVIRONMENT := ^"WorldEnvironment"
const KIND_HEROES := "heroes"
const KIND_CREATURES := "creatures"

var _out_override := ""


func _ready() -> void:
	# The weather clock writes no globals while we render (the stage pins the wind itself).
	var clock := WeatherClock.current()
	if clock != null:
		clock.hold(self)
	_run.call_deferred()


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		printerr("PORTRAIT needs a real renderer: run tools/portraits/render.sh, not --headless")
		get_tree().quit(2)
		return
	var opts := _parse_args()
	_out_override = str(opts.get("out_dir", ""))
	var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string(opts.get("manifest", MANIFEST_PATH)))
	if not manifest is Dictionary:
		printerr("PORTRAIT cannot parse the manifest")
		get_tree().quit(2)
		return
	var defaults: Dictionary = (manifest as Dictionary).get("defaults", {})
	var only: PackedStringArray = opts.get("only", PackedStringArray())
	var emotions: PackedStringArray = opts.get("emotions", PackedStringArray())
	var written := 0
	var failed := 0
	for kind: String in [KIND_HEROES, KIND_CREATURES]:
		for entry_v: Variant in (manifest as Dictionary).get(kind, []):
			var entry := _merged(defaults, entry_v as Dictionary)
			if kind == KIND_CREATURES:
				entry["creature_stage"] = (manifest as Dictionary).get("creature_stage", {})
			var id := str(entry.get("id", ""))
			if not only.is_empty() and not only.has(id):
				continue
			var variants: Array = entry.get("emotions", [""]) if kind == KIND_HEROES else [""]
			for variant: String in variants:
				if kind == KIND_HEROES and not emotions.is_empty() and not emotions.has(variant):
					continue
				var out_name := id if variant == "" else "%s_%s" % [id, variant]
				var error: String
				if kind == KIND_HEROES:
					error = await _render_hero(entry, variant, out_name)
				else:
					error = await _render_creature(entry, out_name)
				if error == "":
					written += 1
				else:
					failed += 1
					printerr("PORTRAIT FAIL %s: %s" % [out_name, error])
	print("Portraits: %d written, %d failed" % [written, failed])
	get_tree().quit(1 if failed > 0 or written == 0 else 0)


## The entry over the defaults; "camera" and "environment" merge key by key.
func _merged(defaults: Dictionary, entry: Dictionary) -> Dictionary:
	var out := defaults.merged(entry, true)
	for key: String in ["camera", "environment"]:
		out[key] = (defaults.get(key, {}) as Dictionary).merged(entry.get(key, {}), true)
	return out


func _render_hero(entry: Dictionary, emotion: String, out_name: String) -> String:
	var packed := load(str(entry.get("stage", ""))) as PackedScene
	if packed == null:
		return "cannot load stage %s" % entry.get("stage", "")
	var stage := packed.instantiate() as AshaStage
	if stage == null:
		return "%s is not an AshaStage" % entry.get("stage", "")
	var cam_d: Dictionary = entry["camera"]
	stage.emotion = emotion
	stage.tier = str(entry.get("tier", stage.tier))
	stage.face_distance = float(cam_d.get("distance", stage.face_distance))
	stage.face_yaw_degrees = float(cam_d.get("yaw_degrees", stage.face_yaw_degrees))
	stage.face_pitch_degrees = float(cam_d.get("pitch_degrees", stage.face_pitch_degrees))
	stage.face_aim_drop = float(cam_d.get("aim_drop", stage.face_aim_drop))
	var cam := stage.get_node_or_null(FACE_CAMERA) as Camera3D
	if cam == null:
		stage.free()
		return "the stage has no %s camera" % FACE_CAMERA
	cam.fov = float(cam_d.get("fov", cam.fov))
	for node_name: String in entry.get("hide_nodes", []):
		var n := stage.get_node_or_null(NodePath(node_name)) as Node3D
		if n != null:
			n.visible = false
	var we := stage.get_node_or_null(WORLD_ENVIRONMENT) as WorldEnvironment
	if we != null and we.environment != null:
		var env := we.environment.duplicate() as Environment
		var overrides: Dictionary = entry["environment"]
		for key: String in overrides:
			env.set(key, overrides[key])
		we.environment = env
	return await _capture(stage, cam, entry, out_name)


## A creature (M2-MNU-302): its battle actor scene (the enemy's `model`) alone in a small world, the
## manifest's creature_stage lights and environment (cool rim for the dark-blue panels), held at
## creatures.json's `portrait` clip and time and framed by CreatureFraming.frame_fit() from that block's
## yaw, pitch, fov and margin; the entry's own `portrait` keys, when it has any, override that block.
func _render_creature(entry: Dictionary, out_name: String) -> String:
	var packed := load(str(entry.get("scene", ""))) as PackedScene
	if packed == null:
		return "cannot load creature scene %s" % entry.get("scene", "")
	var actor := packed.instantiate() as CreatureActor
	if actor == null:
		return "%s is not a CreatureActor" % entry.get("scene", "")
	var stage: Dictionary = entry.get("creature_stage", {})
	var world := Node3D.new()
	world.name = &"CreatureWorld"
	var we := WorldEnvironment.new()
	var env := Environment.new()
	var env_d: Dictionary = stage.get("environment", {})
	for key: String in env_d:
		var v: Variant = _value(env_d[key])
		env.set(key, int(v) if typeof(env.get(key)) == TYPE_INT else v)
	we.environment = env
	world.add_child(we)
	var cam := Camera3D.new()
	cam.name = &"Camera"
	world.add_child(cam)
	world.add_child(actor)
	var cfg: Dictionary = CreatureActor.row_for(actor.creature_id).get("portrait", {})
	cfg = cfg.merged(entry.get("portrait", {}), true)
	var lights: Array = stage.get("lights", [])
	var prepare := func() -> void:
		CreatureFraming.hold(actor, StringName(str(cfg.get("clip", "idle"))), float(cfg.get("clip_time", 0.0)))
		CreatureFraming.frame_fit(
			cam,
			CreatureFraming.bounds([actor]),
			float(cfg.get("yaw_deg", 0.0)),
			float(cfg.get("pitch_deg", 0.0)),
			float(cfg.get("fov_deg", cam.fov)),
			float(cfg.get("margin", 1.0))
		)
		for l: Dictionary in lights:
			world.add_child(_light(l, float(cfg.get("yaw_deg", 0.0))))
	return await _capture(world, cam, entry, out_name, prepare)


## A directional light from the manifest: yaw_deg is relative to the camera's yaw (0 = from the camera's
## side, 180 = from behind the creature), pitch_deg above the horizon.
static func _light(d: Dictionary, camera_yaw_deg: float) -> DirectionalLight3D:
	var light := DirectionalLight3D.new()
	var yaw := deg_to_rad(camera_yaw_deg + float(d.get("yaw_deg", 0.0)))
	var pitch := deg_to_rad(float(d.get("pitch_deg", 0.0)))
	var from := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
	light.basis = Basis.looking_at(-from, Vector3.UP if absf(from.y) < 0.99 else Vector3.FORWARD)
	light.light_color = _value(d.get("color", [1.0, 1.0, 1.0])) as Color
	light.light_energy = float(d.get("energy", 1.0))
	light.shadow_enabled = bool(d.get("shadow", false))
	return light


## A manifest value: a 3- or 4-number array is a Color, anything else as is.
static func _value(v: Variant) -> Variant:
	if v is Array and ((v as Array).size() == 3 or (v as Array).size() == 4):
		var a := v as Array
		return Color(float(a[0]), float(a[1]), float(a[2]), float(a[3]) if a.size() == 4 else 1.0)
	return v


## Renders `root` (freed after) through `cam` in a transparent SubViewport of size x supersample,
## Lanczos-reduced to `size`, and saves <out_dir>/<out_name>.png. `prepare` (when valid) runs once `root` is
## in the tree, before the camera is made current (poses and framing that need global transforms).
## Returns "" or the error.
func _capture(root: Node, cam: Camera3D, entry: Dictionary, out_name: String, prepare := Callable()) -> String:
	var size_a: Array = entry.get("size", [])
	var size := Vector2i(int(size_a[0]), int(size_a[1]))
	var vp := SubViewport.new()
	vp.size = size * int(entry.get("supersample", 1))
	vp.own_world_3d = true
	vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	vp.add_child(root)
	if prepare.is_valid():
		prepare.call()
	cam.make_current()
	for i in int(entry.get("settle_frames", 1)):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := vp.get_texture().get_image()
	vp.queue_free()
	await get_tree().process_frame
	if image == null:
		return "no image"
	image.convert(Image.FORMAT_RGBA8)
	image.resize(size.x, size.y, Image.INTERPOLATE_LANCZOS)
	var out_dir := _out_override
	if out_dir == "":
		out_dir = ProjectSettings.globalize_path(str(entry.get("out_dir", "")))
	DirAccess.make_dir_recursive_absolute(out_dir)
	var path := out_dir.path_join("%s.png" % out_name)
	var err := image.save_png(path)
	if err != OK:
		return "save_png %s: %s" % [path, error_string(err)]
	print("PORTRAIT ok   %s" % path)
	return ""


func _parse_args() -> Dictionary:
	var opts := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--only="):
			opts["only"] = arg.trim_prefix("--only=").split(",", false)
		elif arg.begins_with("--emotions="):
			opts["emotions"] = arg.trim_prefix("--emotions=").split(",", false)
		elif arg.begins_with("--out-dir="):
			opts["out_dir"] = arg.trim_prefix("--out-dir=")
		elif arg.begins_with("--manifest="):
			opts["manifest"] = arg.trim_prefix("--manifest=")
	return opts
