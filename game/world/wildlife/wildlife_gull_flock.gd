class_name WildlifeGullFlock
extends RefCounted
## One flock of ambient gulls (M3-CRE-611, docs/kb/art/wildlife.md): a few birds circling a centre at their own
## radius and height, flapping in bursts between glides, now and then gliding in to a free perch, standing there
## a while turning their heads, and taking off back into the circle. Headless and deterministic: the motion
## depends only on the seed and the frame deltas. Tuning is the `gull` kind of wildlife.json; placement is a
## zone file's `flocks` row. A kind with `dive_chance` (the kingfisher, Ch10: fen_kingfisher.md "it perches long, and
## plunges") on a row with a `water_y` sometimes leaves its perch in a plunge: wings folded, down to the water
## dive_reach_m ahead of the perch, a moment there, and back up to the same perch, which it keeps meanwhile. The party
## coming within flush_radius_m of a perch lifts the bird off it after its own flush_delay_s (so a row of gulls goes
## up one after another, not as one), and a landing bird never picks a perch the party is standing by.

enum State { SOAR, APPROACH, PERCHED, TAKEOFF, DIVE, SURFACE }

## Guards against a zero orbit or segment (numeric floors, not tuning).
const MIN_ORBIT_M := 0.01
const MIN_SEGMENT_S := 0.01


class Gull:
	extends RefCounted
	var state: int = State.SOAR
	var pos := Vector3.ZERO
	var vel := Vector3.ZERO
	var acc := Vector3.ZERO
	var theta := 0.0
	var orbit_r := 1.0
	var alt := 0.0
	var omega := 0.0
	var speed := 1.0
	var undulate_phase := 0.0
	var scale := 1.0
	var flap_phase := 0.0
	var amp := 0.0
	var flapping := false
	var flap_timer := 0.0
	var decide_timer := 0.0
	var perch := -1
	var seg_t := 0.0
	var seg_dur := 1.0
	var p0 := Vector3.ZERO
	var m0 := Vector3.ZERO
	var p1 := Vector3.ZERO
	var m1 := Vector3.ZERO
	var timer := 0.0
	var head_yaw := 0.0
	var head_target := 0.0
	var head_timer := 0.0
	var nod := 0.0
	var nod_phase := 0.0
	## Its own delay before it lifts when the party comes near (the kind's flush_delay_s, drawn once).
	var flush_at := 0.0


var id := ""
var center := Vector3.ZERO
var radius := 1.0
var altitude := Vector2.ONE
## The water's surface under the perches (a row's `water_y`), or NAN: no water to dive to.
var water_y := NAN
## Perches: (x, y, z, yaw radians).
var perches: Array[Vector4] = []
var gulls: Array[Gull] = []
var bounds := AABB()

var _kind: Dictionary = {}
var _rng := RandomNumberGenerator.new()
var _occupied: Array[bool] = []
var _gravity := 0.0
var _bank_max := 0.0
var _pitch_max := 0.0
var _undulate := 0.0
var _amp_rate := 0.0
var _flap_hz := 0.0
var _dihedral := 0.0
var _player := Vector2.ZERO
var _has_player := false


func _init(row: Dictionary, kind: Dictionary, seed_value: int, count: int) -> void:
	_kind = kind
	_rng.seed = seed_value
	id = str(row.get("id", ""))
	var c := WildlifeConfig.vec2(row.get("center", [0.0, 0.0]))
	center = Vector3(c.x, 0.0, c.y)
	radius = float(row.get("radius_m", 1.0))
	altitude = WildlifeConfig.vec2(row.get("altitude_m", [1.0, 1.0]))
	water_y = float(row["water_y"]) if row.has("water_y") else NAN
	for p: Variant in row.get("perches", []):
		var a: Array = p
		perches.append(Vector4(float(a[0]), float(a[1]), float(a[2]), deg_to_rad(float(a[3]))))
		_occupied.append(false)
	_gravity = _f("gravity_mps2")
	_bank_max = deg_to_rad(_f("bank_max_deg"))
	_pitch_max = deg_to_rad(_f("pitch_max_deg"))
	_undulate = _f("undulate_m")
	_amp_rate = _f("amp_rate")
	_flap_hz = _f("flap_hz")
	_dihedral = deg_to_rad(_f("glide_dihedral_deg"))
	for i in count:
		gulls.append(_spawn())
	# `perched_at_start` birds are already standing on the first perches when the zone opens
	for i in mini(int(row.get("perched_at_start", 0)), mini(count, perches.size())):
		var g := gulls[i]
		g.perch = i
		_occupied[i] = true
		g.state = State.PERCHED
		g.timer = _r("perch_s")
		g.amp = 0.0
		g.pos = Vector3(perches[i].x, perches[i].y, perches[i].z)
		g.vel = Vector3.ZERO
	var lo := altitude.x - _undulate
	for p in perches:
		lo = minf(lo, p.y)
	if not is_nan(water_y):
		lo = minf(lo, water_y)
	var hi := altitude.y + _undulate
	bounds = AABB(Vector3(center.x - radius, lo, center.z - radius), Vector3(radius * 2.0, hi - lo, radius * 2.0))


func _spawn() -> Gull:
	var g := Gull.new()
	g.orbit_r = radius * _r("orbit_fraction")
	g.alt = _rng.randf_range(altitude.x, altitude.y)
	g.speed = _r("speed_mps")
	var sense := -1.0 if _rng.randf() < _f("counter_orbit_chance") else 1.0
	g.omega = sense * g.speed / maxf(g.orbit_r, MIN_ORBIT_M)
	g.theta = _rng.randf() * TAU
	g.undulate_phase = _rng.randf() * TAU
	g.scale = _r("scale")
	g.flap_phase = _rng.randf() * TAU
	g.flapping = _rng.randf() < _f("flap_start_chance")
	g.flap_timer = _r("flap_s" if g.flapping else "glide_s")
	g.amp = 1.0 if g.flapping else 0.0
	g.decide_timer = _r("decide_s")
	g.flush_at = _r("flush_delay_s") if _kind.has("flush_delay_s") else 0.0
	_soar_pose(g)
	return g


func _f(key: String) -> float:
	return float(_kind[key])


func _r(key: String) -> float:
	return WildlifeConfig.draw(_rng, _kind[key])


func count() -> int:
	return gulls.size()


func perched_count() -> int:
	var n := 0
	for g in gulls:
		if g.state == State.PERCHED:
			n += 1
	return n


## `player` is in the layer's space; `has_player` false = nobody to flush them.
func step(delta: float, player := Vector3.ZERO, has_player := false) -> void:
	_player = Vector2(player.x, player.z)
	_has_player = has_player
	for g in gulls:
		match g.state:
			State.SOAR:
				_step_soar(g, delta)
			State.APPROACH:
				_step_segment(g, delta, true)
			State.PERCHED:
				_step_perched(g, delta)
			State.TAKEOFF:
				_step_segment(g, delta, false)
			State.DIVE:
				_step_dive(g, delta)
			State.SURFACE:
				_step_surface(g, delta)


func _soar_pose(g: Gull) -> void:
	var u := g.theta * 2.0 + g.undulate_phase
	var c := cos(g.theta)
	var s := sin(g.theta)
	g.pos = center + Vector3(c * g.orbit_r, g.alt + _undulate * sin(u), s * g.orbit_r)
	g.vel = Vector3(-s * g.orbit_r * g.omega, _undulate * 2.0 * g.omega * cos(u), c * g.orbit_r * g.omega)
	g.acc = Vector3(-c, 0.0, -s) * g.orbit_r * g.omega * g.omega


func _step_soar(g: Gull, delta: float) -> void:
	g.theta = fposmod(g.theta + g.omega * delta, TAU)
	_soar_pose(g)
	g.flap_timer -= delta
	if g.flap_timer <= 0.0:
		g.flapping = not g.flapping
		g.flap_timer = _r("flap_s" if g.flapping else "glide_s")
	_flap(g, delta, 1.0 if g.flapping else 0.0)
	g.decide_timer -= delta
	if g.decide_timer <= 0.0:
		g.decide_timer = _r("decide_s")
		if _rng.randf() < _f("perch_chance"):
			_try_land(g)


func _flap(g: Gull, delta: float, target: float) -> void:
	g.amp = WildlifeConfig.approach(g.amp, target, _amp_rate, delta)
	g.flap_phase = fposmod(g.flap_phase + TAU * _flap_hz * delta, TAU)


func _try_land(g: Gull) -> void:
	var free: Array[int] = []
	for k in perches.size():
		if not _occupied[k] and not _near_party(perches[k]):
			free.append(k)
	if free.is_empty():
		return
	var k := free[_rng.randi_range(0, free.size() - 1)]
	_occupied[k] = true
	g.perch = k
	var p := perches[k]
	var target := Vector3(p.x, p.y, p.z)
	var dur := maxf(_r("approach_s"), g.pos.distance_to(target) / g.speed)
	var land_dir := Vector3(sin(p.w), 0.0, cos(p.w))
	_begin_segment(g, target, g.vel, land_dir * _f("landing_speed_mps"), dur)
	g.state = State.APPROACH


func _begin_segment(g: Gull, target: Vector3, v0: Vector3, v1: Vector3, dur: float) -> void:
	g.p0 = g.pos
	g.p1 = target
	g.m0 = v0 * dur
	g.m1 = v1 * dur
	g.seg_t = 0.0
	g.seg_dur = maxf(dur, MIN_SEGMENT_S)


## A cubic Hermite segment (approach and take-off): position, velocity and acceleration at t in 0..1.
func _hermite(g: Gull, t: float) -> void:
	var t2 := t * t
	var t3 := t2 * t
	g.pos = (
		g.p0 * (2.0 * t3 - 3.0 * t2 + 1.0)
		+ g.m0 * (t3 - 2.0 * t2 + t)
		+ g.p1 * (-2.0 * t3 + 3.0 * t2)
		+ g.m1 * (t3 - t2)
	)
	var d := (
		g.p0 * (6.0 * t2 - 6.0 * t)
		+ g.m0 * (3.0 * t2 - 4.0 * t + 1.0)
		+ g.p1 * (-6.0 * t2 + 6.0 * t)
		+ g.m1 * (3.0 * t2 - 2.0 * t)
	)
	var dd := g.p0 * (12.0 * t - 6.0) + g.m0 * (6.0 * t - 4.0) + g.p1 * (-12.0 * t + 6.0) + g.m1 * (6.0 * t - 2.0)
	g.vel = d / g.seg_dur
	g.acc = dd / (g.seg_dur * g.seg_dur)


func _step_segment(g: Gull, delta: float, landing: bool) -> void:
	g.seg_t = minf(g.seg_t + delta / g.seg_dur, 1.0)
	_hermite(g, g.seg_t)
	# landing: glide in, then beat hard over the last stretch (the flare); take-off: beat all the way up
	_flap(g, delta, (1.0 if g.seg_t > _f("flare_from") else _f("approach_amp")) if landing else 1.0)
	if g.seg_t < 1.0:
		return
	if landing:
		g.state = State.PERCHED
		g.timer = _r("perch_s")
		g.head_timer = 0.0
		g.amp = 0.0
		var p := perches[g.perch]
		g.pos = Vector3(p.x, p.y, p.z)
		g.vel = Vector3.ZERO
	else:
		g.state = State.SOAR
		g.flapping = true
		g.flap_timer = _r("flap_s")
		g.decide_timer = _r("decide_s")
		_soar_pose(g)


## True when the party stands within the kind's flush_radius_m of perch `p` (a kind without one never flushes).
func _near_party(p: Vector4) -> bool:
	var r := float(_kind.get("flush_radius_m", 0.0))
	return _has_player and r > 0.0 and _player.distance_to(Vector2(p.x, p.z)) < r


func _step_perched(g: Gull, delta: float) -> void:
	if _near_party(perches[g.perch]) and g.timer > g.flush_at:
		g.timer = g.flush_at  # flushed: it goes after its own delay
	g.timer -= delta
	g.head_timer -= delta
	if g.head_timer <= 0.0:
		g.head_timer = _r("head_turn_s")
		var yaw_max := deg_to_rad(_f("head_yaw_deg"))
		g.head_target = _rng.randf_range(-yaw_max, yaw_max)
		g.nod = 1.0 if _rng.randf() < _f("nod_chance") else 0.0
		g.nod_phase = 0.0
	g.head_yaw = WildlifeConfig.approach_angle(g.head_yaw, g.head_target, _f("head_rate"), delta)
	g.nod_phase = fposmod(g.nod_phase + TAU * _f("nod_hz") * delta, TAU)
	if g.timer > 0.0:
		return
	if (
		not is_nan(water_y)
		and not _near_party(perches[g.perch])
		and _rng.randf() < float(_kind.get("dive_chance", 0.0))
	):
		_begin_dive(g)
		return
	# take off along the perch's facing and climb back into the circle a little ahead of the perch
	var p := perches[g.perch]
	_occupied[g.perch] = false
	g.perch = -1
	var ahead := atan2(p.z - center.z, p.x - center.x) + signf(g.omega) * deg_to_rad(_f("takeoff_lead_deg"))
	g.theta = fposmod(ahead, TAU)
	var from := g.pos
	_soar_pose(g)
	var to := g.pos
	var circle_vel := g.vel
	g.pos = from
	var dir := Vector3(sin(p.w), 0.0, cos(p.w))
	var climb := Vector3.UP * _f("takeoff_lift_m")
	var dur := maxf(_r("takeoff_s"), from.distance_to(to) / g.speed)
	_begin_segment(g, to, dir * g.speed * _f("takeoff_speed_fraction") + climb / dur, circle_vel, dur)
	g.state = State.TAKEOFF


## The plunge: off the perch with a hop, wings folded, steeply down to the water dive_reach_m ahead of it.
func _begin_dive(g: Gull) -> void:
	var p := perches[g.perch]
	var dir := Vector3(sin(p.w), 0.0, cos(p.w))
	var target := Vector3(p.x, water_y, p.z) + dir * _r("dive_reach_m")
	var v1 := (dir * 0.3 + Vector3.DOWN).normalized() * _f("dive_speed_mps")
	_begin_segment(g, target, dir * _f("landing_speed_mps") + Vector3.UP, v1, _r("dive_s"))
	g.state = State.DIVE


func _step_dive(g: Gull, delta: float) -> void:
	g.seg_t = minf(g.seg_t + delta / g.seg_dur, 1.0)
	_hermite(g, g.seg_t)
	_flap(g, delta, 0.0)  # folded
	if g.seg_t < 1.0:
		return
	g.state = State.SURFACE
	g.timer = _r("dive_hold_s")
	g.vel = Vector3(g.vel.x, 0.0, g.vel.z).normalized() * 0.1  # it keeps facing on along its plunge
	g.acc = Vector3.ZERO


## At the water a moment, then beating hard straight back up to its perch (the landing segment).
func _step_surface(g: Gull, delta: float) -> void:
	g.timer -= delta
	_flap(g, delta, 1.0)
	if g.timer > 0.0:
		return
	var p := perches[g.perch]
	var land_dir := Vector3(sin(p.w), 0.0, cos(p.w))
	var up := Vector3.UP * _f("dive_speed_mps") * 0.5
	_begin_segment(g, Vector3(p.x, p.y, p.z), up, land_dir * _f("landing_speed_mps"), _r("dive_return_s"))
	g.state = State.APPROACH


## The bird's transform: in flight it faces along its velocity, pitched within pitch_max and banked into its
## turn (the lift tilts toward the turn's acceleration, within bank_max); on a perch it faces the perch's yaw.
func transform_of(g: Gull) -> Transform3D:
	if g.state == State.PERCHED:
		var p := perches[g.perch]
		return Transform3D(Basis(Vector3.UP, p.w).scaled(Vector3.ONE * g.scale), g.pos)
	var fwd := g.vel
	if fwd.length_squared() < 1e-8:
		fwd = Vector3.BACK
	fwd = fwd.normalized()
	var flat := Vector2(fwd.x, fwd.z).length()
	var pitch := clampf(atan2(fwd.y, flat), -_pitch_max, _pitch_max)
	var h := Vector3(fwd.x, 0.0, fwd.z).normalized() if flat > 1e-6 else Vector3.BACK
	fwd = h * cos(pitch) + Vector3.UP * sin(pitch)
	var lateral := g.acc - fwd * g.acc.dot(fwd)
	lateral.y = 0.0
	var up := (Vector3.UP * _gravity + lateral).normalized()
	var tilt := up.angle_to(Vector3.UP)
	if tilt > _bank_max and tilt > 1e-6:
		up = Vector3.UP.slerp(up, _bank_max / tilt)
	var x := up.cross(fwd).normalized()
	var y := fwd.cross(x)
	return Transform3D(Basis(x, y, fwd).scaled(Vector3.ONE * g.scale), g.pos)


## Writes the flock into the flying and perched buffers from instance `base`.
func write(flying: WildlifeBuffer, perched: WildlifeBuffer, base: int) -> void:
	for i in gulls.size():
		var g := gulls[i]
		if g.state == State.PERCHED:
			flying.hide(base + i)
			perched.put(base + i, transform_of(g), g.nod_phase, g.nod, WildlifeBuffer.MODE_HEAD, g.head_yaw)
		else:
			perched.hide(base + i)
			var param := _dihedral * (1.0 - g.amp)
			flying.put(base + i, transform_of(g), g.flap_phase, g.amp, WildlifeBuffer.MODE_FLAP, param)
