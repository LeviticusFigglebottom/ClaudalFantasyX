class_name CutsceneFace
extends RefCounted
## One actor's face for the sequencer (M2-FP-08): blends emotion poses onto the blend shapes of
## the actor's meshes, and opens and closes the mouth for lip-flap. A pose is a face-poses JSON
## "emotions" row (asha_face_poses.json shape): shape -> weight, where a weight pair [L, R] drives
## `<shape>_L` and `<shape>_R` and a scalar drives both sides, or the unsided shape itself. Shapes
## the meshes don't have are ignored, so a rig with no face keys simply does nothing.

## blend shape name -> [MeshInstance3D, index] for every mesh under the actor that has it.
var _slots: Dictionary = {}
## name -> current weight / start of the blend / target.
var _now: Dictionary = {}
var _from: Dictionary = {}
var _to: Dictionary = {}
var _elapsed := 0.0
var _duration := 0.0
var _mouth: Dictionary = {}
var _mouth_open := false


## `mouth` is sequencer.json "lip_flap": {shape: weight} applied while the mouth is open.
func _init(actor: Node, mouth: Dictionary = {}) -> void:
	_mouth = mouth
	for n in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		var am := mi.mesh as ArrayMesh  # only ArrayMesh has blend shapes (primitives never do)
		if am == null:
			continue
		for i in am.get_blend_shape_count():
			var shape := StringName(am.get_blend_shape_name(i))
			if not _slots.has(shape):
				_slots[shape] = []
			(_slots[shape] as Array).append([mi, i])
			_now[shape] = mi.get_blend_shape_value(i)


func has_shapes() -> bool:
	return not _slots.is_empty()


## Blends every face shape toward `pose` over `sec` (0 = at once). Shapes the pose leaves out go
## back to 0, so expressions never stack.
func blend_to(pose: Dictionary, sec: float) -> void:
	var target := expand(pose)
	_from = {}
	_to = {}
	for shape: StringName in _slots.keys():
		_from[shape] = float(_now.get(shape, 0.0))
		_to[shape] = float(target.get(shape, 0.0))
	_elapsed = 0.0
	_duration = maxf(sec, 0.0)
	advance(0.0)


func set_mouth_open(open: bool) -> void:
	_mouth_open = open
	_apply()


## Moves the expression blend on by `delta` seconds.
func advance(delta: float) -> void:
	if _to.is_empty():
		return
	_elapsed += delta
	var t := 1.0 if _duration <= 0.0 else clampf(_elapsed / _duration, 0.0, 1.0)
	var ease_t := smoothstep(0.0, 1.0, t)
	for shape: StringName in _to.keys():
		_now[shape] = lerpf(float(_from[shape]), float(_to[shape]), ease_t)
	if t >= 1.0:
		_to = {}
	_apply()


## The current weight of a shape (tests, debug).
func weight(shape: StringName) -> float:
	var slots: Array = _slots.get(shape, [])
	if slots.is_empty():
		return 0.0
	var mi := slots[0][0] as MeshInstance3D
	return mi.get_blend_shape_value(int(slots[0][1]))


## A pose row with [L, R] pairs and scalars resolved to blend shape names.
func expand(pose: Dictionary) -> Dictionary:
	var out := {}
	for key: String in pose.keys():
		var v: Variant = pose[key]
		var pair: Array = v if v is Array else [v, v]
		if _slots.has(StringName(key + "_L")) or _slots.has(StringName(key + "_R")):
			out[StringName(key + "_L")] = float(pair[0])
			out[StringName(key + "_R")] = float(pair[1] if pair.size() > 1 else pair[0])
		else:
			out[StringName(key)] = float(pair[0])
	return out


func _apply() -> void:
	for shape: StringName in _slots.keys():
		var w := float(_now.get(shape, 0.0))
		if _mouth_open and _mouth.has(String(shape)):
			w = maxf(w, float(_mouth[String(shape)]))
		for slot: Array in _slots[shape]:
			(slot[0] as MeshInstance3D).set_blend_shape_value(int(slot[1]), w)
