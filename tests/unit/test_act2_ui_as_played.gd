extends TestCase
## M4-A2P-1700 (the Lead's Act II UI pass, 2026-10-30): Ch10-Ch13's UI as it plays, at 100% and 130% text and on the
## pad. Every Ch10-Ch13 location's area title card, every Ch10-Ch13 objective line (main and side) in the objective
## line (and on demand, the Where-to-next card), the shops and inns of Quellan and Ansedra walked with the pad, and
## Asha's battle menu with every Vowbound bound by Ch13 (six Call rows): nothing leaves the screen, no text runs out
## of its panel or is cut short, and the pad reaches every row.

const CHAPTERS: Array[String] = ["ch10", "ch11", "ch12", "ch13"]
const TEXT_SCALES: Array[float] = [1.0, 1.3]
const SHOPS: Array[StringName] = [&"quellan_trader", &"ansedra_purveyor"]
const INNS: Array[StringName] = [&"quellan_inn", &"ansedra_guest"]
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
## The Vowbound Asha has bound by the end of Ch13 (vowbound.json, Kesh is Ch16's).
const BOUND_BY_CH13: Array[StringName] = [&"ilun", &"kahre", &"virel", &"nhoa", &"hesk", &"ethren"]

var made: Array[Node] = []
var flags: Dictionary = {}


func before_each() -> void:
	InputDriver.clear_screen()
	_free_made()


func after_each() -> void:
	_free_made()
	AreaTitleCard.forget()
	UiSettings.set_shared(null)
	(Engine.get_main_loop() as SceneTree).paused = false


func test_every_act2_zone_title_fits() -> void:
	var ids := _act2_locations()
	assert_true(ids.size() >= 10, "Ch10-Ch13's locations were found (%d)" % ids.size())
	for t in TEXT_SCALES:
		_settings(t)
		for loc in ids:
			AreaTitleCard.forget()
			var card := AreaTitleCard.new()
			card.location = loc
			_add(card)
			card.advance(0.0)
			card.advance(float(AreaTitleCard.load_data().get("in_sec", 0.5)) + 0.01)
			assert_true(card.is_showing(), "%s: its card shows" % loc)
			_check(card, "%s title at %d%%" % [loc, roundi(t * 100.0)])
			_free_made()


func test_every_act2_objective_line_fits_and_shows_on_demand() -> void:
	var rows := _act2_objectives()
	assert_true(rows.size() >= 20, "Ch10-Ch13's objective rows were found (%d)" % rows.size())
	for t in TEXT_SCALES:
		_settings(t)
		for row: Dictionary in rows:
			flags = {}
			for f: Variant in row.get("requires", []):
				flags[StringName(str(f))] = true
			var hud := ObjectiveHud.new()
			hud.tracker = ObjectiveTracker.new(func(f: StringName) -> bool: return bool(flags.get(f, false)))
			hud.zone = StringName(str(row["zone"]))
			_add(hud)
			hud.advance(0.0)
			var where := "%s at %d%%" % [row["id"], roundi(t * 100.0)]
			if not bool(row.get("side", false)):
				assert_true(hud.is_showing(), "%s: the line shows" % where)
				assert_eq(hud.line_text(), tr(str(row["line_key"])), "%s: its words" % where)
			if hud.is_showing():
				var panel: PanelContainer = hud._panel
				assert_true(panel.get_combined_minimum_size().y <= panel.size.y + 0.5, "%s: the panel holds it" % where)
				_check(hud, where)
			_free_made()


func test_act2_shops_and_inns_walk_with_the_pad_and_fit() -> void:
	var db := ItemDB.load_default()
	var reader := FlagReader.new()
	for f in ["ch12_reached_quellan", "ch13_started"]:
		reader.values[f] = true
	var d := InputDriver.new(InputDriver.Kind.PAD)
	for t in TEXT_SCALES:
		_settings(t)
		for id in SHOPS:
			var state := GameStateData.new()
			state.currency = 2000
			var shop := (load(ShopMenu.SCENE_PATH) as PackedScene).instantiate() as ShopMenu
			shop.pause_tree = false
			shop.configure(ShopMenuModel.new(db, Shop.new(db, id), PartyGoods.from_state(db, state), reader, NAMES))
			_add(shop)
			var where := "%s at %d%%" % [id, roundi(t * 100.0)]
			_check(shop, "%s: root" % where)
			d.press(&"ui_accept")
			assert_eq(shop.level, ShopMenu.Level.BUY, "%s: the pad opens Buy" % where)
			var page := shop.detail_page()
			for i in page.row_count():
				_check(shop, "%s: stock row %d" % [where, page.cursor])
				d.press(&"ui_down")
			d.press(&"ui_accept")
			_check(shop, "%s: bought" % where)
			d.press(&"ui_cancel")
			d.press(&"ui_cancel")
			assert_false(shop.is_open(), "%s: Cancel leaves" % where)
			_free_made()
		for id in INNS:
			var state := GameStateData.new()
			state.currency = 2000
			var inn := (load(InnMenu.SCENE_PATH) as PackedScene).instantiate() as InnMenu
			inn.pause_tree = false
			var rested: Array[StringName] = []
			inn.configure(
				InnMenuModel.new(
					Inn.new(db, id),
					PartyGoods.from_state(db, state),
					reader,
					func(source: StringName) -> void: rested.append(source)
				)
			)
			_add(inn)
			var where := "%s at %d%%" % [id, roundi(t * 100.0)]
			_check(inn, "%s: root" % where)
			var rest := InnMenuModel.ROOT_IDS.find(InnMenuModel.ROW_REST)
			for i in InnMenuModel.ROOT_IDS.size():
				if inn.root_page().cursor == rest:
					break
				d.press(&"ui_up")
			d.press(&"ui_accept")
			assert_eq(rested.size(), 1, "%s: the pad rests the party" % where)
			_check(inn, "%s: rested" % where)
			d.press(&"ui_cancel")
			assert_false(inn.is_open(), "%s: Cancel leaves" % where)
			_free_made()


## Before the party reaches Quellan or Ansedra, their shops and inns refuse in words (the closed line), whole.
func test_closed_act2_shops_and_inns_say_so_whole() -> void:
	var db := ItemDB.load_default()
	var reader := FlagReader.new()
	for t in TEXT_SCALES:
		_settings(t)
		for id in SHOPS:
			var shop := (load(ShopMenu.SCENE_PATH) as PackedScene).instantiate() as ShopMenu
			shop.pause_tree = false
			var goods := PartyGoods.from_state(db, GameStateData.new())
			shop.configure(ShopMenuModel.new(db, Shop.new(db, id), goods, reader, NAMES))
			_add(shop)
			_check(shop, "%s closed at %d%%" % [id, roundi(t * 100.0)])
			_free_made()
		for id in INNS:
			var inn := (load(InnMenu.SCENE_PATH) as PackedScene).instantiate() as InnMenu
			inn.pause_tree = false
			var goods := PartyGoods.from_state(db, GameStateData.new())
			inn.configure(InnMenuModel.new(Inn.new(db, id), goods, reader, func(_s: StringName) -> void: pass))
			_add(inn)
			var where := "%s closed at %d%%" % [id, roundi(t * 100.0)]
			_check(inn, where)
			_free_made()


func test_asha_s_six_calls_fit_her_menu_and_the_pad_reaches_each() -> void:
	var d := InputDriver.new(InputDriver.Kind.PAD)
	for t in TEXT_SCALES:
		var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
		ctl.auto_start = false
		ctl.pacing_scale = 0.0
		ctl.persist_progress = false
		ctl.show_damage_numbers = false
		_add(ctl)
		ctl.hud.apply_settings(_settings(t))
		ctl.start_fixture(BattleFixture.load_fixture(&"vowbound_call"))
		for row: Variant in BattleVowbound.load_config():  # the fixture's table names Ilun alone
			var vid := StringName(str((row as Dictionary)["id"]))
			if BOUND_BY_CH13.has(vid):
				ctl.engine.vowbound.rows[vid] = row
				if not ctl.engine.vowbound.known.has(vid):
					ctl.engine.vowbound.known.append(vid)
		var guard := 0
		while ctl.current_actor_id() != &"asha" and guard < 30:
			guard += 1
			ctl.act(BattleMenus.ATTACK_SKILL, [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
		assert_eq(ctl.current_actor_id(), &"asha")
		var page := ctl.hud.commands.top_page()
		var calls := 0
		for r: Dictionary in page.rows:
			if str(r.get("id", "")).begins_with(BattleMenus.ROW_CALL_PREFIX):
				calls += 1
		var where := "Asha's menu at %d%%" % roundi(t * 100.0)
		assert_eq(calls, BOUND_BY_CH13.size(), "%s: one Call row per Vowbound bound by Ch13" % where)
		for i in page.row_count():
			_check(ctl.hud.commands, "%s, row %d" % [where, page.cursor])
			var node := page.row_node(page.cursor)
			assert_true(node != null and node.is_visible_in_tree(), "%s: row %d is on screen" % [where, page.cursor])
			d.press(&"ui_down")
		_free_made()


# --- helpers --------------------------------------------------------------------------------------


## No visible Control under `root` leaves the screen, no text runs out of its panel, and no label is cut short.
func _check(root: Node, where: String) -> void:
	for b in AspectHost.outside(root):
		fail("%s: %s leaves the screen" % [where, b])
	for b in AspectHost.spilling(root):
		fail("%s: %s" % [where, b])
	for l in root.find_children("*", "Label", true, false):
		var label := l as Label
		if not label.is_visible_in_tree() or label.text == "" or label.clip_text:
			continue
		if label.text_overrun_behavior == TextServer.OVERRUN_NO_TRIMMING:
			continue
		if label.autowrap_mode != TextServer.AUTOWRAP_OFF:
			var need := HudLayout.lines_height(label)
			if need > label.size.y + 1.0:
				fail("%s: '%s' is cut short (%.0f of %.0f px tall)" % [where, label.text, label.size.y, need])
			continue
		var font := label.get_theme_font(&"font")
		var px := label.get_theme_font_size(&"font_size")
		var w := font.get_string_size(label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x if font != null else 0.0
		if w > label.size.x + 1.0:
			fail("%s: '%s' is cut short (%.0f of %.0f px)" % [where, label.text, label.size.x, w])


func _settings(t: float) -> UiSettings:
	var s := UiSettings.new()
	s.set_value(UiSettings.TEXT_SCALE, t)
	UiSettings.set_shared(s)
	return s


static func _act2_locations() -> Array[StringName]:
	var out: Array[StringName] = []
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://game/data/world/locations.json"))
	for row: Variant in (parsed as Dictionary).get("locations", []):
		var id := str((row as Dictionary).get("id", ""))
		if CHAPTERS.has(id.get_slice("/", 0)):
			out.append(StringName(id))
	return out


static func _act2_objectives() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(ObjectiveTracker.DATA_PATH))
	var rows: Array = ((parsed as Dictionary).get("objectives", {}) as Dictionary).get("rows", [])
	for r: Variant in rows:
		var row := r as Dictionary
		if CHAPTERS.has(str(row.get("zone", "")).get_slice("/", 0)):
			out.append(row)
	return out


func _add(n: Node) -> void:
	ParityHost.scene_root().add_child(n)
	made.append(n)


func _free_made() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()
	(Engine.get_main_loop() as SceneTree).paused = false
