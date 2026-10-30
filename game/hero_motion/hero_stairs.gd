class_name HeroStairs
extends Node
## Steep-stair traversal for the field (M3-ARC-1216, ADR 0193; tuning: game/data/hero_motion/stairs.json). The field
## controller walks floors up to 45° and has no step-up, so a flight steeper than that (HeroStairFlight) is walked on
## its marked profile instead of its collision: added to the FieldController by HeroFieldActor.attach, this node runs
## after the controller's own step each physics frame. When the player is over a flight (or within enter_m of an end,
## heading in), it takes the controller's walking intent (FieldMotor's velocity, before any collision) along the
## flight, slows it to slope_speed_mps along the slope (slope_run_speed_mps while running: a stair run), keeps the
## player side_margin_m inside the edges, and puts
## the controller on the profile: step by step, eased, with no gravity and no sliding (still is still). Past either end
## by enter_m, the player is let go onto the landing and the controller walks on as before.
## Followers and NPCs read the same profile through height_at(). The zone's flights come from HeroStairFlight nodes
## anywhere in the tree, and from its layout's "stairs" rows (GreyboxZone.layout), which this node builds.

const NAME := &"HeroStairs"
const DATA_PATH := "res://game/data/hero_motion/stairs.json"
const LAYOUT_KEY := "stairs"
## Below this a length counts as zero.
const EPS := 1e-4
## The motor's intent counts as a run above walk speed by this (m/s).
const RUN_EPS := 0.05

## stairs.json, read once.
static var _data: Dictionary = {}

var controller: FieldController
var tuning: Dictionary = {}
## The flight the player is on, or null.
var flight: HeroStairFlight
## Where on it: metres of run from the foot, and metres right of the centre line.
var along := 0.0
var across := 0.0


func _ready() -> void:
	name = NAME
	tuning = load_data()
	build_from_layout()


func _physics_process(delta: float) -> void:
	advance(delta)


## stairs.json (read once, then shared: it is asked for every frame by every follower near a flight).
static func load_data() -> Dictionary:
	if not _data.is_empty():
		return _data
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f == null:
		push_error("HeroStairs: cannot read %s" % DATA_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	_data = parsed if parsed is Dictionary else {}
	return _data


## Builds a HeroStairFlight for each "stairs" row of the zone's layout (the controller's parent's `layout`), once.
## Returns how many it built.
func build_from_layout() -> int:
	var zone := controller.get_parent() if controller != null else null
	if zone == null or not "layout" in zone:
		return 0
	var built := 0
	for row: Variant in (zone.get(&"layout") as Dictionary).get(LAYOUT_KEY, []):
		var f := HeroStairFlight.from_row(row as Dictionary)
		if f != null and zone.get_node_or_null(NodePath(String(f.name))) == null:
			# The controller is readied inside the zone's own setup, when the zone can't take children yet.
			if zone.is_node_ready():
				zone.add_child(f)
			else:
				zone.add_child.call_deferred(f)
			built += 1
	return built


## Every flight in `tree`.
static func flights(tree: SceneTree) -> Array[HeroStairFlight]:
	var out: Array[HeroStairFlight] = []
	if tree != null:
		for n in tree.get_nodes_in_group(HeroStairFlight.GROUP):
			if n is HeroStairFlight and (n as Node).is_inside_tree():
				out.append(n as HeroStairFlight)
	return out


## The flight over `point` (world), counting `beyond` metres past its ends, or null.
static func flight_at(tree: SceneTree, point: Vector3, beyond: float = 0.0) -> HeroStairFlight:
	for f in flights(tree):
		if f.covers(point, beyond):
			return f
	return null


## The stair profile's height (world y) at `point` when a flight covers it, else NAN: followers, NPCs and scripted
## walks stand on the steps with it instead of a floor ray (which would find the flight's blocking collision).
static func height_at(context: Node, point: Vector3) -> float:
	if context == null or not context.is_inside_tree():
		return NAN
	var f := flight_at(context.get_tree(), point)
	if f == null:
		return NAN
	var l := f.local_of(point)
	return f.point_at(l.y, l.x).y


## True when `point` (world) is on a flight or within enter_m of one of its ends: there the flight's own blocking
## collision is not a wall (a follower or an NPC is about to climb it).
static func near_flight(context: Node, point: Vector3) -> bool:
	if context == null or not context.is_inside_tree():
		return false
	return flight_at(context.get_tree(), point, float(load_data().get("enter_m", 0.0))) != null


## The fastest a body may move across the ground at `point` (world): a flight's running slope speed times its
## slope's cosine when one covers it (a ceiling: followers and NPCs climb at the player's pace, run or walk), else INF.
static func speed_cap_at(context: Node, point: Vector3) -> float:
	if context == null or not context.is_inside_tree():
		return INF
	var f := flight_at(context.get_tree(), point)
	return INF if f == null else horizontal_cap(f, true)


## A flight's slope speed across the ground (m/s): slope_run_speed_mps when `running` (the walk's otherwise).
static func horizontal_cap(f: HeroStairFlight, running: bool = false) -> float:
	var slope := Vector2(f.run_m, f.rise_m).length()
	var along := float(f.tuning.get("slope_speed_mps", 0.0))
	if running:
		along = float(f.tuning.get("slope_run_speed_mps", along))
	return along * (f.run_m / slope if slope > EPS else 1.0)


## One physics frame, after the controller's own step. Returns true while the player is on a flight.
func advance(delta: float) -> bool:
	if controller == null or not is_instance_valid(controller) or controller.motor == null or delta <= 0.0:
		return false
	var enter := float(tuning.get("enter_m", 0.0))
	var intent := controller.motor.velocity
	if flight == null and not _enter(enter, intent):
		return false
	var fwd := flight.forward()
	var running := Vector2(intent.x, intent.z).length() > controller.motor.walk_speed + RUN_EPS
	var cap := horizontal_cap(flight, running)
	var v := Vector2(intent.dot(fwd), intent.dot(flight.side()))
	if v.length() > cap:
		v = v.normalized() * cap
	along += v.x * delta
	var half := maxf(flight.width_m * 0.5 - float(tuning.get("side_margin_m", 0.0)), 0.0)
	across = clampf(across + v.y * delta, -half, half)
	var on := clampf(along, 0.0, flight.run_m)
	controller.global_position = flight.point_at(on, across) + fwd * (along - on)  # flat past an end
	controller.velocity = fwd * v.x + flight.side() * v.y  # horizontal only: no gravity on the steps
	if along < -enter or along > flight.run_m + enter:
		flight = null  # onto the landing; the controller walks on
	return flight != null


## Takes the player onto the flight under it when it is over one, or within `enter` of an end heading in.
func _enter(enter: float, intent: Vector3) -> bool:
	var f := flight_at(controller.get_tree(), controller.global_position, enter)
	if f == null:
		return false
	var l := f.local_of(controller.global_position)
	var heading := intent.dot(f.forward())
	if (l.y < 0.0 and heading <= 0.0) or (l.y > f.run_m and heading >= 0.0):
		return false  # beside an end and not walking in
	flight = f
	along = l.y
	across = l.x
	return true
