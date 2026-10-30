class_name EncounterGapProbe
extends Node
## Human playtest check (d), 2026-10-30 (cloud QA pass 6): the breather between field encounters on each Act I
## zone's main route, as played.
##   godot --headless --path . --audio-driver Dummy res://tools/gpu_bench/encounter_gap_probe.tscn -- [--zones=...]
## Per zone: the F8 chapter start, the location, the flags that switch its random encounters on; then the zone's own
## live FieldEncounters meter (its table, gap, grace, rate and seeded rng, as the zone set it up) is read, and the
## first ENCOUNTERS gaps are drawn with its own _draw() (its rng restored after), plus its grace (metres and, from
## big23, seconds). The hero is pushed with the field controller's stick toward the route's next spawn for PUSH_S to
## check the run speed he reaches there, and the route's straight-line length through its spawns (a lower bound on
## the walk) is summed. Prints ENCOUNTER_GAP <zone> {json}: metres and seconds at RUN_MPS between encounters (the
## first owes only the grace left at entry).

const CHAPTER_SELECT := "res://game/data/debug/chapter_select.json"
const ENCOUNTERS := 8
## field_movement.json's run_speed_mps: the seconds are at this speed (the measured push is printed beside it).
const RUN_MPS := 3.6
const PUSH_S := 3.0
const SPEED_SKIP_S := 1.0
## [zone, chapter, location, flags, route spawns in walking order]
const ZONES := [
	[
		"underway",
		"ch01",
		"ch01/oruvel_underway",
		[],
		["Drop", "BellRoom1", "Gallery", "GalleryAfter", "GaugeRoom", "ShaftFoot"]
	],
	["causeway", "ch03", "ch03/saltgrass_causeway", ["ch03_harrier_won"], ["AfterHarrier", "ShrineSteps"]],
	[
		"ferry_derelict",
		"ch04",
		"ch04/brightwater_ferry",
		["ch04_boarded_derelict"],
		["DerelictDeck", "AfterLeeches", "AfterHermit"]
	],
	["ashcrown_stair", "ch05", "ch05/ashcrown", ["ch05_tortoises_won"], ["AfterTortoises", "AnvilCourt", "Crown"]],
	["brine_shoals", "ch06", "ch06/brine_shoals", ["ch06_arrived"], ["Entry", "LastRidge", "CampWaterline", "Channel"]],
	["coilspire_path", "ch08", "ch08/coilspire", [], ["PathFoot", "PathMid", "SpireBase"]],
]

var _opts: Dictionary = {}


func _ready() -> void:
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := EncounterGapProbe.new()
		driver.name = "EncounterGapProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_opts[kv[0]] = kv[1] if kv.size() > 1 else "true"
	var saves := get_tree().root.get_node_or_null(^"SaveSystem")
	if saves != null and saves.has_method(&"hold_autosave"):
		saves.call(&"hold_autosave", self)
	var wanted := str(_opts.get("zones", "")).split(",", false)
	for z: Array in ZONES:
		if wanted.is_empty() or wanted.has(str(z[0])):
			await _zone(z)
	get_tree().quit()


func _zone(z: Array) -> void:
	var router := get_tree().root.get_node(^"SceneRouter")
	for start: Dictionary in DebugReadouts.chapter_starts(CHAPTER_SELECT):
		if str(start["id"]) == str(z[1]):
			DebugReadouts.apply_chapter_start(start)
	for f: String in z[3]:
		Game.set_flag(StringName(f))
	FieldEncounters.reset()
	var route: Array = z[4]
	FlowRouting.go_to(StringName(str(z[2])), StringName(str(route[0])))
	var t := Time.get_ticks_msec()
	while (_player() == null or bool(router.call(&"is_busy"))) and Time.get_ticks_msec() - t < 60000:
		await get_tree().process_frame
	await get_tree().create_timer(1.0).timeout
	var zone := get_tree().current_scene
	var meters := zone.find_children("*", "FieldEncounters", true, false)
	if meters.is_empty():
		print('ENCOUNTER_GAP %s {"error": "no FieldEncounters in %s"}' % [z[0], zone.scene_file_path])
		return
	var fe := meters[0] as FieldEncounters
	var mult := float(zone.call(&"encounter_rate_mult")) if zone.has_method(&"encounter_rate_mult") else 1.0
	# The draws walked() would make: the gap in progress, then grace + a fresh draw after each encounter.
	# The gaps the zone's own _draw() makes from its rng (restored after), so a change to the draw is measured too.
	var saved_state := fe.rng.state
	var draws: Array[float] = [maxf(fe.next_m - fe.walked_m, 0.0)]
	for i in ENCOUNTERS - 1:
		draws.append(float(fe.call(&"_draw")))
	fe.rng.state = saved_state
	# The grace (big23 adds grace_s, seconds of field time, beside grace_m walked): the first gap owes what is left
	# now, every later one the full grace.
	var grace_s_after := float(fe.get(&"grace_after_s")) if fe.get(&"grace_after_s") != null else 0.0
	var grace_s_now := float(fe.get(&"grace_s")) if fe.get(&"grace_s") != null else 0.0
	# Every metre walked counts `mult` metres (Ch1's lantern), so the walked distance is gap / mult.
	var m := maxf(mult, 0.001)
	var walked: Array[float] = []
	var secs: Array = []
	for i in draws.size():
		var grace_m := (fe.grace_m if i == 0 else fe.grace_after_m) / m
		var grace_t := grace_s_now if i == 0 else grace_s_after
		var gap := draws[i] / m
		walked.append(snappedf(maxf(grace_m, grace_t * RUN_MPS) + gap, 0.1))
		secs.append(snappedf(maxf(grace_m / RUN_MPS, grace_t) + gap / RUN_MPS, 0.1))
	var spawns: Dictionary = {}
	for s in route:
		var n := zone.get_node_or_null(NodePath("Spawns/" + str(s))) as Node3D
		if n == null:
			n = zone.find_child(str(s), true, false) as Node3D
		if n != null:
			spawns[str(s)] = n.global_position
	var toward := Vector3.ZERO
	if spawns.has(str(route[0])) and spawns.has(str(route[1])):
		toward = (spawns[str(route[1])] as Vector3) - (spawns[str(route[0])] as Vector3)
	var speed := await _run_speed(toward)
	var length := 0.0
	for i in route.size() - 1:
		if spawns.has(str(route[i])) and spawns.has(str(route[i + 1])):
			var a: Vector3 = spawns[str(route[i])]
			var b: Vector3 = spawns[str(route[i + 1])]
			length += Vector2(a.x - b.x, a.z - b.z).length()
	var out := {
		"location": str(z[2]),
		"holds": ZoneStory.holds(fe.when),
		"table": fe.table.map(func(r: Dictionary) -> String: return str(r.get("encounter", ""))),
		"min_m": fe.min_m,
		"max_m": fe.max_m,
		"grace_m": fe.grace_after_m,
		"grace_s": grace_s_after,
		"rate_pct": fe.rate_pct,
		"rate_mult": mult,
		"run_mps": snappedf(speed, 0.01),
		"walked_m": walked,
		"secs": secs,
		"route_m_min": snappedf(length, 0.1),
		"route_encounters_est": _count_within(walked, length),
	}
	print("ENCOUNTER_GAP %s %s" % [z[0], JSON.stringify(out)])


## How many encounters fit in `length` metres of walking.
static func _count_within(walked: Array[float], length: float) -> int:
	var total := 0.0
	var n := 0
	for m in walked:
		total += m
		if total > length:
			break
		n += 1
	return n


## The hero's ground speed (m/s) holding the stick toward `toward` (world XZ; zero = camera forward) for PUSH_S (the
## first SPEED_SKIP_S of acceleration left out).
func _run_speed(toward: Vector3) -> float:
	var p := _player()
	if p == null:
		return 0.0
	var fe_nodes := get_tree().current_scene.find_children("*", "FieldEncounters", true, false)
	for n in fe_nodes:
		n.set_physics_process(false)  # the push is a measurement, not a walk
	p.motor.latch_on_cut = false
	p.motor.latch_on_blend = false
	toward.y = 0.0
	var t := 0.0
	var from := Vector3.INF
	var dist := 0.0
	var prev := p.global_position
	while t < PUSH_S:
		var stick := Vector2(0, -1)
		if toward.length_squared() > 0.0 and p.director != null:
			var local := Basis(Vector3.UP, -p.director.camera_yaw()) * toward.normalized()
			stick = Vector2(local.x, local.z).normalized()
		p.input_override = stick
		await get_tree().physics_frame
		t += get_physics_process_delta_time()
		var now := p.global_position
		if t > SPEED_SKIP_S:
			dist += Vector2(now.x - prev.x, now.z - prev.z).length()
		prev = now
	p.input_override = Vector2(NAN, NAN)
	return dist / (PUSH_S - SPEED_SKIP_S)


func _player() -> FieldController:
	var cur := get_tree().current_scene
	if cur == null:
		return null
	if cur.get(&"player") is FieldController:
		return cur.get(&"player") as FieldController
	var found := cur.find_children("*", "FieldController", true, false)
	return found[0] as FieldController if not found.is_empty() else null
