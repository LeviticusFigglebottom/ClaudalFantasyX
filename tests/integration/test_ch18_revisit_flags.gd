extends TestCase
## M5-A3P-1704 (request from ui): the Kite's log marks a Ch18 town seen once it is revisited. Each revisit side scene
## sets its town's ch18_revisit_<town> as it ends, and Haluna's is set on the visit itself (HalunaStory's arrival with
## ch18_world_open set), whether or not the optional lifting plays.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const COMPILED := "res://game/data/dialogue/compiled/ch18_revisit_%s.json"
const TOWNS: Array[String] = ["ansedra", "corrow", "hollowmere", "oruvel", "pemakar", "quellan", "tamsule"]

var zone: HalunaZone
var story: HalunaStory
var saved_state: GameStateData


func test_every_revisit_scene_sets_its_town_flag() -> void:
	for town in TOWNS:
		var text := FileAccess.get_file_as_string(COMPILED % town)
		assert_true(text.contains('ch18_revisit_%s"' % town), "ch18_revisit_%s sets its flag" % town)


func test_haluna_counts_the_visit_on_arrival_in_the_open_world() -> void:
	_arrive([&"ch02_met_asha", &"ch18_world_open"])
	await story.begin()
	assert_true(bool(Game.get_flag(&"ch18_revisit_haluna")), "seen on arrival, no lifting needed")
	assert_false(bool(Game.get_flag(&"ch18_haluna_lifted")), "the lifting stays optional")
	_done()


func test_haluna_before_act_three_is_not_a_revisit() -> void:
	_arrive([&"ch02_met_asha"])
	await story.begin()
	assert_false(bool(Game.get_flag(&"ch18_revisit_haluna")), "Act I's Haluna is not the Ch18 visit")
	_done()


func _arrive(flags: Array[StringName]) -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	for f in flags:
		Game.set_flag(f, true)
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	story = zone.get_node("Story") as HalunaStory
	story.autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	story.active = true
	story.sequencer.instant = true
	story.hand_off = func(_kind: StringName, _target: String) -> void: pass


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
