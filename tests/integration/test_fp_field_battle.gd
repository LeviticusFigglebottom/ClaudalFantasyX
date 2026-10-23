extends TestCase
## M2-FP-03: BattleRequest and the FieldBattle hand-off and return, on the real field_battle.tscn
## (an inherited battle sandbox) and the real ch02_tideline encounter. Scene changes and travel
## are recorded, never performed; Game.state is a fresh state per test.
## M2-FP-05: a defeat offers Fight again and Return to last save (the newest readable record, read
## from a fixture save dir here; the title when there is none), and never returns to the field; an
## escape returns to the request's escape spawn.

const FIELD_SCENE := "res://game/flow/field_battle.tscn"
const ENCOUNTER := &"ch02_tideline"
const LOCATION := &"ch02/haluna"
const SPAWN := &"Beach"
const FLAG := &"test_flag"
const ESCAPE_SPAWN := &"BeforeBattle"
const SAVE_DIR := "user://test_fp_field_battle_saves"
const TITLE_SCENE := "res://game/core/boot.tscn"
const SAVED_LOCATION := &"ch02/haluna"
const SAVED_SPAWN := &"Shrine"
## More player turns than any of these fights take; a test that needs more is stuck.
const MAX_TURNS := 200

var swaps: Array[String] = []
var travels: Array[Array] = []
var titles: Array[String] = []
var ctl: FieldBattle
var _saved_state: GameStateData
var _saved_dir := ""
var _saved_clock := false


func before_each() -> void:
	_saved_state = Game.state
	_saved_clock = Game.play_clock_running
	_saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = SAVE_DIR
	_clear_saves()
	Game.state = GameStateData.new()
	BattleRequest.clear()
	BattleRequest.change_scene = func(path: String) -> void: swaps.append(path)


func _done() -> void:
	if ctl != null and is_instance_valid(ctl):
		if ctl.get_parent() != null:
			ctl.get_parent().remove_child(ctl)
		ctl.free()
	BattleRequest.clear()
	BattleRequest.change_scene = Callable()
	Game.state = _saved_state
	Game.play_clock_running = _saved_clock
	_clear_saves()
	SaveSystem.save_dir = _saved_dir


func _make_battle() -> FieldBattle:
	ctl = (load(FIELD_SCENE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.travel = func(loc: StringName, spawn: StringName) -> bool:
		travels.append([loc, spawn])
		return true
	ctl.open_title = func(path: String) -> void: titles.append(path)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	return ctl


func _start_requested() -> BattleRequest:
	var r := BattleRequest.start(ENCOUNTER, LOCATION, SPAWN, FLAG)
	_make_battle()
	ctl.start_sandbox()
	return r


func test_request_records_opens_the_field_battle_and_clears() -> void:
	var r := BattleRequest.start(ENCOUNTER, LOCATION, SPAWN, FLAG)
	assert_eq(BattleRequest.pending(), r)
	assert_eq(swaps, [FIELD_SCENE] as Array[String], "start() opens the field battle scene")
	assert_eq(r.encounter, ENCOUNTER)
	assert_eq(r.active, [&"rhen", &"asha"] as Array[StringName], "the data file's active party")
	assert_eq(r.reserve, [&"toma"] as Array[StringName])
	assert_eq(r.return_location, LOCATION)
	assert_eq(r.return_spawn, SPAWN)
	assert_eq(r.victory_flag, FLAG)
	assert_eq(BattleRequest.take(), r)
	assert_eq(BattleRequest.pending(), null, "take() forgets it")
	BattleRequest.start(ENCOUNTER, LOCATION, SPAWN)
	BattleRequest.clear()
	assert_eq(BattleRequest.pending(), null)
	_done()


func test_the_tideline_encounter_exists() -> void:
	var db := BattleDB.load_default()
	assert_true(db.encounters.has(ENCOUNTER))
	_done()


func test_field_battle_starts_the_pending_request_live() -> void:
	_start_requested()
	assert_eq(ctl.engine.encounter_id, ENCOUNTER)
	assert_eq(_ids(ctl.engine.party_active), [&"rhen", &"asha"] as Array[StringName])
	assert_eq(_ids(ctl.engine.party_reserve), [&"toma"] as Array[StringName])
	assert_eq(BattleRequest.pending(), null, "the battle took the request")
	assert_true(ctl.persist_progress, "a field battle is live (carried vitals)")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	_done()


func test_victory_sets_the_flag_and_travels_back() -> void:
	_start_requested()
	for foe in ctl.engine.enemies:
		foe.hp = 1  # the test forces a quick win; the controller never writes combatant state
	_play(func() -> void: ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id]))
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(ctl.hud.result.current_choice(), BattleController.CHOICE_RETURN, "a story win offers Return")
	ctl.hud.result.move_cursor(1)
	assert_eq(ctl.hud.result.current_choice(), BattleController.CHOICE_RETURN, "and only Return")
	assert_false(bool(Game.get_flag(FLAG)), "not before Return")
	ctl.hud.result.accept()
	assert_true(bool(Game.get_flag(FLAG)), "the victory flag is set")
	assert_eq(travels, [[LOCATION, SPAWN]] as Array[Array], "back to the requesting location and spawn")
	assert_false(ctl.return_to_field(), "only once")
	assert_eq(travels.size(), 1)
	_done()


func test_escape_travels_back_without_the_flag() -> void:
	_start_requested()
	_play(func() -> void: ctl.try_escape())
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_ESCAPED)
	assert_eq(ctl.hud.result.current_choice(), BattleController.CHOICE_RETURN)
	ctl.hud.result.accept()
	assert_false(bool(Game.get_flag(FLAG)), "an escape never sets the victory flag")
	assert_eq(travels, [[LOCATION, SPAWN]] as Array[Array])
	_done()


func test_escape_returns_to_the_escape_spawn() -> void:
	var r := BattleRequest.start(ENCOUNTER, LOCATION, SPAWN, FLAG, ESCAPE_SPAWN)
	assert_eq(r.escape_spawn, ESCAPE_SPAWN)
	_make_battle()
	ctl.start_sandbox()
	_play(func() -> void: ctl.try_escape())
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_ESCAPED)
	ctl.hud.result.accept()
	assert_eq(travels, [[LOCATION, ESCAPE_SPAWN]] as Array[Array], "fled back to the near side of the trigger")
	assert_false(bool(Game.get_flag(FLAG)))
	_done()


func test_the_haluna_story_asks_for_the_beach_side_on_escape() -> void:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA)
	assert_eq(str(cfg.get("battle_escape_spawn", "")), String(ESCAPE_SPAWN))
	_done()


func test_defeat_offers_fight_again_and_last_save_never_the_field() -> void:
	_start_requested()
	_lose()
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_DEFEAT)
	assert_eq(ctl.hud.result.current_choice(), BattleController.CHOICE_RETRY, "Fight again first")
	ctl.hud.result.move_cursor(1)
	assert_eq(ctl.hud.result.current_choice(), FieldBattle.CHOICE_LAST_SAVE, "then Return to last save")
	assert_false(ctl.has_last_save(), "no record yet: the row reads Return to title")
	assert_false(ctl.return_to_field(), "a defeat never returns to the field")
	assert_eq(travels, [] as Array[Array])
	assert_false(bool(Game.get_flag(FLAG)))
	# Fight again: the same fight starts over.
	ctl.hud.result.move_cursor(-1)
	ctl.hud.result.accept()
	assert_eq(ctl.state, BattleController.STATE_COMMAND, "Fight again restarts the fight")
	assert_eq(ctl.engine.encounter_id, ENCOUNTER)
	assert_eq(travels, [] as Array[Array])
	assert_eq(titles, [] as Array[String])
	_done()


func test_defeat_returns_to_the_last_save() -> void:
	var saved := GameStateData.new()
	saved.location_id = SAVED_LOCATION
	saved.respawn_location_id = SAVED_LOCATION
	saved.respawn_spawn = SAVED_SPAWN
	saved.chapter = 2
	assert_eq(SaveSystem.save_to_slot(1, saved), OK, "fixture save written")
	_start_requested()
	_lose()
	assert_true(ctl.has_last_save())
	ctl.hud.result.move_cursor(1)
	assert_eq(ctl.hud.result.current_choice(), FieldBattle.CHOICE_LAST_SAVE)
	ctl.hud.result.accept()
	assert_eq(Game.state.chapter, 2, "the newest record is Game.state")
	assert_eq(Game.state.location_id, SAVED_LOCATION)
	assert_eq(travels, [[SAVED_LOCATION, SAVED_SPAWN]] as Array[Array], "back where the record continues")
	assert_eq(titles, [] as Array[String])
	assert_eq(ctl.return_to_last_save(), ERR_UNAVAILABLE, "only once")
	assert_eq(travels.size(), 1)
	_done()


func test_defeat_without_a_save_goes_to_the_title() -> void:
	_start_requested()
	_lose()
	ctl.hud.result.move_cursor(1)
	ctl.hud.result.accept()
	assert_eq(titles, [TITLE_SCENE] as Array[String], "no record: the title")
	assert_eq(travels, [] as Array[Array], "never the field")
	assert_false(bool(Game.get_flag(FLAG)))
	_done()


func test_last_save_is_only_for_a_defeat() -> void:
	_start_requested()
	_play(func() -> void: ctl.try_escape())
	assert_eq(ctl.return_to_last_save(), ERR_UNAVAILABLE)
	assert_eq(titles, [] as Array[String])
	_done()


func test_without_a_request_it_is_the_sandbox() -> void:
	_make_battle()
	ctl.persist_progress = false
	ctl.start_sandbox()
	assert_eq(ctl.engine.encounter_id, &"sandbox_reef")
	assert_eq(ctl.request, null)
	assert_false(ctl.return_to_field(), "nothing to return to")
	assert_eq(travels, [] as Array[Array])
	_done()


## Plays to a defeat: the whole party at 1 HP attacks until the foes have struck everyone down.
func _lose() -> void:
	for c in ctl.engine.party_active + ctl.engine.party_reserve:
		c.hp = 1  # the test forces a quick loss; the controller never writes combatant state
	_play(func() -> void: ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id]))


func _clear_saves() -> void:
	var dir := DirAccess.open(SAVE_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(SAVE_DIR.path_join(f))
	DirAccess.remove_absolute(SAVE_DIR)


## Takes `party_turn` on every party turn until the result panel is up (pacing 0 runs the
## enemy turns in between synchronously).
func _play(party_turn: Callable) -> void:
	for _i in MAX_TURNS:
		if ctl.state == BattleController.STATE_RESULT:
			return
		if not ctl.engine.is_party_turn():
			fail("stuck off a party turn in state %s" % ctl.state)
			return
		party_turn.call()
	fail("no result after %d party turns" % MAX_TURNS)


static func _ids(list: Array[BattleCombatant]) -> Array[StringName]:
	var out: Array[StringName] = []
	for c in list:
		out.append(c.id)
	return out
