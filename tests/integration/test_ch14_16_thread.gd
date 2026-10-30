extends Act2GreyboxCase
## M4-C14-02 .. M4-C16-02: Ch14 "The Peace Wedding", Ch15 "Unlamped" and Ch16 "The Edge of the World" as greybox
## walks, headless, on the real chapter data (chapters/ch14.json .. ch16.json): the Lacquer Court's barge runs the
## escape to the open sea (Ch15), the barge's bow at dawn hands off to Hollowmere, its ship to the Pale Rim (Ch16),
## and the wade to the Drowned Choir. Each arrival sets its chapter. M4-A2P-1012: each sheet's §1 in order.

const COURT := "res://game/levels/ch13/ansedra_lacquer_court/ansedra_lacquer_court.tscn"
const SEA := "res://game/levels/ch15/open_sea/open_sea.tscn"
const HOLLOWMERE := "res://game/levels/ch17/hollowmere/hollowmere.tscn"
const RIM := "res://game/levels/ch16/pale_rim/pale_rim.tscn"
const CHOIR := "res://game/levels/ch16/drowned_choir/drowned_choir.tscn"


func test_the_wedding_court_to_the_choir() -> void:
	visit(COURT)
	assert_eq(Game.state.chapter, 14)
	Game.set_flag(&"ch14_complete")  # the court's story is test_ch13_thread's (the court is a ch13/ zone)
	go(&"barge", "ch15/open_sea", "Deck")
	visit(SEA)
	assert_eq(Game.state.chapter, 15)
	# M4-A2P-1012: the deck at night (B02), the fin at the bow and the Wakefin (B03-B04)
	assert_false(trigger_named(&"dawn").is_available(), "no dawn before the night")
	assert_true(trigger_named(&"deck_liss").try_interact(), "B02: Liss at the bier")
	_battle(&"fin", &"ch15_wakefin", &"ch15_wakefin_felled")
	visit(SEA)
	assert_true(bool(Game.get_flag(&"ch15_kerrid_revealed")), "B06-B08: the shoal and the confession on the return")
	assert_false(trigger_named(&"deck_liss").is_available(), "the night's talk is over")
	go(&"dawn", "ch17/hollowmere", "Dock")
	assert_true(bool(Game.get_flag(&"ch15_hollowmere_answered")), "B09: the current-song")
	assert_true(bool(Game.get_flag(&"ch15_dawn")), "M4-A2P-105: the dawn variant's flag")
	visit(HOLLOWMERE)
	assert_true(bool(Game.get_flag(&"ch15_reached_hollowmere")))
	assert_true(bool(Game.get_flag(&"ch15_liss_told_father")), "B10: the dock-master on arrival")
	assert_false(trigger_named(&"ship").is_available(), "the ship waits on the pyre-raft")
	assert_true(trigger_named(&"shrine").try_interact(), "Hollowmere's shrine")
	assert_true(trigger_named(&"jetty").on_touched())
	assert_true(bool(Game.get_flag(&"ch15_toma_carried_tobin")), "B12: Let me carry him")
	assert_true(bool(Game.get_flag(&"ch15_pyre_raft")), "B13: the pyre-raft")
	go(&"ship", "ch16/pale_rim", "Rim")
	assert_true(bool(Game.get_flag(&"ch15_complete")), "B15: the ship")
	visit(RIM)
	assert_eq(Game.state.chapter, 16)
	go(&"to_choir", "ch16/drowned_choir", "Approach")
	# the ring, Kesh, the memory and the High Warden (B03-B07), then his Abiding guard (B08)
	visit(CHOIR)
	assert_true(bool(Game.get_flag(&"ch16_reached_choir")))
	assert_true(bool(Game.get_flag(&"ch16_refused_sefir")), "B07: the refusal")
	_fought(&"ch16_abiding_guard", &"ch16_guard_beaten")
	visit(CHOIR)
	_fought(&"ch16_storm_wakes", &"ch16_line_held")  # B09: the storm wakes on the return
	visit(CHOIR)
	assert_true(bool(Game.get_flag(&"ch16_act_two_complete")), "B10-B11: swept away")
	after_visits()


## Fires `trigger`, checks the battle it starts and wins it.
func _battle(trigger: StringName, encounter: StringName, victory_flag: StringName) -> void:
	assert_true(trigger_named(trigger).try_interact(), "%s fires" % trigger)
	_fought(encounter, victory_flag)


## Checks the last hand-off is `encounter` with `victory_flag`, and wins it.
func _fought(encounter: StringName, victory_flag: StringName) -> void:
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "%s starts" % encounter)
	if hand_offs.is_empty() or hand_offs.back()[0] != ZoneStory.KIND_BATTLE:
		return
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, encounter)
	assert_eq(r.victory_flag, victory_flag)
	Game.set_flag(victory_flag)
