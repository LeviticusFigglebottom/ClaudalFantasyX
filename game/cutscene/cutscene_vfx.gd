class_name CutsceneVfx
extends RefCounted
## A cutscene's `@vfx glimmer_*` cue at final quality (ADR 0041): Rendering's GlimmerField, not M2-FP-01's placeholder
## spheres (CutsceneMotes). The cue sets the field through GlimmerField.apply_cue (glimmer.json "cues": count, drift,
## motion, rate; docs/kb/tech/glimmer.md "`.dlg` cues"), sequencer.json's "vfx" row sizes its emission volume
## (spread_m, the half-extent across; half that in height), and the scene's end frees it: a counted field keeps its
## motes (no respawn), so nothing else would.


## The field for `effect` under `host`, named `field_name`, freed when `finished` fires. Null for an effect
## glimmer.json's cues don't know.
static func spawn(
	row: Dictionary, effect: String, kwargs: Dictionary, host: Node3D, field_name: String, finished: Signal
) -> GlimmerField:
	var field := GlimmerField.new()
	field.name = field_name
	var spread := float(row.get("spread_m", 1.0))
	field.emission_extents_m = Vector3(spread, spread * 0.5, spread)
	host.add_child(field)
	if not field.apply_cue(effect, kwargs):
		field.queue_free()
		return null
	finished.connect(field.queue_free.unbind(1), CONNECT_ONE_SHOT)
	return field
