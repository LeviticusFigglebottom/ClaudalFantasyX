extends Act2GreyboxCase
## M5-A3P-1015: Ch21 "The heart" and the Ending on the real chapter data (chapters/ch21.json, chapters/ending.json),
## headless: the Cage's return goes down to the heart; the last layer (H01), the two lamps and Kesh (H02-H03), her
## release and the rest (R1), Sefir's three phases (H04-H07), he lets go and the Great Unbinding (H08-H09); then aboard
## the Kite the three goodbyes (E1-E3) and the landing (E4), which goes to Haluna's dock at night.

const HEART := "res://game/levels/ch21/heart/heart.tscn"
const KITE := "res://game/levels/ch18/kite/kite.tscn"


func test_the_cage_goes_down_to_the_heart() -> void:
	for f in [&"ch20_started", &"ch20_rest_two", &"ch20_cage_broken"]:
		Game.set_flag(f)
	visit("res://game/levels/ch20/undertow_layers/undertow_layers.tscn")
	assert_true(bool(Game.get_flag(&"ch20_complete")), "U08")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch21/heart", "spawn": "LastLayer"}])
	after_visits()


func test_the_heart_plays_in_order() -> void:
	Game.set_flag(&"ch20_complete")
	visit(HEART)
	assert_eq(Game.state.chapter, 21, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch21_started")), "H01: the last layer")
	assert_false(trigger_named(&"the_warden").is_available(), "Sefir waits on Kesh")
	assert_true(trigger_named(&"two_lamps").on_touched())
	_fight(&"ch21_kesh", &"ch21_kesh_beaten", &"ysolde")
	visit(HEART)
	assert_true(bool(Game.get_flag(&"ch21_kesh_released")), "H03: Kesh lifts; R1 follows")
	assert_true(trigger_named(&"choir_stone").is_available(), "R1: the Choir-stone saves")
	assert_true(trigger_named(&"the_warden").on_touched())
	_fight(&"ch21_sefir_warden", &"ch21_warden_beaten", &"kerrid")
	visit(HEART)
	_fight(&"ch21_sefir_heart", &"ch21_heart_beaten", &"kerrid")
	visit(HEART)
	_fight(&"ch21_sefir_letting", &"ch21_letting_sung", &"toma")
	visit(HEART)
	assert_true(bool(Game.get_flag(&"ch21_unbound")), "H09: the Great Unbinding")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch18/kite", "spawn": "Deck"}])
	after_visits()


func test_the_ending_aboard_the_kite() -> void:
	Game.set_flag(&"ch21_unbound")
	visit(KITE)
	assert_true(bool(Game.get_flag(&"ending_imra_gone")), "E1: Imra")
	assert_false(trigger_named(&"course_reedhollow").is_available(), "no courses after the Unbinding")
	assert_false(trigger_named(&"kite_rail").is_available(), "the goodbyes go in order")
	assert_true(trigger_named(&"where_dace_stood").on_touched())
	assert_true(bool(Game.get_flag(&"ending_dace_gone")), "E2: Dace")
	assert_true(trigger_named(&"kite_rail").on_touched())
	assert_true(bool(Game.get_flag(&"ending_kerrid_gone")), "E3: Kerrid")
	assert_true(trigger_named(&"the_wheel").try_interact())
	assert_true(bool(Game.get_flag(&"ending_landed")), "E4: the Kite comes down by hand")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch02/haluna", "spawn": "DockNight"}])
	after_visits()


func _fight(encounter: StringName, flag: StringName, hero: StringName) -> void:
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "%s" % encounter)
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, encounter)
	assert_eq(r.victory_flag, flag)
	assert_eq(r.active[0], hero)
	Game.set_flag(flag)
