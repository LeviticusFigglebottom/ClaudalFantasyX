extends TestCase
## M2-MNU-07: the formation saved on the field menu's Formation page is the one the next live
## battle starts with. BattleRequest.make reads Game.state.party_ids / reserve_ids once the party
## has gathered (Haluna's tideline fight, ZoneStory's random and story fights), and FieldBattle
## builds the engine's active line and reserve from the request, in that order. Before anyone has
## joined, the data file's party stands in, as before. Scene changes are recorded, never performed.

const FIELD_SCENE := "res://game/flow/field_battle.tscn"
const ENCOUNTER := &"ch02_tideline"
const LOCATION := &"ch02/haluna"
const SPAWN := &"Beach"

var swaps: Array[String] = []
var ctl: FieldBattle
var _saved_state: GameStateData


func before_each() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	ctl = null
	BattleRequest.clear()
	BattleRequest.change_scene = func(path: String) -> void: swaps.append(path)


func _done() -> void:
	if ctl != null and is_instance_valid(ctl):
		if ctl.get_parent() != null:
			ctl.get_parent().remove_child(ctl)
		ctl.free()
	ctl = null
	BattleRequest.clear()
	BattleRequest.change_scene = Callable()
	Game.state = _saved_state


func test_a_request_takes_the_saved_formation() -> void:
	var stand_in := BattleRequest.make(ENCOUNTER, LOCATION, SPAWN)
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_FIELD_BATTLE)
	assert_eq(stand_in.active, FirstPlayableConfig.ids(cfg.get("active", [])), "nobody joined: the data file's party")
	Game.state.party_ids = [&"rhen", &"asha"] as Array[StringName]
	Game.state.reserve_ids = [&"toma"] as Array[StringName]
	var m := FormationMenuModel.new(PartySheet.new(Game.state, PartyGoods.joined_members(Game.state)))
	assert_true(bool(m.move(FormationMenuModel.LINE_RESERVE, 0, FormationMenuModel.LINE_ACTIVE, 0)["ok"]))
	var r := BattleRequest.make(ENCOUNTER, LOCATION, SPAWN)
	assert_eq(r.active, [&"toma", &"asha"] as Array[StringName], "the formation's active line, in order")
	assert_eq(r.reserve, [&"rhen"] as Array[StringName])
	r.active.append(&"ysolde")
	assert_eq(Game.state.party_ids.size(), 2, "a request copies the line, never shares it")
	_done()


func test_the_live_battle_starts_with_the_formation() -> void:
	Game.state.party_ids = [&"rhen", &"asha"] as Array[StringName]
	Game.state.reserve_ids = [&"toma"] as Array[StringName]
	var m := FormationMenuModel.new(PartySheet.new(Game.state, PartyGoods.joined_members(Game.state)))
	m.move(FormationMenuModel.LINE_ACTIVE, 1, FormationMenuModel.LINE_RESERVE, 0)
	m.move(FormationMenuModel.LINE_ACTIVE, 0, FormationMenuModel.LINE_ACTIVE, 1)
	assert_eq(Game.state.party_ids, [&"toma", &"rhen"] as Array[StringName])
	BattleRequest.start(ENCOUNTER, LOCATION, SPAWN)
	ctl = (load(FIELD_SCENE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_sandbox()
	assert_eq(_ids(ctl.engine.party_active), [&"toma", &"rhen"] as Array[StringName], "the active line")
	assert_eq(_ids(ctl.engine.party_reserve), [&"asha"] as Array[StringName], "the reserve")
	_done()


func _ids(list: Array[BattleCombatant]) -> Array[StringName]:
	var out: Array[StringName] = []
	for c in list:
		out.append(c.id)
	return out
