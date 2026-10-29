extends TestCase
## M4-C11-02: Ch11 "Lowlight" as a greybox walk, headless, on the real chapter data
## (game/data/flow/chapters/ch11.json) and its two zones: the party arrives at Sunken Vey's landing (the chapter
## becomes 11), takes the galleries' end to Lowlight's gate and walks back. The story beats come with the beat sheet
## (M4-C11-01).

const VEY := "res://game/levels/ch11/sunken_vey/sunken_vey.tscn"
const LOWLIGHT := "res://game/levels/ch11/lowlight/lowlight.tscn"

var saved_state: GameStateData
var zone: Ch11Zone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_the_galleries_lead_to_lowlight_and_back() -> void:
	_open(VEY)
	story.begin()
	assert_eq(Game.state.chapter, 11, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch11_started")))
	assert_true(zone.player.position.distance_to(zone.spawn_marker(&"Landing").position) < 0.01, "at the landing")
	assert_true(_trigger(&"to_lowlight").on_touched())
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch11/lowlight", "spawn": "Gate"}])
	_close()

	_open(LOWLIGHT)
	story.begin()
	assert_true(bool(Game.get_flag(&"ch11_reached_lowlight")))
	assert_true(_trigger(&"to_vey").on_touched())
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch11/sunken_vey", "spawn": "FromLowlight"}])
	_close()
	Game.state = saved_state


func _open(path: String) -> void:
	hand_offs.clear()
	zone = (load(path) as PackedScene).instantiate() as Ch11Zone
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
