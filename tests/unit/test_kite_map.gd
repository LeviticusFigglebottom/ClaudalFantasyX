extends TestCase
## The Kite's world map (KiteMapModel, KiteMapMenu; M3-UI-205, SPEC §6.6): places show once their flag is set,
## the one the party stands in is Here and can't be chosen, choosing asks first and Fly goes (recorded here, not
## made), a grounded Kite flies nowhere, and searching a chart square finds a secret place, which joins the list.
## The runner runs no frames and has no after_each.

const ZONE := "res://game/levels/_tests/save_shrine/save_shrine_test.tscn"
const TABLE := {
	"open_flag": "kite_flying",
	"columns": ["A", "B", "C"],
	"rows": 2,
	"regions":
	[
		{"id": "reach", "name_key": "KITE_REGION_LOW_REACHES", "at": [0.2, 0.7]},
		{"id": "fen", "name_key": "KITE_REGION_OSSA_FEN", "at": [0.8, 0.2]},
	],
	"destinations":
	[
		{
			"id": "isle",
			"region": "reach",
			"location_id": "isle",
			"spawn": "Lane",
			"requires_flag": "",
			"at": [0.1, 0.9]
		},
		{
			"id": "shoals",
			"region": "fen",
			"location_id": "shoals",
			"spawn": "Lane",
			"requires_flag": "ch06_arrived",
			"at": [0.9, 0.1]
		},
	],
	"secrets":
	[
		{
			"id": "cove",
			"region": "fen",
			"location_id": "shoals",
			"spawn": "Lane",
			"found_flag": "kite_test_cove",
			"cell": "B2",
			"name_key": "KITE_REGION_HOLLOWMERE",
			"at": [0.5, 0.8]
		}
	],
}

var flags: Dictionary = {}
var trips: Array = []
var host: Node
var _saved_registry: LocationRegistry


func before_each() -> void:
	flags = {&"kite_flying": true, &"ch06_arrived": true}
	trips = []
	UiSettings.set_shared(UiSettings.new())
	_saved_registry = ShrineNetwork.registry
	ShrineNetwork.registry = (
		LocationRegistry
		. from_dict(
			{
				"default_location": "isle",
				"locations":
				[
					{"id": "isle", "scene": ZONE, "spawn": "Lane", "name_key": "LOCATION_FIELD_TEST"},
					{"id": "shoals", "scene": ZONE, "spawn": "Lane", "name_key": "LOCATION_CH06_BRINE_SHOALS"},
				],
				"shrines": [],
			}
		)
	)
	host = Node.new()
	ParityHost.scene_root().add_child(host)


func test_places_show_by_flag_with_region_and_square() -> void:
	var m := _model()
	assert_eq(m.ids(), [&"isle", &"shoals"] as Array[StringName])
	flags.erase(&"ch06_arrived")
	assert_eq(m.ids(), [&"isle"] as Array[StringName], "a place shows once its flag is set")
	flags[&"ch06_arrived"] = true
	assert_eq(m.place_name(&"shoals"), tr("LOCATION_CH06_BRINE_SHOALS"), "by its location's name")
	assert_eq(m.region_name(&"shoals"), tr("KITE_REGION_OSSA_FEN"))
	assert_eq(m.cell_of(&"shoals"), "C1")
	assert_eq(m.cell_of(&"isle"), "A2")
	_done()


func test_flying_goes_except_here_or_grounded() -> void:
	var m := _model()
	m.here = &"isle"
	assert_true(m.is_here(&"isle"))
	assert_false(m.fly(&"isle"), "not where it stands")
	assert_true(m.fly(&"shoals"))
	assert_eq(trips, [[&"shoals", &"Lane"]])
	flags.erase(&"kite_flying")
	assert_false(m.fly(&"shoals"), "a grounded Kite flies nowhere")
	assert_eq(trips.size(), 1)
	_done()


func test_searching_a_square_finds_a_secret_once() -> void:
	var m := _model()
	assert_eq(m.search("A1"), {}, "open water")
	var found := m.search("B2")
	assert_eq(str(found["id"]), "cove")
	assert_true(bool(flags[&"kite_test_cove"]), "found: its flag is set")
	assert_true(m.ids().has(&"cove"), "and it is a destination now")
	assert_eq(m.place_name(&"cove"), tr("KITE_REGION_HOLLOWMERE"), "by its own name")
	_done()


func test_the_menu_asks_first_then_flies_and_marks_here() -> void:
	var m := _model()
	m.here = &"isle"
	var menu := KiteMapMenu.open_in(host, m)
	var rows := menu.rows_page().rows
	assert_eq(str(rows[0]["right"]), tr("KITE_HERE"))
	assert_false(bool(rows[0]["enabled"]), "here: not chosen")
	assert_eq(StringName(str(rows[-3]["id"])), KiteMapMenu.ROW_SEARCH)
	assert_eq(StringName(str(rows[-2]["id"])), KiteMapMenu.ROW_LOG)
	assert_eq(StringName(str(rows[-1]["id"])), KiteMapMenu.ROW_LEAVE)
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), &"shoals", "the cursor skips Here")
	assert_true(menu.desc_text().contains(tr("KITE_REGION_OSSA_FEN")), "the line names the region")
	assert_true(menu.desc_text().contains("C1"), "and the square")
	menu.accept()
	assert_eq(menu.level, KiteMapMenu.Level.CONFIRM)
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), KiteMapMenu.ROW_STAY, "Stay under the cursor")
	menu.handle_input(_ev(&"ui_down"))
	menu.accept()
	assert_eq(trips, [[&"shoals", &"Lane"]], "Fly goes")
	assert_false(menu.is_open())
	_close(menu)
	_done()


func test_the_menu_searches_a_square_and_lists_what_it_finds() -> void:
	var menu := KiteMapMenu.open_in(host, _model())
	menu.rows_page().set_cursor(menu.rows_page().rows.size() - 3, false)
	menu.accept()
	assert_eq(menu.level, KiteMapMenu.Level.SEARCH)
	menu.handle_input(_ev(&"ui_right"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.cell_name(), "B2")
	assert_eq(menu.chart().search_cell, Vector2i(1, 1), "the chart outlines it")
	assert_true(menu.desc_text().contains("B2"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, KiteMapMenu.Level.LIST)
	assert_true(menu.desc_text().contains(tr("KITE_REGION_HOLLOWMERE")), "found, by name")
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), &"cove", "the cursor goes to it")
	menu.rows_page().set_cursor(menu.rows_page().rows.size() - 3, false)
	menu.accept()
	menu.handle_input(_ev(&"ui_left"))
	menu.handle_input(_ev(&"ui_left"))
	assert_eq(menu.cell_name(), "C2", "the column wraps (B, A, then C)")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, KiteMapMenu.Level.LIST, "Cancel backs out of the search")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_open(), "and Cancel on the list leaves")
	_close(menu)
	_done()


## M5-A3P-1702 (act3_ch18 §4): the shipped chart has the Act III revisits. Oruvel is one; Ansedra shows from Ch13 but,
## once the party are heretics, is greyed with its reason and never flown to (seen from the air only).
func test_the_shipped_chart_lists_oruvel_and_refuses_ansedra_to_heretics() -> void:
	var bag := {&"kite_flying": true, &"ch01_started": true, &"ch13_started": true}
	var log := trips
	var m := KiteMapModel.new(
		KiteMapModel.load_data(),
		func(f: StringName) -> Variant: return bag.get(f, false),
		func(f: StringName, v: Variant) -> void: bag[f] = v,
		func(loc: StringName, spawn: StringName) -> bool:
			log.append([loc, spawn])
			return true
	)
	assert_true(m.ids().has(&"oruvel"), "Oruvel is a revisit")
	assert_true(m.ids().has(&"ansedra"), "Ansedra is on the chart from Ch13")
	assert_eq(m.refusal(&"ansedra"), "", "before the heresy it can be flown to")
	bag[&"ch14_declared_heretics"] = true
	assert_eq(m.refusal(&"ansedra"), tr("KITE_CLOSED_HERETICS"), "after it, refused with its reason")
	assert_false(m.fly(&"ansedra"), "and the Kite doesn't land")
	assert_true(trips.is_empty())
	assert_true(m.fly(&"oruvel"))
	var menu := KiteMapMenu.open_in(host, m)
	for r: Dictionary in menu.rows_page().rows:
		if StringName(str(r["id"])) == &"ansedra":
			assert_false(bool(r["enabled"]), "the row is greyed")
			assert_eq(str(r["right"]), tr("KITE_CLOSED_HERETICS"), "and says why")
	_close(menu)
	_done()


## M5-A3P-1703: the log lists a revisit once the chart lists its place (Seen, and what changed, once its scene has
## played) and an heirloom once its requires_flag is set (where it waits, then what is carried); it points the chart
## at the row's place, is read rather than chosen from, and Cancel returns to the list on its own row.
func test_the_log_lists_revisits_and_heirlooms_and_points_the_chart() -> void:
	var m := _model()
	var table := {
		"places":
		[
			{"destination": "isle", "seen_flag": "kite_test_isle_seen", "changed_key": "KITE_LOG_CHANGED_ORUVEL"},
			{"destination": "cove", "seen_flag": "kite_test_cove_seen", "changed_key": "KITE_LOG_CHANGED_TAMSULE"},
		],
		"heirlooms":
		[
			{
				"id": "rhen",
				"label_key": "KITE_LOG_HEIR_RHEN",
				"flag": "kite_test_hooks",
				"requires_flag": "",
				"where": "shoals",
				"where_key": "KITE_LOG_WHERE_RHEN",
				"found_key": "KITE_LOG_FOUND_RHEN"
			},
			{
				"id": "pell",
				"label_key": "KITE_LOG_HEIR_PELL",
				"flag": "kite_test_spear",
				"requires_flag": "kite_test_named",
				"where": "isle",
				"where_key": "KITE_LOG_WHERE_PELL",
				"found_key": "KITE_LOG_FOUND_PELL"
			},
		],
	}
	var log := KiteLogModel.new(table, m)
	var ids: Array = log.entries().map(func(e: Dictionary) -> StringName: return e["id"])
	assert_eq(ids, [&"isle", &"heirloom_rhen"], "the unfound cove and the unnamed hero's errand wait")
	assert_eq(str(log.entry(&"isle")["line"]), tr("KITE_LOG_NOT_YET"))
	assert_eq(str(log.entry(&"isle")["right"]), "", "no mark before it is seen")
	assert_eq(str(log.entry(&"heirloom_rhen")["line"]), tr("KITE_LOG_WHERE_RHEN"), "where it waits")
	flags[&"kite_test_isle_seen"] = true
	flags[&"kite_test_hooks"] = true
	flags[&"kite_test_named"] = true
	assert_eq(str(log.entry(&"isle")["right"]), tr("KITE_LOG_SEEN"))
	assert_eq(str(log.entry(&"isle")["line"]), tr("KITE_LOG_CHANGED_ORUVEL"), "what changed there")
	assert_eq(str(log.entry(&"heirloom_rhen")["right"]), tr("KITE_LOG_CARRIED"))
	assert_eq(str(log.entry(&"heirloom_rhen")["line"]), tr("KITE_LOG_FOUND_RHEN"), "what is carried now")
	assert_false(log.entry(&"heirloom_pell").is_empty(), "named: the errand is listed")
	var menu := KiteMapMenu.open_in(host, m)
	menu.ship_log = log
	menu.rows_page().set_cursor(menu.rows_page().rows.size() - 2, false)
	menu.accept()
	assert_eq(menu.level, KiteMapMenu.Level.LOG)
	assert_eq(menu.help_text(), tr("KITE_LOG_HELP"))
	assert_eq(menu.desc_text(), tr("KITE_LOG_CHANGED_ORUVEL"))
	assert_eq(menu.chart().cursor, &"isle", "the chart points at the place")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.chart().cursor, &"shoals", "and at where an heirloom waits")
	menu.accept()
	assert_eq(menu.level, KiteMapMenu.Level.LOG, "the log is read, not chosen from")
	assert_true(trips.is_empty(), "nothing flies from the log")
	assert_eq(StringName(str(menu.rows_page().rows[-1]["id"])), KiteMapMenu.ROW_LOG_BACK)
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, KiteMapMenu.Level.LIST)
	assert_eq(StringName(str(menu.rows_page().current_row()["id"])), KiteMapMenu.ROW_LOG, "back on the log's row")
	_close(menu)
	_done()


## The shipped log: every flag declared, every key translated, every place on the shipped chart; all eight revisits
## and all seven heirlooms are listed once Act III's flags are set.
func test_the_shipped_log_is_whole() -> void:
	var data := KiteLogModel.load_data()
	var reg := Game.registry
	var chart := KiteMapModel.load_data()
	var dests: Array = (chart.get("destinations", []) as Array).map(func(d: Dictionary) -> String: return str(d["id"]))
	var bag := {}
	for r: Dictionary in data.get("places", []):
		assert_true(dests.has(str(r["destination"])), "%s is on the chart" % r["destination"])
		assert_true(reg.is_declared(StringName(str(r["seen_flag"]))), "%s is declared" % r["seen_flag"])
		assert_ne(tr(str(r["changed_key"])), str(r["changed_key"]), "%s is translated" % r["changed_key"])
	for r: Dictionary in data.get("heirlooms", []):
		assert_true(dests.has(str(r["where"])), "%s is on the chart" % r["where"])
		for f: String in [str(r["flag"]), str(r["requires_flag"])]:
			assert_true(f == "" or reg.is_declared(StringName(f)), "%s is declared" % f)
		for k: String in ["label_key", "where_key", "found_key"]:
			assert_ne(tr(str(r[k])), str(r[k]), "%s is translated" % r[k])
	for d: Dictionary in chart.get("destinations", []):
		bag[StringName(str(d.get("requires_flag", "")))] = true
	bag[&"ch18_pell_named"] = true
	var m := KiteMapModel.new(
		chart, func(f: StringName) -> Variant: return bag.get(f, false), func(_f, _v) -> void: pass
	)
	var log := KiteLogModel.new(data, m)
	var kinds := {}
	for e in log.entries():
		kinds[e["kind"]] = int(kinds.get(e["kind"], 0)) + 1
	assert_eq(int(kinds.get(KiteLogModel.KIND_PLACE, 0)), 8, "the eight revisits")
	assert_eq(int(kinds.get(KiteLogModel.KIND_HEIRLOOM, 0)), 7, "the seven heirlooms")
	_done()


func _model() -> KiteMapModel:
	var bag := flags
	var log := trips
	return KiteMapModel.new(
		TABLE,
		func(f: StringName) -> Variant: return bag.get(f, false),
		func(f: StringName, v: Variant) -> void: bag[f] = v,
		func(loc: StringName, spawn: StringName) -> bool:
			log.append([loc, spawn])
			return true
	)


func _close(menu: KiteMapMenu) -> void:
	if is_instance_valid(menu) and menu.motion() != null:
		menu.motion().finish()


func _done() -> void:
	host.get_tree().paused = false
	host.get_parent().remove_child(host)
	host.free()
	ShrineNetwork.registry = _saved_registry
	UiSettings.set_shared(null)


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
