extends TestCase
## M5-A3P-1001: ChapterRegistry picks a zone's story block by the story's chapter when more than one chapter file
## has the zone (Act III comes back to Ch15's Hollowmere and to Act I's towns); with one file it is that file.

const DIR := "user://test_chapter_registry/"


func before_each() -> void:
	DirAccess.make_dir_recursive_absolute(DIR)
	var ch15 := {"ch17/hollowmere": {"doc": "ch15"}, "ch15/open_sea": {"doc": "sea"}}
	_write("ch15.json", {"chapter": "ch15", "zones": ch15})
	_write("ch16.json", {"chapter": "ch16", "zones": {"ch16/pale_rim": {"doc": "rim"}}})
	_write("ch17.json", {"chapter": "ch17", "zones": {"ch17/hollowmere": {"doc": "ch17"}}})


func test_one_file_with_the_zone_is_that_file_at_any_chapter() -> void:
	for chapter in [0, 15, 16, 30]:
		assert_eq(
			ChapterRegistry.zone_in(_paths(), &"ch15/open_sea", chapter).get("doc"), "sea", "chapter %d" % chapter
		)


func test_a_shared_zone_belongs_to_the_current_chapter_or_the_next() -> void:
	assert_eq(ChapterRegistry.zone_in(_paths(), &"ch17/hollowmere", 15).get("doc"), "ch15", "Ch15 reaches Hollowmere")
	assert_eq(ChapterRegistry.zone_in(_paths(), &"ch17/hollowmere", 16).get("doc"), "ch17", "out of Ch16: Ch17's")
	assert_eq(ChapterRegistry.zone_in(_paths(), &"ch17/hollowmere", 17).get("doc"), "ch17", "Ch17's own")
	assert_eq(ChapterRegistry.zone_in(_paths(), &"ch17/hollowmere", 0).get("doc"), "ch15", "no chapter yet: the first")


func test_past_every_file_it_falls_back_to_the_first() -> void:
	assert_eq(ChapterRegistry.zone_in(_paths(), &"ch17/hollowmere", 18).get("doc"), "ch15")
	assert_true(ChapterRegistry.zone_in(_paths(), &"nowhere", 17).is_empty())


func test_a_pinned_file_gives_way_to_a_later_chapters() -> void:
	_write("ch18.json", {"chapter": "ch18", "zones": {"ch17/hollowmere": {"doc": "ch18"}}})
	var paths := _paths()
	paths.append(DIR + "ch18.json")
	var pin := DIR + "ch17.json"
	assert_eq(
		ChapterRegistry.zone_pinned(paths, &"ch17/hollowmere", pin, 16).get("doc"), "ch17", "out of Ch16: the pin"
	)
	assert_eq(ChapterRegistry.zone_pinned(paths, &"ch17/hollowmere", pin, 17).get("doc"), "ch17", "Ch17: the pin")
	assert_eq(ChapterRegistry.zone_pinned(paths, &"ch17/hollowmere", pin, 18).get("doc"), "ch18", "Ch18 comes back")
	assert_eq(
		ChapterRegistry.zone_pinned(paths, &"ch17/hollowmere", pin, 19).get("doc"), "ch17", "no later file: the pin"
	)
	assert_eq(ChapterRegistry.zone_pinned(paths, &"ch17/hollowmere", "", 18).get("doc"), "ch18", "no pin: by chapter")


func test_chapter_numbers() -> void:
	assert_eq(ChapterRegistry.chapter_number("ch17"), 17)
	assert_eq(ChapterRegistry.chapter_number("ch04"), 4)
	assert_eq(ChapterRegistry.chapter_number(""), 0)
	assert_eq(ChapterRegistry.chapter_number("chx"), 0)


func _paths() -> PackedStringArray:
	return PackedStringArray([DIR + "ch15.json", DIR + "ch16.json", DIR + "ch17.json"])


func _write(name: String, data: Dictionary) -> void:
	var f := FileAccess.open(DIR + name, FileAccess.WRITE)
	f.store_string(JSON.stringify(data))
	f.close()
