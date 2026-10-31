extends Act2GreyboxCase
## M5-A3P-1004: Ch18 "The Kite" on the real chapter data (chapters/ch18.json and the Act III rows of the towns'
## files), headless: the maiden flight on boarding (K01), the chart table opens the world (K02), Reedhollow's gate,
## the new shell and the farewell-tide (K03-K05), back aboard for the night (K07), a town's revisit and Ansedra from
## the air (§4), and Iskarra (K08).

const KITE := "res://game/levels/ch18/kite/kite.tscn"
const REEDHOLLOW := "res://game/levels/ch10/reedhollow/reedhollow.tscn"
const QUELLAN := "res://game/levels/ch12/quellan/quellan.tscn"
const PEMAKAR := "res://game/levels/ch05/pemakar/pemakar.tscn"
## A save at the end of Ch17 (Act II's end and Hollowmere's).
const CH17_END: Array[StringName] = [
	&"ch15_reached_hollowmere",
	&"ch15_liss_told_father",
	&"ch15_pyre_raft",
	&"ch15_complete",
	&"ch16_act_two_complete",
	&"ch17_started",
	&"ch17_saw_the_hull",
	&"ch17_read_the_ledger",
	&"ch17_chose_the_unbinding",
	&"ch17_first_lamp_lit",
	&"ch17_verse_begun",
	&"ch17_complete",
]


func test_the_kite_opens_the_world() -> void:
	for f: StringName in CH17_END:
		Game.set_flag(f)
	visit(KITE)
	assert_eq(Game.state.chapter, 18, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch18_started")), "K01: the maiden flight")
	assert_false(trigger_named(&"course_reedhollow").is_available(), "no course before the charts")
	assert_true(trigger_named(&"chart").try_interact())
	assert_true(bool(Game.get_flag(&"ch18_world_open")), "K02: the world opens")
	assert_false(trigger_named(&"course_iskarra").is_available(), "Iskarra waits on the night aboard")
	go(&"course_reedhollow", "ch10/reedhollow", "Gate")

	visit(REEDHOLLOW)
	assert_true(bool(Game.get_flag(&"ch18_pell_named")), "K03-K04: through the gate, the new shell")
	assert_true(bool(Game.get_flag(&"ch18_learned_farewell_tide")), "K05: the farewell-tide, taught")
	go(&"a3_to_kite", "ch18/kite", "Deck")

	visit(KITE)
	assert_true(bool(Game.get_flag(&"ch18_night_aboard")), "K07: the night aboard")
	assert_true(trigger_named(&"course_ansedra").try_interact())
	assert_true(bool(Game.get_flag(&"ch18_revisit_ansedra_seen")), "§4: Ansedra from the air")
	go(&"course_pemakar", "ch05/pemakar", "Harbour")

	visit(PEMAKAR)
	assert_true(bool(Game.get_flag(&"ch18_revisit_pemakar_seen")), "§4: Pemakar's revisit")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch18/kite", "spawn": "Deck"}], "back aboard")

	visit(QUELLAN)
	assert_true(bool(Game.get_flag(&"ch18_revisit_quellan_seen")), "§4: Quellan's revisit")
	go(&"a3_to_kite", "ch18/kite", "Deck")

	visit(KITE)
	assert_true(trigger_named(&"course_iskarra").try_interact())
	assert_true(bool(Game.get_flag(&"ch18_complete")), "K08: Iskarra")
	after_visits()
