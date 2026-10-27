extends TestCase
## M3-AUD-816: ImpactAudio on battle-presentation's BattleImpact (M3-BPR-401), by listening
## (game/data/audio/impact_audio.json). A stand-in node with the same two signals (never the real class: no
## class_name stubs), carrying the hook's `audio_class` meta, under a stand-in choreography with a `speed`.
## Sounds and ducks are recorded through the listener's Callables, so nothing plays.

const DT := 1.0 / 60.0


class ImpactStandIn:
	extends Node
	signal landed(target_id: StringName, strength: float, stop_sec: float)
	signal slowmo_planned(from_sec: float, sec: float, factor: float)


class ChoreoStandIn:
	extends Node
	var speed := 1.0


var played: Array[StringName] = []
var ducks: Array = []
var low_audio := false
var nodes: Array[Node] = []


func before_each() -> void:
	played = []
	ducks = []
	low_audio = false
	nodes = []


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _audio() -> ImpactAudio:
	var a := ImpactAudio.new((AudioData.table(AudioData.IMPACT) as Dictionary).duplicate(true))
	a.player = func(id: StringName) -> void: played.append(id)
	a.ducker = func(reason: StringName, on: bool) -> void: ducks.append([reason, on])
	a.reduced = func() -> bool: return low_audio
	_host().add_child(a)
	nodes.append(a)
	return a


func _impact(speed: float = 1.0) -> ImpactStandIn:
	var choreo := ChoreoStandIn.new()
	choreo.speed = speed
	var n := ImpactStandIn.new()
	n.set_meta(ImpactAudio.META_CLASS, "BattleImpact")
	choreo.add_child(n)
	_host().add_child(choreo)
	nodes.append(choreo)
	return n


func _done() -> void:
	for n in nodes:
		if is_instance_valid(n):
			n.free()
	nodes = []


func _run(a: ImpactAudio, sec: float) -> void:
	for i in int(round(sec / DT)):
		a.advance(DT)


func test_every_row_exists_and_the_hook_waits_for_battle_presentation() -> void:
	var d := AudioData.table(AudioData.IMPACT)
	var hook := (d.get("hooks", []) as Array)[0] as Dictionary
	assert_eq(str(hook.get("class", "")), "BattleImpact")
	var rows := AudioData.sfx_rows()
	for id: String in ["impact_medium", "impact_heavy", "impact_crushing", "ko_slowmo"]:
		assert_true(rows.has(id), "%s is an sfx row" % id)
		assert_eq(str((rows.get(id, {}) as Dictionary).get("bus", "")), "Combat", "%s on Combat" % id)
		for f: String in (rows.get(id, {}) as Dictionary).get("files", []):
			assert_true(ResourceLoader.exists(f), "%s exists" % f)
	var mix_ducks := AudioData.table(AudioData.MIX).get("ducks", {}) as Dictionary
	assert_true(mix_ducks.has("impact") and mix_ducks.has("ko_slowmo"), "both ducks are mix.json's")


func test_blows_layer_by_weight() -> void:
	var a := _audio()
	var n := _impact()
	assert_true(a.wants(n), "the stand-in is hooked")
	a.watch(n)
	a.watch(n)
	n.landed.emit(&"reef_crab", 0.1, 0.0)
	n.landed.emit(&"reef_crab", 0.3, 0.0)
	n.landed.emit(&"reef_crab", 0.7, 0.0)
	n.landed.emit(&"reef_crab", 1.0, 0.0)
	assert_eq(played, [&"impact_medium", &"impact_heavy", &"impact_crushing"], "light adds nothing; once each")
	assert_eq(ducks, [], "no hit-stop, no duck")
	_done()


func test_a_hit_stop_ducks_the_music_for_its_length() -> void:
	var a := _audio()
	var n := _impact()
	a.watch(n)
	n.landed.emit(&"hullgnaw", 0.8, 0.06)
	assert_eq(ducks, [[&"impact", true]], "the music drops under the frozen frame")
	_run(a, 0.1)
	assert_eq(ducks.size(), 1, "still held (0.06 s + hold)")
	_run(a, 0.2)
	assert_eq(ducks, [[&"impact", true], [&"impact", false]], "and comes back")
	_done()


func test_the_ko_slowmo_swells_at_its_start_and_holds_the_duck_for_the_slowed_time() -> void:
	var a := _audio()
	var n := _impact(2.0)
	a.watch(n)
	n.slowmo_planned.emit(1.0, 0.6, 0.4)  # plan time 1.0 at speed 2: 0.5 s real; 0.6 s at 0.4 lasts 1.5 s
	_run(a, 0.45)
	assert_eq(played, [], "not yet")
	_run(a, 0.1)
	assert_eq(played, [&"ko_slowmo"], "at the slow-mo's start")
	assert_eq(ducks, [[&"ko_slowmo", true]])
	_run(a, 1.6)
	assert_eq(ducks.size(), 1, "held through the slowed time and the hold")
	_run(a, 0.3)
	assert_eq(ducks, [[&"ko_slowmo", true], [&"ko_slowmo", false]])
	_done()


func test_reduced_audio_keeps_only_the_heavy_tier_and_the_swell() -> void:
	low_audio = true
	var a := _audio()
	var n := _impact()
	a.watch(n)
	n.landed.emit(&"a", 0.3, 0.0)
	n.landed.emit(&"a", 0.6, 0.0)
	n.landed.emit(&"a", 0.95, 0.0)
	n.slowmo_planned.emit(0.0, 0.5, 0.5)
	a.advance(DT)
	assert_eq(played, [&"impact_heavy", &"ko_slowmo"])
	_done()


func test_a_node_without_the_signals_is_ignored() -> void:
	var a := _audio()
	var n := Node.new()
	n.set_meta(ImpactAudio.META_CLASS, "BattleImpact")
	_host().add_child(n)
	nodes.append(n)
	a.watch(n)
	assert_eq(played, [], "nothing to connect, nothing plays")
	_done()
