extends TestCase
## M2-UI-16: the objective tracker over game/data/flow/objectives.json and the zone maps. The
## slice is walked flag by flag (a scratch flag set; Game is never touched) and each step must
## name the objective the beat sheet expects, with a target the map knows.

const HALUNA := &"ch02/haluna"
const SHRINE := &"ch03/shell_shrine"
const UNDERWAY := &"ch01/oruvel_underway"
const ORUVEL := &"ch01/oruvel"
const WAKE := &"ch04/haluna_wake"
const FERRY := &"ch04/brightwater_ferry"
const PEMAKAR := &"ch05/pemakar"
const ASHCROWN := &"ch05/ashcrown"
const TAMSULE := &"ch07/tamsule"
const GALLERIES := &"ch07/tamsule_bell_galleries"
const CORROW := &"ch09/corrow_night"

var flags: Dictionary = {}
var t: ObjectiveTracker


func before_each() -> void:
	flags = {}
	t = ObjectiveTracker.new(func(f: StringName) -> bool: return bool(flags.get(f, false)))


func test_the_slice_steps_name_their_objectives() -> void:
	assert_eq(t.current(HALUNA), {}, "before the beach cutscene nothing calls")
	assert_eq(t.line(HALUNA), tr("OBJ_NONE_HALUNA"), "Haluna's own idle line (idle_keys)")
	assert_eq(t.line(&"ch12/keth_pass"), tr("OBJ_NONE"), "M3-UI-206: elsewhere it never names Haluna")
	assert_false(tr("OBJ_NONE").contains(tr("LOCATION_CH02_HALUNA")))
	var steps := [
		[&"ch02_met_asha", HALUNA, &"up_the_beach"],
		[&"ch02_tideline_won", HALUNA, &"to_nemes"],
		[&"ch02_ate_at_nemes", HALUNA, &"save_at_shrine"],
		[&"ch02_saved_once", HALUNA, &"to_causeway_head"],
	]
	for s: Array in steps:
		flags[s[0]] = true
		assert_eq(StringName(str(t.current(s[1]).get("id", ""))), s[2], "after %s" % s[0])
	assert_eq(StringName(str(t.current(SHRINE).get("id", ""))), &"shrine_trial", "in the shrine: the trial")
	flags[&"ch03_shrine_door_open"] = true
	assert_eq(StringName(str(t.current(SHRINE).get("id", ""))), &"shrine_door")
	assert_eq(t.current(HALUNA), {}, "the causeway head is done once the trial opened the door")
	flags[&"ch03_first_verse_sung"] = true
	flags[&"ch03_drownbell_defeated"] = true
	assert_eq(StringName(str(t.current(HALUNA).get("id", ""))), &"find_asha_on_dock")
	flags[&"ch03_rhen_sworn_guardian"] = true
	assert_eq(t.current(HALUNA), {}, "the slice ends with nothing left to do")


func test_zone_rows_stay_in_their_zone_and_side_rows_list_apart() -> void:
	flags[&"ch02_ate_at_nemes"] = true
	assert_eq(StringName(str(t.current(SHRINE).get("id", ""))), &"shrine_trial", "Haluna's row is not the shrine's")
	var side := t.side(HALUNA)
	assert_eq(side.size(), 1)
	assert_eq(StringName(str(side[0]["id"])), &"side_market_fragments")
	assert_eq(t.current(&""), {}, "a scene with no map gets no zoned objective (test zones, shot scenes)")


func test_every_target_resolves_to_a_map_point_in_bounds() -> void:
	var maps := ZoneMaps.new()
	for row: Dictionary in t.rows:
		assert_ne(tr(str(row["line_key"])), str(row["line_key"]), "%s has its line" % row["id"])
		var target: Dictionary = row.get("target", {})
		if target.is_empty():
			continue
		var at := maps.poi_position(StringName(str(target["zone"])), StringName(str(target["poi"])))
		assert_ne(at, Vector3.INF, "%s points at a known POI" % row["id"])


func test_zone_maps_find_zones_by_scene() -> void:
	var maps := ZoneMaps.new()
	assert_eq(maps.zone_for_scene("res://game/levels/ch02/haluna/haluna.tscn"), HALUNA)
	assert_eq(maps.zone_for_scene("res://nowhere.tscn"), &"")
	assert_eq(
		maps.route().size(),
		33,
		"Act I, the Underway to Corrow (M3-UI-04), then Act II's fifteen (M3-UI-206) and Act III's three (M5-A3P-1015)"
	)
	assert_eq(StringName(str(maps.route()[2]["id"])), HALUNA, "Ch1's two zones come before Haluna")
	assert_eq(maps.poi_position(HALUNA, &"shrine"), Vector3(-67.0, 0.0, 44.3))
	assert_eq(maps.zone_for_scene("res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn"), UNDERWAY)


# --- Act I (M3-UI-04) ----------------------------------------------------------------------------


func _id(zone: StringName) -> StringName:
	return StringName(str(t.current(zone).get("id", "")))


func _poi(zone: StringName) -> StringName:
	return StringName(str(t.target(zone).get("poi", "")))


func test_ch1_walks_the_underway_and_oruvel_beat_by_beat() -> void:
	assert_eq(t.current(UNDERWAY), {}, "before the title card nothing calls")
	var steps := [
		[&"ch01_started", UNDERWAY, &"u_crown_tether", &"crown_tether"],
		[&"ch01_saw_bell_room", UNDERWAY, &"u_bell_tether", &"bell_tether"],
		[&"ch01_wickfry_won", UNDERWAY, &"u_galleries", &"stair_lip"],
		[&"ch01_saw_low_lights", UNDERWAY, &"u_gauge_room", &"gauge_room"],
		[&"ch01_oil_slug_won", UNDERWAY, &"u_gauge_wheel", &"gauge_wheel"],
		[&"ch01_cut_gauge_wheel", UNDERWAY, &"u_current_shaft", &"current_shaft"],
		[&"ch01_underway_done", UNDERWAY, &"", &""],
		[&"ch01_sold_gauge_wheel", ORUVEL, &"o_kell", &"kell"],
		[&"ch01_has_kell_wick", ORUVEL, &"o_dive_mooring", &"dive_mooring"],
		[&"ch01_gulls_cried", ORUVEL, &"o_low_run", &"low_run"],
		[&"ch01_scuttlers_won", ORUVEL, &"o_lashing_west", &"lashing_west"],
		[&"ch01_cut_lashing_a", ORUVEL, &"o_lashing_east", &"lashing_east"],
		[&"ch01_cut_lashing_b", ORUVEL, &"o_net_pen", &"net_pen"],
		[&"ch01_children_safe", ORUVEL, &"o_hold_net_pen", &"net_pen"],
		[&"ch01_hullgnaw_defeated", ORUVEL, &"", &""],
	]
	for s: Array in steps:
		flags[s[0]] = true
		assert_eq(_id(s[1]), s[2], "after %s" % s[0])
		assert_eq(_poi(s[1]), s[3], "after %s: the target" % s[0])
		if s[2] != &"":
			assert_eq(StringName(str(t.target(s[1])["zone"])), s[1], "the target is in the zone it is shown in")
	assert_eq(t.current(UNDERWAY), {}, "the Underway is done once Rhen surfaces")


func test_ch1_side_rows_and_either_lashing_first() -> void:
	flags[&"ch01_started"] = true
	assert_eq(t.side(UNDERWAY).size(), 0, "the hinge waits for the bell-room")
	flags[&"ch01_saw_bell_room"] = true
	assert_eq(StringName(str(t.side(UNDERWAY)[0]["id"])), &"u_side_hinge")
	flags[&"ch01_cut_first_hinge"] = true
	assert_eq(t.side(UNDERWAY).size(), 0, "cut: the errand is gone")
	assert_eq(t.current(ORUVEL), {}, "Underway flags call nothing in Oruvel")
	for f: StringName in [&"ch01_sold_gauge_wheel", &"ch01_has_kell_wick", &"ch01_gulls_cried", &"ch01_scuttlers_won"]:
		flags[f] = true
	flags[&"ch01_cut_lashing_b"] = true
	assert_eq(_poi(ORUVEL), &"lashing_west", "the east lashing cut first: the west one is left")
	flags[&"ch01_cut_lashing_a"] = true
	assert_eq(_id(ORUVEL), &"o_net_pen", "both cut: on to the children")


func test_ch4_to_ch9_spot_checks() -> void:
	var checks := [
		[[&"ch04_started"], WAKE, &"w_neme_table", &"neme_table"],
		[[&"ch04_started", &"ch04_feast_neme"], WAKE, &"w_wall", &"wall"],
		[
			[&"ch04_started", &"ch04_feast_neme", &"ch04_shell_set", &"ch04_dock_comforted"],
			WAKE,
			&"w_sleep",
			&"neme_house"
		],
		[[&"ch04_ysolde_joined"], FERRY, &"f_bow", &"bow"],
		[[&"ch04_ysolde_joined", &"ch04_boarded_derelict", &"ch04_leeches_won"], FERRY, &"f_hold", &"hold"],
		[
			[&"ch04_ysolde_joined", &"ch04_boarded_derelict", &"ch04_leeches_won", &"ch04_hermit_won"],
			FERRY,
			&"f_mainmast",
			&"mainmast"
		],
		[[&"ch05_arrived"], PEMAKAR, &"p_crown_bell", &"crown_bell"],
		[
			[&"ch05_arrived", &"ch05_met_kerrid", &"ch05_kahre_bound", &"ch05_after_seen"],
			PEMAKAR,
			&"p_harbour_road",
			&"harbour"
		],
		# the Lead (10-30): the pilgrim stair is staged, a target per level (its foot is 117 m under the crown)
		[[&"ch05_arrived", &"ch05_met_kerrid"], ASHCROWN, &"a_stair", &"grave_tier"],
		[[&"ch05_passed_grave_tier"], ASHCROWN, &"a_upper", &"copper_tier"],
		[[&"ch05_passed_grave_tier", &"ch05_passed_copper_tier"], ASHCROWN, &"a_crown", &"crown"],
		[[&"ch05_trial_begun"], ASHCROWN, &"a_trial", &"tier_1"],
		[[&"ch05_trial_begun", &"ch05_strike_landed"], ASHCROWN, &"a_anvil_court", &"anvil_court"],
		[[&"ch07_arrived"], TAMSULE, &"t_market_boats", &"market_boats"],
		[[&"ch07_arrived", &"ch07_met_tavi"], TAMSULE, &"t_gantry", &"gantry_foot"],
		[[&"ch07_met_tavi", &"ch07_saw_galleries"], GALLERIES, &"g_rim", &"rim"],
		[[&"ch07_saw_galleries", &"ch07_tidecup_played", &"ch07_tavi_withdrew"], GALLERIES, &"g_to_port", &"to_port"],
		[
			[&"ch07_arrived", &"ch07_met_tavi", &"ch07_saw_galleries", &"ch07_tavi_withdrew"],
			TAMSULE,
			&"t_harbour",
			&"harbour"
		],
		[[&"ch09_started"], CORROW, &"c_landing", &"landing"],
		[[&"ch09_started", &"ch09_ebbing_danced", &"ch09_pell_joined"], CORROW, &"c_road", &"milestone"],
		[[&"ch09_started", &"ch09_ebbing_danced", &"ch09_pell_joined", &"ch09_kerrid_on_road"], CORROW, &"", &""],
	]
	for c: Array in checks:
		flags = {}
		for f: StringName in c[0]:
			flags[f] = true
		assert_eq(_id(c[1]), c[2], "%s with %s" % [c[1], c[0]])
		assert_eq(_poi(c[1]), c[3], "%s with %s: the target" % [c[1], c[0]])


## Act II: every Act II zone's line and map point move along its chapter's main path, beat by beat (act1-chapters'
## rows; each case sets the beats before it in the same zone and the row's own requires).
func test_act_two_zones_point_along_the_main_path() -> void:
	var checks := [
		[[&"ch10_started"], &"ch10/ossa_fen", &"f_drowner", &"clearing"],
		[[&"ch10_drowner_defeated", &"ch10_started"], &"ch10/ossa_fen", &"f_to_reedhollow", &"to_reedhollow"],
		[[&"ch10_reached_reedhollow"], &"ch10/reedhollow", &"r_shore", &"shore"],
		[[&"ch10_farewell_tide_seen", &"ch10_reached_reedhollow"], &"ch10/reedhollow", &"r_gate", &"gate"],
		[[&"ch11_started"], &"ch11/sunken_vey", &"v_to_lowlight", &"to_lowlight"],
		[[&"ch11_reached_lowlight"], &"ch11/lowlight", &"l_down", &"sanctum"],
		[[&"ch11_nhoa_bound", &"ch11_reached_lowlight"], &"ch11/lowlight", &"l_out", &"gate"],
		[[&"ch12_started"], &"ch12/keth_pass", &"k_wall", &"terrace"],
		[[&"ch12_ram_felled", &"ch12_started"], &"ch12/keth_pass", &"k_to_quellan", &"to_quellan"],
		[[&"ch12_reached_quellan"], &"ch12/quellan", &"q_road_up", &"road_up"],
		[[&"ch12_reached_cloudloom"], &"ch12/cloudloom", &"c_dais", &"dais"],
		[[&"ch12_hesk_bound", &"ch12_reached_cloudloom", &"ch12_reached_quellan"], &"ch12/quellan", &"q_inn", &"inn"],
		[
			[&"ch12_hesk_bound", &"ch12_reached_cloudloom", &"ch12_reached_quellan", &"ch12_ysolde_confessed"],
			&"ch12/quellan",
			&"q_on",
			&""
		],
		[[&"ch13_started"], &"ch13/ansedra", &"a_sanctum", &"sanctum"],
		[[&"ch13_entered_sanctum"], &"ch13/sanctum", &"s_ledge", &"ledge"],
		[[&"ch13_ethren_bound", &"ch13_started"], &"ch13/ansedra", &"a_archive", &"archive"],
		[[&"ch13_entered_archive"], &"ch13/lamp_archive", &"la_ledgers", &"ledgers"],
		[[&"ch13_entered_archive", &"ch13_read_ledgers"], &"ch13/lamp_archive", &"la_roll", &"door"],  # E9
		[[&"ch13_archive_read", &"ch13_ethren_bound", &"ch13_started"], &"ch13/ansedra", &"a_moorings", &"moorings"],
		[
			[&"ch13_archive_read", &"ch13_ethren_bound", &"ch13_pact_of_silence", &"ch13_started"],
			&"ch13/ansedra",
			&"a_rest",
			&"sefir"
		],
		[[&"ch14_started"], &"ch13/ansedra_lacquer_court", &"lc_vows", &"dais"],
		[
			[&"ch14_declared_heretics", &"ch14_started", &"ch14_vows_spoken"],
			&"ch13/ansedra_lacquer_court",
			&"lc_steps",
			&"steps"
		],
		[
			[&"ch14_declared_heretics", &"ch14_started", &"ch14_steps_held", &"ch14_vows_spoken"],
			&"ch13/ansedra_lacquer_court",
			&"lc_gate",
			&"water_gate"
		],
		[[&"ch15_started"], &"ch15/open_sea", &"os_drift", &"bow"],
		[[&"ch15_reached_hollowmere"], &"ch17/hollowmere", &"h_father", &"dock"],
		[[&"ch15_liss_told_father", &"ch15_reached_hollowmere"], &"ch17/hollowmere", &"h_pyre", &"pyre_raft"],
		[
			[&"ch15_liss_told_father", &"ch15_pyre_raft", &"ch15_reached_hollowmere"],
			&"ch17/hollowmere",
			&"h_ship",
			&"ship"
		],
		[[&"ch16_started"], &"ch16/pale_rim", &"pr_wade", &"choir_edge"],
		[[&"ch16_reached_choir"], &"ch16/drowned_choir", &"dc_choir", &"head"],
		[[&"ch16_kesh_bound", &"ch16_reached_choir", &"ch16_refused_sefir"], &"ch16/drowned_choir", &"dc_hold", &""],
	]
	for c: Array in checks:
		flags = {}
		for f: StringName in c[0]:
			flags[f] = true
		assert_eq(_id(c[1]), c[2], "%s with %s" % [c[1], c[0]])
		assert_eq(_poi(c[1]), c[3], "%s with %s: the target" % [c[1], c[0]])


func test_act_one_errands_come_and_go() -> void:
	flags = {&"ch04_started": true, &"ch04_feast_neme": true, &"ch04_shell_set": true, &"ch04_dock_comforted": true}
	assert_eq(StringName(str(t.side(WAKE)[0]["id"])), &"w_side_ink", "the lamp at the wall, after the dock")
	flags[&"ch04_saw_ysolde_ink"] = true
	assert_eq(t.side(WAKE).size(), 0)
	flags = {&"ch05_trial_begun": true, &"ch05_quench_alcove_open": true}
	assert_eq(StringName(str(t.side(ASHCROWN)[0]["id"])), &"a_side_quench")
	flags = {&"ch07_tavi_withdrew": true}
	assert_eq(StringName(str(t.side(GALLERIES)[0]["id"])), &"g_side_moorings")
	flags[&"ch07_blessed_moorings"] = true
	assert_eq(t.side(GALLERIES).size(), 0, "the moorings blessed: done")
	assert_eq(_id(GALLERIES), &"g_to_port", "the way back to the port stays")
	flags = {&"ch09_started": true}
	assert_eq(t.side(CORROW).size(), 1, "Toma's vigil; Liss's needs Ch8's hoist")
	flags[&"ch08_hoist_cut_down"] = true
	assert_eq(t.side(CORROW).size(), 2)
	flags[&"ch09_ebbing_danced"] = true
	flags[&"ch09_toma_knelt_with_ivo"] = true
	assert_eq(t.side(CORROW).size(), 0, "after the Ebbing nothing is left on the strand")
