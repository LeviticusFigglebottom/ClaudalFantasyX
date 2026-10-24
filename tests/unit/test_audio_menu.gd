extends TestCase
## M3-UI-02: the Audio settings page. The Audio track's volume rows and reduced_audio are in accessibility.json
## (merged at big8); the hub's "no audio rows" case uses a scratch copy of the file with them taken out.

const SCRATCH := "user://test_audio_menu_accessibility.json"
const VOLUMES: Array[StringName] = [&"master_volume", &"music_volume", &"sfx_volume", &"voice_volume"]

var s: UiSettings
var made: Array[Node] = []


func before_each() -> void:
	s = UiSettings.new()
	UiSettings.set_shared(s)


## UiSettings over a scratch accessibility.json with none of audio_menu.json's rows.
func _without_audio_rows() -> UiSettings:
	var parsed: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(UiSettings.DATA_PATH))
	var acc: Dictionary = parsed["accessibility"]
	var ids := AudioMenuModel.audio_ids()
	acc["settings"] = (acc["settings"] as Array).filter(
		func(r: Dictionary) -> bool: return not ids.has(StringName(r["id"]))
	)
	var f := FileAccess.open(SCRATCH, FileAccess.WRITE)
	f.store_string(JSON.stringify(parsed))
	f.close()
	return UiSettings.new(SCRATCH)


func test_the_page_lists_the_volumes_and_accessibility_leaves_them_out() -> void:
	var audio := AudioMenuModel.new(s, "")
	var want: Array[StringName] = VOLUMES.duplicate()
	want.append(&"reduced_audio")
	assert_eq(audio.row_ids(), want, "audio_menu.json order")
	assert_eq(audio.title_key(), "SET_MENU_AUDIO")
	var acc := AccessibilityMenuModel.new(s, "")
	for id in VOLUMES:
		assert_false(acc.row_ids().has(id), "%s is on the Audio page only" % id)
	assert_true(acc.row_ids().has(UiSettings.TEXT_SCALE))
	audio.set_cursor(1)
	assert_true(audio.cycle(-1))
	assert_true(is_equal_approx(float(s.get_value(&"music_volume")), 0.9), "a step down")
	_done()


func test_the_hub_shows_audio_only_when_there_are_audio_rows() -> void:
	var hub := _hub(s)
	assert_eq(
		hub.row_ids(),
		[SettingsMenu.ROW_GRAPHICS, SettingsMenu.ROW_AUDIO, SettingsMenu.ROW_ACCESSIBILITY, SettingsMenu.ROW_CONTROLS]
	)
	_free()
	var bare := _hub(_without_audio_rows())
	assert_false(bare.row_ids().has(SettingsMenu.ROW_AUDIO), "no volume rows yet: no Audio row")
	_done()


func test_audio_page_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var hub := _hub(s)
		var at := hub.row_ids().find(SettingsMenu.ROW_AUDIO)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(hub._list.row_node(at))
			InputDriver.click(hub._list.row_node(at))
		else:
			d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_true(hub.page is AudioMenu, "%s: Audio opens" % d.label())
		var page := hub.page as AudioMenu
		var row := page.model.current()
		var before: Variant = s.get_value(row)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(page._page.row_node(page.model.cursor))
		else:
			d.press(&"ui_left")
		assert_ne(s.get_value(row), before, "%s: the volume steps" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.right_click(page)
		else:
			d.press(&"ui_cancel")
		assert_false(hub.is_page_open(), "%s: Cancel backs out" % d.label())
		_free()
		s.reset()
	_done()


func _hub(with: UiSettings) -> SettingsMenu:
	var hub := SettingsMenu.new()
	hub.ui_settings = with
	hub.save_path = ""
	var vp := SubViewport.new()
	hub.graphics_viewport = vp
	_add(vp)
	_add(hub)
	return hub


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _free() -> void:
	for n in made:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func _done() -> void:
	_free()
	DirAccess.remove_absolute(SCRATCH)
	UiSettings.set_shared(null)
