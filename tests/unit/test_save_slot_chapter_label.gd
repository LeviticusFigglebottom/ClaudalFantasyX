extends TestCase
## M2-FP-27: a save slot's chapter label. Chapter 0 (a save before Chapter 1) reads "Prologue";
## every later chapter reads "Chapter n", from the loc keys.


func test_chapter_zero_is_the_prologue() -> void:
	var info := SaveSlotInfo.from_dict({"slot": 1, "status": "ok", "chapter": 0})
	assert_eq(info.chapter_text(), String(TranslationServer.translate("SAVE_SLOT_PROLOGUE")))


func test_later_chapters_are_numbered() -> void:
	var info := SaveSlotInfo.from_dict({"slot": 1, "status": "ok", "chapter": 3})
	assert_eq(info.chapter_text(), String(TranslationServer.translate("SAVE_SLOT_CHAPTER_FMT")).format({"n": 3}))
	assert_true("3" in info.chapter_text())


## Act II (M4-A2P-082): a save made after the wedding trap says so on its chapter line, quietly.
func test_a_heretic_save_carries_its_tag() -> void:
	var info := SaveSlotInfo.from_dict({"chapter": 14, "heretic": true})
	assert_eq(
		info.chapter_text(),
		tr("SAVE_SLOT_HERETIC_FMT").format({"chapter": tr("SAVE_SLOT_CHAPTER_FMT").format({"n": 14})})
	)
	assert_eq(SaveSlotInfo.from_dict({"chapter": 13}).chapter_text(), tr("SAVE_SLOT_CHAPTER_FMT").format({"n": 13}))


## The field menu's title row carries the heretic subtitle once the flag is set, and never before.
func test_the_field_menu_says_heretics_after_the_trap() -> void:
	var state := GameStateData.new()
	var menu := ParityHost.open_field_menu(state)
	assert_false(_shows(menu, tr("FIELD_MENU_SUBTITLE_HERETIC")), "before the trap: no subtitle")
	ParityHost.free_field_menu(menu)
	state.flags["ch14_declared_heretics"] = true
	menu = ParityHost.open_field_menu(state)
	assert_true(_shows(menu, tr("FIELD_MENU_SUBTITLE_HERETIC")), "after it: the subtitle on the title row")
	ParityHost.free_field_menu(menu)


static func _shows(root: Node, text: String) -> bool:
	for l in root.find_children("*", "Label", true, false):
		if (l as Label).text == text and (l as Label).is_visible_in_tree():
			return true
	return false
