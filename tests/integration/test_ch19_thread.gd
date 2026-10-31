extends Act2GreyboxCase
## M5-A3P-1007: Ch19 "Iskarra" on the real chapter data (chapters/ch19.json), headless: the Kite comes down and the
## vigil (I01-I02), the hitch (I03) opens the spire's gate, the words (I04), the four tiers (I06), the signatures and
## the Wardens (I07-I08), the engine stops on the return to the crown (I09-I10).

const SPIRE := "res://game/levels/ch19/iskarra_spire/iskarra_spire.tscn"


func test_iskarra_plays_in_order() -> void:
	Game.set_flag(&"ch18_complete")
	visit(SPIRE)
	assert_eq(Game.state.chapter, 19, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch19_started")), "I01: the Kite comes down")
	assert_true(bool(Game.get_flag(&"ch19_vigil")), "I02: the vigil")
	assert_true((zone as Ch19Zone).block_shown("SpireGate"), "the spire waits on the night")
	assert_true(trigger_named(&"hitch").try_interact())
	assert_true(bool(Game.get_flag(&"ch19_learned_the_hitch")), "I03: the hitch")
	assert_false((zone as Ch19Zone).block_shown("SpireGate"), "the gate opens")
	assert_true(trigger_named(&"words").try_interact())
	assert_true(bool(Game.get_flag(&"ch19_words_whole")), "I04: the words")
	assert_false(trigger_named(&"signatures").is_available(), "the antechamber waits on the climb")
	for n in range(1, 5):
		assert_true(trigger_named(StringName("tier_%d" % n)).on_touched())
		assert_true(bool(Game.get_flag(StringName("ch19_spire_tier_%d" % n))), "I06: tier %d" % n)
	assert_true(trigger_named(&"signatures").on_touched())
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "I08: the Wardens")
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, &"ch19_abiding_wardens")
	assert_eq(r.victory_flag, &"ch19_abiding_beaten")
	Game.set_flag(&"ch19_abiding_beaten")
	visit(SPIRE)
	assert_true(bool(Game.get_flag(&"ch19_engine_stopped")), "I09: the engine stops")
	assert_true(bool(Game.get_flag(&"ch19_complete")), "I10")
	after_visits()
