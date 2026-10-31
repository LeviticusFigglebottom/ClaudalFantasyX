extends Act2GreyboxCase
## M5-A3P-1001: Ch17 "Hollowmere" on the real chapter data (chapters/ch17.json), headless: once Act II is over the
## zone reads Ch17's file (Ch17Zone's chapter_path), not Ch15's. Pulled from the sea on arrival (B01); the gangway's
## dock-master (B03); aboard by the ladder; the hatch: the ledger and dusk (B05-B06); night: the choice, the first
## lamp, Ysolde's table (B08, B10, B11); boarding the hull closes the chapter (B12).

const HOLLOWMERE := "res://game/levels/ch17/hollowmere/hollowmere.tscn"
## Ch15's Hollowmere (the zone's objectives) and Act II's end, as a save carries them into Ch17.
const ACT_TWO_END: Array[StringName] = [
	&"ch15_reached_hollowmere", &"ch15_liss_told_father", &"ch15_pyre_raft", &"ch15_complete", &"ch16_act_two_complete"
]


func test_ch15s_visit_keeps_ch15s_story() -> void:
	visit(HOLLOWMERE)
	assert_eq(story.cfg.get("beats", {}).has("jetty"), true, "Ch15's beats before Act II ends")
	assert_false(trigger_named(&"a3_berths").is_available(), "and none of Ch17's triggers")
	assert_false((zone as Ch17Zone).block_shown("Gangway"), "no gangway before Ch17")
	after_visits()


func test_ch17_plays_hollowmere_in_order() -> void:
	for f: StringName in ACT_TWO_END:  # a save at the end of Act II
		Game.set_flag(f)
	visit(HOLLOWMERE)
	assert_eq(Game.state.chapter, 17, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch17_started")), "B01: pulled from the sea")
	assert_false(trigger_named(&"ship").is_available(), "Ch15's ship is gone")
	assert_true((zone as Ch17Zone).block_shown("Gangway"), "the gangway to the berths")
	assert_true(trigger_named(&"a3_berths").on_touched())
	assert_true(bool(Game.get_flag(&"ch17_saw_the_hull")), "B03: the dock-master points")
	assert_true(trigger_named(&"a3_hull_sails").try_interact(), "B04: the sails")
	assert_true(trigger_named(&"a3_board").try_interact())
	assert_true(zone.player.position.distance_to(zone.spawn_marker(&"HullDeck").position) < 0.01, "aboard")
	assert_false(trigger_named(&"a3_night").is_available(), "the night waits on the ledger")
	assert_true(trigger_named(&"a3_hatch").try_interact())
	assert_true(bool(Game.get_flag(&"ch17_read_the_ledger")), "B05: the ledger")
	assert_true(trigger_named(&"a3_first_berth").is_available(), "B07: Tobin's post, at dusk")
	assert_true(trigger_named(&"a3_night").try_interact())
	for f: StringName in [&"ch17_chose_the_unbinding", &"ch17_first_lamp_lit", &"ch17_verse_begun"]:
		assert_true(bool(Game.get_flag(f)), "B08-B11: %s" % f)
	assert_true(trigger_named(&"a3_aboard").try_interact())
	assert_true(bool(Game.get_flag(&"ch17_complete")), "B12: aboard the hull")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch18/kite", "spawn": "Deck"}], "on to Ch18")
	after_visits()
