extends TestCase
## M2-FP-03: BattleRequest and the FieldBattle hand-off and return, on the real field_battle.tscn
## (an inherited battle sandbox) and the real ch02_tideline encounter. Scene changes and travel
## are recorded, never performed; Game.state is a fresh state per test.

const FIELD_SCENE := "res://game/flow/field_battle.tscn"
const ENCOUNTER := &"ch02_tideline"
const LOCATION := &"ch02/haluna"
const SPAWN := &"Beach"
const FLAG := &"test_flag"
## More player turns than any of these fights take; a test that needs more is stuck.
const MAX_TURNS := 200

var swaps: Array[String] = []
var travels: Array[Array] = []
var ctl: FieldBattle
var _saved_state: GameStateData


func before_each() -> void:
	_saved_state = Game.state
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


func _make_battle() -> FieldBattle:
	ctl = (load(FIELD_SCENE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.travel = func(loc: StringName, spawn: StringName) -> bool:
		travels.append([loc, spawn])
		return true
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


func test_without_a_request_it_is_the_sandbox() -> void:
	_make_battle()
	ctl.persist_progress = false
	ctl.start_sandbox()
	assert_eq(ctl.engine.encounter_id, &"sandbox_reef")
	assert_eq(ctl.request, null)
	assert_false(ctl.return_to_field(), "nothing to return to")
	assert_eq(travels, [] as Array[Array])
	_done()


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
