extends TestCase
## M4-C13-02: Ch13 "Gold and Lacquer" as a greybox walk, headless, on the real chapter data
## (game/data/flow/chapters/ch13.json) and its three zones: the party arrives at Ansedra's outer moorings (the chapter
## becomes 13), goes into the Sanctum (without Kerrid, who never enters it) and the Lamp Archive, and back out. The
## story beats come with the beat sheet (M4-C13-01).

const CITY := "res://game/levels/ch13/ansedra/ansedra.tscn"
const SANCTUM := "res://game/levels/ch13/sanctum/sanctum.tscn"
const ARCHIVE := "res://game/levels/ch13/lamp_archive/lamp_archive.tscn"

var saved_state: GameStateData
var zone: Ch13Zone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_the_city_leads_to_the_sanctum_and_the_archive_and_back() -> void:
	_visit(CITY)
	assert_eq(Game.state.chapter, 13, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch13_started")))
	_go(&"to_sanctum", "ch13/sanctum", "Gate")
	_visit(CITY)
	_go(&"to_archive", "ch13/lamp_archive", "Door")

	_visit(SANCTUM)
	assert_true(bool(Game.get_flag(&"ch13_entered_sanctum")))
	assert_false(&"kerrid" in Game.state.party_ids or &"kerrid" in Game.state.reserve_ids, "Kerrid never comes in")
	_go(&"to_city", "ch13/ansedra", "FromSanctum")

	_visit(ARCHIVE)
	assert_true(bool(Game.get_flag(&"ch13_entered_archive")))
	assert_true(&"kerrid" in Game.state.reserve_ids, "back in the party out of the Sanctum")
	_go(&"to_city", "ch13/ansedra", "FromArchive")
	_close()
	Game.state = saved_state


## Opens `path` (closing the zone before) and runs its arrival: a `go` ends the story's run, so each way is a visit.
func _visit(path: String) -> void:
	_close()
	hand_offs.clear()
	zone = (load(path) as PackedScene).instantiate() as Ch13Zone
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


func _go(trigger: StringName, location: String, spawn: String) -> void:
	assert_true(_trigger(trigger).on_touched(), "%s fires" % trigger)
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": location, "spawn": spawn}])


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
