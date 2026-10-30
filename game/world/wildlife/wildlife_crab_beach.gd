class_name WildlifeCrabBeach
extends RefCounted
## One beach of ambient shore crabs (M3-CRE-611, docs/kb/art/wildlife.md): each crab keeps a home spot in its
## area, shuffles near it now and then, and when the player comes within flee_radius_m it turns side-on and
## scuttles away until it is safe_radius_m off (never leaving the area), holds still a few seconds, and walks
## back home once the player has gone. Headless and deterministic (the seed and the frame deltas). Tuning is
## the `crab` kind of wildlife.json; placement is a zone file's `beaches` row.

enum State { IDLE, WALK, FLEE, WARY, RETURN }

const MIN_DISTANCE_M := 1e-4
## Below this gait amplitude (and turn left, radians) a resting crab is settled and skips its update.
const AMP_REST := 1e-3


class Crab:
	extends RefCounted
	var state: int = State.IDLE
	var home := Vector2.ZERO
	var pos := Vector2.ZERO
	var y := 0.0
	var yaw := 0.0
	var target_yaw := 0.0
	var target := Vector2.ZERO
	var speed := 0.0
	var timer := 0.0
	var amp := 0.0
	var gait_phase := 0.0
	var gait_hz := 0.0
	var scale := 1.0


var id := ""
var center := Vector2.ZERO
var half := Vector2.ONE
var yaw := 0.0
var base_y := 0.0
var crabs: Array[Crab] = []
var bounds := AABB()
## Ground height (x, z) -> y; empty = the area's flat `y`.
var ground := Callable()

var _kind: Dictionary = {}
var _rng := RandomNumberGenerator.new()
var _turn_rate := 0.0
var _amp_rate := 0.0
var _arrive := 0.0
var _flee_r := 0.0
var _safe_r := 0.0


func _init(row: Dictionary, kind: Dictionary, seed_value: int, count: int, ground_fn: Callable) -> void:
	_kind = kind
	_rng.seed = seed_value
	ground = ground_fn
	id = str(row.get("id", ""))
	center = WildlifeConfig.vec2(row["center"])
	half = WildlifeConfig.vec2(row["half_extents"])
	yaw = deg_to_rad(float(row.get("yaw_deg", 0.0)))
	base_y = float(row.get("y", 0.0))
	_turn_rate = _f("turn_rate")
	_amp_rate = _f("amp_rate")
	_arrive = _f("arrive_m")
	_flee_r = _f("flee_radius_m")
	_safe_r = _f("safe_radius_m")
	for i in count:
		var c := Crab.new()
		c.home = to_world(Vector2(_rng.randf_range(-half.x, half.x), _rng.randf_range(-half.y, half.y)))
		c.pos = c.home
		c.yaw = _rng.randf() * TAU
		c.target_yaw = c.yaw
		c.scale = _r("scale")
		c.timer = _r("shuffle_s")
		c.gait_phase = _rng.randf() * TAU
		c.y = height(c.pos)
		crabs.append(c)
	var r := absf(half.x * cos(yaw)) + absf(half.y * sin(yaw))
	var s := absf(half.x * sin(yaw)) + absf(half.y * cos(yaw))
	var lo := base_y
	var hi := base_y
	for c in crabs:
		lo = minf(lo, c.y)
		hi = maxf(hi, c.y)
	var pad := _f("safe_radius_m")
	bounds = AABB(Vector3(center.x - r, lo - pad, center.y - s), Vector3(r * 2.0, hi - lo + pad * 2.0, s * 2.0))


func _f(key: String) -> float:
	return float(_kind[key])


func _r(key: String) -> float:
	return WildlifeConfig.draw(_rng, _kind[key])


func count() -> int:
	return crabs.size()


func height(p: Vector2) -> float:
	if ground.is_valid():
		var h := float(ground.call(p.x, p.y))
		if not is_nan(h):  # a physics ground answers NAN until the zone's collision is ready
			return h
	return base_y


## Area-local (x along the area's yawed x, y along its z) to world (x, z), and back.
func to_world(local: Vector2) -> Vector2:
	return center + local.rotated(-yaw)


func to_local(world: Vector2) -> Vector2:
	return (world - center).rotated(yaw)


func clamp_to_area(world: Vector2) -> Vector2:
	var l := to_local(world)
	return to_world(Vector2(clampf(l.x, -half.x, half.x), clampf(l.y, -half.y, half.y)))


func contains(world: Vector2, margin: float = 0.0) -> bool:
	var l := to_local(world)
	return absf(l.x) <= half.x + margin and absf(l.y) <= half.y + margin


## `player` is in the layer's space; `has_player` false = nobody to flee from.
func step(delta: float, player: Vector3, has_player: bool) -> void:
	var pp := Vector2(player.x, player.z)
	var flee_r := _flee_r
	var safe_r := _safe_r
	for c in crabs:
		var d := c.pos.distance_to(pp) if has_player else INF
		match c.state:
			State.IDLE:
				c.timer -= delta
				if d < flee_r:
					_flee(c, pp, d)
				elif c.timer <= 0.0:
					var off := Vector2(_rng.randf_range(-1.0, 1.0), _rng.randf_range(-1.0, 1.0)) * _f("shuffle_m")
					_walk(c, clamp_to_area(c.home + off), State.WALK)
			State.WALK, State.RETURN:
				if d < flee_r:
					_flee(c, pp, d)
			State.FLEE:
				pass
			State.WARY:
				c.timer -= delta
				if d < flee_r:
					_flee(c, pp, d)
				elif c.timer <= 0.0 and d > safe_r:
					_walk(c, c.home, State.RETURN)
		_move(c, delta, pp, d)


func _flee(c: Crab, pp: Vector2, d: float) -> void:
	var away := (c.pos - pp) / d if d > MIN_DISTANCE_M else Vector2.RIGHT.rotated(c.yaw)
	var goal := clamp_to_area(c.pos + away * (_f("safe_radius_m") - d))
	if goal.distance_to(c.pos) < _f("arrive_m"):
		# cornered against the area's edge: run along it instead, the side that leads away
		var along := Vector2(-away.y, away.x)
		var g1 := clamp_to_area(c.pos + along * _f("safe_radius_m"))
		var g2 := clamp_to_area(c.pos - along * _f("safe_radius_m"))
		goal = g1 if g1.distance_to(pp) >= g2.distance_to(pp) else g2
	c.state = State.FLEE
	c.target = goal
	c.speed = _f("flee_speed_mps")
	c.gait_hz = _f("gait_hz")
	_face_sideways(c, goal - c.pos)


func _walk(c: Crab, goal: Vector2, state: int) -> void:
	c.state = state
	c.target = goal
	c.speed = _f("walk_speed_mps")
	c.gait_hz = _f("walk_gait_hz")
	_face_sideways(c, goal - c.pos)


## A crab runs sideways: turn so its local +x or -x (whichever is nearer) points along `dir`.
func _face_sideways(c: Crab, dir: Vector2) -> void:
	if dir.length_squared() < MIN_DISTANCE_M * MIN_DISTANCE_M:
		return
	var a := atan2(-dir.y, dir.x)
	var b := a + PI
	c.target_yaw = a if absf(angle_difference(c.yaw, a)) <= absf(angle_difference(c.yaw, b)) else b


func _move(c: Crab, delta: float, pp: Vector2, d: float) -> void:
	var moving := c.state == State.WALK or c.state == State.FLEE or c.state == State.RETURN
	if not moving and c.amp < AMP_REST and absf(angle_difference(c.yaw, c.target_yaw)) < AMP_REST:
		c.amp = 0.0
		return  # at rest: nothing to move (the common case, kept cheap)
	c.yaw = WildlifeConfig.approach_angle(c.yaw, c.target_yaw, _turn_rate, delta)
	c.amp = WildlifeConfig.approach(c.amp, 1.0 if moving else 0.0, _amp_rate, delta)
	if c.amp > 0.0:
		c.gait_phase = fposmod(c.gait_phase + TAU * c.gait_hz * delta, TAU)
	if not moving:
		return
	var to := c.target - c.pos
	var step_len := c.speed * delta
	if to.length() <= maxf(step_len, _arrive):
		c.pos = c.target
		c.y = height(c.pos)
		match c.state:
			State.FLEE:
				var now := c.pos.distance_to(pp) if d < INF else INF
				if now < _flee_r:
					_flee(c, pp, now)
				else:
					c.state = State.WARY
					c.timer = _r("return_after_s")
			State.WALK, State.RETURN:
				c.state = State.IDLE
				c.timer = _r("shuffle_s")
		return
	c.pos += to.normalized() * step_len
	c.y = height(c.pos)


func transform_of(c: Crab) -> Transform3D:
	return Transform3D(Basis(Vector3.UP, c.yaw).scaled(Vector3.ONE * c.scale), Vector3(c.pos.x, c.y, c.pos.y))


func write(buf: WildlifeBuffer, base: int) -> void:
	for i in crabs.size():
		var c := crabs[i]
		buf.put(base + i, transform_of(c), c.gait_phase, c.amp, WildlifeBuffer.MODE_LEGS, 0.0)
