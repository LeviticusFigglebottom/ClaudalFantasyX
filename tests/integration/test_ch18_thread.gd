extends TestCase
## M5-A3P-1004: Ch18 "The Kite", the critical path, headless, on the real chapter data
## (game/data/flow/chapters/ch18.json): the maiden flight, the chart table (the world opens), Reedhollow's Act III block
## (Pell through the gate, the farewell-tide taught), back aboard at night and Iskarra at the chart table in the
## morning; and the Hollowmere revisit with its two heirlooms.

const KITE := "res://game/levels/ch18/kite/kite.tscn"
const REEDHOLLOW := "res://game/levels/ch10/reedhollow/reedhollow.tscn"
const HOLLOWMERE := "res://game/levels/ch17/hollowmere/hollowmere.tscn"

var saved_state: GameStateData
var zone: Ch05Zone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_the_kite_flies_to_reedhollow_and_on_to_iskarra() -> void:
	Game.state.chapter = 17
	_open(KITE)
	story.begin()
	assert_eq(Game.state.chapter, 18, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch18_started")), "K01 the maiden flight")
	assert_true(_trigger(&"ch18_chart").try_interact())
	assert_true(bool(Game.get_flag(&"ch18_world_open")), "K02")
	assert_true(bool(Game.get_flag(&"kite_flying")), "the Kite's world map opens")
	_close()

	_open(REEDHOLLOW)  # the Kite's map lands at Reedhollow's gate
	story.begin()
	assert_true(bool(Game.get_flag(&"ch18_pell_named")), "K03-K04 on arrival: Pell's new shell")
	assert_false(bool(Game.get_flag(&"ch10_started")), "Ch18's block, not Ch10's")
	assert_true(_trigger(&"ch18_heirloom_pell").is_available(), "Ressa's reed-spear")
	assert_true(_trigger(&"ch18_shore_teach").on_touched())
	assert_true(bool(Game.get_flag(&"ch18_learned_farewell_tide")), "K05")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch18/kite", "spawn": "Deck"}])
	_close()

	_open(KITE)
	story.begin()
	assert_true(bool(Game.get_flag(&"ch18_night_aboard")), "K07 on arrival")
	assert_true(bool(Game.get_flag(&"ch18_complete")), "K08 in the morning, on the same arrival")
	assert_eq(hand_offs.back()[0], ZoneStory.KIND_SCENE, "the end card until Ch19's Iskarra exists")
	_close()
	Game.state = saved_state


func test_the_child_waits_on_her_question() -> void:
	Game.state.chapter = 18
	for f: StringName in [&"ch18_started", &"ch18_world_open", &"ch18_pell_named"]:
		Game.set_flag(f)
	_open(REEDHOLLOW)
	story.begin()
	assert_false(_trigger(&"ch18_child").is_available(), "no question asked in Ch10: no answer")
	_close()
	Game.set_flag(&"ch10_child_asked")
	_open(REEDHOLLOW)
	story.begin()
	assert_true(_trigger(&"ch18_child").try_interact())
	assert_true(bool(Game.get_flag(&"ch18_child_answered")), "K06")
	_close()
	Game.state = saved_state


func test_hollowmere_in_ch18_is_the_kites_berth() -> void:
	Game.state.chapter = 18
	for f: StringName in [
		&"ch15_reached_hollowmere", &"ch17_started", &"ch17_complete", &"ch18_started", &"ch18_world_open"
	]:
		Game.set_flag(f)
	_open(HOLLOWMERE)
	story.begin()
	assert_false(_trigger(&"ch17_tool_rack").is_available(), "Ch17's hull interactables end with Ch17")
	assert_false(_trigger(&"ch17_board").is_available())
	assert_true(_trigger(&"ch18_heirloom_rhen").try_interact())
	assert_true(bool(Game.get_flag(&"ch18_heirloom_rhen")), "Dace's hooks")
	assert_true(_trigger(&"ch18_heirloom_liss").try_interact())
	assert_true(bool(Game.get_flag(&"ch18_heirloom_liss")), "Tobin's drawings")
	assert_true(_trigger(&"ch18_revisit").try_interact(), "the dock-master working again")
	_close()
	Game.state = saved_state


func _open(path: String) -> void:
	hand_offs.clear()
	zone = (load(path) as PackedScene).instantiate() as Ch05Zone
	story = zone.story
	story.autostart = false
	_host().add_child(zone)
	zone.set_process(false)
	zone.set_physics_process(false)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	story.active = true
	story.sequencer.instant = true
	story.hand_off = func(kind: StringName, target: Variant) -> void: hand_offs.append([kind, target])


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		_host().remove_child(zone)
		zone.free()
	zone = null


func _trigger(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	fail("no trigger %s" % id)
	return Interactable.new()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
