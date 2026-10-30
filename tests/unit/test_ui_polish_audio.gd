extends TestCase
## The Lead's 10-30 18:24 polish pass (the slice path, as played): every menu action is heard. Every ui_sfx.json hook's
## watch expressions parse (a typo there is silence, not an error), and the Kite's flight map, which had only the
## field submenu's open and close, now says its cursor, its pages and the flight chosen. Rows are recorded through the
## listener's player Callable, so nothing plays.

var played: Array[StringName] = []
var _host: Node


func before_each() -> void:
	played = []
	_host = Node.new()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(_host)


func _done() -> void:
	_host.free()


func _ui() -> UiAudio:
	var ui := UiAudio.new(AudioData.table(AudioData.UI_SFX))
	ui.player = func(id: StringName) -> void: played.append(id)
	_host.add_child(ui)
	return ui


func test_every_hook_expression_parses() -> void:
	var table := AudioData.table(AudioData.UI_SFX)
	var bank := AudioData.sfx_rows()
	for hook: Dictionary in table.get("hooks", []):
		for row: Variant in hook.get("watch", []):
			var e := Expression.new()
			var expr := str((row as Dictionary).get("expr", ""))
			assert_eq(e.parse(expr, ["node"]), OK, "%s: `%s` parses" % [hook.get("class"), expr])
		for sig: String in hook.get("signals", {}) as Dictionary:
			var id := str(hook["signals"][sig])
			assert_true(bank.has(id), "%s.%s plays a real row (%s)" % [hook.get("class"), sig, id])
	_done()


func test_the_kite_map_says_its_cursor_its_pages_and_the_flight() -> void:
	var ui := _ui()
	var menu := KiteMapMenu.open_in(_host, KiteMapShot.fixed_model())
	ui.watch(menu)
	ui.step()
	assert_true(played.has(&"ui_menu_open"), "it opens as a field page (%s)" % [played])
	played.clear()
	menu.cell += Vector2i(1, 0)
	ui.step()
	assert_eq(played, [&"ui_cursor"] as Array[StringName], "the chart's cursor ticks")
	played.clear()
	menu.flight_chosen.emit(&"haluna")
	ui.step()
	assert_eq(played, [&"ui_confirm"] as Array[StringName], "a flight chosen confirms")
	_done()
