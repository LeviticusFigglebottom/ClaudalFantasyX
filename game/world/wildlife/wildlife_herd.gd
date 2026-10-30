class_name WildlifeHerd
extends RefCounted
## A few grazing woolbacks (Ch12 Keth Pass, M4-A2P-056; docs/kb/art/wildlife.md): skinned actors, not MultiMesh,
## since a herd is two or three animals close to the path. Each grazes (its `idle` clip) for a while, now and then
## lifts its head and looks round (`look`), and every so often ambles (`walk`) to a new spot in the herd's area,
## turning toward it on the way. A player within look_radius_m makes a grazing animal look up; nothing flees. The
## walk moves the animal at walk_speed_mps, the speed the walk clip's planted hooves slide back at (its build,
## build_woolback.py WALK_SPEED x its scale), so the hooves stay put. Headless and deterministic (the seed and the
## frame deltas); WildlifeLayer puts the actors where this says and plays the clip it names. Tuning is the
## `woolback` kind of wildlife.json; placement is a zone file's `herds` row.

enum State { GRAZE, LOOK, WALK }

const CLIP_GRAZE := &"idle"
const CLIP_LOOK := &"look"
const CLIP_WALK := &"walk"
const MIN_DISTANCE_M := 1e-4
## Tries for a walk target that keeps spacing_m from the others' spots.
const SPACING_TRIES := 6


class Animal:
	extends RefCounted
	var state: int = State.GRAZE
	var pos := Vector2.ZERO
	var y := 0.0
	var yaw := 0.0
	var target := Vector2.ZERO
	var timer := 0.0
	var scale := 1.0
	## The clip to play, and whether it changed since the layer last started it (the layer clears it).
	var clip: StringName = CLIP_GRAZE
	var clip_changed := true


var id := ""
var center := Vector2.ZERO
var radius := 1.0
var base_y := 0.0
var animals: Array[Animal] = []
var bounds := AABB()
## Ground height (x, z) -> y; empty = the row's flat `y`.
var ground := Callable()

var _kind: Dictionary = {}
var _rng := RandomNumberGenerator.new()


func _init(row: Dictionary, kind: Dictionary, seed_value: int, count: int, ground_fn: Callable) -> void:
	_kind = kind
	_rng.seed = seed_value
	ground = ground_fn
	id = str(row.get("id", ""))
	center = WildlifeConfig.vec2(row["center"])
	radius = float(row["radius_m"])
	base_y = float(row.get("y", 0.0))
	for i in count:
		var a := Animal.new()
		a.pos = _free_spot(a)
		a.target = a.pos
		a.yaw = _rng.randf() * TAU
		a.scale = _r("scale")
		a.timer = _r("graze_s") * _rng.randf()
		a.y = height(a.pos)
		animals.append(a)
	var pad := _f("bounds_pad_m")
	bounds = AABB(
		Vector3(center.x - radius - pad, base_y - pad, center.y - radius - pad),
		Vector3((radius + pad) * 2.0, pad * 2.0 + _f("height_m"), (radius + pad) * 2.0)
	)


func _f(key: String) -> float:
	return float(_kind[key])


func _r(key: String) -> float:
	return WildlifeConfig.draw(_rng, _kind[key])


func count() -> int:
	return animals.size()


func height(p: Vector2) -> float:
	if ground.is_valid():
		var h := float(ground.call(p.x, p.y))
		if not is_nan(h):  # a physics ground answers NAN until the zone's collision is ready
			return h
	return base_y


## A spot in the area at least spacing_m from every other animal's spot (the best of a few tries).
func _free_spot(me: Animal) -> Vector2:
	var best := center
	var best_gap := -1.0
	for t in SPACING_TRIES:
		var a := _rng.randf() * TAU
		var p := center + Vector2(cos(a), sin(a)) * radius * sqrt(_rng.randf())
		var gap := INF
		for o in animals:
			if o != me:
				gap = minf(gap, minf(o.pos.distance_to(p), o.target.distance_to(p)))
		if gap >= _f("spacing_m"):
			return p
		if gap > best_gap:
			best_gap = gap
			best = p
	return best


func _set_clip(a: Animal, clip: StringName) -> void:
	a.clip_changed = a.clip_changed or a.clip != clip
	a.clip = clip


func step(delta: float, player: Vector3, has_player: bool) -> void:
	var pp := Vector2(player.x, player.z)
	for a in animals:
		a.timer -= delta
		match a.state:
			State.GRAZE:
				var near := has_player and a.pos.distance_to(pp) < _f("look_radius_m")
				if near and _rng.randf() < _f("look_rate") * delta:
					_look(a)
				elif a.timer <= 0.0:
					if _rng.randf() < _f("look_chance"):
						_look(a)
					else:
						_walk(a)
			State.LOOK:
				if a.timer <= 0.0:
					_graze(a)
			State.WALK:
				var to := a.target - a.pos
				var d := to.length()
				if d <= _f("arrive_m"):
					_graze(a)
				else:
					a.yaw = WildlifeConfig.approach_angle(a.yaw, atan2(to.x, to.y), _f("turn_rate"), delta)
					var fwd := Vector2(sin(a.yaw), cos(a.yaw))
					# it walks along its heading (no side-slip), slowing while it turns hard toward the target
					var along := maxf(fwd.dot(to / d), 0.0)
					var s := minf(_f("walk_speed_mps") * a.scale * along * delta, d)
					a.pos += fwd * s
					a.y = height(a.pos)


func _graze(a: Animal) -> void:
	a.state = State.GRAZE
	a.timer = _r("graze_s")
	_set_clip(a, CLIP_GRAZE)


func _look(a: Animal) -> void:
	a.state = State.LOOK
	a.timer = _f("look_s")
	_set_clip(a, CLIP_LOOK)


func _walk(a: Animal) -> void:
	a.state = State.WALK
	var dist := _r("wander_m")
	for t in SPACING_TRIES:
		var p := _free_spot(a)
		if p.distance_to(a.pos) > MIN_DISTANCE_M:
			a.target = a.pos + (p - a.pos).limit_length(dist)
			break
	_set_clip(a, CLIP_WALK)


func transform_of(a: Animal) -> Transform3D:
	return Transform3D(Basis(Vector3.UP, a.yaw).scaled(Vector3.ONE * a.scale), Vector3(a.pos.x, a.y, a.pos.y))
