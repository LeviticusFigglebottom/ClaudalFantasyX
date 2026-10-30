class_name WildlifeSwarm
extends RefCounted
## One group of ambient insects (M3-CRE-616, docs/kb/art/wildlife.md), of one of three types:
## - moth: a few moths looping round a point (a lamp), each on its own tilted, bobbing orbit, with a jitter that is
##   re-drawn every fraction of a second and, now and then, a dart (a sudden larger jitter, chased fast). Moths
##   ignore the player.
## - dragonfly: a few dragonflies holding a hover (a slight drift), then darting in a straight, eased line to a new
##   spot within the area; now and then one darts to a free perch (if the row has `perches`) and sits there with
##   its wings still. A player within flee_radius_m makes a dragonfly dart away, perched or not.
## - firefly (Ch10, M4-A2P-056): the moth's orbit, slower and lower, each with a lantern that flashes once every
##   blink_s (its own period and phase), rising and falling over blink_on_s, and between flashes keeps a faint
##   glow_floor. The blink is the instance's mode parameter (the shader's mode 6).
## Every insect stays inside the area: within radius_m of the centre and height_m of its y (a perch excepted).
## The wing beat is the shader's flutter (mode 5), driven by each insect's phase. Headless and deterministic (the
## seed and the frame deltas). Tuning is the `insect` kind of wildlife.json (its `moth`, `dragonfly` and `firefly`
## tables); placement is a zone file's `swarms` row.

enum State { HOVER, DART, PERCHED }

const TYPE_MOTH := "moth"
const TYPE_DRAGONFLY := "dragonfly"
const TYPE_FIREFLY := "firefly"
## Numeric floors (not tuning): a zero distance or segment.
const MIN_DISTANCE_M := 1e-4
const MIN_SEGMENT_S := 0.01
## Tries for a flee target that leaves the player behind (a cornered dragonfly runs along the area's edge).
const FLEE_TRIES := 4
## How far a hovering dragonfly can stray from the spot it arrived at, in drift_m: two drift offsets (each at most
## sqrt(1.5) drift_m long) apart.
const DRIFT_REACH := 2.5


class Insect:
	extends RefCounted
	var state: int = State.HOVER
	var pos := Vector3.ZERO
	var yaw := 0.0
	var scale := 1.0
	var phase := 0.0
	var flutter_hz := 0.0
	var amp := 0.0
	var timer := 0.0
	## Moth: the orbit (angle, angular speed, radius), the bob and the jitter.
	var theta := 0.0
	var omega := 0.0
	var orbit_r := 0.0
	var bob_phase := 0.0
	var bob_hz := 0.0
	var jitter := Vector3.ZERO
	var jitter_goal := Vector3.ZERO
	var dart_timer := 0.0
	var darting := 0.0
	## Dragonfly: the hover point, the dart segment and the perch.
	var home := Vector3.ZERO
	var start := Vector3.ZERO
	var target := Vector3.ZERO
	var seg_t := 0.0
	var seg_dur := 1.0
	var perch := -1
	var drift_phase := 0.0
	var drift_hz := 0.0
	## Firefly: where it is in its blink cycle (seconds), the cycle's length, and the lantern now (0 .. 1).
	var blink_t := 0.0
	var blink_period := 1.0
	var glow := 0.0


var id := ""
var swarm_type := TYPE_MOTH
var center := Vector3.ZERO
var radius := 1.0
var height := 0.0
## Perches (dragonflies only): (x, y, z, yaw radians).
var perches: Array[Vector4] = []
var insects: Array[Insect] = []
var bounds := AABB()

var _kind: Dictionary = {}
var _rng := RandomNumberGenerator.new()
var _occupied: Array[bool] = []


## `kind` is the whole `insect` kind; the row's `type` picks its table.
func _init(row: Dictionary, kind: Dictionary, seed_value: int, count: int) -> void:
	_rng.seed = seed_value
	id = str(row.get("id", ""))
	swarm_type = str(row.get("type", TYPE_MOTH))
	_kind = kind[swarm_type]
	center = WildlifeConfig.vec3(row["center"])
	radius = float(row["radius_m"])
	height = _f("height_m")
	for p: Variant in row.get("perches", []):
		var a: Array = p
		perches.append(Vector4(float(a[0]), float(a[1]), float(a[2]), deg_to_rad(float(a[3]))))
		_occupied.append(false)
	for i in count:
		insects.append(_new_moth() if is_orbiter() else _new_dragonfly())
	var pad := 0.0 if is_orbiter() else _f("drift_m") * DRIFT_REACH
	var ext := Vector3(radius + pad, height + pad, radius + pad)
	bounds = AABB(center - ext, ext * 2.0)
	for p in perches:
		bounds = bounds.expand(Vector3(p.x, p.y, p.z))


func _f(key: String) -> float:
	return float(_kind[key])


func _r(key: String) -> float:
	return WildlifeConfig.draw(_rng, _kind[key])


func count() -> int:
	return insects.size()


func is_moth() -> bool:
	return swarm_type == TYPE_MOTH


func is_firefly() -> bool:
	return swarm_type == TYPE_FIREFLY


## Moths and fireflies fly the orbit; dragonflies hover and dart.
func is_orbiter() -> bool:
	return is_moth() or is_firefly()


func perched_count() -> int:
	var n := 0
	for d in insects:
		if d.state == State.PERCHED:
			n += 1
	return n


## Keeps a flight point inside the area: within `radius` of the centre (horizontally) and `height` of its y.
func clamp_to_area(p: Vector3) -> Vector3:
	var h := Vector2(p.x - center.x, p.z - center.z)
	if h.length() > radius:
		h = h.normalized() * radius
	return Vector3(center.x + h.x, clampf(p.y, center.y - height, center.y + height), center.z + h.y)


func _random_dir() -> Vector3:
	var v := Vector3(_rng.randf_range(-1.0, 1.0), _rng.randf_range(-1.0, 1.0), _rng.randf_range(-1.0, 1.0))
	return v.normalized() if v.length() > MIN_DISTANCE_M else Vector3.RIGHT


func _random_point() -> Vector3:
	var a := _rng.randf() * TAU
	var r := radius * sqrt(_rng.randf())
	return Vector3(center.x + cos(a) * r, center.y + _rng.randf_range(-height, height), center.z + sin(a) * r)


func step(delta: float, player: Vector3, has_player: bool) -> void:
	if is_orbiter():
		for m in insects:
			_step_moth(m, delta)
			if is_firefly():
				_step_blink(m, delta)
		return
	var pp := Vector2(player.x, player.z)
	var flee_r := _f("flee_radius_m")
	for d in insects:
		var near := has_player and Vector2(d.pos.x, d.pos.z).distance_to(pp) < flee_r
		match d.state:
			State.HOVER:
				d.timer -= delta
				if near:
					_flee(d, pp)
				elif d.timer <= 0.0:
					_next(d)
			State.PERCHED:
				d.timer -= delta
				if near:
					_flee(d, pp)
				elif d.timer <= 0.0:
					_dart(d, _hop_from(d.pos), _r("dart_speed_mps"))
			State.DART:
				pass
		_move_dragonfly(d, delta)


# --- moths ------------------------------------------------------------------------------------------------------
func _new_moth() -> Insect:
	var m := Insect.new()
	m.scale = _r("scale")
	m.orbit_r = radius * _r("orbit_fraction")
	m.omega = TAU * _r("orbit_hz") * (-1.0 if _rng.randf() < _f("counter_orbit_chance") else 1.0)
	m.theta = _rng.randf() * TAU
	m.bob_phase = _rng.randf() * TAU
	m.bob_hz = _r("bob_hz")
	m.flutter_hz = _r("flutter_hz")
	m.phase = _rng.randf() * TAU
	m.amp = _f("flutter_amp")
	m.dart_timer = _r("dart_s") * _rng.randf()
	if is_firefly():
		m.blink_period = _r("blink_s")
		m.blink_t = _rng.randf() * m.blink_period
		m.glow = _blink_glow(m)
	m.pos = _moth_goal(m)
	var turn := signf(m.omega)
	m.yaw = atan2(-sin(m.theta) * turn, cos(m.theta) * turn)  # along the orbit
	return m


func _moth_goal(m: Insect) -> Vector3:
	var orbit := Vector3(cos(m.theta) * m.orbit_r, sin(m.bob_phase) * _f("bob_m"), sin(m.theta) * m.orbit_r)
	return clamp_to_area(center + orbit + m.jitter)


func _step_moth(m: Insect, delta: float) -> void:
	m.theta = fposmod(m.theta + m.omega * delta, TAU)
	m.bob_phase = fposmod(m.bob_phase + TAU * m.bob_hz * delta, TAU)
	m.timer -= delta
	if m.timer <= 0.0:
		m.jitter_goal = _random_dir() * _f("jitter_m") * _rng.randf()
		m.timer = _r("jitter_s")
	m.dart_timer -= delta
	if m.dart_timer <= 0.0:
		m.jitter_goal = _random_dir() * _f("dart_m")
		m.darting = _f("dart_time_s")
		m.timer = _f("dart_time_s")
		m.dart_timer = _r("dart_s")
	var rate := _f("jitter_rate") * (_f("dart_rate_mult") if m.darting > 0.0 else 1.0)
	m.darting = maxf(m.darting - delta, 0.0)
	m.jitter = m.jitter.lerp(m.jitter_goal, 1.0 - exp(-rate * delta))
	var before := m.pos
	m.pos = _moth_goal(m)
	var vx := m.pos.x - before.x
	var vz := m.pos.z - before.z
	if vx * vx + vz * vz > MIN_DISTANCE_M * MIN_DISTANCE_M:
		m.yaw = WildlifeConfig.approach_angle(m.yaw, atan2(vx, vz), _f("turn_rate"), delta)
	m.phase = fposmod(m.phase + TAU * m.flutter_hz * delta, TAU)


# --- dragonflies ------------------------------------------------------------------------------------------------
func _new_dragonfly() -> Insect:
	var d := Insect.new()
	d.scale = _r("scale")
	d.flutter_hz = _r("flutter_hz")
	d.drift_hz = _r("drift_hz")
	d.drift_phase = _rng.randf() * TAU
	d.phase = _rng.randf() * TAU
	d.yaw = _rng.randf() * TAU
	d.amp = _f("hover_amp")
	d.timer = _r("hover_s") * _rng.randf()
	_settle(d, _random_point())
	return d


func _drift(d: Insect) -> Vector3:
	var p := d.drift_phase
	return Vector3(sin(p), 0.5 * sin(2.0 * p), sin(p + PI * 0.5) * 0.5) * _f("drift_m")


## Hovers at `at`: the drift's centre is put so the hover starts exactly there.
func _settle(d: Insect, at: Vector3) -> void:
	d.state = State.HOVER
	d.pos = at
	d.home = at - _drift(d)


## A new spot a dart away, inside the area.
func _hop_from(p: Vector3) -> Vector3:
	var a := _rng.randf() * TAU
	var dist := _r("dart_m")
	var y := center.y + _rng.randf_range(-height, height)
	return clamp_to_area(Vector3(p.x + cos(a) * dist, y, p.z + sin(a) * dist))


func _next(d: Insect) -> void:
	if not perches.is_empty() and _rng.randf() < _f("perch_chance"):
		var open_perches: Array[int] = []
		for k in perches.size():
			if not _occupied[k]:
				open_perches.append(k)
		if not open_perches.is_empty():
			var k := open_perches[_rng.randi() % open_perches.size()]
			_occupied[k] = true
			var p := perches[k]
			_dart(d, Vector3(p.x, p.y, p.z), _r("dart_speed_mps"))
			d.perch = k
			return
	_dart(d, _hop_from(d.pos), _r("dart_speed_mps"))


func _dart(d: Insect, to: Vector3, speed: float) -> void:
	if d.perch >= 0:
		_occupied[d.perch] = false
		d.perch = -1
	d.state = State.DART
	d.start = d.pos
	d.target = to
	d.seg_t = 0.0
	d.seg_dur = maxf(d.start.distance_to(to) / maxf(speed, MIN_DISTANCE_M), MIN_SEGMENT_S)


## Darts away from the player (pp, horizontal): straight away if the area allows, else along its edge.
func _flee(d: Insect, pp: Vector2) -> void:
	var here := Vector2(d.pos.x, d.pos.z)
	var away := here - pp
	away = away.normalized() if away.length() > MIN_DISTANCE_M else Vector2.RIGHT.rotated(d.yaw)
	var dist := _f("flee_m")
	var y := center.y + _rng.randf_range(-height, height)
	var best := d.pos
	var best_d := -1.0
	for k in FLEE_TRIES:
		var dir := away.rotated(k * PI / float(FLEE_TRIES) * (1.0 if k % 2 == 0 else -1.0))
		var t := clamp_to_area(Vector3(here.x + dir.x * dist, y, here.y + dir.y * dist))
		var dd := Vector2(t.x, t.z).distance_to(pp)
		if dd > best_d:
			best = t
			best_d = dd
	_dart(d, best, _f("flee_speed_mps"))


func _move_dragonfly(d: Insect, delta: float) -> void:
	var rate := _f("amp_rate")
	match d.state:
		State.DART:
			d.seg_t += delta
			var t := clampf(d.seg_t / d.seg_dur, 0.0, 1.0)
			d.pos = d.start.lerp(d.target, smoothstep(0.0, 1.0, t))
			var to := d.target - d.start
			if to.x * to.x + to.z * to.z > MIN_DISTANCE_M * MIN_DISTANCE_M:
				d.yaw = WildlifeConfig.approach_angle(d.yaw, atan2(to.x, to.z), _f("turn_rate"), delta)
			d.amp = WildlifeConfig.approach(d.amp, _f("dart_amp"), rate, delta)
			if t >= 1.0:
				if d.perch >= 0:
					d.state = State.PERCHED
					d.pos = d.target
					d.timer = _r("perch_s")
				else:
					_settle(d, d.target)
					d.timer = _r("hover_s")
		State.HOVER:
			d.drift_phase = fposmod(d.drift_phase + TAU * d.drift_hz * delta, TAU)
			d.pos = d.home + _drift(d)
			d.amp = WildlifeConfig.approach(d.amp, _f("hover_amp"), rate, delta)
		State.PERCHED:
			d.yaw = WildlifeConfig.approach_angle(d.yaw, perches[d.perch].w, _f("turn_rate"), delta)
			d.amp = WildlifeConfig.approach(d.amp, 0.0, rate, delta)
	d.phase = fposmod(d.phase + TAU * d.flutter_hz * delta, TAU)


# --- fireflies --------------------------------------------------------------------------------------------------
## The lantern over its cycle: a flash that rises and falls over blink_on_s (a sine squared), then glow_floor.
func _blink_glow(m: Insect) -> float:
	var on := _f("blink_on_s")
	var floor_glow := _f("glow_floor")
	if m.blink_t >= on:
		return floor_glow
	var s := sin(PI * m.blink_t / on)
	return maxf(s * s, floor_glow)


func _step_blink(m: Insect, delta: float) -> void:
	m.blink_t += delta
	if m.blink_t >= m.blink_period:
		m.blink_t -= m.blink_period
		m.blink_period = _r("blink_s")
	m.glow = _blink_glow(m)


func transform_of(i: Insect) -> Transform3D:
	return Transform3D(Basis(Vector3.UP, i.yaw).scaled(Vector3.ONE * i.scale), i.pos)


func write(buf: WildlifeBuffer, base: int) -> void:
	var glows := is_firefly()
	for i in insects.size():
		var it := insects[i]
		var mode := WildlifeBuffer.MODE_GLOW if glows else WildlifeBuffer.MODE_FLUTTER
		buf.put(base + i, transform_of(it), it.phase, it.amp, mode, it.glow if glows else 0.0)
