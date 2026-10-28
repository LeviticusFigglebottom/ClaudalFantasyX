class_name Act2GreyboxCase
extends TestCase
## The visit-and-hand-off pattern of the Act II greybox thread tests (M4-C14-02 onward): `visit` opens a zone headless
## with an instant sequencer and runs its arrival (a `go` ends the story's run, so each way out is its own visit), `go`
## touches a trigger and checks the hand-off it records.

var saved_state: GameStateData
var zone: GreyboxZone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func after_visits() -> void:
	close_zone()
	Game.state = saved_state


func visit(path: String) -> void:
	close_zone()
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


func go(trigger: StringName, location: String, spawn: String) -> void:
	var t := trigger_named(trigger)
	assert_true(t.on_touched() or t.try_interact(), "%s fires" % trigger)
	assert_eq(
		hand_offs.back() if not hand_offs.is_empty() else [],
		[ZoneStory.KIND_GO, {"location": location, "spawn": spawn}]
	)


func close_zone() -> void:
	if zone != null and is_instance_valid(zone):
		_host().remove_child(zone)
		zone.free()
	zone = null


func trigger_named(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	fail("no trigger %s" % id)
	return Interactable.new()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
