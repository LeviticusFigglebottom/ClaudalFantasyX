extends TestCase
## M4-C12-02: Ch12 "The Cold Road" as a greybox walk, headless, on the real chapter data
## (game/data/flow/chapters/ch12.json) and its three zones: the party arrives at the foot of Keth Pass (the chapter
## becomes 12), crosses to Quellan, climbs to Cloudloom, and every way back hands off to the right spawn. The story
## beats come with the beat sheet (M4-C12-01).

const PASS := "res://game/levels/ch12/keth_pass/keth_pass.tscn"
const QUELLAN := "res://game/levels/ch12/quellan/quellan.tscn"
const CLOUDLOOM := "res://game/levels/ch12/cloudloom/cloudloom.tscn"

var saved_state: GameStateData
var zone: Ch12Zone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_the_cold_road_runs_from_the_pass_to_the_summit_and_back() -> void:
	_open(PASS)
	story.begin()
	assert_eq(Game.state.chapter, 12, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch12_started")))
	_go(&"to_quellan", "ch12/quellan", "FromPass")
	_close()

	_open(QUELLAN)
	story.begin()
	assert_true(bool(Game.get_flag(&"ch12_reached_quellan")))
	_go(&"to_cloudloom", "ch12/cloudloom", "Approach")
	_close()
	_open(QUELLAN)  # a `go` ends the story's run: the way back is another visit
	story.begin()
	_go(&"to_pass", "ch12/keth_pass", "FromQuellan")
	_close()

	_open(CLOUDLOOM)
	story.begin()
	assert_true(bool(Game.get_flag(&"ch12_reached_cloudloom")))
	_go(&"to_quellan", "ch12/quellan", "FromCloudloom")
	_close()
	Game.state = saved_state


func _go(trigger: StringName, location: String, spawn: String) -> void:
	var t := _trigger(trigger)
	assert_true(t.on_touched(), "%s fires" % trigger)
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": location, "spawn": spawn}])


func _open(path: String) -> void:
	hand_offs.clear()
	zone = (load(path) as PackedScene).instantiate() as Ch12Zone
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
