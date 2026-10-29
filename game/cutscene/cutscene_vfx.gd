class_name CutsceneVfx
extends RefCounted
## A cutscene's `@vfx glimmer_*` cue at final quality (ADR 0041): Rendering's GlimmerField, not M2-FP-01's placeholder
## spheres (CutsceneMotes). The cue sets the field through GlimmerField.apply_cue (glimmer.json "cues": count, drift,
## motion, rate; docs/kb/tech/glimmer.md "`.dlg` cues"), sequencer.json's "vfx" row sizes and lifts its emission
## volume (spread_m, the half-extent across, half that in height; center_y_m above the place) and sets an uncounted
## field's density (amount_multiplier). The scene's end frees it (a counted field keeps its motes, no respawn), or
## end_after_sec (scene time) for a light that belongs to one shot. M2-FP-120: `form=<id>` stands the motes still on a
## creature's outline (game/data/cutscene/glimmer_forms.json, tools/cutscene/glimmer_forms.py), one mote a point.

const FORMS_PATH := "res://game/data/cutscene/glimmer_forms.json"

static var _forms: Dictionary = {}


## The field for `effect` under `host`, named `field_name`, freed when `finished` fires. Null for an effect
## glimmer.json's cues don't know, or a form glimmer_forms.json doesn't.
static func spawn(
	row: Dictionary, effect: String, kwargs: Dictionary, host: Node3D, field_name: String, finished: Signal
) -> GlimmerField:
	var field := GlimmerField.new()
	field.name = field_name
	if kwargs.has("form") and not _shape(field, StringName(str(kwargs["form"]))):
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
	finished.connect(field.queue_free.unbind(1), CONNECT_ONE_SHOT)
	var end_after := float(row.get("end_after_sec", 0.0))  # a light that belongs to one shot (S08's bound Ilun)
	if end_after > 0.0:
		host.get_tree().create_timer(end_after).timeout.connect(field.queue_free)
	return field


## The form's points as the field's spawn points, a mote each, never respawned. False for an unknown form.
static func _shape(field: GlimmerField, form: StringName) -> bool:
	if _forms.is_empty():
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(FORMS_PATH))
		_forms = (data as Dictionary).get("forms", {}) if typeof(data) == TYPE_DICTIONARY else {}
	var row: Dictionary = _forms.get(String(form), {})
	var points := PackedVector3Array()
	for p: Array in row.get("points", []):
		points.append(Vector3(float(p[0]), float(p[1]), float(p[2])))
	if points.is_empty():
		return false
	field.spawn_points = points
	field.fixed_count = points.size()
	field.respawn = false
	return true
