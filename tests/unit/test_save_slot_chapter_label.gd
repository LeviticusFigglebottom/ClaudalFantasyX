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
