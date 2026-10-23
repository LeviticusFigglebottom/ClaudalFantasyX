extends TestCase
## M1-ARC-06: party HP/MP and carried statuses between battles. Game.state.party_vitals is
## written back from EventBus.battle_party_returned, restored by a shrine's
## party_full_heal_requested, and read at battle setup through Game.vitals_modifier() (a
## BattleEngine.party_modifier; the engine core is untouched). Rules: party_rest.json.

const SEED := 7
const ENCOUNTER := &"sandbox_reef"

var bdb: BattleDB
var db: ItemDB
var _saved_state: GameStateData


func before_each() -> void:
	bdb = BattleDB.load_default()
	db = ItemDB.load_default()
	_saved_state = Game.state
	Game.state = GameStateData.new()


func _engine(modifier: Callable) -> BattleEngine:
	var e := BattleEngine.new()
	e.party_modifier = modifier
	e.setup(bdb, [&"rhen", &"asha"] as Array[StringName], [&"toma"] as Array[StringName], ENCOUNTER, SEED)
	return e


func _snapshot(e: BattleEngine) -> Array:
	var out := []
	for c in e.party_active + e.party_reserve:
		out.append([c.id, c.hp, c.max_hp, c.mp, c.max_mp, c.statuses.duplicate()])
	return out


func test_rules_come_from_data() -> void:
	var rules := Game.load_rest_rules()
	assert_eq(Game.carried_statuses(), [&"poison", &"petrify", &"zombie"] as Array[StringName])
	assert_eq(Game.shrine_cures(), [&"poison", &"petrify", &"zombie"] as Array[StringName])
	assert_eq(Game.carried_duration(), int(rules["carried_duration"]))
	for sid in Game.shrine_cures():
		assert_true(bdb.statuses.has(sid), "%s is a battle status" % sid)
	_done()


func test_no_saved_vitals_changes_nothing_in_battle() -> void:
	var plain := _snapshot(_engine(Callable()))
	var with_vitals := _snapshot(_engine(Game.vitals_modifier()))
	assert_eq(with_vitals, plain, "an empty party_vitals leaves setup exactly as before")
	_done()


func test_battle_setup_reads_saved_hp_mp_and_statuses() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 150, "mp": 4, "statuses": ["poison"]}, "toma": {"hp": 9999}}
	var e := _engine(Game.vitals_modifier())
	var rhen := e.find(&"rhen")
	assert_eq(rhen.hp, 150)
	assert_eq(rhen.mp, 4)
	assert_eq(rhen.max_hp, 420, "the maximum is untouched")
	assert_eq(rhen.statuses.get(&"poison"), Game.carried_duration())
	assert_eq(e.find(&"toma").hp, e.find(&"toma").max_hp, "clamped to the maximum")
	assert_eq(e.find(&"asha").hp, e.find(&"asha").max_hp, "no entry = full")
	_done()


func test_ko_and_stone_come_back_as_saved() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 0, "statuses": ["poison"]}, "asha": {"statuses": ["petrify"]}}
	var e := _engine(Game.vitals_modifier())
	assert_false(e.find(&"rhen").is_alive())
	assert_true(e.find(&"rhen").statuses.is_empty(), "KO carries no statuses")
	assert_true(e.find(&"asha").is_petrified())
	assert_eq(e.find(&"asha").mp, e.find(&"asha").max_mp, "missing MP = full")
	_done()


func test_vitals_apply_after_gear_raises_the_maximum() -> void:
	var bag := EquipmentBag.new(db)
	bag.grant_starting(&"rhen")
	var harness := bag.add_piece(&"rhen_reefline_harness")
	bag.equip(&"rhen", harness)
	Game.state.party_vitals = {"rhen": {"hp": 455}}
	var fx := EquipmentEffects.new(db, bag)
	var e := _engine(EquipmentEffects.compose([fx.modifier(), Game.vitals_modifier()]))
	assert_eq(e.find(&"rhen").max_hp, 460)
	assert_eq(e.find(&"rhen").hp, 455, "saved HP fits the geared maximum")
	_done()


func test_battle_end_writes_hp_mp_and_only_carried_statuses_back() -> void:
	var e := _engine(Callable())
	var rhen := e.find(&"rhen")
	rhen.hp = 200
	rhen.mp = 10
	rhen.add_status(&"poison", -1)
	rhen.add_status(&"haste", 3)
	var asha := e.find(&"asha")
	asha.add_status(&"zombie", -1)
	e.find(&"toma").hp = 0
	EventBus.battle_party_returned.emit(ENCOUNTER, BattleEngine.OUTCOME_VICTORY, e.party_active + e.party_reserve)
	assert_eq(
		Game.state.vitals_of(&"rhen"), {"hp": 200, "mp": 10, "statuses": ["poison"]}, "haste ends with the battle"
	)
	assert_eq(Game.state.vitals_of(&"asha"), {"statuses": ["zombie"]}, "full HP/MP are not written")
	assert_eq(Game.state.vitals_of(&"toma"), {"hp": 0})
	var again := _engine(Game.vitals_modifier())
	assert_eq(again.find(&"rhen").hp, 200, "the next battle starts where this one ended")
	assert_false(again.find(&"toma").is_alive())
	_done()


func test_a_member_back_at_full_loses_their_entry() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 1}}
	var e := _engine(Callable())
	Game.record_party(ENCOUNTER, BattleEngine.OUTCOME_VICTORY, [e.find(&"rhen"), "not a combatant"])
	assert_false(Game.state.party_vitals.has("rhen"))
	_done()


func test_shrine_heal_fills_hp_mp_and_cures_per_rules() -> void:
	Game.state.party_vitals = {
		"rhen": {"hp": 0},
		"asha": {"mp": 5, "statuses": ["zombie", "poison"]},
		"toma": {"statuses": ["petrify"]},
		"ysolde": {"statuses": ["curse_of_test"]},
	}
	EventBus.party_full_heal_requested.emit(&"test_shrine")
	assert_eq(Game.state.party_vitals, {"ysolde": {"statuses": ["curse_of_test"]}}, "only non-cured statuses stay")
	var e := _engine(Game.vitals_modifier())
	assert_eq(e.find(&"rhen").hp, e.find(&"rhen").max_hp, "KO lifted")
	assert_true(e.find(&"asha").statuses.is_empty())
	assert_eq(e.find(&"asha").mp, e.find(&"asha").max_mp)
	assert_false(e.find(&"toma").is_petrified())
	_done()


func test_heal_reports_who_changed() -> void:
	Game.state.party_vitals = {"toma": {"hp": 3}, "asha": {"hp": 1}}
	assert_eq(Game.heal_party(&"x"), [&"asha", &"toma"] as Array[StringName])
	assert_eq(Game.heal_party(&"x"), [] as Array[StringName], "a second rest changes nothing")
	_done()


func test_vitals_modifier_holds_its_state() -> void:
	var st := GameStateData.new()
	st.party_vitals = {"rhen": {"hp": 77}}
	var mod := Game.vitals_modifier(st)
	Game.state = GameStateData.new()
	st = null
	assert_eq(_engine(mod).find(&"rhen").hp, 77, "the hook keeps the state it was made for")
	_done()


func test_vitals_survive_a_save_round_trip() -> void:
	var saves: Node = (load("res://game/core/save_system.gd") as GDScript).new()
	Game.state.party_vitals = {"asha": {"hp": 12, "statuses": ["poison"]}}
	var back: GameStateData = saves.deserialize(JSON.parse_string(JSON.stringify(saves.serialize(Game.state))))
	assert_eq(_engine(Game.vitals_modifier(back)).find(&"asha").hp, 12)
	saves.free()
	_done()


func _done() -> void:
	Game.state = _saved_state
