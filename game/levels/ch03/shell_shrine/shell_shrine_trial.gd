class_name ShellShrineTrial
extends RefCounted
## The Shell Shrine trial's rules (M2-FP-16; vertical_slice.md B07): headless and deterministic,
## no nodes. Data: game/data/trials/shell_shrine.json (see its "doc"). The level
## (ShellShrineLevel) is a view of this: it turns basins on interaction, calls advance(delta)
## every frame and shows what the signals report.
##   rotate(basin)  one 90° step clockwise; resets the idle clock
##   trace()        where the water runs now: [source_into, ..., the node it ends on]
##   advance(dt)    fills the inner pool while the water reaches it, drains the side pool the first
##                  time it reaches the sluice, and counts the idle time toward the hint

signal rotated(basin: StringName, rotation: int)
## The traced path changed (after a turn): the view relights its channels.
signal flow_changed(path: Array[StringName])
signal pool_filled
signal side_pool_drained
## No turn for hint_idle_sec (once per trial).
signal hint_due

const DATA_PATH := "res://game/data/trials/shell_shrine.json"

var data: Dictionary = {}
## basin id -> rotation (0..steps-1).
var rotations: Dictionary = {}
## 0..1; the door opens at 1.
var pool_level := 0.0
var door_open := false
var side_drained := false
var turns := 0
var idle_sec := 0.0
var hint_given := false


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("shell_shrine")) != TYPE_DICTIONARY:
		push_error("ShellShrineTrial: could not read 'shell_shrine' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["shell_shrine"] as Dictionary


func _init(d: Dictionary = {}) -> void:
	data = d if not d.is_empty() else load_data()
	for id: String in basins().keys():
		rotations[StringName(id)] = int((basins()[id] as Dictionary).get("rotation", 0))


func basins() -> Dictionary:
	return data.get("basins", {}) as Dictionary


func basin_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for id: String in basins().keys():
		out.append(StringName(id))
	return out


func steps() -> int:
	return maxi(int(data.get("steps", 4)), 1)


## The node `basin`'s lip faces now.
func outlet(basin: StringName) -> StringName:
	var outs: Array = (basins().get(String(basin), {}) as Dictionary).get("outlets", [])
	if outs.is_empty():
		return StringName(str(data.get("spill", "")))
	return StringName(str(outs[int(rotations.get(basin, 0)) % outs.size()]))


## Turns `basin` one step. False for an unknown basin or once the door is open (the trial is over).
func rotate(basin: StringName) -> bool:
	if door_open or not rotations.has(basin):
		return false
	var before := trace()
	rotations[basin] = (int(rotations[basin]) + 1) % steps()
	turns += 1
	idle_sec = 0.0
	rotated.emit(basin, int(rotations[basin]))
	var after := trace()
	if after != before:
		flow_changed.emit(after)
	return true


## The water's path: source_into, then each basin's outlet, ending on the first node that is not a
## basin (or, in a loop, on `spill`: water going round in circles is lost).
func trace() -> Array[StringName]:
	var path: Array[StringName] = []
	var node := StringName(str(data.get("source_into", "")))
	while node != &"":
		if path.has(node):
			path.append(StringName(str(data.get("spill", ""))))
			break
		path.append(node)
		if not rotations.has(node):
			break
		node = outlet(node)
	return path


func reaches(node: StringName) -> bool:
	var path := trace()
	return not path.is_empty() and path.back() == node


func goal() -> StringName:
	return StringName(str(data.get("goal", "")))


func drain() -> StringName:
	return StringName(str(data.get("drain", "")))


func advance(delta: float) -> void:
	if door_open:
		return
	if reaches(drain()) and not side_drained:
		side_drained = true
		side_pool_drained.emit()
	if reaches(goal()):
		var fill := float(data.get("fill_sec", 1.0))
		pool_level = minf(pool_level + (delta / fill if fill > 0.0 else 1.0), 1.0)
		if pool_level >= 1.0:
			door_open = true
			pool_filled.emit()
		return
	idle_sec += delta
	if not hint_given and idle_sec >= float(data.get("hint_idle_sec", INF)):
		hint_given = true
		hint_due.emit()


## The fewest turns from the current state that bring the water to `target` (-1 if none). A
## breadth-first search over rotations; tests and the data check use it.
func min_turns_to(target: StringName) -> int:
	var ids := basin_ids()
	var start: Array = []
	for id in ids:
		start.append(int(rotations[id]))
	var seen := {str(start): true}
	var frontier: Array = [start]
	var depth := 0
	var probe := ShellShrineTrial.new(data)
	while not frontier.is_empty():
		var next: Array = []
		for state: Array in frontier:
			for i in ids.size():
				probe.rotations[ids[i]] = int(state[i])
			if probe.reaches(target):
				return depth
			for i in ids.size():
				var s2: Array = state.duplicate()
				s2[i] = (int(s2[i]) + 1) % steps()
				if not seen.has(str(s2)):
					seen[str(s2)] = true
					next.append(s2)
		frontier = next
		depth += 1
	return -1
