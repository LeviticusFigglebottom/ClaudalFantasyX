extends TestCase
## M3-UI-03: the lore codex. CodexModel (unlocks by story flag, by a found record, always; read
## flags), the field record hook (CodexNotice over {"record": id} payloads), CodexMenu (columns,
## "New" markers, the text page and its scroll), the field menu's Codex row, and input parity with
## the keyboard, the controller and the mouse (InputDriver, ADR 0036). Models run on a scratch
## flag set, so Game.state is never touched.

const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
## Not a loc key: TranslationServer hands it back as it is, so the text overflows its page.
const LONG_WORD := "tide "
const LONG_REPEAT := 400

var flags: Dictionary = {}
var made: Array[Node] = []


func before_each() -> void:
	_free_made()
	flags = {}
	_tree().paused = false
	UiSettings.set_shared(UiSettings.new())


# --- the model ----------------------------------------------------------------------------------


func test_the_shipped_codex_has_four_categories_and_a_small_starter_set() -> void:
	var m := _model()
	var ids: Array[StringName] = []
	for c in m.categories():
		ids.append(c["id"])
	assert_eq(ids, [&"world", &"places", &"people", &"records"] as Array[StringName], "data order")
	assert_true(m.entry_rows.size() >= 32, "the starter set and Act I's (Ch1 to Ch9); Narrative reviews it (M3-NAR-01)")
	for e in m.entry_rows:
		var id := StringName(str(e["id"]))
		assert_ne(m.title(id), str(e["title_key"]), "%s: its title is in codex.csv" % id)
		assert_ne(m.body(id), str(e["body_key"]), "%s: its body is in codex.csv" % id)
		assert_true(Game.registry.is_declared(CodexModel.read_flag(id)), "%s: read flag declared" % id)
		if m.is_record(id):
			assert_true(Game.registry.is_declared(CodexModel.found_flag(id)), "%s: found flag declared" % id)
			assert_eq(e["category"], "records", "%s: records live under Records" % id)
	for c in m.categories():
		assert_true(int(c["total"]) > 0, "%s has entries" % c["id"])


func test_entries_unlock_by_flag_by_record_or_always_and_locked_ones_are_not_listed() -> void:
	var m := _model()
	assert_eq(_ids(m.entries_in(&"world")), [&"glimmer"] as Array[StringName], "only the always entry at first")
	assert_true(m.entries_in(&"records").is_empty())
	assert_eq(m.categories()[0]["found"], 1)
	assert_eq(
		m.categories()[0]["total"],
		17,
		"locked entries still count (Act I's ten, the Kirru and Ullari, the farewell-tide, name-shells, keth, the Conclave and the heresy)"
	)
	flags[&"ch02_met_asha"] = true
	assert_eq(
		_ids(m.entries_in(&"world")),
		[&"glimmer", &"undertow", &"order", &"the_calm"] as Array[StringName],
		"data order"
	)
	assert_eq(_ids(m.entries_in(&"people")), [&"asha", &"toma"] as Array[StringName])
	assert_eq(m.summary(), tr("CODEX_TOTAL_FMT").format({"found": 7, "total": m.entry_rows.size()}))
	assert_false(m.is_unlocked(&"causeway_notice"), "a record waits to be found")
	assert_false(m.is_unlocked(&"no_such_entry"))


func test_reading_clears_new_once_and_only_for_unlocked_entries() -> void:
	var m := _model()
	assert_eq(m.categories()[0]["new"], 1, "Glimmer is new")
	assert_false(m.mark_read(&"undertow"), "a locked entry cannot be read")
	assert_false(flags.has(CodexModel.read_flag(&"undertow")))
	assert_true(m.mark_read(&"glimmer"))
	assert_true(flags.get(&"codex_glimmer_read", false), "its read flag (declared, saved with the flags)")
	assert_false(m.mark_read(&"glimmer"), "only once")
	assert_eq(m.categories()[0]["new"], 0)
	assert_true(bool(m.entries_in(&"world")[0]["read"]))


func test_add_record_finds_a_record_once_and_ignores_other_ids() -> void:
	var m := _model()
	assert_false(m.add_record(&"glimmer"), "not a record")
	assert_false(m.add_record(&"no_such_entry"))
	assert_true(m.add_record(&"causeway_notice"))
	assert_true(flags.get(&"codex_causeway_notice_found", false))
	assert_eq(_ids(m.entries_in(&"records")), [&"causeway_notice"] as Array[StringName])
	assert_true(bool(m.entries_in(&"records")[0]["record"]))
	assert_false(m.add_record(&"causeway_notice"), "already found")
	assert_eq(m.count_text(m.categories()[3]), tr("CODEX_ROW_COUNT_FMT").format({"found": 1, "total": 2}))


# --- the field record hook ----------------------------------------------------------------------


func test_a_record_payload_marks_it_found_and_the_notice_shows_its_title() -> void:
	var notice := _notice()
	assert_false(notice.handle({"shop": "haluna_general"}), "other payloads are not ours")
	assert_false(notice.handle({"record": "glimmer"}), "an entry that is not a record")
	assert_true(notice.handle({"record": "basin_steps"}))
	assert_true(flags.get(&"codex_basin_steps_found", false), "found through the flag writer")
	notice.advance(0.0)
	assert_true(notice.is_showing())
	assert_eq(notice.head_text(), tr("CODEX_NOTICE_TITLE"))
	assert_eq(notice.name_text(), tr("CODEX_BASIN_STEPS_TITLE"))
	assert_false(notice.handle({"record": "basin_steps"}), "found once: no second notice")
	var d := CodexNotice.load_data()
	notice.advance(float(d["fade_sec"]) + 0.01)
	notice.advance(float(d["hold_sec"]) + 0.01)
	notice.advance(float(d["fade_sec"]) + 0.01)
	assert_false(notice.is_showing(), "it fades out")
	assert_true(notice.queue.is_empty())
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_the_notice_hears_the_event_bus_and_hides_while_a_menu_pauses() -> void:
	var notice := _notice()
	FieldEvents.emit_interacted(&"scratch_note", Interactable.KIND_INTERACT, {"record": "causeway_notice"})
	assert_true(flags.get(&"codex_causeway_notice_found", false), "the hook listens on FieldEvents.INTERACTED")
	_tree().paused = true
	notice.advance(1.0)
	assert_false(notice.panel_visible(), "a menu hides it")
	assert_false(notice.is_showing(), "and it waits")
	_tree().paused = false
	notice.advance(0.0)
	assert_true(notice.is_showing())
	assert_eq(notice.name_text(), tr("CODEX_CAUSEWAY_NOTICE_TITLE"))
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_a_scratch_interactable_with_a_record_payload_adds_it() -> void:
	var notice := _notice()
	var it := Interactable.new()
	it.id = &"scratch_record"
	it.payload = {"record": "basin_steps"}
	_add(it)
	it.try_interact()
	assert_true(flags.get(&"codex_basin_steps_found", false), "interacting finds the record")
	notice.advance(0.0)
	assert_eq(notice.name_text(), tr("CODEX_BASIN_STEPS_TITLE"))

# --- the menu -----------------------------------------------------------------------------------
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_the_menu_lists_categories_with_counts_and_new_and_shows_a_category_line() -> void:
	flags[&"ch02_met_asha"] = true
	var menu := _menu()
	var cats := menu.categories_page()
	assert_eq(cats.row_count(), 4)
	assert_eq(cats.rows[0]["right"], tr("CODEX_ROW_COUNT_FMT").format({"found": 4, "total": 17}))
	assert_eq(cats.rows[0]["mp"], tr("CODEX_NEW_TAG"), "unread entries: New, in words")
	assert_eq(cats.rows[3]["mp"], "", "nothing found: nothing new")
	assert_eq(menu.column, CodexMenu.Column.CATEGORIES)
	assert_eq(menu.title_text(), tr("CODEX_CAT_WORLD"))
	assert_eq(menu.body_text(), tr("CODEX_CAT_WORLD_DESC"))
	assert_eq(menu.entries_page().row_count(), 4, "World's unlocked entries, listed under it")
	assert_eq(menu.entries_page().rows[1]["right"], tr("CODEX_NEW_TAG"))
	assert_eq(flags.get(&"codex_glimmer_read", false), false, "showing a category reads nothing")
	assert_eq(menu.summary_text(), menu.model.summary())
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_opening_an_entry_shows_it_and_clears_its_new_marker() -> void:
	flags[&"ch02_met_asha"] = true
	var menu := _menu()
	assert_true(menu.handle_input(_ev(&"ui_accept")))
	assert_eq(menu.column, CodexMenu.Column.ENTRIES)
	assert_eq(menu.current_id, &"glimmer")
	assert_eq(menu.title_text(), tr("CODEX_GLIMMER_TITLE"))
	assert_eq(menu.body_text(), tr("CODEX_GLIMMER_BODY"))
	assert_true(flags.get(&"codex_glimmer_read", false))
	assert_eq(menu.entries_page().rows[0]["right"], "", "read: no marker")
	assert_eq(menu.entries_page().rows[1]["right"], tr("CODEX_NEW_TAG"), "the next one is still new")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_id, &"undertow")
	assert_eq(menu.categories_page().rows[0]["mp"], tr("CODEX_NEW_TAG"), "the Order is still new")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_id, &"order")
	assert_eq(menu.categories_page().rows[0]["mp"], tr("CODEX_NEW_TAG"), "the Calm is still new")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_id, &"the_calm")
	assert_eq(menu.categories_page().rows[0]["mp"], "", "the category has nothing new left")
	assert_eq(menu.entries_page().cursor, 3, "the cursor stays where it was")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.column, CodexMenu.Column.CATEGORIES, "Cancel comes back a column")
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.category, &"records")
	assert_eq(menu.entries_page().row_count(), 0)
	assert_eq(menu.title_text(), tr("CODEX_CAT_RECORDS"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.column, CodexMenu.Column.CATEGORIES, "an empty category does not open")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_open(), "Cancel on the categories closes")
	assert_false(_tree().paused, "and gives the pause back")
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_a_record_reads_in_its_own_voice() -> void:
	flags[&"codex_basin_steps_found"] = true
	var menu := _menu()
	menu.select_category(3)
	menu.select_entry(0)
	assert_eq(menu.current_id, &"basin_steps")
	assert_eq(menu._body.theme_type_variation, &"FlavorLabel", "a record is quoted")
	assert_eq(menu._sub.text, tr("CODEX_RECORD_TAG"))
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_a_record_with_a_reader_row_opens_in_the_document_reader() -> void:
	var was := DocumentReaderModel.records_path
	DocumentReaderModel.records_path = "res://game/levels/_tests/document_reader/reader_fixture.json"
	var doc := CodexModel.load_data().duplicate(true)
	for e: Dictionary in doc["entries"]:
		if e["id"] == "basin_steps":
			e["reader"] = "fixture_one"
	flags[&"codex_basin_steps_found"] = true
	var menu := _menu(_model(doc))
	menu.select_category(3)
	menu.select_entry(0)
	assert_eq(menu.current_id, &"basin_steps")
	menu.handle_input(_ev(&"ui_accept"))
	var reader := menu.reader()
	assert_true(reader != null and reader.is_open(), "Confirm opens the record in the reader")
	if reader != null:
		assert_eq(reader.model.pane_count(), 1, "alone, one pane")
		assert_false(menu.handle_input(_ev(&"ui_down")), "the reader has the input, not the codex")
		reader.close()
		reader.motion().finish()
	assert_false(menu.reader_open())
	assert_true(menu.handle_input(_ev(&"ui_up")), "the codex has it back")
	assert_true(menu.is_open() and _tree().paused, "still open, still paused")
	DocumentReaderModel.records_path = was
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_long_text_scrolls_and_a_pad_can_read_it_through_the_text_column() -> void:
	var menu := _menu(_long_model())
	menu.handle_input(_ev(&"ui_accept"))
	assert_true(menu.max_scroll() > 0.0, "the long entry overflows its page")
	assert_eq(menu.scroll_offset(), 0.0)
	menu.handle_input(_ev(&"ui_page_down"))
	var step := HudLayout.num(CodexMenu.load_data()["text"], "scroll_step_px")
	assert_eq(menu.scroll_offset(), step, "Page Down scrolls one step")
	menu.handle_input(_ev(&"ui_page_up"))
	assert_eq(menu.scroll_offset(), 0.0)
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.column, CodexMenu.Column.TEXT, "Right goes into the long text")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.scroll_offset(), step, "Down scrolls it there")
	for i in 200:
		menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.scroll_offset(), menu.max_scroll(), "and stops at the end")
	assert_eq(menu.current_id, &"long", "the entry under the cursor never changed")
	menu.handle_input(_ev(&"ui_left"))
	assert_eq(menu.column, CodexMenu.Column.ENTRIES)
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_id, &"short")
	assert_eq(menu.scroll_offset(), 0.0, "a new entry starts at the top")
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.column, CodexMenu.Column.ENTRIES, "a short text has nothing to scroll into")

# --- the field menu row -------------------------------------------------------------------------
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_the_field_menu_codex_row_follows_the_bestiary_and_opens_the_codex() -> void:
	var fm := FieldMenuModel.new(GameStateData.new(), [&"rhen"] as Array[StringName], NAMES)
	var at := FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_CODEX)
	assert_eq(at, FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_BESTIARY) + 1, "after Bestiary")
	assert_eq(fm.root_rows()[at]["label"], tr("FIELD_MENU_CODEX"))
	assert_eq(fm.root_desc(FieldMenuModel.ROW_CODEX), tr("FIELD_MENU_CODEX_DESC"))
	fm.codex = _model()
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(fm)
	_add(menu)
	menu.root_page().set_cursor(at, false)
	menu.accept()
	var codex := menu.codex_menu
	assert_true(codex != null and codex.is_open(), "the Codex row opens the codex")
	assert_eq(codex.model, fm.codex, "over the menu's model")
	assert_false(menu.visible, "the field menu steps aside")
	assert_false(menu.handle_input(_ev(&"ui_down")), "the codex has the input")
	var layer := codex.get_parent() as CanvasLayer
	assert_true(layer.layer > int(FieldMenu.load_data()["canvas_layer"]), "over the field menu")
	codex.handle_input(_ev(&"ui_cancel"))
	assert_true(menu.visible, "back to the field menu")
	assert_eq(menu.codex_menu, null)
	assert_true(menu.is_open())
	_free_made()  # the runner has no after_each: no menu may outlive its test


# --- input parity (M2-UI-26) --------------------------------------------------------------------


func test_open_read_scroll_and_close_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		flags = {&"ch02_met_asha": true, &"ch03_causeway_arrived": true}
		var menu := _menu(_long_model(true))
		var cats := menu.categories_page()
		var list := menu.entries_page()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(cats.row_node(1))
			assert_eq(menu.category, &"places", "mouse: hover shows a category")
			InputDriver.click(cats.row_node(1))
		else:
			d.press(&"ui_down")
			assert_eq(menu.category, &"places", "%s: Down moves to Places" % d.label())
			d.press(&"ui_accept")
		assert_eq(menu.column, CodexMenu.Column.ENTRIES, "%s: the category opens" % d.label())
		assert_eq(menu.current_id, &"haluna")
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(list.row_node(1))
		else:
			d.press(&"ui_down")
		assert_eq(menu.current_id, &"long", "%s: the next entry" % d.label())
		assert_true(flags.get(&"codex_long_read", false), "%s: opening it reads it" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(menu.text_area(), 2)
		else:
			d.press(&"ui_right")
			assert_eq(menu.column, CodexMenu.Column.TEXT, "%s: Right goes into the text" % d.label())
			d.press(&"ui_down")
			d.press(&"ui_down")
		var step := HudLayout.num(CodexMenu.load_data()["text"], "scroll_step_px")
		assert_eq(menu.scroll_offset(), step * 2.0, "%s: the text scrolls" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(list.row_node(1), -1)
			assert_eq(menu.current_id, &"haluna", "mouse: the wheel over the list steps it")
			InputDriver.right_click(menu.text_area())
		else:
			d.press(&"ui_cancel")
			d.press(&"ui_cancel")
		assert_eq(menu.column, CodexMenu.Column.CATEGORIES, "%s: Cancel comes back" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.right_click(cats.row_node(0))
		else:
			d.press(&"ui_cancel")
		assert_false(menu.is_open(), "%s: Cancel closes" % d.label())
		_free_made()
	_tree().paused = false
	_free_made()  # the runner has no after_each: no menu may outlive its test


func test_the_mouse_can_reach_a_record_from_the_categories_in_one_click() -> void:
	flags[&"codex_causeway_notice_found"] = true
	var menu := _menu()
	InputDriver.click(menu.categories_page().row_node(3))
	assert_eq(menu.column, CodexMenu.Column.ENTRIES)
	assert_eq(menu.current_id, &"causeway_notice")
	# The categories page is dimmed now: hover passes it by (M2-UI-26), a click still reaches it.
	InputDriver.hover(menu.categories_page().row_node(0))
	assert_eq(menu.column, CodexMenu.Column.ENTRIES, "a dimmed page ignores hover")
	InputDriver.click(menu.categories_page().row_node(0))
	assert_eq(menu.category, &"world", "a click on another category opens it")
	assert_eq(menu.column, CodexMenu.Column.ENTRIES)
	assert_eq(menu.current_id, &"glimmer")
	menu.close()

# --- helpers ------------------------------------------------------------------------------------
	_free_made()  # the runner has no after_each: no menu may outlive its test


func _model(doc: Dictionary = {}) -> CodexModel:
	return CodexModel.new(
		doc, func(f: StringName) -> bool: return flags.has(f), func(f: StringName) -> void: flags[f] = true
	)


## The shipped categories with a long entry and a short one: in Places after Haluna when
## `in_places`, else alone in World.
func _long_model(in_places: bool = false) -> CodexModel:
	var doc := CodexModel.load_data().duplicate(true)
	var long_body := LONG_WORD.repeat(LONG_REPEAT)
	var cat := "places" if in_places else "world"
	var extra: Array = [
		{
			"id": "long",
			"category": cat,
			"title_key": "CODEX_HALUNA_TITLE",
			"body_key": long_body,
			"unlock": {"always": true}
		},
		{
			"id": "short",
			"category": cat,
			"title_key": "CODEX_TOMA_TITLE",
			"body_key": "CODEX_TOMA_BODY",
			"unlock": {"always": true}
		},
	]
	var rows: Array = []
	for e: Variant in doc["entries"]:
		var row := e as Dictionary
		if not in_places and row["category"] == "world":
			continue
		rows.append(row)
		if in_places and row["id"] == "haluna":
			rows.append_array(extra)
	if not in_places:
		rows = extra + rows
	doc["entries"] = rows
	return _model(doc)


func _menu(m: CodexModel = null) -> CodexMenu:
	var menu := CodexMenu.open_in(_host(), m if m != null else _model())
	made.append(menu.get_parent())
	return menu


func _notice() -> CodexNotice:
	var notice := CodexNotice.new()
	notice.model = _model()
	_add(notice)
	return notice


func _add(n: Node) -> void:
	_host().add_child(n)
	made.append(n)


func _host() -> Node:
	var tree := _tree()
	return tree.current_scene if tree.current_scene != null else tree.root


func _tree() -> SceneTree:
	return Engine.get_main_loop() as SceneTree


func _free_made() -> void:
	for n in made:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	_tree().paused = false


func _ids(rows: Array[Dictionary]) -> Array[StringName]:
	var out: Array[StringName] = []
	for r in rows:
		out.append(StringName(str(r["id"])))
	return out


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


## M3-NAR-01: both Act I records stand in the field. The Tide-Readers' Notice is an interact trigger on the
## causeway's first marker post, before the first banter post. The Words at the Basin Steps are on the shrine's
## first step inside the entrance. Each is a once-only "Examine" whose payload names the record.
func test_the_two_act1_records_are_placed_in_the_field() -> void:
	var causeway := (
		JSON.parse_string(
			FileAccess.get_file_as_string("res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway_layout.json")
		)
		as Dictionary
	)
	var ids: Array = (causeway["triggers"] as Array).map(func(t: Dictionary) -> String: return str(t["id"]))
	var notice := (causeway["triggers"] as Array)[ids.find("causeway_notice")] as Dictionary
	assert_eq(str(notice.get("activation", "")), "interact", "examined, not walked into")
	assert_eq(notice.get("payload", {}), {"record": "causeway_notice"})
	assert_true(ids.find("causeway_notice") < ids.find("banter_posts"), "read before the first banter post")
	var shrine := (
		JSON.parse_string(FileAccess.get_file_as_string("res://game/data/trials/shell_shrine.json")) as Dictionary
	)
	var layout := (shrine["shell_shrine"] as Dictionary)["layout"] as Dictionary
	assert_true(layout.has("basin_steps"), "the shrine's step for the record")
	assert_true(float(layout["basin_steps"][0]) > float(layout["spawn"][0]), "a step in from the entrance")
	assert_true(float(layout["basin_steps"][0]) < float(layout["source"][0]), "before the basins")
	var spot := CodexRecordSpot.make("basin_steps", Vector3(1, 0, 2), 0.9)
	assert_eq(spot.payload, {"record": "basin_steps"})
	assert_eq(spot.activation, Interactable.Activation.INTERACT)
	assert_eq(spot.prompt_key, "FIELD_PROMPT_DEFAULT", "Examine, not Read (a battle command)")
	assert_true(spot.once)
	assert_eq(spot.position, Vector3(1, 0, 2))
	spot.free()
