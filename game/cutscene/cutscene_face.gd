class_name CutsceneFace
extends RefCounted
## One actor's face for the sequencer (M2-FP-08): blends emotion poses onto the blend shapes of
## the actor's meshes, and opens and closes the mouth for lip-flap. A pose is a face-poses JSON
## "emotions" row (asha_face_poses.json shape): shape -> weight, where a weight pair [L, R] drives
## `<shape>_L` and `<shape>_R` and a scalar drives both sides, or the unsided shape itself. Shapes
## the meshes don't have are ignored, so a rig with no face keys simply does nothing.
##
## M2-FP-18 adds two layers over the expression, each taken as the max with the pose's weight:
##   blinks   configure_blink(): a seeded timer closes the lids every interval_s (a range), and
##            blink_now() (called on every emotion change when on_emotion_change) adds one more.
##   visemes  say(text) loads the line's FaceVisemes track; each set_mouth_open(true) shows the next
##            syllable's vowel shape and each set_mouth_open(false) its closing shape. With no
##            track, or a rig without those shapes, lip-flap holds the `mouth` shapes as before.

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
## sequencer.json "visemes" (vowels, closers, shapes) and the current line's track.
var _visemes: Dictionary = {}
var _track: Array[Dictionary] = []
var _track_i := 0
## The viseme shapes held now (shape -> weight), or empty for lip-flap / closed.
var _mouth_now: Dictionary = {}
## sequencer.json "blink"; empty = no blinks.
var _blink: Dictionary = {}
var _blink_shapes: Dictionary = {}
var _rng := RandomNumberGenerator.new()
## Seconds to the next timed blink, and how far into the blink in progress (< 0: none).
var _blink_wait := 0.0
var _blink_t := -1.0


## `mouth` is sequencer.json "lip_flap": {shape: weight} applied while the mouth is open;
## `visemes` is sequencer.json "visemes" (M2-FP-18).
func _init(actor: Node, mouth: Dictionary = {}, visemes: Dictionary = {}) -> void:
	_mouth = mouth
	_visemes = visemes
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
	if bool(_blink.get("on_emotion_change", false)) and not _blink.is_empty() and not _same_pose(target):
		blink_now()
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
	_mouth_now = {}
	if not _track.is_empty() and _track_i < _track.size():
		var row: Dictionary = _track[_track_i]
		_mouth_now = _viseme_shapes(row["open"] if open else row["close"])
		if not open:
			_track_i += 1
	_apply()


## Loads `text`'s viseme track for the lip-flap to follow (M2-FP-18). An empty text clears it.
func say(text: String) -> void:
	_track = []
	if not _visemes.is_empty() and _has_visemes():
		_track = FaceVisemes.track(text, _visemes)
	_track_i = 0


func viseme_track() -> Array[Dictionary]:
	return _track


## Turns blinks on: `cfg` is sequencer.json "blink"; `rng_seed` keeps each actor's timing fixed.
func configure_blink(cfg: Dictionary, rng_seed: int) -> void:
	_blink = cfg
	_blink_shapes = expand(_list_pose(cfg.get("shapes", []), float(cfg.get("weight", 1.0))))
	_rng.seed = rng_seed
	_blink_wait = _next_wait()
	_blink_t = -1.0


## Starts a blink now unless one is under way.
func blink_now() -> void:
	if not _blink.is_empty() and _blink_t < 0.0:
		_blink_t = 0.0


func is_blinking() -> bool:
	return _blink_t >= 0.0


## Moves the expression blend and the blink on by `delta` seconds.
func advance(delta: float) -> void:
	var changed := _advance_blink(delta)
	if not _to.is_empty():
		_elapsed += delta
		var t := 1.0 if _duration <= 0.0 else clampf(_elapsed / _duration, 0.0, 1.0)
		var ease_t := smoothstep(0.0, 1.0, t)
		for shape: StringName in _to.keys():
			_now[shape] = lerpf(float(_from[shape]), float(_to[shape]), ease_t)
		if t >= 1.0:
			_to = {}
		changed = true
	if changed:
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


## The blink's weight now, 0..1: a ramp down over close_s, held for hold_s, a ramp up over open_s.
func blink_amount() -> float:
	if _blink_t < 0.0:
		return 0.0
	var c := float(_blink.get("close_s", 0.0))
	var h := float(_blink.get("hold_s", 0.0))
	var o := float(_blink.get("open_s", 0.0))
	if _blink_t < c:
		return _blink_t / c
	if _blink_t < c + h:
		return 1.0
	return clampf(1.0 - (_blink_t - c - h) / maxf(o, 0.001), 0.0, 1.0)


func _advance_blink(delta: float) -> bool:
	if _blink.is_empty():
		return false
	if _blink_t >= 0.0:
		_blink_t += delta
		var total := float(_blink.get("close_s", 0.0)) + float(_blink.get("hold_s", 0.0))
		if _blink_t >= total + float(_blink.get("open_s", 0.0)):
			_blink_t = -1.0
			_blink_wait = _next_wait()
		return true
	_blink_wait -= delta
	if _blink_wait <= 0.0:
		_blink_t = 0.0
		return true
	return false


func _next_wait() -> float:
	var r: Array = _blink.get("interval_s", [0.0, 0.0])
	return _rng.randf_range(float(r[0]), float(r[1]))


func _viseme_shapes(viseme: StringName) -> Dictionary:
	return expand((_visemes.get("shapes", {}) as Dictionary).get(String(viseme), {}))


## True when the rig has every shape some viseme row names (else the plain lip-flap is used).
func _has_visemes() -> bool:
	for row: Variant in (_visemes.get("shapes", {}) as Dictionary).values():
		for shape: StringName in expand(row as Dictionary).keys():
			if not _slots.has(shape):
				return false
	return true


func _same_pose(target: Dictionary) -> bool:
	for shape: StringName in _slots.keys():
		var to := float(target.get(shape, 0.0))
		var at := float(_to.get(shape, _now.get(shape, 0.0)))
		if absf(to - at) > 0.001:
			return false
	return true


static func _list_pose(shapes: Array, w: float) -> Dictionary:
	var out := {}
	for s: Variant in shapes:
		out[str(s)] = w
	return out


func _apply() -> void:
	var blink := blink_amount()
	for shape: StringName in _slots.keys():
		var w := float(_now.get(shape, 0.0))
		if _mouth_open and _mouth_now.is_empty() and _mouth.has(String(shape)):
			w = maxf(w, float(_mouth[String(shape)]))
		if _mouth_now.has(shape):
			w = maxf(w, float(_mouth_now[shape]))
		if blink > 0.0 and _blink_shapes.has(shape):
			w = maxf(w, float(_blink_shapes[shape]) * blink)
		for slot: Array in _slots[shape]:
			(slot[0] as MeshInstance3D).set_blend_shape_value(int(slot[1]), w)
