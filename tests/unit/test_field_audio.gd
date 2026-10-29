extends TestCase
## M2-AUD-05: field audio. The ambience beds loop and ambience.json's beds reach a zone where music.json names none
## (day, night, the wind bed scaled by the zone's wind); FootstepAudio's strides on a walker; the director hangs a
## FootstepAudio on a real FieldController; and UiAudio plays ui_sfx.json's rows from the real menus (CommandMenu,
## FieldMenu and, M2-AUD-17, the pages claude/menus brought: Lattice, Equip, Items, Status, the battle pause, the
## shop, the inn, the zone map and the tip card), one row a frame by priority. Stand-ins only where a class is absent
## or cannot do the thing yet.

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
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]


class Walker:
	extends Node3D
	var on_ground := true

	func grounded() -> bool:
		return on_ground


# M2-AUD-14: stand-ins for the classes not on this branch yet (Formation) and for what the real ones cannot do yet
# (a pan: ZoneMapView fits the zone; the title's launch changes the scene). They carry only the names ui_sfx.json's
# hooks read, and name their hook with the `audio_class` meta (no class_name stubs: they would collide on merge).
class PageStandIn:
	extends RefCounted
	var cursor := 0


class MapViewStandIn:
	extends Control
	signal poi_clicked(poi_id: StringName)
	var origin := Vector2.ZERO
	var px_per_m := 1.0

	func map_point(world: Vector2) -> Vector2:
		return origin + world * px_per_m

	func map_scale() -> float:
		return px_per_m


class TitleModelStandIn:
	extends RefCounted
	var cursor := 0
	var confirm_cursor := 0
	var confirming := false


class TitleStandIn:
	extends Control
	signal chosen(choice: StringName, error: int)
	var model := TitleModelStandIn.new()
	var launched := false

	func is_launched() -> bool:
		return launched


class FormationModelStandIn:
	extends RefCounted
	var active: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var reserve: Array[StringName] = [&"ysolde"]


class FormationStandIn:
	extends Control
	signal closed
	var focus: StringName = &"active"
	var chosen: Dictionary = {}
	var model := FormationModelStandIn.new()
	var pages: Dictionary = {&"active": PageStandIn.new(), &"reserve": PageStandIn.new()}

	func focus_page() -> PageStandIn:
		return pages[focus]


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


func test_change_rows_and_live_hooks() -> void:
	assert_eq(UiAudio.change_row({"rise": "a", "fall": "b"}, 0, 1), &"a")
	assert_eq(UiAudio.change_row({"rise": "a", "fall": "b"}, 2, 1), &"b")
	assert_eq(UiAudio.change_row({"values": {"2": "e"}, "sfx": "s"}, 0, 2), &"e")
	assert_eq(UiAudio.change_row({"values": {"2": "e"}, "sfx": "s"}, 0, 3), &"s")
	assert_eq(UiAudio.change_row({"sfx": "s", "on_true": true}, 5, 0), &"")
	var hooks := _ui()
	var rows := AudioData.sfx_rows()
	for id: StringName in hooks.priority:
		assert_true(rows.has(String(id)), "priority row %s exists" % id)
	# M2-AUD-17: a hook is pending exactly while its class is missing from this branch.
	var classes: Array[String] = []
	for c: Dictionary in ProjectSettings.get_global_class_list():
		classes.append(str(c["class"]))
	for cls: String in hooks.hooks:
		var pending := bool((hooks.hooks[cls] as Dictionary).get("pending", false))
		assert_eq(pending, not classes.has(cls), "%s: pending only while its class is absent" % cls)
	hooks.free()
	_done()


func test_new_menu_rows_exist_and_the_pages_are_live() -> void:
	var ui := _ui()
	var rows := AudioData.sfx_rows()
	for cls: String in [
		"ShopMenu",
		"InnMenu",
		"FieldSubmenu",
		"LatticeMenu",
		"EquipMenu",
		"ZoneMapMenu",
		"ZoneMapView",
		"TipCard",
		"ItemsMenu",
		"StatusMenu",
		"BattlePauseMenu",
		"FormationMenu",
		"MemoriesMenu"
	]:
		assert_true(ui.hooks.has(cls), "%s has a hook" % cls)
		assert_false(
			bool((ui.hooks[cls] as Dictionary).get("pending", false)), "%s is live (M2-AUD-17, M2-MNU-303)" % cls
		)
	for id: String in [
		"ui_lattice_node",
		"ui_lattice_unlock",
		"ui_lattice_step",
		"ui_equip",
		"ui_unequip",
		"ui_map_open",
		"ui_map_close",
		"ui_map_tick",
		"ui_map_marker",
		"ui_tip",
		"ui_title_confirm",
		"ui_title_swell",
		"ui_item_use",
		"ui_item_sort",
		"ui_formation_pick",
		"ui_formation_swap",
		"ui_customize_open",
		"ui_craft",
		"ui_map_pan"
	]:
		assert_true(rows.has(id), "row %s" % id)
		assert_true(ResourceLoader.exists(str((rows[id]["files"] as Array)[0])), "%s's file imports" % id)
		assert_eq(str(rows[id]["bus"]), "UI", "%s on UI" % id)
		assert_true(ui.priority.has(StringName(id)), "%s is ranked" % id)
	ui.free()
	_done()


func test_ui_hooks_play_the_real_lattice_page() -> void:
	var ui := _ui()
	var state := GameStateData.new()
	state.inventory = {"facet_speed": 1}
	var menu := LatticeMenu.create(PartySheet.new(state, PARTY))
	menu.pause_tree = false
	_watch_real(ui, menu)
	assert_eq(played, [&"ui_menu_open"], "the Lattice opens")
	menu.model.traveler().movement_points = 1
	_keys(
		ui,
		menu,
		[
			[&"ui_right", &"ui_cursor", "the cursor to the next node"],
			[&"ui_accept", &"ui_confirm", "Confirm asks before walking"],
			[&"ui_down", &"ui_cursor", "the question's rows"],
			[&"ui_cancel", &"ui_cancel", "Cancel steps back from the question"],
			[&"ui_accept", &"ui_confirm", "asked again"],
			[&"ui_accept", &"ui_lattice_step", "walked: the step, not the question closing"],
			[&"ui_accept", &"ui_confirm", "standing on it: wake it?"],
			[&"ui_accept", &"ui_lattice_node", "woken with its Facet: the bell"],
			[&"ui_right", &"ui_cursor", "on to the next node"],
			[&"ui_accept", &"ui_error", "no movement left: refused in words"],
			[&"ui_left", &"ui_cursor", "a move clears the refusal quietly"],
		]
	)
	assert_eq(menu.model.position(), &"rh_01", "the walk was real")
	assert_true(menu.model.progress().is_activated_by(&"rhen", &"rh_01"), "and so was the wake")
	menu.model.traveler().movement_points = 6
	menu.set_cursor(&"rh_06", false)
	menu.request_act()
	menu.choose(0)
	ui.step()
	assert_eq(menu.model.position(), &"rh_06", "beside the gate")
	menu.model.facets().add(&"facet_key_1", 1)
	menu.set_cursor(&"rh_07", false)
	menu.request_act()
	ui.step()
	played.clear()
	menu.choose(0)
	ui.step()
	assert_eq(played, [&"ui_lattice_unlock"], "the gate opens with its Key")
	_keys(
		ui,
		menu,
		[
			[&"ui_page_down", &"ui_page", "another hero: a page, no wake or walk"],
			[&"ui_cancel", &"ui_menu_close", "the Lattice closes"],
		]
	)
	_free_real(menu)
	ui.free()
	_done()


func test_ui_hooks_play_the_real_equip_and_customize_page() -> void:
	var ui := _ui()
	var sheet := PartySheet.new(GameStateData.new(), PARTY)
	var bag := sheet.goods.equipment
	bag.grant_starting(&"rhen")  # the starting weapon and armor first, as opening the page would
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	bag.equip(&"rhen", hooks)
	var spare := bag.add_piece(&"rhen_coral_hooks")
	sheet.goods.inventory.add(&"tide_pearl", 4)
	var menu := EquipMenu.create(sheet)
	menu.pause_tree = false
	_watch_real(ui, menu)
	assert_eq(played, [&"ui_menu_open"], "Equip opens")
	_keys(
		ui,
		menu,
		[
			[&"ui_down", &"ui_cursor", "the next hero"],
			[&"ui_up", &"ui_cursor", "back to Rhen"],
			[&"ui_accept", &"ui_confirm", "into Rhen's gear"],
			[&"ui_right", &"ui_cursor", "Right: the next hero's gear"],
			[&"ui_left", &"ui_cursor", "and back"],
			[&"ui_down", &"ui_cursor", "the weapon's first ability slot (Ember Edge)"],
			[&"ui_accept", &"ui_error", "a filled slot is refused"],
			[&"ui_down", &"ui_cursor", "the empty slot (the refusal clears)"],
			[&"ui_accept", &"ui_customize_open", "Customize's recipes"],
			[&"ui_accept", &"", "the first Confirm only asks (Customize arms it in private)"],
			[&"ui_accept", &"ui_craft", "the second crafts, back to the gear: the hammer, not the cancel"],
			[&"ui_up", &"ui_cursor", "up the gear"],
			[&"ui_up", &"ui_cursor", "to the weapon"],
			[&"ui_accept", &"ui_confirm", "the pieces Rhen can wield"],
		]
	)
	assert_eq(bag.slots_of(hooks)[1], &"tide_edge", "the craft was real")
	_seek(ui, menu, func(r: Dictionary) -> bool: return int(r.get("uid", -1)) == spare, menu.choice_page())
	_keys(ui, menu, [[&"ui_accept", &"ui_equip", "the spare worn: the clasp, not the level's cancel"]])
	assert_eq(bag.equipped(&"rhen", ItemDB.SLOT_WEAPON), spare, "worn")
	_seek(ui, menu, func(r: Dictionary) -> bool: return str(r.get("id", "")) == "slot:armor", menu.gear_page())
	_keys(ui, menu, [[&"ui_accept", &"ui_confirm", "the armor"]])
	var remove := func(r: Dictionary) -> bool: return r.get("kind", &"") == EquipMenuModel.KIND_REMOVE
	_seek(ui, menu, remove, menu.choice_page())
	_keys(
		ui,
		menu,
		[
			[&"ui_accept", &"ui_unequip", "taken off"],
			[&"ui_cancel", &"ui_cancel", "back to the party"],
			[&"ui_cancel", &"ui_menu_close", "Equip closes"],
		]
	)
	_free_real(menu)
	ui.free()
	_done()


func test_ui_hooks_play_the_real_items_page() -> void:
	var ui := _ui()
	var state := GameStateData.new()
	state.party_ids = PARTY.duplicate()
	state.inventory = {"salt_tonic": 2, "quiet_tea": 1, "brass_lantern": 1}
	state.party_vitals = {"rhen": {"hp": 100}, "toma": {"hp": 10}}
	ItemsMenu.session_sort = ItemsMenuModel.SORT_KIND
	var menu := ItemsMenu.create(PartySheet.new(state, PARTY))
	menu.pause_tree = false
	_watch_real(ui, menu)
	assert_eq(played, [&"ui_menu_open"], "Items opens")
	_keys(
		ui,
		menu,
		[
			[&"ui_down", &"ui_cursor", "down the bag"],
			[&"ui_right", &"ui_item_sort", "a sort, not the cursor it moves"],
			[&"ui_left", &"ui_item_sort", "and back"],
		]
	)
	# M3-MNU-03: key items have their own tab.
	_keys(ui, menu, [[&"ui_page_down", &"ui_page", "the Key Items tab"]])
	_seek(ui, menu, func(r: Dictionary) -> bool: return r.get("id", &"") == &"brass_lantern", menu.list_page())
	_keys(ui, menu, [[&"ui_accept", &"", "a key item opens nothing (a refusal its line already said)"]])
	_keys(ui, menu, [[&"ui_page_up", &"ui_page", "back to the Bag tab"]])
	_seek(ui, menu, func(r: Dictionary) -> bool: return r.get("id", &"") == &"salt_tonic", menu.list_page())
	_keys(
		ui,
		menu,
		[
			[&"ui_accept", &"ui_confirm", "the picker opens"],
			[&"ui_accept", &"ui_item_use", "a tonic on Rhen"],
			[&"ui_down", &"ui_cursor", "Asha"],
			[&"ui_down", &"ui_cursor", "Toma"],
			[&"ui_accept", &"ui_item_use", "the last one: the use, not the picker's close"],
		]
	)
	assert_eq(menu.level, ItemsMenu.Level.LIST, "back to the bag")
	assert_eq(int(state.inventory.get("salt_tonic", 0)), 0, "both tonics spent")
	_keys(ui, menu, [[&"ui_cancel", &"ui_menu_close", "Items closes"]])
	_free_real(menu)
	ItemsMenu.session_sort = ItemsMenuModel.SORT_KIND
	ui.free()
	_done()


func test_ui_hooks_play_the_real_status_page() -> void:
	var ui := _ui()
	var menu := StatusMenu.create(PartySheet.new(GameStateData.new(), PARTY))
	menu.pause_tree = false
	_watch_real(ui, menu)
	assert_eq(played, [&"ui_menu_open"], "Status opens")
	_keys(
		ui,
		menu,
		[
			[&"ui_down", &"ui_page", "the next hero's sheet, not the list's tick as well"],
			[&"ui_right", &"ui_page", "Right does the same"],
			[&"ui_up", &"ui_page", "and back"],
			[&"ui_accept", &"", "nothing to confirm"],
			[&"ui_cancel", &"ui_menu_close", "Status closes"],
		]
	)
	_free_real(menu)
	ui.free()
	_done()


func test_ui_hooks_play_the_real_battle_pause() -> void:
	var ui := _ui()
	var menu := BattlePauseMenu.create()
	menu.pause_tree = false
	_watch_real(ui, menu)
	assert_eq(played, [&"ui_menu_open"], "the pause opens")
	_keys(
		ui,
		menu,
		[
			[&"ui_down", &"ui_cursor", "Settings"],
			[&"ui_accept", &"ui_confirm", "the Settings hub over the pause"],
		]
	)
	assert_true(menu.settings_menu != null, "the hub is open")
	played.clear()
	if menu.settings_menu != null:
		menu.settings_menu.close()
	ui.step()
	assert_eq(played, [&"ui_cancel"], "and hands back")
	_keys(
		ui,
		menu,
		[
			[&"ui_down", &"ui_cursor", "Quit"],
			[&"ui_accept", &"ui_confirm", "Quit asks first (Stay under the cursor)"],
			[&"ui_down", &"ui_cursor", "Quit to the title"],
			[&"ui_cancel", &"ui_cancel", "Cancel backs out of the question"],
			[&"ui_up", &"ui_cursor", "up"],
			[&"ui_up", &"ui_cursor", "to Resume"],
			[&"ui_accept", &"ui_menu_close", "Resume lifts the pause"],
		]
	)
	_free_real(menu)
	ui.free()
	_done()


func test_ui_hooks_play_the_real_shop_and_inn() -> void:
	var ui := _ui()
	var db := ItemDB.load_default()
	var state := GameStateData.new()
	state.currency = 100
	var flags := FlagReader.new()
	flags.values["ch02_met_asha"] = true
	var goods := PartyGoods.from_state(db, state)
	var shop := (load(ShopMenu.SCENE_PATH) as PackedScene).instantiate() as ShopMenu
	shop.pause_tree = false
	shop.configure(ShopMenuModel.new(db, Shop.new(db, &"haluna_market"), goods, flags, NAMES))
	_watch_real(ui, shop)
	assert_eq(played, [&"ui_menu_open"], "the shop opens")
	_keys(
		ui,
		shop,
		[
			[&"ui_down", &"ui_cursor", "Sell"],
			[&"ui_up", &"ui_cursor", "Buy"],
			[&"ui_accept", &"ui_confirm", "the stock"],
			[&"ui_right", &"ui_cursor", "two of them"],
			[&"ui_left", &"ui_cursor", "one"],
			[&"ui_accept", &"ui_buy", "a Salt Tonic bought"],
			[&"ui_cancel", &"ui_cancel", "back to the counter"],
			[&"ui_down", &"ui_cursor", "Sell"],
			[&"ui_accept", &"ui_confirm", "the bag"],
			[&"ui_accept", &"ui_buy", "the tonic sold back"],
			[&"ui_cancel", &"ui_cancel", "back to the counter"],
			[&"ui_cancel", &"ui_menu_close", "the shop closes"],
		]
	)
	assert_eq(goods.inventory.count(&"salt_tonic"), 0, "bought and sold for real")
	_free_real(shop)
	var healed: Array[StringName] = []
	var heal := func(source: StringName) -> void: healed.append(source)
	var inn := (load(InnMenu.SCENE_PATH) as PackedScene).instantiate() as InnMenu
	inn.pause_tree = false
	inn.configure(InnMenuModel.new(Inn.new(db, &"haluna_inn"), goods, flags, heal))
	_watch_real(ui, inn)
	assert_eq(played, [&"ui_menu_open"], "the inn opens")
	_keys(
		ui,
		inn,
		[
			[&"ui_down", &"ui_cursor", "Leave"],
			[&"ui_up", &"ui_cursor", "Rest"],
			[&"ui_accept", &"ui_inn_rest", "a night paid for, not the cursor's move to Leave"],
			[&"ui_cancel", &"ui_menu_close", "the inn closes"],
		]
	)
	assert_eq(healed.size(), 1, "the rest was real")
	_free_real(inn)
	ui.free()
	_done()


func test_ui_hooks_play_the_real_zone_map_and_tip_card() -> void:
	var ui := _ui()
	var page := (load(ZoneMapMenu.SCENE_PATH) as PackedScene).instantiate() as ZoneMapMenu
	page.pause_tree = false
	var on: Array[StringName] = [&"ch02_met_asha", &"ch02_tideline_won", &"ch02_ate_at_nemes"]
	var flag := func(f: StringName) -> bool: return on.has(f)
	page.configure(MapModel.new(&"ch02/haluna", Vector3(-8.0, 0.0, 6.0), PI * 0.5, flag))
	_watch_real(ui, page)
	ui.watch(page.view())
	ui.step()
	assert_eq(played, [&"ui_map_open"], "the map unrolls (the view alone plays nothing)")
	_keys(ui, page, [[&"ui_down", &"ui_map_tick", "a place in the legend ticks"]])
	played.clear()
	page.view().poi_clicked.emit(&"dock")
	ui.step()
	assert_eq(page.current_poi(), &"dock", "the click chose the dock")
	assert_eq(played, [&"ui_map_marker"], "a place clicked on the map: the pin, not the tick as well")
	_keys(ui, page, [[&"ui_cancel", &"ui_map_close", "the map rolls up"]])
	_free_real(page)
	played.clear()
	UiSettings.set_shared(UiSettings.new())
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()
	var seen: Dictionary = {&"ch02_met_asha": true}
	var card := TipCard.new()
	card.tips = TutorialTips.new(
		func(f: StringName) -> bool: return bool(seen.get(f, false)),
		func(f: StringName) -> void: seen[f] = true,
		func() -> bool: return true
	)
	_host().add_child(card)
	ui.watch(card)
	ui.step()
	var fade := float(TutorialTips.load_data()["fade_sec"]) + 0.01
	card.advance(0.0)
	ui.step()
	assert_eq(played, [&"ui_tip"], "the objective tip fades in")
	card.tips.raise_flag(&"ch02_tideline_won", true)
	for dt: float in [fade, card.hold_for(card.body_text()) + 0.01, fade, 0.0]:
		card.advance(dt)
		ui.step()
	assert_eq(played, [&"ui_tip", &"ui_tip"], "the next tip pops in once it fades in, and only then")
	_free_real(card)
	UiSettings.set_shared(null)
	InputNames.using_pad = false
	ui.free()
	_done()


func test_ui_hooks_play_the_title() -> void:
	var ui := _ui()
	var title := TitleStandIn.new()
	_watch(ui, title, "TitleMenu")
	assert_eq(played, [&"ui_title_swell"], "the title's first swell")
	played.clear()
	title.model.cursor = 1
	ui.step()
	title.launched = true
	title.chosen.emit(&"new_game", OK)
	ui.step()
	assert_eq(played, [&"ui_cursor", &"ui_title_confirm"], "Begin: the title's own confirm over chosen's")
	title.free()
	ui.free()
	_done()


func test_ui_hooks_play_formation_and_map_pan_stand_ins() -> void:
	var ui := _ui()
	var form := FormationStandIn.new()
	_watch(ui, form, "FormationMenu")
	assert_eq(played, [&"ui_menu_open"], "Formation opens")
	_play_steps(
		ui,
		[
			[func() -> void: form.pages[&"active"].cursor = 1, &"ui_cursor", "down the line"],
			[func() -> void: form.chosen = {"line": &"active", "index": 1}, &"ui_formation_pick", "Asha picked up"],
			[func() -> void: form.focus = &"reserve", &"ui_cursor", "across to the reserve"],
			[func() -> void: _swap(form), &"ui_formation_swap", "Asha and Ysolde trade places, not a cancel"],
			[func() -> void: form.chosen = {"line": &"reserve", "index": 0}, &"ui_formation_pick", "picked again"],
			[func() -> void: form.chosen = {}, &"ui_cancel", "put back: nothing moved"],
			[func() -> void: form.closed.emit(), &"ui_menu_close", "Formation closes"],
		]
	)
	assert_eq(ui.item_total(null), -1, "an unreadable bag reads -1")
	assert_eq(ui.crafted_count(null), -1, "an unreadable bag reads -1")
	assert_eq(ui.lattice_woken(null), -1, "an unreadable board reads -1")
	played.clear()
	var view := MapViewStandIn.new()
	_watch(ui, view, "ZoneMapView")
	assert_eq(played, [], "the view alone plays nothing")
	_play_steps(
		ui,
		[
			[func() -> void: view.origin = Vector2(40, 0), &"ui_map_pan", "a drag pans"],
			[func() -> void: view.origin = Vector2(41, 0), &"", "under 2 px: nothing yet"],
			[func() -> void: view.origin = Vector2(42.5, 0), &"ui_map_pan", "small moves add up"],
			[func() -> void: _zoom(view, 2.0, Vector2(10, 10)), &"", "a resize or a zoom is not a pan"],
			[func() -> void: view.origin = Vector2(10, 30), &"ui_map_pan", "a pan at the new scale"],
		]
	)
	assert_eq(ui.pans(null, Vector2.ZERO, 1.0, 1.0), -1, "no view reads -1")
	for n: Node in [form, view]:
		n.free()
	ui.step()
	assert_true(ui._pans.is_empty(), "a freed view's pans are forgotten")
	ui.free()
	_done()


func _play_steps(ui: UiAudio, steps: Array) -> void:
	for step: Array in steps:
		played.clear()
		(step[0] as Callable).call()
		ui.step()
		assert_eq(played.back() if not played.is_empty() else &"", step[1], step[2])


## Presses each [action, row, note] on a real menu and hears exactly that row (&"" for silence) that frame.
## M3-AUD-861 (ADR 0041): Act I's last unhooked screens, heard on the real classes.
func test_ui_hooks_play_the_real_codex_and_settings() -> void:
	var ui := _ui()
	FieldInput.ensure_actions()
	var codex := CodexMenu.open_in(_host())
	assert_true(ui.wants(codex), "CodexMenu has a hook")
	played.clear()
	ui.watch(codex)
	ui.step()
	assert_eq(played, [&"ui_page"], "the codex opens as a page")
	_keys(
		ui,
		codex,
		[[&"ui_down", &"ui_cursor", "a category"], [&"ui_cancel", &"ui_page", "back from the categories closes"]]
	)
	ui.step()
	var settings := SettingsMenu.open_in(_host())
	assert_true(ui.wants(settings), "SettingsMenu has a hook")
	played.clear()
	ui.watch(settings)
	ui.step()
	assert_eq(played, [&"ui_menu_open"], "the settings list opens")
	_keys(ui, settings, [[&"ui_down", &"ui_cursor", "the next settings page in the list"]])
	played.clear()
	settings.open_page(settings.row_ids()[0])
	ui.step()
	assert_true(played.has(&"ui_confirm"), "a settings page opening is a confirm (a bool watch, by `values`)")
	settings.close()
	ui.step()
	assert_eq(played.back(), &"ui_menu_close", "and closes")
	(Engine.get_main_loop() as SceneTree).paused = false
	for layer: Node in [codex.get_parent(), settings.get_parent()]:  # open_in's CanvasLayers
		if is_instance_valid(layer):
			layer.get_parent().remove_child(layer)
			layer.free()
	ui.free()


## M3-AUD-861: the Reefball outfitter (claude/ui, live since big14) heard on the real class: a cursor, a buy.
func test_ui_hooks_play_the_real_reefball_outfitter() -> void:
	var ui := _ui()
	FieldInput.ensure_actions()
	var state := GameStateData.new()
	state.currency = 1000
	var bag: Dictionary = {}
	var model := ReefballOutfitterModel.new(
		ReefballDB.load_default(),
		Wallet.new(state, 9999),
		func(f: StringName) -> Variant: return bag.get(f, ""),
		func(f: StringName, v: Variant) -> void: bag[f] = v
	)
	var menu := (load(ReefballOutfitterMenu.SCENE_PATH) as PackedScene).instantiate() as ReefballOutfitterMenu
	menu.configure(model)
	_watch_real(ui, menu)
	assert_eq(played, [&"ui_menu_open"], "the outfitter opens")
	played.clear()
	menu.accept()
	ui.step()
	assert_true(played.has(&"ui_buy"), "Confirm buys the first piece: %s" % [played])
	_keys(ui, menu, [[&"ui_down", &"ui_cursor", "the next piece"]])
	_free_real(menu)
	ui.free()


func test_ui_hooks_play_the_real_read_panel_and_objective_card() -> void:
	var ui := _ui()
	var panel := ReadPanel.new()
	_watch_real(ui, panel)
	panel.visible = false
	ui.step()
	played.clear()
	panel.visible = true
	ui.step()
	assert_eq(played, [&"ui_page"], "the Read panel turns in")
	panel.close()
	ui.step()
	assert_eq(played, [&"ui_page", &"ui_page"], "and out")
	_free_real(panel)
	played.clear()
	var hud := ObjectiveHud.new()
	_watch_real(ui, hud)
	played.clear()
	hud.phase = ObjectiveHud.Phase.IN
	ui.step()
	assert_eq(played, [&"ui_tip"], "an objective card fades in, heard as a tip")
	_free_real(hud)
	ui.free()


func _keys(ui: UiAudio, menu: Node, steps: Array) -> void:
	for step: Array in steps:
		played.clear()
		menu.call(&"handle_input", _ev(step[0]))
		ui.step()
		var want: Array = [] if step[1] == &"" else [step[1]]
		assert_eq(played, want, "%s: %s" % [step[0], step[2]])


## Presses ui_down on `menu` until `page`'s current row matches `pred`; every step is a cursor tick.
func _seek(ui: UiAudio, menu: Node, pred: Callable, page: MenuPage) -> void:
	for i in page.row_count():
		if pred.call(page.current_row()):
			return
		_keys(ui, menu, [[&"ui_down", &"ui_cursor", "seeking a row"]])
	assert_true(pred.call(page.current_row()), "the row was found")


func _swap(form: FormationStandIn) -> void:
	form.model.active[1] = &"ysolde"
	form.model.reserve[0] = &"asha"
	form.chosen = {}


func _zoom(view: MapViewStandIn, px_per_m: float, origin: Vector2) -> void:
	view.px_per_m = px_per_m
	view.origin = origin


func _watch(ui: UiAudio, node: Node, cls: String) -> void:
	node.set_meta(UiAudio.META_CLASS, cls)
	if node.get_parent() == null:
		_host().add_child(node)
	ui.watch(node)
	ui.step()


## A real menu: into the tree (its _ready builds it), watched by its own class name, its open heard.
func _watch_real(ui: UiAudio, node: Node) -> void:
	played.clear()
	_host().add_child(node)
	assert_true(ui.wants(node), "%s has a hook" % node.get_script().get_global_name())
	ui.watch(node)
	ui.step()


func _free_real(node: Node) -> void:
	if node.has_method(&"close"):
		node.call(&"close")
	if node.get_parent() != null:
		node.get_parent().remove_child(node)
	node.free()
	(Engine.get_main_loop() as SceneTree).paused = false


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
