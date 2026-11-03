extends TestCase
## M3-CMB-04 (the human's playtest, 2026-11-03): after a won fight the KO'd party members come
## back at 1 HP (Formulas.victory_rise_hp, BattleSpoils.returning_party), on the real data. The
## battle's own combatants are left as they ended, so the XP credit rule still skips the fallen;
## an escape keeps them down. BattleVitals.send_back hands the risen copies to Game.record_party.

const ENCOUNTER := &"sandbox_reef"

var engine: BattleEngine
var _saved_state: GameStateData
var _returned: Array = []


func before_each() -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	engine.setup(BattleDB.load_default(), active, reserve, ENCOUNTER, 1)
	engine.begin()
	_returned = []


func test_a_win_raises_the_fallen_to_one_hp_and_keeps_the_rest() -> void:
	var rhen := engine.party_active[0]
	var asha := engine.party_active[1]
	rhen.hp = 37
	asha.swell = 40
	asha.mp = 9
	asha.apply_damage(asha.max_hp)
	assert_eq(asha.hp, 0)
	engine.outcome = BattleEngine.OUTCOME_VICTORY
	var back := BattleSpoils.returning_party(engine)
	assert_eq(back.size(), 3, "active then reserve")
	assert_eq(back[0], rhen, "the standing go back as they are")
	assert_eq(back[0].hp, 37)
	assert_eq(back[1].id, &"asha")
	assert_eq(back[1].hp, Formulas.VICTORY_RISE_HP)
	assert_eq(back[1].hp, 1)
	assert_eq(back[1].max_hp, asha.max_hp)
	assert_eq(back[1].mp, 9, "MP is kept")
	assert_eq(back[1].swell, 40, "the gauge is kept")
	assert_eq(back[1].swell_mode, asha.swell_mode)
	assert_eq(back[2], engine.party_reserve[0])
	assert_eq(asha.hp, 0, "the battle's own combatant is untouched")
	assert_false(engine.xp_awards().has(&"asha"), "the fallen still earn no XP")
	assert_true(engine.xp_awards().has(&"rhen"))


func test_a_scripted_way_out_counts_as_a_win() -> void:
	engine.party_active[1].apply_damage(9999)
	engine.outcome = BattleEngine.OUTCOME_SCRIPTED_ESCAPE
	assert_eq(BattleSpoils.returning_party(engine)[1].hp, 1)


func test_an_escape_keeps_the_fallen_down() -> void:
	var asha := engine.party_active[1]
	asha.apply_damage(9999)
	engine.outcome = BattleEngine.OUTCOME_ESCAPED
	var back := BattleSpoils.returning_party(engine)
	assert_eq(back[1], asha)
	assert_eq(back[1].hp, 0)


func test_stone_is_not_a_ko_and_stays() -> void:
	var asha := engine.party_active[1]
	asha.hp = 50
	asha.statuses[BattleCombatant.STATUS_PETRIFY] = -1
	engine.outcome = BattleEngine.OUTCOME_VICTORY
	var back := BattleSpoils.returning_party(engine)
	assert_eq(back[1], asha)
	assert_true(back[1].is_petrified())


func test_send_back_saves_the_risen_at_one_hp() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	EventBus.battle_party_returned.connect(_on_returned)
	var asha := engine.party_active[1]
	asha.apply_damage(9999)
	engine.outcome = BattleEngine.OUTCOME_VICTORY
	assert_true(BattleVitals.send_back(engine))
	var entry: Dictionary = Game.state.vitals_of(&"asha")
	EventBus.battle_party_returned.disconnect(_on_returned)
	SaveSystem.cancel_pending_autosave()
	Game.state = _saved_state
	assert_eq(_returned.size(), 3)
	assert_eq((_returned[1] as BattleCombatant).hp, 1)
	assert_eq(int(entry.get("hp", -1)), 1, "saved standing at 1 HP: %s" % entry)


func _on_returned(_encounter: StringName, _outcome: StringName, party: Array) -> void:
	_returned = party
