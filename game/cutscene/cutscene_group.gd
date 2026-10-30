class_name CutsceneGroup
extends RefCounted
## M4-CIN-1302 (act2_ch10.md B09 T04, the clutch turning its back all at once): `@anim <group> <clip>` with no stage
## actor of that id plays the clip on every actor named `<group>_*` (clutch_01 … clutch_30), each after its own small
## delay, so thirty people turn as many people, not as one copy. The delay is fixed per actor (from its name), up to
## sequencer.json's group_spread_sec, so a scene plays the same way every time.

const KEY_SPREAD := "group_spread_sec"
## Delays are taken in this many steps of the spread.
const SPREAD_STEPS := 1000


## The stage actors in `group` (by name, `<group>_*`), sorted; empty when the stage has an actor of that very id.
static func members(stage: CutsceneStage, group: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	if stage == null or stage.actor(group) != null:
		return out
	var actors := stage.get_node_or_null(^"Actors")
	if actors == null:
		return out
	var prefix := "%s_" % group
	for n in actors.get_children():
		if String(n.name).begins_with(prefix):
			out.append(StringName(n.name))
	out.sort()
	return out


## Plays `step` (an @anim) member by member when its first argument names a group: each member's own `anim` cue
## after its delay, on `start_motion` (key, sec, apply(t)). False when it names no group.
static func play(
	step: DialogueStep, stage: CutsceneStage, config: Dictionary, start_motion: Callable, anim: Callable
) -> bool:
	var group := members(stage, StringName(str(step.args[0])))
	for m in group:
		start_motion.call(StringName("group:%s" % m), delay(config, m), once(anim.bind(step_for(step, m))))
	return not group.is_empty()


## The member's delay in seconds: a fixed fraction of the spread, from its name.
static func delay(config: Dictionary, member: StringName) -> float:
	var spread := float(config.get(KEY_SPREAD, 0.0))
	# String.hash() is djb2: clutch_01 and clutch_02 hash one apart, so it is mixed (PCG, the same on every machine).
	var mixed := int(rand_from_seed(String(member).hash())[0])
	return spread * float(absi(mixed) % SPREAD_STEPS) / float(SPREAD_STEPS)


## `step` for one member: the same cue with the member in the group's place.
static func step_for(step: DialogueStep, member: StringName) -> DialogueStep:
	var s := DialogueStep.new()
	s.kind = step.kind
	s.src_line = step.src_line
	s.cue = step.cue
	s.args = step.args.duplicate()
	s.args[0] = String(member)
	s.kwargs = step.kwargs.duplicate()
	return s


## A motion's apply that calls `fn` once, when the motion ends (t = 1).
static func once(fn: Callable) -> Callable:
	var done := [false]
	return func(t: float) -> void:
		if t >= 1.0 and not done[0]:
			done[0] = true
			fn.call()
