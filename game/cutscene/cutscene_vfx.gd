class_name CutsceneVfx
extends RefCounted
## A cutscene's `@vfx glimmer_*` cue at final quality (ADR 0041): Rendering's GlimmerField, not M2-FP-01's placeholder
## spheres (CutsceneMotes). The cue sets the field through GlimmerField.apply_cue (glimmer.json "cues": count, drift,
## motion, rate; docs/kb/tech/glimmer.md "`.dlg` cues"), sequencer.json's "vfx" row sizes and lifts its emission
## volume (spread_m, the half-extent across, half that in height; center_y_m above the place) and sets an uncounted
## field's density (amount_multiplier). The scene's end frees it (a counted field keeps its motes, no respawn), or
## end_after_sec (scene time) for a light that belongs to one shot.


## The field for `effect` under `host`, named `field_name`, freed when `finished` fires. Null for an effect
## glimmer.json's cues don't know.
static func spawn(
	row: Dictionary, effect: String, kwargs: Dictionary, host: Node3D, field_name: String, finished: Signal
) -> GlimmerField:
	var field := GlimmerField.new()
	field.name = field_name
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
