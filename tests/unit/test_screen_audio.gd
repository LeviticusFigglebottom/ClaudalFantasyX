extends TestCase
## M3-AUD-832: the UI track's new screens by listening (ui_sfx.json): the menu motion whooshes on a real page, Reduced
## motion silencing them, `layer` and `initial` watch rows, the save slots, and stand-ins for the screens that are on
## claude/ui only (ShrineTravelMenu, ReefballHud, TitleMenu's reveal), each carrying the `audio_class` meta of the
## hook it stands in for (no class_name stubs: they would collide on merge). Sounds are recorded through the
## listener's player Callable, so nothing plays. The runner runs no frames: the tests drive the tweens themselves.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const DT := 1.0 / 60.0

var played: Array[StringName] = []
var _saved_settings: UiSettings
var _host: Node


class Rows:
	extends RefCounted
	var cursor := 0


class ShrineStandIn:
	extends Control
	signal travel_chosen(destination: StringName)
	signal closed
	var level := 0
	var _notice := ""
	var _rows := Rows.new()

	func rows_page() -> Rows:
		return _rows


class HudStandIn:
	extends Control
	signal action_chosen(action: StringName, target: StringName)
	var options: Array[Dictionary] = []
	var at := -1

	func is_choosing() -> bool:
		return not options.is_empty()

	func cursor() -> int:
		return at

	func current_option() -> Dictionary:
		return options[at] if at >= 0 and at < options.size() else {}


class Reveal:
	extends RefCounted
	var playing := true

	func is_playing() -> bool:
		return playing


class TitleStandIn:
	extends Control
	var reveal := Reveal.new()


class ResultStandIn:
	extends Control
	signal choice_made(choice_id: StringName)
	var counting := false
	var choice: StringName = &"continue"

	func is_counting() -> bool:
		return counting

	func current_choice() -> StringName:
		return choice


class Purse:
	extends RefCounted
	var lume := 500

	func amount() -> int:
		return lume


class OutfitModel:
	extends RefCounted
	var wallet := Purse.new()
	var worn := ""

	func rows() -> Array:
		return [{"id": "float", "right": worn}]


class OutfitterStandIn:
	extends Control
	signal closed
	var model := OutfitModel.new()
	var _notice: Dictionary = {}
	var _rows := Rows.new()

	func root_page() -> Rows:
		return _rows


class SaveStandIn:
	extends Control
	signal saved(slot: int)
	signal loaded(slot: int)
	signal closed(outcome: int)


func before_each() -> void:
	_saved_settings = UiSettings.shared()
	UiSettings.set_shared(UiSettings.new())
	_host = Node.new()
	_root().add_child(_host)
	played = []


func _ui() -> UiAudio:
	var ui := UiAudio.new(AudioData.table(AudioData.UI_SFX))
	ui.player = func(id: StringName) -> void: played.append(id)
	_host.add_child(ui)
	return ui


func _stand_in(n: Control, cls: String) -> Control:
	n.set_meta(UiAudio.META_CLASS, cls)
	_host.add_child(n)
	return n


## Steps a page's transition and the listener frame by frame until it rests.
func _run(ui: UiAudio, m: MenuMotion) -> void:
	for i in 60:
		m.advance(DT)
		ui.step()
		if not m.is_moving():
			break
	ui.step()


func test_every_new_row_exists_and_imports() -> void:
	var rows := AudioData.sfx_rows()
	for id: String in [
		"ui_whoosh_in",
		"ui_whoosh_out",
		"ui_title_reveal",
		"ui_save_slot",
		"ui_load_slot",
		"ui_shrine_travel",
		"ui_reefball_choices",
		"ui_reefball_glint"
	]:
		assert_true(rows.has(id), "%s is an sfx row" % id)
		for f: String in (rows.get(id, {}) as Dictionary).get("files", []):
			assert_true(ResourceLoader.exists(f), "%s imports" % f)
	var whoosh := float((rows["ui_whoosh_in"] as Dictionary).get("volume_db", 0.0))
	assert_true(whoosh <= -10.0, "a whoosh sits well under the page's open sound (%.1f dB)" % whoosh)
	_done()


func test_a_page_whooshes_in_as_it_rises_and_out_as_it_sinks() -> void:
	var ui := _ui()
	var page := StatusMenu.open_in(_host, _sheet())
	ui.watch(page)
	ui.step()
	assert_eq(played, [&"ui_menu_open"] as Array[StringName], "the open sound first")
	played.clear()
	_run(ui, page.motion())
	assert_eq(played, [&"ui_whoosh_in"] as Array[StringName], "one whoosh as it rises into place")
	played.clear()
	page.close()
	ui.step()
	assert_eq(played, [&"ui_menu_close"] as Array[StringName], "the close sound at once")
	played.clear()
	_run(ui, page.motion())
	assert_eq(played, [&"ui_whoosh_out"] as Array[StringName], "one whoosh as it sinks away")
	_done()


func test_reduced_motion_moves_nothing_so_nothing_whooshes() -> void:
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	var ui := _ui()
	var page := StatusMenu.open_in(_host, _sheet())
	ui.watch(page)
	_run(ui, page.motion())
	page.close()
	_run(ui, page.motion())
	assert_eq(played, [&"ui_menu_open", &"ui_menu_close"] as Array[StringName], "the open and the close, no whoosh")
	_done()


func test_a_layer_row_plays_beside_the_frames_chosen_row() -> void:
	var ui := _ui()
	var hud := _stand_in(HudStandIn.new(), "ReefballHud") as HudStandIn
	ui.watch(hud)
	ui.step()
	hud.options = [{"action": &"rise", "scores": false}, {"action": &"loft", "scores": true}]
	hud.at = 0
	ui.step()
	assert_eq(played, [&"ui_reefball_choices"] as Array[StringName], "the choices rising outrank the cursor")
	played.clear()
	hud.at = 1
	ui.step()
	assert_eq(played, [&"ui_reefball_glint", &"ui_cursor"] as Array[StringName], "a scoring preview glints under it")
	played.clear()
	hud.at = 0
	ui.step()
	assert_eq(played, [&"ui_cursor"] as Array[StringName], "no glint off a scoring choice")
	played.clear()
	hud.action_chosen.emit(&"rise", &"")
	ui.step()
	assert_eq(played, [&"ui_confirm"] as Array[StringName])
	_done()


func test_an_initial_row_plays_on_its_first_read() -> void:
	var ui := _ui()
	var title := _stand_in(TitleStandIn.new(), "TitleMenu") as TitleStandIn
	ui.watch(title)
	ui.step()
	assert_eq(played, [&"ui_title_reveal", &"ui_title_swell"] as Array[StringName], "the reveal under the swell")
	played.clear()
	title.reveal.playing = false
	ui.step()
	assert_eq(played, [] as Array[StringName], "once")
	var still := _stand_in(TitleStandIn.new(), "TitleMenu") as TitleStandIn
	still.reveal.playing = false
	ui.watch(still)
	ui.step()
	assert_eq(played, [&"ui_title_swell"] as Array[StringName], "Reduced motion: no reveal, so only the swell")
	_done()


func test_the_save_slots_have_their_own_sounds() -> void:
	var ui := _ui()
	var menu := _stand_in(SaveStandIn.new(), "SaveMenu") as SaveStandIn
	ui.watch(menu)
	ui.step()
	played.clear()
	menu.saved.emit(1)
	ui.step()
	menu.loaded.emit(2)
	ui.step()
	assert_eq(played, [&"ui_save_slot", &"ui_load_slot"] as Array[StringName])
	_done()


func test_the_shrine_travel_list() -> void:
	var ui := _ui()
	var list := _stand_in(ShrineStandIn.new(), "ShrineTravelMenu") as ShrineStandIn
	ui.watch(list)
	ui.step()
	assert_eq(played, [&"ui_page"] as Array[StringName], "it opens over the shrine like a page turned")
	played.clear()
	list.rows_page().cursor = 1
	ui.step()
	list.level = 1
	ui.step()
	assert_eq(played, [&"ui_cursor", &"ui_page"] as Array[StringName], "a move, then the confirm")
	played.clear()
	list._notice = "refused"
	list.level = 0
	ui.step()
	assert_eq(played, [&"ui_error"] as Array[StringName], "a refused trip says so")
	played.clear()
	list.travel_chosen.emit(&"oruvel")
	list.closed.emit()
	ui.step()
	assert_eq(played, [&"ui_shrine_travel"] as Array[StringName], "leaving outranks the page's close")
	_done()


func test_the_hud_hook_reads_on_the_real_reefball_hud() -> void:
	var ui := _ui()
	var m := ReefballMatch.new()
	m.setup(ReefballDB.load_default(), &"tidecup_opening", 7)
	var hud := ReefballHud.new()
	_host.add_child(hud)
	var ctl := ReefballHudController.new()
	ctl.pacing_scale = 0.0
	ctl.manual = true
	_host.add_child(ctl)
	ctl.start(m, hud)
	for _i in 600:
		if hud.is_choosing() or not ctl.flush():
			break
	assert_true(hud.is_choosing(), "the player's contact")
	var hook := ui.hook_for(hud)
	assert_eq(str(hook.get("class", "")), "ReefballHud")
	assert_false(bool(hook.get("pending", false)), "live since big11")
	ui.watch(hud)
	for x: Dictionary in (ui.watched[-1] as Dictionary)["watch"]:
		(x["expr"] as Expression).execute([hud], ui, false)
		assert_false((x["expr"] as Expression).has_execute_failed(), "%s reads" % (x["row"] as Dictionary)["expr"])
	ui.step()
	played.clear()
	hud.set_cursor(1)
	ui.step()
	assert_true(played.has(&"ui_cursor"), "a move under the real cursor")
	_done()


func test_the_result_counts_up_and_settles() -> void:
	var ui := _ui()
	var panel := _stand_in(ResultStandIn.new(), "BattleResultPanel") as ResultStandIn
	ui.watch(panel)
	ui.step()
	panel.counting = true
	ui.step()
	assert_eq(played, [&"ui_count_run"] as Array[StringName], "the numbers start counting")
	played.clear()
	panel.counting = false
	ui.step()
	assert_eq(played, [&"ui_count_done"] as Array[StringName], "and settle")
	played.clear()
	panel.choice = &"retry"
	ui.step()
	panel.choice_made.emit(&"retry")
	ui.step()
	assert_eq(played, [&"ui_cursor", &"ui_confirm"] as Array[StringName])
	_done()


func test_the_outfitter_buys_wears_and_refuses() -> void:
	var ui := _ui()
	var shop := _stand_in(OutfitterStandIn.new(), "ReefballOutfitterMenu") as OutfitterStandIn
	ui.watch(shop)
	ui.step()
	assert_eq(played, [&"ui_menu_open"] as Array[StringName])
	played.clear()
	shop.model.wallet.lume = 380
	shop.model.worn = "worn"
	shop._notice = {"ok": true}
	ui.step()
	assert_eq(played, [&"ui_buy"] as Array[StringName], "bought (and worn at once): the buy is heard")
	played.clear()
	shop.model.worn = ""
	ui.step()
	assert_eq(played, [&"ui_equip"] as Array[StringName], "taken off: the gear moves")
	played.clear()
	shop._notice = {"ok": false}
	ui.step()
	assert_eq(played, [&"ui_error"] as Array[StringName], "can't afford it")
	_done()


func test_the_field_prompt_ticks_and_using_something_touches() -> void:
	var ui := _ui()
	var thing := Interactable.new()
	_host.add_child(thing)
	assert_eq(str(ui.hook_for(thing).get("class", "")), "Interactable", "any interactable has the touch")
	ui.watch(thing)
	ui.step()
	thing.used.emit(thing)
	ui.step()
	assert_eq(played, [&"ui_interact"] as Array[StringName])
	played.clear()
	var prompt := InteractPrompt.new()
	_host.add_child(prompt)
	ui.watch(prompt)
	ui.step()
	assert_eq(played, [] as Array[StringName], "no prompt shown, no tick")
	_done()


# --------------------------------------------------------------------------- helpers


func _sheet() -> PartySheet:
	var state := GameStateData.new()
	state.party_ids = HEROES.duplicate()
	return PartySheet.new(state, HEROES)


func _done() -> void:
	var tree := _host.get_tree()
	tree.paused = false
	_root().remove_child(_host)
	_host.free()
	_host = null
	UiSettings.set_shared(_saved_settings)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
