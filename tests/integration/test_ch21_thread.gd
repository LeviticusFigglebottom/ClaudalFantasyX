extends TestCase
## M5-A3P-1015: Ch21 "The Heart" and the Ending on the Kite, headless, on the real chapter data
## (game/data/flow/chapters/ch21.json): the last layer and the two lamps, Kesh, then each fight's return (combat's
## encounters, M5-A3P-1017: the victory flags stand in here) to the Letting and the Great Unbinding, and the Ending's
## scenes on the Kite.

const HEART := "res://game/levels/ch21/heart/heart.tscn"
const KITE := "res://game/levels/ch18/kite/kite.tscn"
## Each fight's victory flag, and a flag its return sets or the stage it reaches.
const STAGES: Array[StringName] = [&"ch21_kesh_fought", &"ch21_warden_fought", &"ch21_heart_fought"]

var saved_state: GameStateData
var zone: GreyboxZone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_the_heart_to_the_unbinding_and_the_ending() -> void:
	Game.state.chapter = 20
	_open(HEART)
	assert_eq(Game.state.chapter, 21, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch21_started")), "H01-H02")
	assert_true(_trigger(&"ch21_kesh").on_touched(), "H03")
	for flag in STAGES:
		Game.set_flag(flag)  # the encounter's victory (M5-A3P-1017)
		_close()
		_open(HEART)
		assert_true(hand_offs.is_empty(), "%s: the next stage plays here" % flag)
		assert_false(bool(Game.get_flag(&"ch21_unbound")), "%s: not yet" % flag)
	Game.set_flag(&"ch21_letting_fought")
	_close()
	_open(HEART)
	assert_true(bool(Game.get_flag(&"ch21_unbound")), "H08-H09: the Great Unbinding")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch18/kite", "spawn": "Deck"}], "to the Kite")
	_close()
	_open(KITE)
	assert_true(bool(Game.get_flag(&"ending_landed")), "E1-E5 on the Kite")
	assert_eq(hand_offs.back()[0], ZoneStory.KIND_SCENE, "the end card until the credits roll has a scene")
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
	story.begin()


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
