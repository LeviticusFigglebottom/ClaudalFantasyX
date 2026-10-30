extends TestCase
## M4-C10-02: Ch10 "Fen of the Kirru" as a greybox walk, headless, on the real chapter data
## (game/data/flow/chapters/ch10.json) and its two zones: the party arrives at Ossa Fen's edge (the chapter becomes 10,
## Pell standing at the edge), takes the root-walks' end to Reedhollow (without Pell, who isn't let in) and walks back.
## The story beats come with the beat sheet (M4-C10-01).

const FEN := "res://game/levels/ch10/ossa_fen/ossa_fen.tscn"
const REEDHOLLOW := "res://game/levels/ch10/reedhollow/reedhollow.tscn"
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const RESERVE: Array[StringName] = [&"ysolde", &"kerrid", &"liss"]

var saved_state: GameStateData
var zone: Ch10Zone
var story: ZoneStory
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()


func test_the_fen_opens_act_two_and_leads_to_reedhollow_and_back() -> void:
	_open(FEN)
	story.begin()
	assert_eq(Game.state.chapter, 10, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch10_started")))
	assert_eq(Game.state.party_ids, PARTY)
	assert_eq(Game.state.reserve_ids, RESERVE)
	assert_true(zone.player.position.distance_to(zone.spawn_marker(&"FenEdge").position) < 0.01, "at the fen's edge")
	var pell := zone.stage.actor(&"pell")
	assert_true(pell != null and pell.position.distance_to(zone.stage.mark(&"pell_edge").position) < 0.01, "Pell stops")
	assert_false(_trigger(&"to_reedhollow").is_available(), "the way on waits on the Drowner")
	assert_true(_trigger(&"clearing").on_touched())
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "the Drowner rises")
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, &"ch10_mangrove_drowner")
	assert_eq(r.victory_flag, &"ch10_drowner_defeated")
	Game.set_flag(&"ch10_drowner_defeated")  # the battle's victory
	_close()
	_open(FEN)
	story.begin()
	assert_false(_trigger(&"clearing").is_available(), "the clearing is quiet")
	assert_true(_trigger(&"to_reedhollow").on_touched())
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch10/reedhollow", "spawn": "Gate"}])
	_close()

	_open(REEDHOLLOW)
	story.begin()
	assert_true(bool(Game.get_flag(&"ch10_reached_reedhollow")))
	assert_false(&"pell" in Game.state.party_ids or &"pell" in Game.state.reserve_ids, "Pell isn't let in")
	# M4-A2P-114: the shore plays the farewell-tide (B09), then the dawn gate (B11)
	assert_true(_trigger(&"shore").on_touched())
	assert_true(bool(Game.get_flag(&"ch10_farewell_tide_seen")), "the tide is watched")
	assert_true(bool(Game.get_flag(&"ch10_complete")), "and the chapter closes at the dawn gate")
	assert_false(_trigger(&"shore").is_available(), "once")
	assert_true(_trigger(&"to_fen").on_touched())
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch10/ossa_fen", "spawn": "FromReedhollow"}])
	_close()
	Game.state = saved_state


func _open(path: String) -> void:
	hand_offs.clear()
	zone = (load(path) as PackedScene).instantiate() as Ch10Zone
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
