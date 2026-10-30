class_name CutsceneLight
extends RefCounted
## M2-FP-102: `@light <name> on|off [sec]` eases a stage practical's energy (a Light3D found by name under the stage,
## wherever a body carries it) to its authored energy or to 0 (sequencer.json light_ease). Split out of the
## sequencer (M2-FP-119, its line cap); the sequencer passes its own motion runner.

const META_AUTHORED_ENERGY := &"cutscene_authored_energy"


## Starts the ease through `start_motion` (key, sec, apply(t)). False when the stage has no such light.
static func cue(stage: Node, args: Array, light_ease: float, switch_on: StringName, start_motion: Callable) -> bool:
	var light_name := str(args[0])
	var light := stage.find_child(light_name, true, false) as Light3D if stage != null else null
	if light == null:
		return false
	if not light.has_meta(META_AUTHORED_ENERGY):
		light.set_meta(META_AUTHORED_ENERGY, light.light_energy)
	var from := light.light_energy if light.visible else 0.0
	var to := float(light.get_meta(META_AUTHORED_ENERGY)) if StringName(str(args[1])) == switch_on else 0.0
	var sec := float(args[2]) if args.size() > 2 else 0.0
	light.visible = true
	start_motion.call(
		StringName("light:%s" % light_name),
		sec,
		func(t: float) -> void:
			if is_instance_valid(light):
				light.light_energy = lerpf(from, to, CutsceneMotion.eased(t, light_ease))
	)
	return true
