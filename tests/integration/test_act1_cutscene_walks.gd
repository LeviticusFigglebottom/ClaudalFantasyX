extends TestCase
## Queue item 6, the cutscene quality bar (ADR 0200): the sequencer's `@mark` walks an actor to a mark in a straight
## line with its height lerped (no ground following), so on a kit's heights a walk could cut through a rail or a wall
## or float over a drop. This plays the Act I chapter threads (test_ch04..09_thread, every beat with the real zone
## states) and records each `@mark` walk from where the actor really stands, then checks the straight line against
## the zone's collision with KitWalkProbe's maths: on a floor all the way (within FLOOR_TOL_M of the lerped height)
## and clear of every box (each leg of a `via=` path). Walks of hidden actors, and walks under a full fade, are not
## seen and are left out.
## Known walks still to fix are listed in act1_cutscene_walks_known.json (M3-CIN-1220); the test fails on any other.

const THREADS: Array[String] = [
	"res://tests/integration/test_ch04_thread.gd",
	"res://tests/integration/test_ch05_thread.gd",
	"res://tests/integration/test_ch06_thread.gd",
	"res://tests/integration/test_ch07_thread.gd",
	"res://tests/integration/test_ch08_thread.gd",
	"res://tests/integration/test_ch09_thread.gd",
]
const KNOWN_PATH := "res://tests/integration/act1_cutscene_walks_known.json"
const STEP_M := 0.25
const FLOOR_TOL_M := 0.45
const UNSEEN_FADE := 0.99
const KIT_EVERY := 4
const TERRAIN: Array[String] = ["mountain_massif.glb", "coilspire_ground.glb"]

var problems: Dictionary = {}  # problem text -> true (a walk replayed by several threads counts once)
var walks := 0
var _probes: Dictionary = {}  # zone instance id -> KitWalkProbe with its boxes read


func test_every_act1_cutscene_walk_stays_on_the_floor() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	tree.node_added.connect(_on_node_added)
	for path in THREADS:
		var script := load(path) as GDScript
		for method in script.get_script_method_list():
			var mname := String(method["name"])
			if not mname.begins_with("test_"):
				continue
			var tc: TestCase = script.new()
			tc.begin_test("%s::%s" % [path.get_file(), mname])
			tc.before_each()
			tc.call(mname)
			_probes.clear()
	tree.node_added.disconnect(_on_node_added)
	assert_true(walks > 20, "the threads walk people about (%d walks)" % walks)
	var known: Array = GreyboxZone.read_json(KNOWN_PATH).get("known", [])
	var exempt: Dictionary = GreyboxZone.read_json(KNOWN_PATH).get("exempt", {})  # off the floor by design, with why
	var seen: Dictionary = {}
	var lines: Array = problems.keys()
	lines.sort()
	for line: String in lines:
		if OS.get_environment("HYMN_WALKS") != "":
			print("WALK: %s" % line)  # the whole list, for fixing them
		var key := line.get_slice(": ", 0) + ": " + line.get_slice(": ", 1)
		seen[key] = true
		if not known.has(key) and not exempt.has(key):
			fail("a cutscene walk leaves the floor or passes through a box: %s" % line)
	for key: String in known:
		assert_true(seen.has(key), "%s is clean now: take it off %s" % [key, KNOWN_PATH])


func _on_node_added(n: Node) -> void:
	if n is CutsceneSequencer and not (n as CutsceneSequencer).cue_played.is_connected(_on_cue):
		(n as CutsceneSequencer).cue_played.connect(_on_cue.bind(n))


func _on_cue(cue: StringName, args: Array, kwargs: Dictionary, seq: CutsceneSequencer) -> void:
	if cue != &"mark" or args.size() < 2 or seq._stage == null:
		return
	var stage: CutsceneStage = seq._stage
	var actor := stage.actor(StringName(str(args[0])))
	var mark := stage.mark(StringName(str(args[1])))
	var zone := _zone_of(stage)
	if actor == null or mark == null or zone == null or not actor.is_visible_in_tree() or actor is FieldController:
		return  # the player walks from wherever he set the scene off, which the threads don't stand him at
	if seq.overlay != null and seq.overlay.fade_alpha() >= UNSEEN_FADE:
		return
	walks += 1
	var path: Array[Vector3] = [actor.global_position]
	for via_id in str(kwargs.get("via", "")).split(",", false):
		var via := stage.mark(StringName(via_id.strip_edges()))
		if via != null:
			path.append(via.global_position)
	path.append(mark.global_position)
	var why := ""
	for i in range(1, path.size()):
		why = _check(_probe(zone), path[i - 1], path[i])
		if why != "":
			break
	if why != "":
		var ends := "from %s to %s" % [_short(path[0]), _short(path[path.size() - 1])]
		problems["%s %s: @mark %s %s: %s; %s" % [zone.location_id, seq._scene_id, args[0], args[1], why, ends]] = true


static func _short(v: Vector3) -> String:
	return "(%.1f, %.2f, %.1f)" % [v.x, v.y, v.z]


func _zone_of(n: Node) -> GreyboxZone:
	var p := n.get_parent()
	while p != null and not p is GreyboxZone:
		p = p.get_parent()
	return p as GreyboxZone


func _probe(zone: GreyboxZone) -> KitWalkProbe:
	var key := zone.get_instance_id()
	if not _probes.has(key):
		var probe := KitWalkProbe.new()
		probe.zone = zone
		probe.read_boxes()
		_probes[key] = probe
	return _probes[key]


## "" when the straight walk from `a` to `b` (its height lerped) keeps to a floor and clear of every box. The floor
## is the highest of the zone's boxes and ramps (KitWalkProbe) and a ray down through the physics space (the kit's
## trimesh floors: Coilspire's tiers, Pemakar's massif); a body is blocked by a box or a kit collider.
func _check(probe: KitWalkProbe, a: Vector3, b: Vector3) -> String:
	var root := probe.zone.global_transform.affine_inverse()
	a = root * a
	b = root * b
	var n := maxi(1, ceili(Vector2(b.x - a.x, b.z - a.z).length() / STEP_M))
	for k in n + 1:
		var p := a.lerp(b, float(k) / n)
		var f := maxf(probe.floor_y(p.x, p.z, p.y + FLOOR_TOL_M), probe.ray_floor_y(p, FLOOR_TOL_M))
		if f == -INF or p.y - f > FLOOR_TOL_M:
			return "off the floor at (%.1f, %.2f, %.1f), floor %.2f" % [p.x, p.y, p.z, f]
		var feet := Vector3(p.x, f, p.z)
		var hit := probe.blocked_by(feet)
		if hit == "" and k % KIT_EVERY == 0:
			hit = probe.inside_kit(feet, TERRAIN)
		if hit != "":
			return "through %s at (%.1f, %.2f, %.1f)" % [hit, p.x, f, p.z]
	return ""
