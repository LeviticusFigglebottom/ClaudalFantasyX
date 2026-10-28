class_name HeroStairFlight
extends Node3D
## One steep flight of stairs walked on a path (M3-ARC-1216, ADR 0193; tuning: game/data/hero_motion/stairs.json).
## The node's origin is the centre of the flight's foot (on the lower floor); the flight climbs along the node's -Z
## (its forward) by `run_m` across the ground and `rise_m` up, `width_m` wide. Its collision (a blocking box or ramp,
## the zone's own) stays as it is: HeroStairs walks the player up the profile below, and followers and NPCs read it
## through HeroStairs.height_at.
##
## The profile steps tread by tread: each step's height rises over the first riser_share of its run, eased, then holds
## flat, so a body on it climbs step by step, continuously (no ramp, no jump). Zones place this node, or give their
## layout a "stairs" row: {"id", "foot": [x, y, z], "head": [x, y, z], "width_m", "step_rise_m"?} (from_row).

const GROUP := &"hero_stair_flight"

@export var run_m := 2.0
@export var rise_m := 1.8
@export var width_m := 1.6
## The riser height; 0 takes stairs.json step_rise_m.
@export var step_rise_m := 0.0

var tuning: Dictionary = {}


func _init() -> void:
	tuning = HeroStairs.load_data()


func _enter_tree() -> void:
	add_to_group(GROUP)


## A flight from a zone layout row {"id", "foot": [x, y, z], "head": [x, y, z], "width_m", "step_rise_m"?}, in the
## coordinates of the node it will be added to. Null for a row without a foot and a head apart.
static func from_row(row: Dictionary) -> HeroStairFlight:
	var foot := _vec3(row.get("foot", []))
	var head := _vec3(row.get("head", []))
	var flat := Vector3(head.x - foot.x, 0.0, head.z - foot.z)
	if flat.length() < HeroStairs.EPS:
		return null
	var f := HeroStairFlight.new()
	f.name = str(row.get("id", "Flight"))
	f.run_m = flat.length()
	f.rise_m = head.y - foot.y
	f.width_m = float(row.get("width_m", f.width_m))
	f.step_rise_m = float(row.get("step_rise_m", 0.0))
	f.transform = Transform3D(Basis.looking_at(flat.normalized(), Vector3.UP), foot)
	return f


static func _vec3(v: Variant) -> Vector3:
	var a := v as Array
	return Vector3(float(a[0]), float(a[1]), float(a[2])) if a != null and a.size() >= 3 else Vector3.ZERO


## How many steps the flight has (at least one).
func steps() -> int:
	var rise := step_rise_m if step_rise_m > 0.0 else float(tuning.get("step_rise_m", 0.0))
	return maxi(1, roundi(absf(rise_m) / rise)) if rise > 0.0 else 1


## The flight's climb, degrees.
func angle_deg() -> float:
	return rad_to_deg(atan2(absf(rise_m), run_m))


## The flight's forward across the ground (world, unit).
func forward() -> Vector3:
	var z := -global_basis.z
	return Vector3(z.x, 0.0, z.z).normalized()


## The flight's right across the ground (world, unit).
func side() -> Vector3:
	return forward().cross(Vector3.UP).normalized()


## `point` (world) in the flight's terms: x = metres to the right of the centre line, y = metres along the flight's
## run from the foot (0 at the foot, run_m at the head).
func local_of(point: Vector3) -> Vector2:
	var d := point - global_position
	return Vector2(d.dot(side()), d.dot(forward()))


## The profile's height above the foot at `along` metres of run (clamped to the flight).
func height_at_run(along: float) -> float:
	var n := steps()
	var u := clampf(along / run_m, 0.0, 1.0) * n
	var k := minf(floorf(u), n - 1.0)
	var share := clampf(float(tuning.get("riser_share", 1.0)), HeroStairs.EPS, 1.0)
	var t := clampf((u - k) / share, 0.0, 1.0)
	return rise_m * (k + smoothstep(0.0, 1.0, t)) / n


## The world point at `along` metres of run and `across` metres right of the centre line, on the profile.
func point_at(along: float, across: float) -> Vector3:
	var a := clampf(along, 0.0, run_m)
	return global_position + forward() * a + side() * across + Vector3.UP * height_at_run(a)


## True when `point` (world) is on the flight: over it (`beyond` metres past either end counting), within its width,
## and within height_tolerance_m of its profile (a body walking under a flying stair is not on it).
func covers(point: Vector3, beyond: float = 0.0) -> bool:
	var l := local_of(point)
	if absf(l.x) > width_m * 0.5 or l.y < -beyond or l.y > run_m + beyond:
		return false
	return absf(point.y - point_at(l.y, l.x).y) <= float(tuning.get("height_tolerance_m", INF))
