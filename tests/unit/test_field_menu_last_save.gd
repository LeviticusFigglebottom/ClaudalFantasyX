extends TestCase
## M2-MNU-300: the field menu has no save row (the Lead's call: saving stays at shrines and the chapter
## autosaves); its root shows where and when the newest save was made, and the shrine reminder.

const NAMES := {&"rhen": "CHAR_RHEN"}
## 2026-10-24 14:05 UTC.
const SAVED_AT := 1792850700


## A save system with fixed slots: list_slots and slot_info, as TitleSaveEntry reads them.
class FakeSaves:
	extends Node
	var infos: Dictionary = {}

	func slot_info(slot: int) -> Dictionary:
		return infos.get(slot, {"slot": slot, "status": SaveSystem.STATUS_EMPTY})

	func list_slots(slots: Array[int]) -> Array[Dictionary]:
		var out: Array[Dictionary] = []
		for s in slots:
			out.append(slot_info(s))
		return out


func test_no_save_system_hides_the_line() -> void:
	var m := FieldMenuModel.new(GameStateData.new(), [&"rhen"], NAMES)
	assert_eq(m.last_save_line(), "", "tests and test rooms: no block")
	assert_eq(m.last_save(), null)


func test_no_save_yet_says_so() -> void:
	var saves := FakeSaves.new()
	var m := _model(saves)
	assert_eq(m.last_save(), null)
	assert_eq(m.last_save_line(), tr("FIELD_MENU_NOT_SAVED"))
	saves.free()


func test_the_newest_readable_save_names_its_place_and_time() -> void:
	var saves := FakeSaves.new()
	saves.infos[0] = _info(0, SAVED_AT - 600, "LOCATION_CH01_ORUVEL_UNDERWAY")
	saves.infos[1] = _info(1, SAVED_AT, "LOCATION_CH01_ORUVEL")
	saves.infos[2] = {"slot": 2, "status": SaveSystem.STATUS_CORRUPT, "saved_at": SAVED_AT + 600}
	var m := _model(saves)
	assert_eq(m.last_save().slot, 1, "the newest loadable slot, as Continue picks it; a damaged one never counts")
	var line := m.last_save_line()
	assert_true(line.contains(tr("LOCATION_CH01_ORUVEL")), "the place: %s" % line)
	assert_true(line.contains("2026-10-24") and line.contains("14:05"), "the time at bias 0: %s" % line)
	m.time_bias_min = 60
	assert_true(m.last_save_line().contains("15:05"), "the viewer's time zone")
	saves.free()


func test_the_root_shows_the_block_and_hides_it_off_the_root() -> void:
	var saves := FakeSaves.new()
	saves.infos[0] = _info(0, SAVED_AT, "LOCATION_CH01_ORUVEL")
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(_model(saves))
	_root().add_child(menu)
	assert_true(menu.last_save_text().contains(tr("LOCATION_CH01_ORUVEL")), "shown on the root")
	assert_false(FieldMenuModel.ROOT_IDS.has(&"save"), "no save row: saving stays at shrines and chapter autosaves")
	menu.root_page().set_cursor(FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_QUIT), false)
	menu.accept()
	assert_eq(menu.last_save_text(), "", "the Quit question hides it")
	menu.free()
	saves.free()


func test_the_tips_carry_the_shrine_hint() -> void:
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://game/data/ui/tutorial_tips.json"))
	var found := false
	for t: Dictionary in raw["tutorial_tips"]["tips"]:
		if str(t.get("id")) == "menu_save":
			found = true
			assert_eq(str(t.get("body_key")), "TIP_MENU_SAVE_BODY")
			assert_true(Game.registry.is_declared(StringName(str(t.get("flag")))), "its seen flag is declared")
	assert_true(found, "a tip says the menu does not save")
	assert_ne(tr("TIP_MENU_SAVE_BODY"), "TIP_MENU_SAVE_BODY")


func _model(saves: Node) -> FieldMenuModel:
	var m := FieldMenuModel.new(GameStateData.new(), [&"rhen"], NAMES)
	m.save_system = saves
	return m


func _info(slot: int, at: int, key: String) -> Dictionary:
	return {"slot": slot, "status": SaveSystem.STATUS_OK, "saved_at": at, "location_key": key, "version": 1}


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
