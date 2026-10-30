class_name WildlifeShoal
extends RefCounted
## One shoal of small fish in the shallows (M3-CRE-611, docs/kb/art/wildlife.md): the shoal's centre wanders
## between points inside its area, turning as it goes; each fish holds its own place in the school (an offset
## turned with the shoal's heading, plus a slow wobble) and follows it with a lag, so the school stretches and
## wheels. A player wading close startles it into a dart away. The swim itself is the shader's (mode 4), driven
## by each fish's phase. Headless and deterministic. Tuning is the `fish` kind of wildlife.json; placement is a
## zone file's `shoals` row. The rim rays (Ch16, M4-A2P-056) are a shoal too, of the `ray` kind (a `rays` row), drawn
## with the shader's flap (mode 1: their fins beat) instead of the swim.

const MIN_SPEED_MPS := 1e-3
const TARGET_TRIES := 6


class Fish:
	extends RefCounted
	var pos := Vector3.ZERO
	var yaw := 0.0
	var offset := Vector3.ZERO
	var phase := 0.0
	var wobble_phase := 0.0
	var wobble_hz := 0.0
	var speed := 0.0
	var scale := 1.0


var id := ""
var center := Vector3.ZERO
var radius := 1.0
var scale := 1.0
var spread := Vector3.ZERO
var fish: Array[Fish] = []
var bounds := AABB()
## The shoal's moving centre and heading.
var lead := Vector3.ZERO
var heading := 0.0
## Ground height (x, z) -> y; empty = no check. Wander targets keep `bottom_clearance_m` above it.
var ground := Callable()

var _kind: Dictionary = {}
var _rng := RandomNumberGenerator.new()
var _target := Vector3.ZERO
var _cruise := 0.0
var _startle := 0.0
var _mode := WildlifeBuffer.MODE_SWIM


## True while the shoal darts away from a wader (the startle timer runs; read by audio's LifeAudio, M3-AUD-815).
func startled() -> bool:
	return _startle > 0.0


## `mode` is the shader's motion for every fish: WildlifeBuffer.MODE_SWIM (fish) or MODE_FLAP (rays).
func _init(
	row: Dictionary,
	kind: Dictionary,
	seed_value: int,
	count: int,
	ground_fn: Callable,
	mode: float = WildlifeBuffer.MODE_SWIM
) -> void:
	_kind = kind
	_mode = mode
	_rng.seed = seed_value
	ground = ground_fn
	id = str(row.get("id", ""))
	center = WildlifeConfig.vec3(row["center"])
	radius = float(row["radius_m"])
	scale = float(row.get("scale", 1.0))
	spread = WildlifeConfig.vec3(row.get("spread_m", kind["spread_m"])) * scale
	_cruise = _r("speed_mps")
	lead = center
	heading = _rng.randf() * TAU
	_target = _pick_target(Vector2.ZERO, false)
	for i in count:
		var f := Fish.new()
		f.offset = Vector3(
			_rng.randf_range(-1.0, 1.0) * spread.x,
			_rng.randf_range(-1.0, 1.0) * spread.y,
			_rng.randf_range(-1.0, 1.0) * spread.z
		)
		f.pos = lead + f.offset.rotated(Vector3.UP, heading)
		f.yaw = heading
		f.phase = _rng.randf() * TAU
		f.wobble_phase = _rng.randf() * TAU
		f.wobble_hz = _r("wobble_hz")
		f.scale = scale * _r("scale")
		fish.append(f)
	var wide := spread * maxf(_scatter(), 1.0)  # a scattered school still fits its bounds
	var reach := radius + wide.length() + _f("wobble_m")
	var ext := Vector3(reach, wide.y + _f("wobble_m"), reach)
	bounds = AABB(center - ext, ext * 2.0)


func _f(key: String) -> float:
	return float(_kind[key])


func _r(key: String) -> float:
	return WildlifeConfig.draw(_rng, _kind[key])


func count() -> int:
	return fish.size()


## How far a startle throws the school apart: its spread is scaled by up to this, easing back as the startle fades.
func _scatter() -> float:
	return float(_kind.get("scatter_spread", 1.0))


## How far the centre may wander from `center` (the school's spread stays inside the radius).
func wander_radius() -> float:
	return maxf(radius - maxf(spread.x, spread.z), 0.0)


## A wander point in the area; with `away`, the point is on the far side from `from` (a startle).
func _pick_target(from: Vector2, away: bool) -> Vector3:
	var r := wander_radius()
	for _k in TARGET_TRIES:
		var a := _rng.randf() * TAU
		var p := Vector2(center.x, center.z) + Vector2(cos(a), sin(a)) * r * sqrt(_rng.randf())
		if away:
			var dir := Vector2(lead.x, lead.z) - from
			p = Vector2(center.x, center.z) + (dir.normalized() if dir.length() > MIN_SPEED_MPS else Vector2.RIGHT) * r
		var t := Vector3(p.x, center.y, p.y)
		if not ground.is_valid() or float(ground.call(p.x, p.y)) <= center.y - _f("bottom_clearance_m"):
			return t
	return center


func step(delta: float, player: Vector3, has_player: bool) -> void:
	var pp := Vector2(player.x, player.z)
	if has_player and pp.distance_to(Vector2(lead.x, lead.z)) < _f("startle_radius_m"):
		if _startle <= 0.0:
			_target = _pick_target(pp, true)
		_startle = _f("startle_s")
	_startle = maxf(_startle - delta, 0.0)
	var speed := _f("dart_speed_mps") if _startle > 0.0 else _cruise
	var to := _target - lead
	to.y = 0.0
	if to.length() <= maxf(speed * delta, _f("wander_arrive_m")):
		_target = _pick_target(pp, false)
	else:
		heading = WildlifeConfig.approach_angle(heading, atan2(to.x, to.z), _f("turn_rate"), delta)
		var fwd := Vector3(sin(heading), 0.0, cos(heading))
		lead += fwd * speed * maxf(fwd.dot(to.normalized()), 0.0) * delta
	var follow := 1.0 - exp(-_f("follow_rate") * (_f("startle_follow_mult") if _startle > 0.0 else 1.0) * delta)
	var turn := 1.0 - exp(-_f("turn_rate") * delta)
	var wob := _f("wobble_m")
	var wob_y := _f("wobble_y_fraction")
	var hz0 := _f("swim_hz")
	var hz_per := _f("swim_hz_per_mps")
	var inv_dt := 1.0 / maxf(delta, MIN_SPEED_MPS)
	var turned := Basis(Vector3.UP, heading)
	var apart := 1.0 + (_scatter() - 1.0) * (_startle / _f("startle_s") if _startle > 0.0 else 0.0)
	for f in fish:
		f.wobble_phase = fposmod(f.wobble_phase + TAU * f.wobble_hz * delta, TAU)
		var w := Vector3(sin(f.wobble_phase), wob_y * sin(f.wobble_phase * 2.0), cos(f.wobble_phase)) * wob
		var goal := lead + turned * (f.offset * apart + w)
		var before := f.pos
		f.pos = f.pos.lerp(goal, follow)
		var vx := f.pos.x - before.x
		var vz := f.pos.z - before.z
		f.speed = sqrt(vx * vx + vz * vz) * inv_dt
		var face := atan2(vx, vz) if f.speed > MIN_SPEED_MPS else heading
		f.yaw += angle_difference(f.yaw, face) * turn
		f.phase = fposmod(f.phase + TAU * (hz0 + hz_per * f.speed) * delta, TAU)


func transform_of(f: Fish) -> Transform3D:
	return Transform3D(Basis(Vector3.UP, f.yaw).scaled(Vector3.ONE * f.scale), f.pos)


func write(buf: WildlifeBuffer, base: int) -> void:
	var amp := _f("swim_amp")
	var dart := _f("dart_speed_mps")
	for i in fish.size():
		var f := fish[i]
		var a := amp * (1.0 + clampf(f.speed / dart, 0.0, 1.0))
		buf.put(base + i, transform_of(f), f.phase, a, _mode, 0.0)
