extends TestCase
## M4-C13-02: Ch13 "Gold and Lacquer" as a greybox walk, headless, on the real chapter data
## (game/data/flow/chapters/ch13.json) and its three zones: the party arrives at Ansedra's outer moorings (the chapter
## becomes 13), goes into the Sanctum (without Kerrid, who never enters it) and the Lamp Archive, and back out. The
## story beats come with the beat sheet (M4-C13-01).

const CITY := "res://game/levels/ch13/ansedra/ansedra.tscn"
const SANCTUM := "res://game/levels/ch13/sanctum/sanctum.tscn"
const ARCHIVE := "res://game/levels/ch13/lamp_archive/lamp_archive.tscn"
## Ch14's Lacquer Court is a ch13/ zone, so this thread is the one test_qa_threads checks its rows on (M3-UI-1242).
const COURT := "res://game/levels/ch13/ansedra_lacquer_court/ansedra_lacquer_court.tscn"

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


## M4-A2P-114: the chapter's story in order: Ethren at the basin's edge (B05-B06), the Archive's three days (the
## ledgers B07, the Cantor roll B08, the hands B09 on the third visit) and the pact at night back in the city (B10-B11).
func test_the_still_city_plays_its_scenes_in_order() -> void:
	_visit(CITY)
	assert_true(bool(Game.get_flag(&"ch13_wedding_announced")), "M4-A2P-1003 E3: the still city plays on arrival")
	assert_true(bool(Game.get_flag(&"ch13_met_tobin")), "and Tobin after it")
	assert_true(bool(Game.get_flag(&"ch13_guest_of_sefir")), "the party are Sefir's guests")
	_go(&"to_archive", "ch13/lamp_archive", "Door")
	_visit(ARCHIVE)
	assert_false(_trigger(&"ledgers").is_available(), "E2: the Archive waits on Ethren")
	_go(&"to_city", "ch13/ansedra", "FromArchive")
	_visit(CITY)
	_go(&"to_sanctum", "ch13/sanctum", "Gate")
	_visit(SANCTUM)
	assert_true(_trigger(&"ledge").on_touched())
	assert_true(bool(Game.get_flag(&"ch13_ethren_bound")), "Ethren is bound")
	_go(&"to_city", "ch13/ansedra", "FromSanctum")
	_visit(ARCHIVE)
	assert_true(_trigger(&"ledgers").on_touched())
	assert_true(bool(Game.get_flag(&"ch13_read_ledgers")), "the first day")
	assert_false(bool(Game.get_flag(&"ch13_read_cantor_roll")), "E9: the roll waits on the next visit")
	_go(&"to_city", "ch13/ansedra", "FromArchive")
	_visit(ARCHIVE)
	assert_true(bool(Game.get_flag(&"ch13_read_cantor_roll")), "the second day")
	assert_false(bool(Game.get_flag(&"ch13_archive_read")), "one day a visit")
	_go(&"to_city", "ch13/ansedra", "FromArchive")
	_visit(CITY)
	assert_false(bool(Game.get_flag(&"ch13_pact_of_silence")), "no pact before the third day")
	_visit(ARCHIVE)
	assert_true(bool(Game.get_flag(&"ch13_archive_read")), "the third day: the hands")
	_go(&"to_city", "ch13/ansedra", "FromArchive")
	_visit(CITY)
	assert_false(bool(Game.get_flag(&"ch13_pact_of_silence")), "E8: the pact waits at the moorings")
	assert_true(_trigger(&"pact").on_touched())
	assert_true(bool(Game.get_flag(&"ch13_pact_of_silence")), "the pact at night")
	assert_true(bool(Game.get_flag(&"ch13_complete")), "closes the chapter")
	_visit(CITY)
	assert_true(_trigger(&"rest").try_interact())
	assert_eq(
		hand_offs.back(),
		[ZoneStory.KIND_GO, {"location": "ch13/ansedra_lacquer_court", "spawn": "CourtEntry"}],
		"E1: Sefir's door, then the Lacquer Court"
	)
	_close()
	Game.state = saved_state


## M4-A2P-1200: Ch14 in the court: the vows and the trap at the dais (B02-B05), the water-steps held (B06), the first
## ripple and Warden Venn on the lagoon (B07-B09), left standing (B10), then the barge out to the open sea.
func test_the_wedding_court_plays_its_story_in_order() -> void:
	_visit(COURT)
	assert_eq(Game.state.chapter, 14, "the chapter step")
	assert_false(_trigger(&"barge").is_available(), "no escape before the trap")
	assert_true(_trigger(&"dais").on_touched())
	assert_true(bool(Game.get_flag(&"ch14_vows_spoken")), "the vows")
	assert_true(bool(Game.get_flag(&"ch14_declared_heretics")), "and the trap")
	_battle(&"ch14_water_steps", &"ch14_steps_held")
	_visit(COURT)
	assert_true(bool(Game.get_flag(&"ch14_merel_taken")), "the first ripple: Merel at the water-gate")
	_battle(&"ch14_malcor_venn", &"ch14_venn_beaten")
	_visit(COURT)
	assert_true(bool(Game.get_flag(&"ch14_complete")), "left standing")
	_go(&"barge", "ch15/open_sea", "Deck")
	_close()
	Game.state = saved_state


## The last hand-off is battle `encounter` with `victory_flag`; the win is set as the battle would.
func _battle(encounter: StringName, victory_flag: StringName) -> void:
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "%s starts" % encounter)
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, encounter)
	assert_eq(r.victory_flag, victory_flag)
	Game.set_flag(victory_flag)


## Opens `path` (closing the zone before) and runs its arrival: a `go` ends the story's run, so each way is a visit.
## M4-A2P-104: each pole stroke of the escape (`@sfx pole_stroke`) sends a ring out from the barge's stern.
func test_a_pole_stroke_ripples_the_lagoon() -> void:
	_visit(COURT)
	var field := RippleField.find(zone.get_tree())
	assert_true(field != null, "the court has its ripple field")
	if field == null:
		return
	var before := field.sources.size()
	story.sequencer.cue_played.emit(&"sfx", [&"pole_stroke"], {})
	assert_eq(field.sources.size(), before + 1, "one ring per stroke")
	story.sequencer.cue_played.emit(&"sfx", [&"bell_toll"], {})
	assert_eq(field.sources.size(), before + 1, "other sounds leave the water still")
	_close()
	Game.state = saved_state


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
