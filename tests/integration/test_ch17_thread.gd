extends TestCase
## M5-A3P-1001: Ch17 "The Wright's Son" at Hollowmere, headless, on the real chapter data
## (game/data/flow/chapters/ch17.json) and the Ch15 zone it shares (ChapterRegistry gives Ch17 the zone from chapter
## 16 on): pulled from the sea, the dock-master's walk, the hull, the ledger, the first berth, the choice, the first
## lamp, Ysolde's table, and boarding the hull ends the chapter.

const HOLLOWMERE := "res://game/levels/ch17/hollowmere/hollowmere.tscn"

var saved_state: GameStateData
var zone: Ch17Zone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_out_of_ch16_hollowmere_is_ch17s() -> void:
	Game.state.chapter = 16
	_open()
	story.begin()
	assert_eq(Game.state.chapter, 17, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch17_started")), "B01 pulled from the sea")
	assert_false(bool(Game.get_flag(&"ch15_reached_hollowmere")), "not Ch15's arrival")
	assert_true(zone.player.position.distance_to(zone.spawn_marker(&"Dock").position) < 0.01, "on the dock")
	_close()
	Game.state = saved_state


func test_ch15_still_gets_its_own_hollowmere() -> void:
	Game.state.chapter = 15
	_open()
	story.begin()
	assert_true(bool(Game.get_flag(&"ch15_reached_hollowmere")))
	assert_false(bool(Game.get_flag(&"ch17_started")))
	assert_false(_trigger(&"ch17_dock_master").is_available(), "no Ch17 trigger in Ch15")
	_close()
	Game.state = saved_state


func test_the_chapter_runs_to_the_hull() -> void:
	Game.state.chapter = 16
	_open()
	story.begin()
	assert_false(_trigger(&"ch17_ledger").is_available(), "the hull waits on the dock-master")
	assert_true(_trigger(&"ch17_dock_master").on_touched())
	assert_true(bool(Game.get_flag(&"ch17_saw_the_hull")), "B03")
	for id: StringName in [&"ch17_hull_sails", &"ch17_tool_rack", &"ch17_chart_wall"]:
		assert_true(_trigger(id).is_available(), "B04 %s" % id)
	assert_false(_trigger(&"ch17_choice").is_available(), "the choice waits on the ledger")
	assert_true(_trigger(&"ch17_ledger").try_interact())
	assert_true(bool(Game.get_flag(&"ch17_read_the_ledger")), "B05-B06")
	assert_true(_trigger(&"ch17_first_berth").try_interact())
	assert_true(bool(Game.get_flag(&"ch17_first_berth")), "B07, optional")
	assert_true(_trigger(&"ch17_choice").on_touched())
	assert_true(bool(Game.get_flag(&"ch17_chose_the_unbinding")), "B08")
	assert_true(bool(Game.get_flag(&"ch17_night")), "the choice is at night")
	assert_false(_trigger(&"ch17_board").is_available(), "boarding waits on the verse")
	assert_true(_trigger(&"ch17_engine").try_interact())
	assert_true(bool(Game.get_flag(&"ch17_first_lamp_lit")), "B10")
	assert_true(_trigger(&"ch17_table").try_interact())
	assert_true(bool(Game.get_flag(&"ch17_verse_begun")), "B11")
	assert_true(_trigger(&"ch17_board").try_interact())
	assert_true(bool(Game.get_flag(&"ch17_complete")), "B12: boarding ends the chapter")
	assert_eq(hand_offs.back()[0], ZoneStory.KIND_SCENE, "the end card until Ch18's Kite zone exists")
	_close()
	Game.state = saved_state


func _open() -> void:
	hand_offs.clear()
	zone = (load(HOLLOWMERE) as PackedScene).instantiate() as Ch17Zone
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
