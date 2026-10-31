extends TestCase
## M5-A3P-1011: Ch20 "The Undertow", headless, on the real chapter data (game/data/flow/chapters/ch20.json) and its zone
## on env-art's Undertow kit: down the eye, then each layer's scene, its fight (combat's encounters, M5-A3P-1013: each
## victory flag stands in here) and on the return its release and the next layer, the Cage, and the thank-yous.

const UNDERTOW := "res://game/levels/ch20/undertow_layers/undertow_layers.tscn"
const LAYERS: Array[String] = ["ilun", "kahre", "virel", "hesk", "nhoa", "ethren"]

var saved_state: GameStateData
var zone: GreyboxZone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_down_the_eye_through_six_layers_and_the_cage() -> void:
	Game.state.chapter = 19
	_open()
	assert_eq(Game.state.chapter, 20, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch20_started")), "U00")
	_near(&"Layer1", "on the first layer")
	for k in LAYERS.size():
		var v := LAYERS[k]
		for later in range(k + 1, LAYERS.size()):
			assert_false(_trigger(StringName("ch20_" + LAYERS[later])).is_available(), "%s waits" % LAYERS[later])
		assert_true(_trigger(StringName("ch20_" + v)).on_touched(), "layer %d: %s" % [k + 1, v])
		Game.set_flag(StringName("ch20_%s_fought" % v))  # the encounter's victory (M5-A3P-1013)
		_close()
		_open()
		assert_true(bool(Game.get_flag(StringName("ch20_%s_released" % v))), "%s released on the return" % v)
		_near(&"Layer%d" % (k + 2) if k < LAYERS.size() - 1 else &"Cage", "placed on the next floor")
	assert_true(_trigger(&"ch20_cage").on_touched(), "U07")
	Game.set_flag(&"ch20_cage_broken")  # the Cage's victory (M5-A3P-1013)
	_close()
	_open()
	assert_true(bool(Game.get_flag(&"ch20_complete")), "U08: the thank-yous")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch21/heart", "spawn": "HeartEdge"}], "the Heart")
	_close()
	Game.state = saved_state


func _near(spawn: StringName, what: String) -> void:
	assert_true(zone.player.position.distance_to(zone.spawn_marker(spawn).position) < 0.01, what)


func _open() -> void:
	hand_offs.clear()
	zone = (load(UNDERTOW) as PackedScene).instantiate() as GreyboxZone
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
