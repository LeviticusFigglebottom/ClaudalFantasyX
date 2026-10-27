class_name CutsceneCameraBreath
extends RefCounted
## M2-FP-104 (the playtest: "parts look primitive", every cutscene frame dead still): a held cutscene shot
## breathes. Once the director has landed a scripted shot, the camera turns by a slow, tiny sum of sines
## about its own axes (an operator's hand on a fluid head, never a shake), easing in over ramp_sec; a cut
## or a blend resets it. Deterministic (no rng), so a frame grab or a replay is the same every time.
## Applied after the director's update each frame, on top of the pose it set; the director sets the whole
## pose again on its next update, so nothing accumulates. Tuning: sequencer.json camera_breath.

var _time := 0.0
var _weight := 0.0
var _cfg: Dictionary = {}


func _init(cfg: Dictionary = {}) -> void:
	_cfg = cfg


## Starts over at zero weight (a cut, a blend, a new scene).
func reset() -> void:
	_time = 0.0
	_weight = 0.0


## The (yaw, pitch) offset in radians `delta` seconds on; advances the clock and the ease-in.
func step(delta: float) -> Vector2:
	_time += delta
	var ramp := float(_cfg.get("ramp_sec", 0.0))
	_weight = 1.0 if ramp <= 0.0 else minf(_weight + delta / ramp, 1.0)
	var w := _weight * _weight * (3.0 - 2.0 * _weight)
	var yaw := _wave(float(_cfg.get("yaw_deg", 0.0)), _cfg.get("yaw_periods_sec", []) as Array)
	var pitch := _wave(float(_cfg.get("pitch_deg", 0.0)), _cfg.get("pitch_periods_sec", []) as Array)
	return Vector2(deg_to_rad(yaw), deg_to_rad(pitch)) * w


## Turns `camera` by this frame's offset (call after the director has posed it).
func apply(camera: Camera3D, delta: float) -> void:
	if camera == null or not bool(_cfg.get("enabled", false)):
		return
	var off := step(delta)
	camera.rotate_object_local(Vector3.UP, off.x)
	camera.rotate_object_local(Vector3.RIGHT, off.y)


func _wave(amp_deg: float, periods: Array) -> float:
	if periods.is_empty():
		return 0.0
	var sum := 0.0
	for p: Variant in periods:
		sum += sin(TAU * _time / maxf(float(p), 0.01))
	return amp_deg * sum / float(periods.size())
