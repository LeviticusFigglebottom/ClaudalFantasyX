extends TestCase
## M5-A3P-1007: Ch19 "Iskarra", headless, on the real chapter data (game/data/flow/chapters/ch19.json) and its two
## zones on env-art's Iskarra kit: the Kite comes down, the vigil, the hitch, the words, up to the spire (the
## signatures), and after the Wardens' fight (combat's encounter, M5-A3P-1009: its victory flag stands in here) the
## engine stops and the eye opens.

const PLAZA := "res://game/levels/ch19/iskarra/iskarra.tscn"
const SPIRE := "res://game/levels/ch19/iskarra_spire/iskarra_spire.tscn"

var saved_state: GameStateData
var zone: GreyboxZone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_iskarra_from_the_kite_to_the_engine() -> void:
	Game.state.chapter = 18
	_open(PLAZA)
	story.begin()
	assert_eq(Game.state.chapter, 19, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch19_started")), "I01")
	assert_false(_trigger(&"ch19_hitch").is_available(), "the hitch waits on the vigil")
	assert_true(_trigger(&"ch19_vigil").on_touched())
	assert_true(bool(Game.get_flag(&"ch19_vigil")), "I02")
	assert_true(_trigger(&"ch19_hitch").try_interact())
	assert_true(bool(Game.get_flag(&"ch19_learned_the_hitch")), "I03")
	assert_true(_trigger(&"ch19_words").try_interact())
	assert_true(bool(Game.get_flag(&"ch19_words_whole")), "I04, optional")
	assert_true(_trigger(&"ch19_to_spire").on_touched())
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch19/iskarra_spire", "spawn": "Antechamber"}])
	_close()

	_open(SPIRE)
	story.begin()
	assert_false(_trigger(&"ch19_engine").is_available(), "the engine waits on the Wardens")
	_close()
	Game.set_flag(&"ch19_abiding_beaten")  # the encounter's victory (M5-A3P-1009)
	_open(SPIRE)
	story.begin()
	assert_true(_trigger(&"ch19_engine").try_interact())
	assert_true(bool(Game.get_flag(&"ch19_engine_stopped")), "I09")
	assert_true(bool(Game.get_flag(&"ch19_complete")), "I10")
	assert_eq(hand_offs.back()[0], ZoneStory.KIND_SCENE, "the end card until Ch20's Undertow exists")
	_close()
	Game.state = saved_state


func _open(path: String) -> void:
	hand_offs.clear()
	zone = (load(path) as PackedScene).instantiate() as GreyboxZone
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
