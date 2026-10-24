extends TestCase
## M2-AUD-05: field audio. The ambience beds loop and ambience.json's beds reach a zone where music.json names none
## (day, night, the wind bed scaled by the zone's wind); FootstepAudio's strides on a walker; the director hangs a
## FootstepAudio on a real FieldController; and UiAudio plays ui_sfx.json's rows from a real CommandMenu and
## FieldMenu, one row a frame by priority.

const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const SHRINE := "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"
const NIGHT := &"ch03_drownbell_defeated"
const BEDS: Array[String] = ["haluna_day", "haluna_night", "surf", "dock", "shrine_interior", "wind"]
const MIX := {"buses": [{"name": "Ambience", "send": "Master"}], "music": {"crossfade_sec": 1.0, "floor_db": -60.0}}
const MUSIC := {
	"cues": {"a": {"file": "res://assets/audio/music/temple_trial.ogg"}},
	"ambience": {},
	"zones": [{"scene": SHRINE, "music": "a", "ambience": []}],
	"battle": {"default": "a"},
}
const STEPS := {
	"walk_step_m": 1.0,
	"run_step_m": 1.6,
	"run_above_m_s": 3.5,
	"walk_db": -3.0,
	"run_db": 0.0,
	"first_step": 0.5,
	"stop_sec": 0.2,
	"still_m": 0.001,
	"teleport_m": 3.0,
	"speed_smooth_sec": 0.05,
	"surfaces": {"sand": "step_sand", "stone": "step_stone"},
	"default": "stone",
	"scenes": {HALUNA: "sand"},
}
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}


class Walker:
	extends Node3D
	var on_ground := true

	func grounded() -> bool:
		return on_ground


var played: Array = []


func before_each() -> void:
	played = []


func test_beds_import_as_loops_of_40_to_70_s() -> void:
	var amb := AudioData.table(AudioData.AMBIENCE)
	for id in BEDS:
		var row := (amb["ambience"] as Dictionary).get(id, {}) as Dictionary
		var s := load(str(row.get("file", ""))) as AudioStreamOggVorbis
		assert_true(s != null, "%s imports as Ogg Vorbis" % id)
		if s == null:
			continue
		assert_true(s.loop, "%s loops" % id)
		assert_eq(s.loop_offset, 0.0, "%s loops from its start" % id)
		assert_between(s.get_length(), 40.0, 70.0, "%s length" % id)
	_done()


func test_wind_level_follows_the_zone_wind() -> void:
	var amb := {"wind": {"bed": "wind", "min_m_s": 2.0, "max_m_s": 10.0, "min_db": -18.0, "max_db": 0.0}}
	assert_eq(AudioData.wind_db(amb, 0.0), -18.0, "calm: the floor")
	assert_eq(AudioData.wind_db(amb, 6.0), -9.0, "halfway")
	assert_eq(AudioData.wind_db(amb, 14.0), 0.0, "a gale: the ceiling")
	_done()


func test_zone_beds_merge_by_day_and_night_unless_music_names_some() -> void:
	var amb := AudioData.table(AudioData.AMBIENCE)
	var no := func(_f: StringName) -> bool: return false
	var yes := func(f: StringName) -> bool: return f == NIGHT
	var day := AudioData.merge_zone_beds({}, amb, HALUNA, no)
	assert_eq(day["ambience"], ["haluna_day", "surf", "wind"], "Haluna by day, with its wind")
	assert_false(day.has("music"), "no music key: the music is left as it is")
	var night := AudioData.merge_zone_beds({}, amb, HALUNA, yes)
	assert_eq(night["ambience"], ["haluna_night", "surf", "dock", "wind"], "after the Drownbell: the night dock")
	var shrine := AudioData.merge_zone_beds({"music": "a", "ambience": []}, amb, SHRINE, no)
	assert_eq(shrine["ambience"], ["shrine_interior"], "an empty music.json list takes ambience.json's beds")
	assert_eq(str(shrine["music"]), "a", "and keeps its music")
	var own := AudioData.merge_zone_beds({"ambience": ["x"]}, amb, SHRINE, no)
	assert_eq(own["ambience"], ["x"], "music.json's own beds win")
	assert_true(AudioData.merge_zone_beds({}, amb, "res://nowhere.tscn", no).is_empty(), "no row, no beds")
	assert_true(AudioData.bed_rows({"ambience": {"wind": {"file": "x"}}}, amb)["wind"]["file"] == "x", "clash")
	_done()


func test_the_director_plays_haluna_beds_with_the_wind_scaled() -> void:
	var dir := _director()
	dir.flag_reader = func(_f: StringName) -> bool: return false
	dir.apply_zone(HALUNA)
	for id: StringName in [&"haluna_day", &"surf", &"wind"]:
		assert_true(dir.beds.has(id) and (dir.beds[id] as FadeVoice).target == 1.0, "%s fades in" % id)
	var w := WeatherClock.zone_wind(HALUNA)
	var want := AudioData.wind_db(dir.ambience_data, Vector3(w.x, w.y, w.z).length())
	assert_between(want, -17.9, -0.1, "Haluna's trade wind sits inside the range")
	assert_eq((dir.beds[&"wind"] as FadeVoice).base_db, want, "the wind bed's level")
	assert_eq((dir.beds[&"surf"] as FadeVoice).base_db, 0.0, "the other beds at their own level")
	dir.flag_reader = func(f: StringName) -> bool: return f == NIGHT
	dir.apply_zone(HALUNA)
	assert_eq((dir.beds[&"haluna_day"] as FadeVoice).target, 0.0, "night: the day bed fades out")
	assert_true(dir.beds.has(&"dock") and (dir.beds[&"dock"] as FadeVoice).target == 1.0, "and the dock comes in")
	dir.apply_zone(SHRINE)
	dir.flush_pending()  # zone music loads on a worker thread
	assert_eq(dir.music.current, &"a", "the shrine's music.json row still plays its cue")
	assert_eq((dir.beds[&"shrine_interior"] as FadeVoice).target, 1.0, "under its interior bed")
	assert_eq((dir.beds[&"wind"] as FadeVoice).target, 0.0, "and no wind indoors")
	dir.free()
	_done()


func test_footsteps_walk_run_and_stop() -> void:
	var w := Walker.new()
	_host().add_child(w)
	var f := FootstepAudio.new(STEPS)
	f.player = func(id: StringName, at: Vector3, opts: Dictionary) -> void: played.append([id, at, opts])
	f.attach(w, HALUNA)
	assert_eq(f.surface, &"sand", "Haluna is sand")
	assert_eq(FootstepAudio.surface_for(STEPS, "res://elsewhere.tscn"), &"stone", "else the default")
	_walk(f, w, 2.4, 10.0)
	assert_eq(played.size(), 10, "a 10 m walk at 1 m strides, the first half a stride in")
	assert_eq(played[0][0], &"step_sand", "on the scene's surface")
	assert_eq(float((played[0][2] as Dictionary)["volume_db"]), -3.0, "walking is quieter")
	assert_between((played[-1][1] as Vector3).x, 9.45, 9.55, "at the walker's feet as it takes the step")
	played.clear()
	_still(f, 0.5)
	_walk(f, w, 4.6, 8.0)
	assert_eq(played.size(), 5, "8 m at 1.6 m strides after a stop restarts half a (walk) stride in")
	assert_eq(float((played[-1][2] as Dictionary)["volume_db"]), 0.0, "a run at full level")
	played.clear()
	w.on_ground = false
	_walk(f, w, 2.4, 5.0)
	assert_eq(played.size(), 0, "no steps in the air")
	w.on_ground = true
	w.global_position += Vector3(20.0, 0.0, 0.0)
	f.advance(1.0 / 60.0)
	assert_eq(played.size(), 0, "a warp is not walked")
	w.free()
	f.free()
	_done()


func test_the_director_hangs_footsteps_on_a_field_controller() -> void:
	var dir := _director()
	dir.footstep_data = STEPS
	dir.zone_path = HALUNA
	var ctl := FieldController.new()
	_host().add_child(ctl)
	dir.attach_footsteps(ctl)
	var l := dir.listeners.get(ctl) as FootstepAudio
	assert_true(l != null and l.walker == ctl, "a FootstepAudio listens to the controller")
	assert_eq(l.surface if l != null else &"", &"sand", "on the zone's surface")
	dir.attach_footsteps(ctl)
	assert_eq(dir.get_children().filter(func(n: Node) -> bool: return n is FootstepAudio).size(), 1, "only one")
	ctl.global_position = Vector3(0.5, 0.0, 0.0)
	dir.advance(1.0 / 60.0)
	assert_eq(ctl.global_position, Vector3(0.5, 0.0, 0.0), "listening never moves it")
	ctl.free()
	dir.advance(1.0 / 60.0)
	assert_false(dir.listeners.has(ctl), "a freed controller drops its listener")
	dir.free()
	_done()


func test_ui_hooks_play_a_command_menu_by_priority() -> void:
	var ui := _ui()
	var menu := CommandMenu.new()
	_host().add_child(menu)
	menu.open_root(&"root", "Rhen", _rows(["attack", "skills", "escape"]))
	assert_true(ui.wants(menu), "CommandMenu has a hook")
	ui.watch(menu)
	ui.step()
	played.clear()
	menu.move_cursor(1)
	ui.step()
	assert_eq(played, [&"ui_cursor"], "a cursor move")
	menu.accept()
	ui.step()
	menu.cancel()
	ui.step()
	assert_eq(played.slice(1), [&"ui_confirm", &"ui_cancel"], "chosen and cancelled")
	played.clear()
	menu.open_root(&"root", "Ilun", _rows(["attack", "unleash", "dismiss"]))
	ui.step()
	assert_eq(played, [&"ui_vowbound_open"], "the Vowbound's page: the glass tone, not the cursor tick as well")
	menu.open_root(&"root", "Ilun", _rows(["attack", "unleash", "dismiss"]))
	ui.step()
	assert_eq(played.size(), 2, "a new Vowbound page sounds again")
	played.clear()
	menu.open_root(&"root", "Asha", _rows(["attack", "skills"]))
	ui.step()
	assert_eq(played, [&"ui_cursor"], "back to a hero's page: just the cursor")
	menu.free()
	ui.step()
	assert_eq(ui.watched.size(), 0, "a freed menu is dropped")
	ui.free()
	_done()


func test_ui_hooks_play_the_field_menu() -> void:
	var ui := _ui()
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(FieldMenuModel.new(GameStateData.new(), [&"rhen", &"asha", &"toma"], NAMES))
	_host().add_child(menu)
	ui.watch(menu)
	ui.step()
	assert_eq(played, [&"ui_menu_open"], "opening")
	played.clear()
	# M2-MNU-01..03: Equip (the second root row) opens a FieldSubmenu child; opening and closing it are heard.
	menu.handle_input(_ev(&"ui_down"))
	ui.step()
	assert_eq(played.back() if not played.is_empty() else &"", &"ui_cursor", "ui_down plays ui_cursor")
	played.clear()
	menu.handle_input(_ev(&"ui_accept"))
	ui.step()
	assert_true(menu.child != null, "Equip opens its page")
	assert_eq(played.back() if not played.is_empty() else &"", &"ui_confirm", "opening a page plays ui_confirm")
	played.clear()
	if menu.child != null:
		menu.child.close()
	ui.step()
	assert_eq(played.back() if not played.is_empty() else &"", &"ui_cancel", "closing it plays ui_cancel")
	played.clear()
	# Then down to the Swell row, whose hero and mode pages are the menu's own levels.
	var swell := -1
	for i in menu.root_page().rows.size():
		if StringName(str(menu.root_page().rows[i].get("id", ""))) == FieldMenuModel.ROW_SWELL:
			swell = i
	assert_true(swell > menu.root_page().cursor, "the Swell row is below Equip")
	while menu.root_page().cursor < swell:
		menu.handle_input(_ev(&"ui_down"))
		ui.step()
		assert_eq(played.back() if not played.is_empty() else &"", &"ui_cursor", "ui_down plays ui_cursor")
		played.clear()
	for step: Array in [
		[&"ui_accept", &"ui_confirm"],
		[&"ui_down", &"ui_cursor"],
		[&"ui_accept", &"ui_confirm"],
		[&"ui_down", &"ui_cursor"],
		[&"ui_accept", &"ui_confirm"],
		[&"ui_cancel", &"ui_cancel"],
		[&"ui_cancel", &"ui_cancel"],
		[&"ui_cancel", &"ui_menu_close"],
	]:
		menu.handle_input(_ev(step[0]))
		ui.step()
		assert_eq(played.back() if not played.is_empty() else &"", step[1], "%s plays %s" % step)
		played.clear()
	menu.free()
	ui.free()
	_done()


func test_change_rows_and_pending_hooks() -> void:
	assert_eq(UiAudio.change_row({"rise": "a", "fall": "b"}, 0, 1), &"a")
	assert_eq(UiAudio.change_row({"rise": "a", "fall": "b"}, 2, 1), &"b")
	assert_eq(UiAudio.change_row({"values": {"2": "e"}, "sfx": "s"}, 0, 2), &"e")
	assert_eq(UiAudio.change_row({"values": {"2": "e"}, "sfx": "s"}, 0, 3), &"s")
	assert_eq(UiAudio.change_row({"sfx": "s", "on_true": true}, 5, 0), &"")
	var hooks := _ui()
	assert_true(hooks.hooks.has("ShopMenu") and hooks.hooks.has("InnMenu"), "the shop and inn rows wait for M2-UI-06")
	var rows := AudioData.sfx_rows()
	for id: StringName in hooks.priority:
		assert_true(rows.has(String(id)), "priority row %s exists" % id)
	hooks.free()
	_done()


# --------------------------------------------------------------------------- helpers


func _director() -> AudioDirector:
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.setup(MIX, MUSIC, {"sfx": AudioData.sfx_rows()}, AudioData.table(AudioData.AMBIENCE))
	dir.set_process(false)
	return dir


func _ui() -> UiAudio:
	var ui := UiAudio.new(AudioData.table(AudioData.UI_SFX))
	ui.player = func(id: StringName) -> void: played.append(id)
	_host().add_child(ui)
	return ui


func _walk(f: FootstepAudio, w: Node3D, speed: float, metres: float) -> void:
	var dt := 1.0 / 60.0
	var n := int(round(metres / (speed * dt)))
	f.advance(dt)
	for i in n:
		w.global_position += Vector3(speed * dt, 0.0, 0.0)
		f.advance(dt)


func _still(f: FootstepAudio, sec: float) -> void:
	for i in int(sec * 60.0):
		f.advance(1.0 / 60.0)


func _rows(ids: Array) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id: String in ids:
		out.append({"id": StringName(id), "label": id})
	return out


func _ev(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	pass
