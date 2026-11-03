class_name CutsceneStorm
extends RefCounted
## FAST-TRACK (the human's 11-03 playtest: "the seagull/storm scene doesn't show the actual vortex"):
## `@storm view [look=<id>]` turns the scene's Undertow (the zone's UndertowStorm, M3-C01-100) toward the camera for a
## storm shot. Its clock runs (the vortex turns; a zone holds it still), the zone fog gives way to the look's
## density (a storm zone's spray fog is kilometres thick and greys the maelstrom's throat out from any shot that
## stands off it), the sun takes the look's energy (above the canopy is full sun; a storm zone's sun is the
## dimmed light under it), and a bolt strikes on the side facing the current camera. `@storm off` puts all of it back,
## and so does the scene's end, however it ends. The looks are sequencer.json's `storm` rows; `view` with no
## look= takes default_look. False (and nothing changes) when the scene has no Undertow or the look isn't there.

const KEY := "storm"
const KEY_LOOKS := "looks"
const KEY_DEFAULT := "default_look"
const SWITCH_VIEW := &"view"
## On the storm while a view is up: what `off` restores.
const META_SAVED := &"cutscene_storm_saved"


static func cue(host: Node, step: DialogueStep, config: Dictionary, finished: Signal) -> bool:
	var storm := find(host.get_tree().root)
	if storm == null:
		return false
	if StringName(str(step.args[0])) != SWITCH_VIEW:
		restore(storm)
		return true
	var cfg: Dictionary = config.get(KEY, {})
	var looks: Dictionary = cfg.get(KEY_LOOKS, {})
	var look_id := str(step.kwargs.get("look", cfg.get(KEY_DEFAULT, "")))
	if not looks.has(look_id):
		return false
	var first := not storm.has_meta(META_SAVED)
	view(storm, looks[look_id] as Dictionary)
	var cam := host.get_viewport().get_camera_3d()
	if bool((looks[look_id] as Dictionary).get("flash", false)) and cam != null:
		storm.force_flash(storm.site_facing(cam.global_position))
	if first:
		finished.connect(func(_id: StringName) -> void: restore(storm), CONNECT_ONE_SHOT)
	return true


## Puts the look on `storm` (saving what it changes the first time).
static func view(storm: UndertowStorm, look: Dictionary) -> void:
	var we := storm.world_environment
	if not storm.has_meta(META_SAVED):
		var saved := {"playing": storm.playing, "time_scale": storm.time_scale}
		if we != null:
			saved["environment"] = we.environment
		if storm.sun != null:
			saved["sun_energy"] = storm.sun.light_energy
		storm.set_meta(META_SAVED, saved)
	storm.playing = bool(look.get("playing", storm.playing))
	storm.time_scale = float(look.get("time_scale", storm.time_scale))
	var base := (storm.get_meta(META_SAVED) as Dictionary).get("environment") as Environment
	if we != null and base != null and look.has("fog_density"):
		var env := base.duplicate() as Environment
		env.fog_density = float(look["fog_density"])
		we.environment = env
	if storm.sun != null and look.has("sun_energy"):
		storm.sun.light_energy = float(look["sun_energy"])


## Takes the view off `storm` (no-op when none is up).
static func restore(storm: UndertowStorm) -> void:
	if not is_instance_valid(storm) or not storm.has_meta(META_SAVED):
		return
	var saved: Dictionary = storm.get_meta(META_SAVED)
	storm.playing = bool(saved["playing"])
	storm.time_scale = float(saved["time_scale"])
	if storm.world_environment != null and saved.has("environment"):
		storm.world_environment.environment = saved["environment"] as Environment
	if storm.sun != null and saved.has("sun_energy"):
		storm.sun.light_energy = float(saved["sun_energy"])
	storm.remove_meta(META_SAVED)


## The first visible UndertowStorm under `node` (depth first), or null.
static func find(node: Node) -> UndertowStorm:
	if node is UndertowStorm and (node as UndertowStorm).is_visible_in_tree():
		return node as UndertowStorm
	for child in node.get_children():
		var hit := find(child)
		if hit != null:
			return hit
	return null
