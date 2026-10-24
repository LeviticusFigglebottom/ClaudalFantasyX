extends TestCase
## M2-UI-05: BattleVowbound.preview_call and preview_dismiss, the orders the HUD shows before a call
## and a dismissal (pillar 4). Each must match the order the engine really has after the action,
## and change nothing.

const REEF := &"sandbox_reef"
const ILUN := &"ilun"

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	engine.setup(
		BattleDB.load_default(), [&"rhen", &"asha"] as Array[StringName], [&"toma"] as Array[StringName], REEF, 7
	)
	engine.vowbound = BattleVowbound.new(BattleVowbound.load_config(), [ILUN] as Array[StringName])
	engine.begin()
	_turn_of(&"asha")


func test_the_call_preview_is_the_order_after_the_call() -> void:
	var before := _ids(engine.preview())
	var now := engine.now
	var predicted := engine.vowbound.preview_call(engine, ILUN)
	assert_eq(_ids(engine.preview()), before, "the preview changes nothing")
	assert_eq(engine.now, now)
	assert_false(engine.vowbound.is_out())
	assert_eq(predicted[0].combatant_id, ILUN, "Ilun takes this very turn")
	assert_false(_ids(predicted).has(&"asha"), "the party is off the order")
	assert_false(_ids(predicted).has(&"rhen"))
	assert_true(engine.summon(ILUN))
	assert_eq(_ids(predicted), _ids(engine.preview()))
	assert_eq(_times(predicted), _times(engine.preview()))


func test_the_dismiss_preview_is_the_order_after_the_dismissal() -> void:
	assert_true(engine.summon(ILUN))
	var predicted := engine.vowbound.preview_dismiss(engine)
	assert_true(engine.vowbound.is_out(), "the preview changes nothing")
	assert_false(predicted.is_empty())
	assert_false(_ids(predicted).has(ILUN), "Ilun is gone from the order")
	assert_true(_ids(predicted).has(&"asha"), "the caller is back")
	assert_true(engine.dismiss())
	assert_eq(_ids(predicted), _ids(engine.preview()))
	assert_eq(_times(predicted), _times(engine.preview()))


func test_the_caller_waits_her_call_delay_in_the_dismiss_preview() -> void:
	var asha := engine.find(&"asha")
	var rank := int(engine.vowbound.rows[ILUN]["call_rank"])
	var wait := Formulas.action_delay(asha.agility, rank, asha.speed_mult())
	var called_at := engine.now
	assert_true(engine.summon(ILUN))
	var predicted := engine.vowbound.preview_dismiss(engine)
	for e in predicted:
		if e.combatant_id == &"asha":
			assert_eq(e.time, called_at + wait, "Asha acts her rank-%d delay after the call" % rank)
			return
	fail("Asha is on the preview")


func test_a_refused_call_or_dismissal_previews_nothing() -> void:
	assert_true(engine.vowbound.preview_dismiss(engine).is_empty(), "nobody is out")
	engine.find(&"asha").add_status(&"silence", 3)
	assert_true(engine.vowbound.preview_call(engine, ILUN).is_empty(), "a Silenced caller cannot call")
	assert_true(engine.vowbound.preview_call(engine, &"nobody").is_empty())


func test_a_second_call_previews_the_vowbound_as_it_left() -> void:
	assert_true(engine.summon(ILUN))
	var ilun := engine.vowbound.summon
	ilun.add_status(&"haste", 9)
	assert_true(engine.dismiss())
	for cid: StringName in [&"rhen", &"asha"]:
		var c := engine.find(cid)
		c.max_hp = 9999  # the party must live to Asha's next turn whatever the seed's foes roll
		c.hp = 9999
	_turn_of(&"asha")
	var predicted := engine.vowbound.preview_call(engine, ILUN)
	assert_true(engine.summon(ILUN))
	assert_eq(engine.vowbound.summon, ilun, "the same Ilun comes back")
	assert_eq(_times(predicted), _times(engine.preview()), "his Haste is in the preview")


func _turn_of(cid: StringName) -> void:
	var guard := 0
	while engine.outcome == &"" and engine.current.id != cid and guard < 50:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"attack", [engine.living_foes_of(engine.current)[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()


static func _ids(entries: Array[TurnEntry]) -> Array[StringName]:
	var out: Array[StringName] = []
	for e in entries:
		out.append(e.combatant_id)
	return out


static func _times(entries: Array[TurnEntry]) -> Array[int]:
	var out: Array[int] = []
	for e in entries:
		out.append(e.time)
	return out
