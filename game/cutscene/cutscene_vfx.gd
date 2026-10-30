class_name CutsceneVfx
extends RefCounted
## A cutscene's `@vfx glimmer_*` cue at final quality (ADR 0041): Rendering's GlimmerField, not M2-FP-01's placeholder
## spheres (CutsceneMotes). The cue sets the field through GlimmerField.apply_cue (glimmer.json "cues": count, drift,
## motion, rate; docs/kb/tech/glimmer.md "`.dlg` cues"), sequencer.json's "vfx" row sizes and lifts its emission
## volume (spread_m, the half-extent across, half that in height; center_y_m above the place) and sets an uncounted
## field's density (amount_multiplier). The scene's end frees it (a counted field keeps its motes, no respawn), or
## end_after_sec of scene time for a light that belongs to one shot (the sequencer's clock: a paused or held scene
## keeps it). M2-FP-120: `form=<id>` is a Vowbound's form in bound light (palette.json glimmer_bound: "Vowbound
## forms ... Steady"): the creature's rest-pose model as steady, translucent bound light in the field's colour and
## energy, with the motes standing still on its outline, one a point (game/data/cutscene/glimmer_forms.json, made by
## tools/cutscene/glimmer_forms.py).

const FORMS_PATH := "res://game/data/cutscene/glimmer_forms.json"

static var _forms: Dictionary = {}


## The field for `effect` under `host`, named `field_name`, freed when `finished` fires. Null for an effect
## glimmer.json's cues don't know, or a form glimmer_forms.json doesn't.
static func spawn(
	row: Dictionary, effect: String, kwargs: Dictionary, host: Node3D, field_name: String, finished: Signal
) -> GlimmerField:
	var field := GlimmerField.new()
	field.name = field_name
	var form: Dictionary = _shape(field, StringName(str(kwargs["form"]))) if kwargs.has("form") else {}
	if kwargs.has("form") and form.is_empty():
		field.free()
		return null
	# A cue is the beat's own light: glimmer.json's per-mode energy, not the zone's hymn_glimmer (0 where no zone
	# writes it, which would leave the beat's motes invisible).
	field.follow_scene_intensity = false
	field.position.y = float(row.get("center_y_m", 0.0))  # over the actor's body, not at its feet
	field.amount_multiplier = float(row.get("amount_multiplier", 1.0))  # an uncounted field's density
	var spread := float(row.get("spread_m", 1.0))
	field.emission_extents_m = Vector3(spread, spread * 0.5, spread)
	host.add_child(field)
	if not field.apply_cue(effect, kwargs):
		field.queue_free()
		return null
	var model := load(str(form.get("model", ""))) as PackedScene if not form.is_empty() else null
	if model != null:
		field.add_child(_body(model, form, field))  # after apply_cue: the field is in its cue's mode and colour
	finished.connect(field.queue_free.unbind(1), CONNECT_ONE_SHOT)
	return field


## A motion step (the sequencer's clock, t 0..1) that frees `field` when it completes: end_after_sec.
static func ender(field: GlimmerField) -> Callable:
	return func(t: float) -> void:
		if t >= 1.0 and is_instance_valid(field):
			field.queue_free()


## The form's points as the field's spawn points, a mote each, never respawned. Its row ({} for an unknown form).
static func _shape(field: GlimmerField, form: StringName) -> Dictionary:
	if _forms.is_empty():
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(FORMS_PATH))
		_forms = (data as Dictionary).get("forms", {}) if typeof(data) == TYPE_DICTIONARY else {}
	var row: Dictionary = _forms.get(String(form), {})
	var points := PackedVector3Array()
	for p: Array in row.get("points", []):
		points.append(Vector3(float(p[0]), float(p[1]), float(p[2])))
	if points.is_empty():
		return {}
	field.spawn_points = points
	field.fixed_count = points.size()
	field.respawn = false
	return row


## The form's body: the model, centred on the outline's centre, every mesh in steady bound light (unshaded,
## emissive in the field's colour at its mode's energy, body_alpha opaque, casting no shadow).
static func _body(model: PackedScene, row: Dictionary, field: GlimmerField) -> Node3D:
	var body := model.instantiate() as Node3D
	body.name = "Form"
	var c: Array = row.get("centre", [0.0, 0.0, 0.0])
	body.position = -Vector3(float(c[0]), float(c[1]), float(c[2]))
	var colour := field.current_color()
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.albedo_color = Color(colour, float(row.get("body_alpha", 1.0)))
	mat.emission_enabled = true
	mat.emission = colour
	mat.emission_energy_multiplier = float(field.config.get("modes", {}).get("machine", {}).get("energy", 1.0))
	for mi: Node in body.find_children("*", "MeshInstance3D", true, false):
		(mi as MeshInstance3D).material_override = mat
		(mi as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return body
