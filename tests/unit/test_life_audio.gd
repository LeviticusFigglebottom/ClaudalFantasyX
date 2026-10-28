extends TestCase
## M3-AUD-814: LifeAudio, villagers' talk and work and the wildlife, by listening (game/data/audio/life.json).
## Stand-ins built here, never the real classes (no class_name stubs: creatures' FieldNpc and WildlifeLayer would
## collide on merge); each carries the `audio_class` meta of the hook it stands in for. Sounds are recorded through
## the listener's player Callable, so nothing plays.

const DT := 1.0 / 60.0


class NpcStandIn:
	extends Node3D
	var npc_id: StringName = &""
	var chat := false
	var work := false
	var point := Vector3.ZERO
	var _chat_speaker: StringName = &""

	func chatting() -> bool:
		return chat

	func working() -> bool:
		return work

	func work_point() -> Vector3:
		return point


class SpeakingNpc:
	extends NpcStandIn
	var speak := false

	func chat_speaking() -> bool:
		return speak


class Bird:
	extends RefCounted
	var state := 0
	var pos := Vector3.ZERO


class Flock:
	extends RefCounted
	var gulls: Array = []


class Crab:
	extends RefCounted
	var state := 0
	var pos := Vector2.ZERO
	var y := 0.0


class Beach:
	extends RefCounted
	var crabs: Array = []


class Shoal:
	extends RefCounted
	var lead := Vector3.ZERO
	var _startle := 0.0


class LayerStandIn:
	extends Node3D
	var flocks: Array = []
	var beaches: Array = []
	var shoals: Array = []


var played: Array = []
var nodes: Array[Node] = []


func before_each() -> void:
	played = []
	nodes = []


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _data() -> Dictionary:
	return (AudioData.table(AudioData.LIFE) as Dictionary).duplicate(true)


func _life(table: Dictionary = {}, ear_at: Variant = null) -> LifeAudio:
	var l := LifeAudio.new(table if not table.is_empty() else _data())
	l.player_at = func(id: StringName, at: Vector3) -> void: played.append([id, at])
	l.ear = func() -> Variant: return ear_at
	_add(l)
	return l


func _add(n: Node) -> Node:
	_host().add_child(n)
	nodes.append(n)
	return n


func _done() -> void:
	for n in nodes:
		if is_instance_valid(n):
			n.free()
	nodes = []


func _npc(id: StringName, cls: Script = NpcStandIn) -> NpcStandIn:
	var n := cls.new() as NpcStandIn
	n.npc_id = id
	n.set_meta(LifeAudio.META_CLASS, "FieldNpc")
	_add(n)
	return n


func _ids() -> Array:
	return played.map(func(p: Array) -> String: return String(p[0]))


func _run(l: LifeAudio, sec: float) -> void:
	for i in int(sec / DT):
		l.advance(DT)


func test_hooks_wait_for_creatures_and_every_row_exists() -> void:
	var d := _data()
	var classes: Array = (d.get("hooks", []) as Array).map(func(h: Dictionary) -> String: return str(h["class"]))
	assert_eq(classes, ["FieldNpc", "WildlifeLayer"])
	var rows := AudioData.sfx_rows()
	for id: String in [
		"villager_murmur_low",
		"villager_murmur_high",
		"work_net",
		"work_sweep",
		"work_wares",
		"work_bowl",
		"gull_call_near",
		"gull_takeoff",
		"crab_scuttle",
		"fish_dart"
	]:
		assert_true(rows.has(id), "%s is an sfx row" % id)
		for f: String in (rows.get(id, {}) as Dictionary).get("files", []):
			assert_true(ResourceLoader.exists(f), "%s exists" % f)


func test_the_director_hands_life_its_nodes() -> void:
	var l := _life()
	var npc := _npc(&"netmender")
	var other := Node3D.new()
	_add(other)
	assert_true(l.wants(npc), "a FieldNpc stand-in is watched")
	assert_false(l.wants(other), "a plain node is not")
	l.watch(npc)
	l.watch(npc)
	assert_eq(l.watched.size(), 1, "once")
	_done()


func test_a_chat_turn_murmurs_once_at_its_start_in_the_villagers_voice() -> void:
	var l := _life()
	var a := _npc(&"child")
	var b := _npc(&"fisher")
	b.position = Vector3(2.0, 0.0, 0.0)
	l.watch(a)
	l.watch(b)
	a.chat = true
	b.chat = true
	a._chat_speaker = &"child"
	b._chat_speaker = &"child"
	_run(l, 2.0)
	assert_eq(_ids(), ["villager_murmur_high"], "the child's turn, once, in a high voice")
	assert_between((played[0][1] as Vector3).y, 1.4, 1.6, "at the head")
	a._chat_speaker = &"fisher"
	b._chat_speaker = &"fisher"
	_run(l, 1.0)
	assert_eq(_ids(), ["villager_murmur_high", "villager_murmur_low"], "the fisher answers, low")
	assert_between((played[1][1] as Vector3).x, 1.9, 2.1, "from the fisher")
	a._chat_speaker = &""
	b._chat_speaker = &""
	_run(l, 1.0)
	a._chat_speaker = &"fisher"
	b._chat_speaker = &"fisher"
	b.chat = false
	_run(l, 1.0)
	assert_eq(played.size(), 2, "no murmur once the chat is over")
	_done()


func test_a_public_speaking_read_wins_over_the_field() -> void:
	var l := _life()
	var n := _npc(&"vendor", SpeakingNpc) as SpeakingNpc
	l.watch(n)
	n.chat = true
	n._chat_speaker = &"vendor"
	_run(l, 0.5)
	assert_eq(played.size(), 0, "chat_speaking() says no")
	n.speak = true
	_run(l, 0.5)
	assert_eq(_ids(), ["villager_murmur_high"], "chat_speaking() says yes")
	_done()


func test_work_sounds_at_the_work_point_while_working() -> void:
	var l := _life()
	var n := _npc(&"netmender")
	n.point = Vector3(0.3, 0.75, -0.45)
	l.watch(n)
	_run(l, 12.0)
	assert_eq(played.size(), 0, "not working yet")
	n.work = true
	_run(l, 30.0)
	var nets := _ids().filter(func(id: String) -> bool: return id == "work_net")
	assert_between(nets.size(), 5, 13, "every 2.5-5.5 s over 30 s (%d)" % nets.size())
	assert_eq(played.size(), nets.size(), "only its own work row")
	assert_true((played[0][1] as Vector3).is_equal_approx(n.point), "at the work point")
	n.work = false
	var before := played.size()
	_run(l, 12.0)
	assert_eq(played.size(), before, "stops with the work")
	var idle := _npc(&"fisher")
	idle.work = true
	l.watch(idle)
	_run(l, 12.0)
	assert_eq(played.size(), before, "a villager with no work row is silent")
	_done()


func test_far_villagers_are_not_heard() -> void:
	var l := _life({}, Vector3(100.0, 0.0, 0.0))
	var n := _npc(&"reed")
	l.watch(n)
	n.work = true
	n.chat = true
	n._chat_speaker = &"reed"
	_run(l, 20.0)
	assert_eq(played.size(), 0, "past hear_m")
	_done()


func _layer() -> LayerStandIn:
	var layer := LayerStandIn.new()
	layer.position = Vector3(10.0, 0.0, 0.0)
	layer.set_meta(LifeAudio.META_CLASS, "WildlifeLayer")
	_add(layer)
	return layer


func test_gulls_call_and_clap_off() -> void:
	var l := _life()
	var layer := _layer()
	var flock := Flock.new()
	for i in 3:
		var b := Bird.new()
		b.pos = Vector3(i, 8.0, 0.0)
		flock.gulls.append(b)
	layer.flocks = [flock]
	l.watch(layer)
	_run(l, 60.0)
	var calls := _ids().filter(func(id: String) -> bool: return id == "gull_call_near")
	assert_between(calls.size(), 4, 13, "a flock calls every 5-13 s (%d in 60 s)" % calls.size())
	assert_between((played[0][1] as Vector3).y, 7.9, 8.1, "from a gull, in the air")
	assert_true((played[0][1] as Vector3).x >= 10.0, "in the layer's space")
	played.clear()
	(flock.gulls[1] as Bird).state = 3
	l.advance(DT)
	l.advance(DT)
	assert_eq(_ids().filter(func(id: String) -> bool: return id == "gull_takeoff").size(), 1, "one takeoff")
	_done()


func test_a_fleeing_crab_scuttles_with_a_cooldown_per_beach() -> void:
	var l := _life()
	var layer := _layer()
	var beach := Beach.new()
	for i in 3:
		var c := Crab.new()
		c.pos = Vector2(i, 1.0)
		beach.crabs.append(c)
	layer.beaches = [beach]
	l.watch(layer)
	l.advance(DT)
	for c: Crab in beach.crabs:
		c.state = 2
	l.advance(DT)
	assert_eq(_ids(), ["crab_scuttle"], "three crabs bolt at once: one scuttle")
	assert_true((played[0][1] as Vector3).is_equal_approx(Vector3(10.0, 0.0, 1.0)), "at the crab")
	_run(l, 1.0)
	(beach.crabs[0] as Crab).state = 3
	l.advance(DT)
	(beach.crabs[0] as Crab).state = 2
	l.advance(DT)
	assert_eq(played.size(), 2, "after the cooldown a new bolt scuttles again")
	_done()


func test_a_startled_shoal_darts_once() -> void:
	var l := _life()
	var layer := _layer()
	var shoal := Shoal.new()
	shoal.lead = Vector3(1.0, -0.3, 2.0)
	layer.shoals = [shoal]
	l.watch(layer)
	l.advance(DT)
	shoal._startle = 0.8
	_run(l, 0.5)
	assert_eq(_ids(), ["fish_dart"], "one dart per startle")
	shoal._startle = 0.0
	l.advance(DT)
	shoal._startle = 0.8
	l.advance(DT)
	assert_eq(played.size(), 2, "a new startle darts again")
	_done()


func test_a_villager_walking_its_route_steps_quietly_without_hero_gear() -> void:
	var l := _life()
	var steps: Array = []
	l.footstep_data = (AudioData.table(AudioData.FOOTSTEPS) as Dictionary).duplicate(true)
	l.step_player = func(id: StringName, _at: Vector3, opts: Dictionary) -> void: steps.append([id, opts])
	var n := _npc(&"fisher")
	l.watch(n)
	for i in int(5.0 / 0.66 / DT):  # 5 m at a villager's 0.66 m/s
		n.position.z += 0.66 * DT
		l.advance(DT)
	var ids: Array = steps.map(func(s: Array) -> String: return String(s[0]))
	var feet := ids.filter(func(id: String) -> bool: return id.begins_with("hero_step_"))
	assert_between(feet.size(), 8, 13, "5 m at a 0.45 m stride (%d)" % feet.size())
	assert_true(ids.any(func(id: String) -> bool: return id.begins_with("hero_cloth_")), "cloth moves with them")
	assert_false(ids.any(func(id: String) -> bool: return id.begins_with("hero_gear_")), "no hero's lantern or shells")
	var walk_db := float((steps[ids.find(feet[0])][1] as Dictionary).get("volume_db", 0.0))
	assert_eq(walk_db, -9.0, "quieter than the heroes")
	_done()


func test_a_freed_zone_is_dropped_without_a_cast_error() -> void:
	# big12's capture shards: a zone freed at shutdown left LifeAudio casting freed villagers ("Trying to cast a freed
	# object" at advance). The cast aborted advance, so the dead entries stayed; now they are dropped first.
	var l := _life()
	var npc := _npc(&"netmender")
	var layer := _layer()
	l.watch(npc)
	l.watch(layer)
	assert_eq(l.watched.size(), 2)
	npc.free()
	layer.free()
	l.advance(DT)
	assert_eq(l.watched.size(), 0, "freed nodes are dropped, not cast")
	_done()


func test_a_real_villager_zone_loads_and_frees_cleanly() -> void:
	var zone := (load("res://game/levels/ch02/haluna/haluna.tscn") as PackedScene).instantiate() as Node3D
	_add(zone)
	var l := _life()
	for n in zone.find_children("*", "", true, false):
		if l.wants(n):
			l.watch(n)
	assert_true(l.watched.size() > 0, "Haluna's villagers or wildlife are watched (%d)" % l.watched.size())
	_run(l, 0.5)
	zone.free()
	l.advance(DT)
	assert_eq(l.watched.size(), 0, "the freed zone's villagers and wildlife are all dropped")
	l.get_parent().remove_child(l)
	assert_eq(l.watched.size(), 0, "and leaving the tree keeps nothing")
	_done()


func test_a_villager_never_murmurs_over_a_line() -> void:
	var l := _life()
	var hushed := [true]
	l.quiet = func() -> bool: return hushed[0]
	var a := _npc(&"child")
	l.watch(a)
	a.chat = true
	a._chat_speaker = &"child"
	_run(l, 1.0)
	assert_eq(played.size(), 0, "a dialogue box is open: the chat is held")
	a._chat_speaker = &""
	_run(l, 0.2)
	hushed[0] = false
	a._chat_speaker = &"child"
	_run(l, 0.5)
	assert_eq(_ids(), ["villager_murmur_high"], "the line is gone: the next turn murmurs")
	_done()


func test_the_dialogue_duck_takes_the_world_bus_down() -> void:
	var mix := AudioData.table(AudioData.MIX) as Dictionary
	var buses := ((mix["ducks"] as Dictionary)["dialogue"] as Dictionary)["buses"] as Dictionary
	assert_true(float(buses.get("World", 0.0)) < 0.0, "footsteps, villagers' work, wildlife and foley sit under a line")
	assert_true(float(buses.get("World", 0.0)) >= -6.0, "but stay present (a gentle dip)")
