extends TestCase
## M3-C04-02: Ch4 "The Pilgrim's Wake" end to end, headless, on the real chapter data
## (game/data/flow/chapters/ch04.json) and its two greybox zones, from the slice's end (B11 has sworn
## Rhen in) to the chapter's exit: Haluna's wake night (the lamps to the wall and the chapter step, the
## dark town's barks, the closed inn, the feast and its tables, Neme's table and the wall's call, the
## shell set and Rhen walking out, the dark dock and the Kell choice, the stranger re-inking the shells,
## Neme's door and the dawn causeway) → the ferry (the gangplank and Ysolde, in reserve; the crossing's
## banters, the purser and the shrine's rest; no fight on the ferry, ever: ADR 0017 (d); the Seventh
## Terrace at the bow) → the derelict (the barks, the leech ambush, the bottle-hermit lesson with
## Ysolde in reserve, random fights only aboard her, the Spar-Wraith after a breath) → the name-board,
## under way, and the hand-off (the end card, standing in for Ch5's Pemakar). Instant sequencers;
## every hand-off is recorded through ZoneStory.hand_off, and every fight is played in the real field
## battle (three heroes and a reserve) to a forced win, as test_ch01_thread does.

const WAKE := "res://game/levels/ch04/haluna_wake/haluna_wake.tscn"
const FERRY := "res://game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn"
const BATTLE := "res://game/flow/field_battle.tscn"
const SAVE_DIR := "user://test_ch04_thread_saves"
const MAX_TURNS := 200
## Far more metres than the derelict's longest gap between random fights.
const LONG_WALK_M := 500.0
const ACTIVE: Array[StringName] = [&"rhen", &"asha", &"toma"]
const RESERVE: Array[StringName] = [&"ysolde"]
## The slice's end state Ch4 starts from (B11 and before).
const SLICE_FLAGS: Array[StringName] = [
	&"ch02_met_asha",
	&"ch03_ilun_bound",
	&"ch03_first_verse_sung",
	&"ch03_drownbell_defeated",
	&"ch03_rhen_sworn_guardian"
]
## Staging problems a scene must never have on its own stage (music and sounds are Audio's, still to
## come; placeholder cue keys are the sequencer's).
const STAGING_WARNINGS: Array[String] = ["no shot", "no mark", "no actor", "cannot place", "no look_at"]

var saved_state: GameStateData
var saved_dir := ""
var zone: Ch04Zone
var story: ZoneStory
var hand_offs: Array[Array] = []
var travels: Array[Array] = []
var lines: Array[StringName] = []
var restore_at_line: Dictionary = {}
var warnings: Array[String] = []


func before_each() -> void:
	FieldEncounters.reset()
	saved_state = Game.state
	Game.state = GameStateData.new()
	BattleRequest.clear()
	BattleRequest.change_scene = func(_p: String) -> void: pass
	saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = SAVE_DIR
	hand_offs.clear()
	travels.clear()
	lines.clear()
	restore_at_line.clear()
	warnings.clear()


func test_ch4_plays_from_the_wake_to_the_crossings_end() -> void:
	_slice_end()
	_wake_night()
	_ferry_and_derelict()
	_check_staging()
	_done()


func test_the_wake_waits_for_rhen_to_be_sworn_in() -> void:
	Game.state.party_ids.assign(ACTIVE)
	_open(WAKE)
	story.begin()
	assert_false(bool(Game.get_flag(&"ch04_started")), "Ch4 doesn't start without B11")
	assert_eq(lines.size(), 0)
	_done()


func test_not_tonight_and_the_asked_after_payoff() -> void:
	_slice_end()
	Game.set_flag(&"ch03_rhen_asked_after")
	Game.set_flag(&"ch04_started")
	Game.set_flag(&"ch04_feast_neme")
	_open(WAKE)
	story.sequencer.auto_choice = 1  # "Not tonight."
	assert_true(_trigger(&"wall").on_touched())
	assert_true(&"ch04_shell_018" in lines, "Toma: 'You asked me. On the steps.' (the B08 payoff)")
	assert_false(&"ch04_shell_020" in lines)
	assert_false(bool(Game.get_flag(&"ch04_rhen_named_kell")), "'Not tonight.'")
	assert_true(&"ch04_dock_012" in lines, "'Then another night.'")
	assert_true(bool(Game.get_flag(&"ch04_dock_comforted")))
	assert_true(_trigger(&"neme_door").try_interact(), "Neme's door ends the night")
	assert_false(bool(Game.get_flag(&"ch04_saw_ysolde_ink")), "and the side scene is gone")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch04/brightwater_ferry", "spawn": "Landing"}])
	_close()
	hand_offs.clear()
	_open(FERRY)
	story.begin()
	assert_true(&"ch04_plank_007" in lines, "Ysolde: 'I have decided not to notice.'")
	assert_false(&"ch04_plank_008" in lines, "no 'You did the shells.' without the ink")
	_done()


func _slice_end() -> void:
	for f in SLICE_FLAGS:
		Game.set_flag(f)
	Game.state.party_ids.assign(ACTIVE)
	Game.state.chapter = 3


func _wake_night() -> void:
	_open(WAKE)
	assert_true(zone.story_set_shown("ch04_wake"), "the lamps line the way to the wall")
	assert_false(zone.story_set_shown("ch04_shell_asha"), "the gap in the wall is still a gap")
	story.begin()
	assert_true(bool(Game.get_flag(&"ch04_started")), "C4-01")
	assert_eq(Game.state.chapter, 4, "the chapter step (the chapter autosave follows)")
	assert_eq(Game.state.party_ids, ACTIVE, "Rhen, Asha and Toma")
	assert_true(&"ch04_lamps_002" in lines, "Toma: 'To her.'")
	assert_true(_at(&"NemeDoor"))

	assert_false(_trigger(&"neme_door").is_available(), "the night isn't over")
	assert_false(_trigger(&"wall").is_available(), "the wall's call waits for Neme's table")
	for id: StringName in [&"npc_child", &"npc_netmender", &"npc_reed", &"inn_door"]:
		var before := lines.size()
		assert_true(_trigger(id).try_interact(), "%s answers" % id)
		assert_true(lines.size() > before, "%s spoke" % id)
	assert_true(&"ch04_bark_rhyme_001" in lines, "the end of the skipping rhyme, as promised")
	assert_true(&"ch04_bark_inn_001" in lines, "the inn is closed tonight")

	assert_true(_trigger(&"feast").on_touched())
	assert_true(&"ch04_wake_001" in lines, "C4-03: into the lamplight")
	assert_false(_trigger(&"feast").on_touched(), "once")
	for id: StringName in [&"table_vendor", &"table_osu", &"table_fisher"]:
		var before := lines.size()
		assert_true(_trigger(id).try_interact(), "%s" % id)
		assert_true(lines.size() > before)
	assert_false(&"ch04_wake_osu_003" in lines, "Teyo's hello only after Ch2's side scene")
	assert_true(_trigger(&"table_neme").try_interact())
	assert_true(bool(Game.get_flag(&"ch04_feast_neme")))
	assert_true(&"ch04_wake_neme_001" in lines)

	assert_true(_trigger(&"wall").on_touched())
	assert_true(bool(Game.get_flag(&"ch04_shell_set")), "C4-04")
	assert_true(&"ch04_shell_004" in lines, "Osu: 'Asha Velamir.'")
	assert_true(&"ch04_shell_010" in lines, "Asha says it for Neme")
	assert_true(&"ch04_shell_017" in lines, "Rhen understands")
	assert_true(&"ch04_shell_020" in lines, "Toma: 'No. They do not.'")
	assert_true(&"ch04_shell_024" in lines, "C4-05: 'Then I can leave it if I like.'")
	assert_true(zone.story_set_shown("ch04_shell_asha"), "her shell is in the wall")
	assert_false(zone.block_shown("ysolde_edge"), "the figure at the lamplight's edge is gone")
	assert_true(&"ch04_dock_001" in lines, "C4-06: 'Don't be kind about it.'")
	assert_true(bool(Game.get_flag(&"ch04_rhen_named_kell")), "'Tell her about Oruvel.' (the first option)")
	assert_true(&"ch04_dock_008" in lines, "Mother Kell")
	assert_false(&"ch04_dock_009" in lines, "Kell's favour line only after Ch1's side scene")
	assert_true(&"ch04_dock_015" in lines, "'Someone humming in the next room.'")
	assert_true(bool(Game.get_flag(&"ch04_dock_comforted")))
	assert_true(_at(&"DockShore"), "back to the shore end of the dock")
	assert_false(zone.block_shown("vendor"), "the village has gone home")
	assert_true(zone.block_shown("ysolde"), "a tall figure kneels at the wall")
	assert_false(story.busy)

	assert_true(_trigger(&"the_ink").try_interact())
	assert_true(bool(Game.get_flag(&"ch04_saw_ysolde_ink")), "C4-07")
	assert_true(&"ch04_ink_010" in lines, "'Once.'")
	assert_false(zone.block_shown("ysolde"), "she goes")
	assert_false(_trigger(&"the_ink").is_available(), "once")

	assert_true(_trigger(&"neme_door").try_interact())
	assert_true(bool(Game.get_flag(&"ch04_left_haluna")), "C4-08")
	assert_true(&"ch04_dawn_001" in lines, "Neme: 'Eat when they feed you.'")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch04/brightwater_ferry", "spawn": "Landing"}])
	assert_false(restore_at_line.get(&"ch04_dawn_002", true), "the causeway hands off on black")
	assert_true(LocationRegistry.load_default().has_location(&"ch04/brightwater_ferry"))
	_close()


func _ferry_and_derelict() -> void:
	hand_offs.clear()
	_open(FERRY)
	assert_true(zone.block_shown("Gangplank"))
	story.begin()
	assert_true(&"ch04_plank_007" in lines, "C4-09: 'I have decided not to notice.'")
	assert_true(&"ch04_plank_008" in lines, "'You did the shells.' (he held the lamp)")
	assert_true(bool(Game.get_flag(&"ch04_ysolde_joined")))
	assert_eq(Game.state.party_ids, ACTIVE, "three active")
	assert_eq(Game.state.reserve_ids, RESERVE, "Ysolde in reserve")
	assert_true(_at(&"Deck"))
	assert_false(zone.block_shown("Gangplank"), "the gangplank is shipped")

	var met: Array[StringName] = []
	zone.encounters.on_encounter = func(id: StringName) -> void: met.append(id)
	assert_eq(zone.encounters.walked(LONG_WALK_M), &"", "the ferry is never attacked (ADR 0017)")
	for id: StringName in [&"banter_ennu", &"banter_once", &"banter_salt"]:
		assert_true(_trigger(id).on_touched(), "%s plays as Rhen walks past" % id)
		assert_false(_trigger(id).on_touched(), "%s once" % id)
	assert_eq((_trigger(&"purser").payload as Dictionary).get("shop"), "brightwater_purser", "the purser's shop")
	assert_true(_trigger(&"purser").is_available())
	assert_true(_trigger(&"shrine").try_interact())
	assert_eq(zone.rests, 1, "the deckhouse shrine rests the party")

	assert_true(_trigger(&"bow").on_touched())
	assert_true(&"ch04_terrace_003" in lines, "C4-11: 'Her skipper paid me short.'")
	assert_true(&"ch04_terrace_007" in lines, "never lash a living hull to a drowned one")
	assert_true(bool(Game.get_flag(&"ch04_boarded_derelict")))
	assert_true(_at(&"DerelictDeck"))
	assert_true(_actor_at(&"asha", &"derelict_asha"), "Asha won't let him go alone")
	assert_true(zone.encounters.walked(LONG_WALK_M) in [&"ch04_derelict_leeches", &"ch04_derelict_glass"])
	assert_eq(met.size(), 1, "random fights only aboard the derelict")
	assert_eq(hand_offs.size(), 0, "the test recorder took it")

	for id: StringName in [&"galley_bowls", &"hourglass"]:
		var before := lines.size()
		assert_true(_trigger(id).try_interact(), "%s" % id)
		assert_true(lines.size() > before)
	assert_false(_trigger(&"hold_housing").is_available(), "the hold after the yards")
	assert_false(_trigger(&"hermit").is_available(), "the hermit waits for the leeches")
	assert_false(_trigger(&"wraith").is_available(), "the wraith waits for the hermit")

	assert_true(_trigger(&"leeches").on_touched())
	_fight(&"ch04_sail_leeches", &"AfterLeeches", &"ch04_leeches_won")
	_reopen(FERRY, &"AfterLeeches")
	assert_true(_actor_at(&"asha", &"derelict_asha"), "a fight's return finds the party still aboard her")
	assert_true(_trigger(&"hold_housing").try_interact())
	assert_true(&"ch04_bark_housing_001" in lines)
	assert_true(_trigger(&"hermit").on_touched())
	_fight(&"ch04_bottle_hermit", &"AfterHermit", &"ch04_hermit_won")
	_reopen(FERRY, &"AfterHermit")
	assert_true(_trigger(&"wraith").on_touched())
	assert_eq(zone.rests, 1, "a breath before the boss")
	assert_true(&"ch04_wraith_002" in lines, "Toma: 'On my shield.'")
	_fight(&"ch04_spar_wraith", &"Stern", &"ch04_spar_wraith_defeated")

	_reopen(FERRY, &"Stern")
	assert_true(bool(Game.get_flag(&"ch04_name_board_carried")), "C4-14")
	assert_true(&"ch04_board_004" in lines, "'Tell them it's paid.'")
	assert_true(&"ch04_board_006" in lines, "the older Rhen, once")
	assert_eq(_count(&"name_board_seventh_terrace"), 1, "the key item")
	assert_false(zone.block_shown("SailsSet"), "the sails come down")
	assert_true(zone.block_shown("SailsLowered"))
	assert_false(zone.block_shown("spar_wraith"))
	assert_false(zone.block_shown("NameBoard"), "the board is off her stern")
	assert_true(zone.block_shown("NameBoardWrapped"), "and wrapped on the ferry's deck")
	assert_true(_actor_at(&"asha", &"ferry_asha"), "the party is back aboard the ferry")
	assert_true(&"ch04_under_way_001" in lines, "C4-15")
	assert_eq(
		hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch05/pemakar", "spawn": "Harbour"}], "on to Ch5's Pemakar"
	)
	assert_false(restore_at_line.get(&"ch04_under_way_001", true), "it hands off on black")
	_close()


## Plays the pending request in the real field battle (three heroes, Ysolde in reserve) to a forced
## win and presses Return. Checks the request and the travel back.
func _fight(encounter: StringName, spawn: StringName, flag: StringName) -> void:
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "%s opens" % encounter)
	if hand_offs.is_empty():
		return
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, encounter)
	assert_eq(r.active, ACTIVE, "%s: Rhen, Asha and Toma" % encounter)
	assert_eq(r.reserve, RESERVE, "%s: Ysolde in reserve" % encounter)
	assert_eq(r.return_spawn, spawn)
	assert_eq(r.victory_flag, flag)
	_close()
	BattleRequest.submit(r)
	var ctl := (load(BATTLE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.travel = func(loc: StringName, sp: StringName) -> bool:
		travels.append([loc, sp])
		return true
	ctl.open_title = func(_p: String) -> void: pass
	ctl.save_system = SaveSystem
	_host().add_child(ctl)
	ctl.start_sandbox()
	assert_eq(ctl.engine.encounter_id, encounter)
	assert_eq(ctl.engine.party_active.size(), 3, "three heroes on the field")
	assert_eq(ctl.engine.party_reserve.size(), 1, "and one in reserve")
	for _i in MAX_TURNS:
		if ctl.state == BattleController.STATE_RESULT:
			break
		for foe in ctl.engine.enemies:
			foe.hp = mini(foe.hp, 1)  # force a quick win; the controller never writes combatant state
		var foes := ctl.engine.living_foes_of(ctl.engine.current)
		if foes.is_empty():
			break
		ctl.act(&"attack", [foes[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY, "%s won" % encounter)
	ctl.hud.result.accept()
	_host().remove_child(ctl)
	ctl.free()
	assert_true(bool(Game.get_flag(flag)), "%s sets %s" % [encounter, flag])
	assert_eq(travels.back(), [&"ch04/brightwater_ferry", spawn], "%s returns to the derelict" % encounter)


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as Ch04Zone
	story = zone.story
	story.autostart = false
	_host().add_child(zone)
	zone.set_process(false)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	if zone.encounters != null:
		zone.encounters.set_physics_process(false)
	zone.hint.instant = true
	story.active = true
	story.sequencer.instant = true
	story.overhear.instant = true
	story.sequencer.line_shown.connect(
		func(s: DialogueStep) -> void:
			lines.append(s.line_id)
			restore_at_line[s.line_id] = story.sequencer.restore_fade
	)
	story.hand_off = func(kind: StringName, target: Variant) -> void: hand_offs.append([kind, target])


## Opens the zone again where a hand-off left it (the router would), and runs its arrival.
func _reopen(path: String, spawn: StringName) -> void:
	_close()
	hand_offs.clear()
	_open(path)
	assert_true(zone.place_at(spawn, zone.spawn_yaw_deg(spawn)))
	story.begin()


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		warnings.append_array(story.sequencer.warnings)
		_host().remove_child(zone)
		zone.free()
	zone = null


func _check_staging() -> void:
	for w in warnings:
		for needle in STAGING_WARNINGS:
			assert_false(w.contains(needle), "staged on this zone: %s" % w)


func _trigger(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	fail("no trigger %s" % id)
	return Interactable.new()


func _at(spawn: StringName) -> bool:
	return zone.player.position.distance_to(zone.spawn_marker(spawn).position) < 0.01


func _actor_at(actor: StringName, mark: StringName) -> bool:
	return zone.stage.actor(actor).position.distance_to(zone.stage.mark(mark).position) < 0.01


func _count(item: StringName) -> int:
	return Inventory.new(ItemDB.load_default(), Game.state.inventory).count(item)


func _done() -> void:
	_close()
	BattleRequest.clear()
	BattleRequest.change_scene = Callable()
	var dir := DirAccess.open(SAVE_DIR)
	if dir != null:
		for f in dir.get_files():
			DirAccess.remove_absolute(SAVE_DIR.path_join(f))
		DirAccess.remove_absolute(SAVE_DIR)
	SaveSystem.save_dir = saved_dir
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
