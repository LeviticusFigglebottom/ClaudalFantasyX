extends TestCase
## M2-UI-28: every screen in the pseudo-locale (PseudoLoc: every string accented and about 40%
## longer), at 100% and 130% text (UiSettings text_scale), at the 1920 x 1080 reference. Each
## screen is built the way its capture driver or input parity test builds it, then TextFitProbe
## checks every visible Label, Button and RichTextLabel: text past its panel, or cut with no sign,
## fails; an ellipsis is a warning, printed for review (docs/kb/tech/ui.md 'Pseudo-localisation').
## One test per screen group; each names the screen, the scale, the node and the text that broke.

const SEQUENCER_CONFIG := "res://game/data/cutscene/sequencer.json"
const COMPILED_DIALOGUE := "res://game/data/dialogue/compiled"
const BOX_SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SET_PIECE_SEED := 20261027
const THEME_PATH := "res://game/ui/theme/hymn_theme.tres"
const TEST_DIR := "user://test_pseudo_loc_screens"
const TITLE_SETTINGS_DRIVERS: Array[String] = ["res://game/ui/menus/memories/shots/memories_menu.tscn"]
const FIELD_MENU_DRIVERS: Array[String] = [
	"res://game/ui/field_menu/shots/field_menu.tscn",
	"res://game/ui/field_menu/shots/field_menu_kite.tscn",
	"res://game/ui/field_menu/shots/field_menu_swell_modes.tscn",
]
const PARTY_PAGE_DRIVERS: Array[String] = [
	"res://game/ui/menus/items/shots/items_menu.tscn",
	"res://game/ui/menus/items/shots/items_menu_use.tscn",
	"res://game/ui/menus/equip/shots/equip_menu.tscn",
	"res://game/ui/menus/equip/shots/equip_customize.tscn",
	"res://game/ui/menus/lattice/shots/lattice_menu.tscn",
	"res://game/ui/menus/lattice/shots/lattice_menu_activate.tscn",
	"res://game/ui/menus/status/shots/status_menu.tscn",
	"res://game/ui/menus/formation/shots/formation_menu.tscn",
]
const MAP_BOOK_DRIVERS: Array[String] = [
	"res://game/ui/map/shots/field_menu_map_haluna.tscn",
	"res://game/ui/map/shots/field_menu_map_shrine.tscn",
	"res://game/ui/map/shots/field_menu_map_keth_pass.tscn",
	"res://game/ui/map/shots/field_menu_map_lowlight.tscn",
	"res://game/ui/map/shots/field_menu_map_ansedra.tscn",
	"res://game/ui/bestiary/shots/bestiary_menu.tscn",
	"res://game/ui/codex/shots/field_menu_codex.tscn",
	"res://game/levels/_tests/document_reader/document_reader_three.tscn",
	"res://game/levels/_tests/document_reader/document_reader_one.tscn",
]
const TOWN_DRIVERS: Array[String] = [
	"res://game/ui/shop/shots/shop_buy.tscn",
	"res://game/ui/shop/shots/shop_sell.tscn",
	"res://game/ui/shop/shots/inn.tscn",
	"res://game/ui/reefball/shots/reefball_outfitter.tscn",
]
const REEFBALL_CHOICE := "res://game/ui/reefball/shots/reefball_hud_choice.tscn"
const REEFBALL_GOAL := "res://game/ui/reefball/shots/reefball_hud_goal.tscn"
## Overflows in screens another track owns, filed as request tasks: printed as KNOWN, not failed,
## until the owner fixes them and deletes the row. Key: the start of the finding.
const KNOWN := {}

var failures_seen: PackedStringArray = []
var warnings_seen: PackedStringArray = []
var _scale := 1.0
var _saved_state: GameStateData
var _saved_dir := ""
var _kept: Array[Node] = []
var _was_aspect := Window.CONTENT_SCALE_ASPECT_EXPAND


func before_each() -> void:
	InputDriver.clear_screen()
	_kept.assign(ParityHost.scene_root().get_children())
	# The headless window is square, so "expand" would give anchored screens a 1920 x 1920 canvas:
	# "keep" holds it at the 1920 x 1080 reference the layouts are drawn for.
	var root := InputDriver.root()
	_was_aspect = root.content_scale_aspect
	root.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP
	failures_seen.clear()
	warnings_seen.clear()
	_saved_state = Game.state
	_saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = TEST_DIR
	PseudoLoc.enable()


func test_the_pseudo_locale_is_live() -> void:
	assert_eq(TranslationServer.get_locale(), PseudoLoc.locale())
	assert_eq(tr("FIELD_MENU_TITLE"), PseudoLoc.pseudo(_english("FIELD_MENU_TITLE")))
	assert_eq(tr("DLG_CH02_BEACH_004"), PseudoLoc.pseudo(_english("DLG_CH02_BEACH_004")), "dialogue CSVs too")
	_done("live")


func test_title_and_settings_fit() -> void:
	for scale in _scales():
		var s := _settings_at(scale)
		var title := TitleMenu.new()
		title.save_system = SaveSystem
		_host(title)
		_probe(title, "title")
		_clear()
		for row: StringName in [&""] + Array(SettingsMenu.ROW_IDS):
			var hub := SettingsMenu.new()
			hub.ui_settings = s
			hub.save_path = ""
			var vp := SubViewport.new()
			hub.graphics_viewport = vp
			_host(vp)
			_host(hub)
			if row != &"":
				hub.open_page(row)
			_probe(hub, "settings " + (String(row) if row != &"" else "hub"))
			_clear()
		_drivers(TITLE_SETTINGS_DRIVERS)
	_done("title and settings")


## The options pass: the Accessibility page's speed previews (SpeedPreview) with the cursor on each speed row.
func test_speed_previews_fit() -> void:
	for scale in _scales():
		var s := _settings_at(scale)
		for row: StringName in [UiSettings.TEXT_SPEED, UiSettings.BATTLE_SPEED]:
			var page := AccessibilityMenu.new(s, "")
			_host(page)
			page.model.set_cursor(page.model.row_ids().find(row))
			_probe(page, "speed preview " + String(row))
			_clear()
	_done("speed previews")


func test_field_menu_fits() -> void:
	for scale in _scales():
		_settings_at(scale)
		_drivers(FIELD_MENU_DRIVERS)
		for level: StringName in [FieldMenuModel.ROW_SWELL, FieldMenuModel.ROW_QUIT]:
			var menu := ParityHost.open_field_menu(GameStateData.new())
			menu.root_page().set_cursor(ParityHost.row_of(menu.root_page(), level), false)
			menu.accept()
			_probe(menu, "field menu " + String(level))
			ParityHost.free_field_menu(menu)
	_done("field menu")


func test_party_pages_fit() -> void:
	for scale in _scales():
		_settings_at(scale)
		_drivers(PARTY_PAGE_DRIVERS)
	_done("party pages")


func test_map_bestiary_and_codex_fit() -> void:
	for scale in _scales():
		_settings_at(scale)
		_drivers(MAP_BOOK_DRIVERS)
	_done("map, bestiary, codex")


func test_shop_and_inn_fit() -> void:
	for scale in _scales():
		_settings_at(scale)
		_drivers(TOWN_DRIVERS)
	_done("shop and inn")


func test_save_menu_fits() -> void:
	var clock := SaveSystem.clock
	var autosave := SaveSystem.autosave_enabled
	SaveSystem.autosave_enabled = false
	SaveSystem.clock = func() -> int: return 1792500000
	var fx := SaveShrineShot.load_fixtures()
	fx["save_dir"] = TEST_DIR
	SaveShrineShot.write_fixtures(fx)
	for scale in _scales():
		_settings_at(scale)
		Game.state = GameStateData.new()
		for mode: SaveMenuModel.Mode in [SaveMenuModel.Mode.SAVE, SaveMenuModel.Mode.LOAD]:
			var menu := SaveMenu.open_in(ParityHost.scene_root(), mode, {}, "", SaveSystem)
			menu.animate = false
			menu.set_time_zone_bias(0)
			_probe(menu.get_parent(), "save menu %s" % SaveMenuModel.Mode.keys()[mode])
			_clear()
	SaveShrineShot.clear_fixtures(fx)
	SaveSystem.clock = clock
	SaveSystem.autosave_enabled = autosave
	_done("save menu")


## Every line and every choice of the compiled dialogue, in the box and in the cutscene choices;
## then the backlog over the box.
func test_dialogue_box_backlog_and_choices_fit() -> void:
	var lines := _dialogue_ops("line")
	var choices := _dialogue_ops("options")
	assert_true(lines.size() > 0 and choices.size() > 0, "the compiled dialogue has lines and choices")
	for scale in _scales():
		_settings_at(scale)
		var overlay := _overlay()
		var box := overlay.box
		for op in lines:
			box.show_text(StringName(str(op.get("speaker", ""))), StringName(str(op["key"])))
			box.skip_reveal()
			_probe(overlay, "dialogue %s" % op["key"])
		for op in choices:
			var options: Array[DialogueOption] = []
			for c: Dictionary in op["choices"]:
				var o := DialogueOption.new()
				o.index = options.size()
				o.text_key = StringName(str(c["key"]))
				options.append(o)
			overlay.choices.show_options(options)
			_probe(overlay, "choices %s" % op["choices"][0]["key"])
			overlay.choices.clear()
		var assist := box.get_node(^"DialogueAssist") as DialogueAssist
		assist.pause_backlog = false
		assist.open_backlog()
		_probe(overlay, "backlog")
		_clear()
		DialogueBacklog.forget()
	_done("dialogue")


## The objective line (every objective), the tip card (every tip), the interaction prompt (every
## verb) and the area title card (every location).
func test_field_hud_fits() -> void:
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()
	InputNames.using_pad = false
	for scale in _scales():
		_settings_at(scale)
		for row in ObjectiveTracker.load_rows():
			var r := (row as Dictionary).duplicate(true)
			r.erase("requires")
			r.erase("until")
			r["side"] = false
			var hud := ObjectiveHud.new()
			hud.tracker = ObjectiveTracker.new(func(_f: StringName) -> bool: return false)
			hud.tracker.rows = [r] as Array[Dictionary]
			hud.zone = StringName(str(r.get("zone", "")))
			_hud_root().add_child(hud)
			hud.show_now()
			hud.advance(float(ObjectiveHud.load_data()["in_sec"]))
			_probe(hud, "objective %s" % r.get("line_key", ""))
			_clear()
		var tips := TutorialTips.new(
			func(_f: StringName) -> bool: return false, func(_f: StringName) -> void: pass, func() -> bool: return true
		)
		for tip in tips.tips:
			var card := TipCard.new()
			card.tips = tips
			_hud_root().add_child(card)
			tips.queue = [tip] as Array[Dictionary]
			card.advance(0.0)
			card.advance(float(TutorialTips.load_data()["fade_sec"]))
			card.set_process(false)
			_probe(card, "tip %s" % tip.get("title_key", ""))
			_clear()
		for key in _keys_with_prefix("FIELD_PROMPT_"):
			var it := Interactable.new()
			it.prompt_key = key
			_host(it)
			var prompt := InteractPrompt.new()
			prompt.pick = func() -> Interactable: return it
			_hud_root().add_child(prompt)
			prompt.advance(float(HudLayout.num(InteractPrompt.load_data(), "fade_sec")))
			prompt.set_process(false)
			_probe(prompt, "prompt %s" % key)
			_clear()
		var registry := LocationRegistry.load_default()
		for loc in registry.location_ids():
			AreaTitleCard.forget()
			var card := AreaTitleCard.new()
			card.location = loc
			_hud_root().add_child(card)
			card.advance(0.0)
			card.advance(float(AreaTitleCard.load_data()["in_sec"]))
			card.set_process(false)
			_probe(card, "area title %s" % loc)
			_clear()
	AreaTitleCard.forget()
	_done("field HUD")


## M3-C09-05: the held-input prompt (every hold prompt verb, key and pad button), every act card and
## the one-line caption card, and the unnamed-character labels in the dialogue box's name plate.
func test_cutscene_cards_and_prompts_fit() -> void:
	FieldInput.ensure_actions()
	var prompt_keys: Array[String] = ["FIELD_PROMPT_CH09_RAISE_STAFF"]
	var acts := (ActCard.load_data().get("acts", {}) as Dictionary).keys()
	for scale in _scales():
		_settings_at(scale)
		for key in prompt_keys:
			for pad in [false, true]:
				InputNames.using_pad = pad
				var prompt := HoldPrompt.new()
				prompt.action = FieldInput.INTERACT
				_hud_root().add_child(prompt)
				prompt.show_prompt(key)
				prompt.set_held(true)
				prompt.advance(float(HoldPrompt.load_data()["fade_sec"]))
				prompt.set_process(false)
				_probe(prompt, "hold prompt %s%s" % [key, " (pad)" if pad else ""])
				_clear()
		for n: Variant in acts:
			var card := ActCard.new()
			_hud_root().add_child(card)
			card.show_act(int(str(n)))
			card.advance(float(ActCard.load_data()["in_sec"]))
			card.set_process(false)
			_probe(card, "act card %s" % n)
			_clear()
		var caption := ActCard.new()
		_hud_root().add_child(caption)
		caption.show_caption("DLG_CH01_DROP_001")
		caption.advance(float(ActCard.load_data()["in_sec"]))
		caption.set_process(false)
		_probe(caption, "caption card")
		_clear()
		for id: Variant in CharacterNames.rows():
			var box := (load(BOX_SCENE) as PackedScene).instantiate() as DialogueBox
			_host(box)
			box.show_text(
				StringName(str(id)),
				&"DLG_CH09_ROAD_005",
				StringName(str((CharacterNames.rows()[id] as Dictionary)["name_key"]))
			)
			box.skip_reveal()
			_probe(box, "name plate %s unnamed" % id)
			_clear()
	InputNames.using_pad = false
	_done("cutscene cards and prompts")


## Every battle capture state (the command menu and its pages, the target and read panels, the
## Swell panels, the Vowbound call, the result panel), then the pause page over a turn.
func test_battle_fits() -> void:
	for scale in _scales():
		_settings_at(scale)
		for sid in BattleFixture.fixture_ids():
			var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
			ctl.auto_start = false
			ctl.pacing_scale = 0.0
			ctl.persist_progress = false
			ctl.show_damage_numbers = false
			_host(ctl)
			ctl.hud.apply_settings(UiSettings.shared())
			ctl.run_script(sid)
			_probe(ctl.hud, "battle " + String(sid))
			_clear()
		var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
		ctl.auto_start = false
		ctl.pacing_scale = 0.0
		ctl.persist_progress = false
		ctl.show_damage_numbers = false
		_host(ctl)
		ctl.run_script(&"player_preview")
		var pause := BattlePauseMenu.create()
		pause.pause_tree = false
		FieldSubmenu.mount(pause, ctl)
		_probe(pause, "battle pause")
		_clear()
	_done("battle")


## M3-UI-100: a Ch8 set piece: the stair meter, the lock's help line and the reserve page with the hero kept out.
func test_set_piece_fits() -> void:
	for scale in _scales():
		_settings_at(scale)
		var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
		ctl.auto_start = false
		ctl.pacing_scale = 0.0
		ctl.persist_progress = false
		ctl.show_damage_numbers = false
		_host(ctl)
		ctl.hud.apply_settings(UiSettings.shared())
		var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
		var reserve: Array[StringName] = [&"ysolde", &"kerrid"]
		ctl.start_battle(party, reserve, &"ch08_stair_hold_1", SET_PIECE_SEED)
		ctl.engine.objective_count = 2
		ctl.set_piece.refresh()
		ctl.hud.set_help(ctl.menus.swap_lock_text(ctl.engine, &"toma"))
		ctl.hud.commands.push(BattleMenus.PAGE_SWAP, tr("HUD_PAGE_RESERVE"), ctl.menus.reserve_rows(ctl.engine))
		_probe(ctl.hud, "battle set piece")
		_clear()
	_done("set piece")


## The shrine travel list (the teleport network's menu): the list with a long place name, then the question.
func test_shrine_travel_fits() -> void:
	var saved_state := Game.state
	var saved_registry := ShrineNetwork.registry
	ShrineNetwork.registry = (
		LocationRegistry
		. from_dict(
			{
				"default_location": "a",
				"locations":
				[
					{"id": "a", "scene": SANDBOX, "spawn": "S", "name_key": "LOCATION_CH04_BRIGHTWATER_FERRY"},
					{"id": "b", "scene": SANDBOX, "spawn": "S", "name_key": "LOCATION_CH04_HALUNA_WAKE"},
				],
				"shrines": [{"id": "a_shrine", "location_id": "a"}, {"id": "b_shrine", "location_id": "b"}],
			}
		)
	)
	for scale in _scales():
		_settings_at(scale)
		Game.state = GameStateData.new()
		Game.state.attuned_shrines = [&"a_shrine", &"b_shrine"] as Array[StringName]
		var here := SaveShrine.new()
		here.network_id = &"a_shrine"
		here.opens_menu = false
		_host(here)
		var menu := here.open_travel()
		_probe(menu, "shrine travel list")
		menu.accept()
		_probe(menu, "shrine travel question")
		_clear()
	Game.state = saved_state
	ShrineNetwork.registry = saved_registry
	_done("shrine travel")


## M3-UI-205: the Kite's world map: the list (a long place name), the question, then a square's search.
func test_kite_map_fits() -> void:
	for scale in _scales():
		_settings_at(scale)
		var host := Node.new()
		_host(host)
		var menu := KiteMapMenu.open_in(host, KiteMapShot.fixed_model())
		menu.rows_page().set_cursor(menu.model.ids().find(KiteMapShot.CURSOR), false)
		_probe(menu, "kite map list")
		menu.accept()
		_probe(menu, "kite map question")
		menu.back()
		menu.rows_page().set_cursor(menu.rows_page().rows.size() - 2, false)
		menu.accept()
		_probe(menu, "kite map search")
		_clear()
	_done("kite map")


## M3-UI-205: the field menu a row taller once the Kite flies, on the Kite row (its line).
func test_field_menu_with_the_kite_fits() -> void:
	for scale in _scales():
		_settings_at(scale)
		var m := FieldMenuModel.new(GameStateData.new(), ParityHost.HEROES, ParityHost.NAMES)
		m.kite = KiteMapShot.fixed_model()
		var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
		menu.pause_tree = false
		menu.configure(m)
		_host(menu)
		menu.root_page().set_cursor(ParityHost.row_of(menu.root_page(), FieldMenuModel.ROW_KITE), false)
		_probe(menu, "field menu with the Kite")
		ParityHost.free_field_menu(menu)
	_done("field menu with the Kite")


## M3-UI-01: the Reefball HUD on a pass choice (menu, preview, the read's marks) and just after a
## goal (the banner), then on every option of that choice, then at the final banner.
func test_reefball_hud_fits() -> void:
	for scale in _scales():
		_settings_at(scale)
		for path: String in [REEFBALL_CHOICE, REEFBALL_GOAL]:
			var shot := (load(path) as PackedScene).instantiate() as ReefballHudShot
			shot.fresh_settings = false
			_host(shot)
			_probe(shot.hud, path.get_file().get_basename())
			if shot.hud.is_choosing():
				for i in shot.hud.options.size():
					shot.hud.set_cursor(i)
					_probe(shot.hud, "reefball option %d" % i)
			else:
				for _i in ReefballHudShot.MAX_STEPS * 4:
					if not shot.controller.flush():
						break
				_probe(shot.hud, "reefball final")
			_clear()
	_done("reefball HUD")


# --- helpers -------------------------------------------------------------------------------------


## The text scales to walk: the smallest and the largest UiSettings offers (100% and 130%).
func _scales() -> Array[float]:
	var opts := UiSettings.new().options(UiSettings.TEXT_SCALE)
	return [float(opts.front()), float(opts.back())]


## A fresh shared UiSettings at text scale `scale` (the screens read UiSettings.shared()).
func _settings_at(scale: float) -> UiSettings:
	_scale = scale
	var s := UiSettings.new()
	s.set_value(UiSettings.TEXT_SCALE, scale)
	UiSettings.set_shared(s)
	return s


func _probe(screen: Node, what: String) -> void:
	var p := TextFitProbe.probe(screen, "%s @%d%%" % [what, roundi(_scale * 100.0)])
	for f in p.failures:
		var known := _known(f)
		if known != "":
			warnings_seen.append("KNOWN (%s) %s" % [known, f])
		else:
			failures_seen.append(f)
	warnings_seen.append_array(p.warnings)


func _known(finding: String) -> String:
	for start: String in KNOWN:
		if finding.begins_with(start):
			return str(KNOWN[start])
	return ""


## Builds each capture driver scene, probes it, and frees it.
func _drivers(paths: Array[String]) -> void:
	for path in paths:
		var root := (load(path) as PackedScene).instantiate()
		_host(root)
		_probe(root, path.get_file().get_basename())
		_clear()


func _host(n: Node) -> void:
	ParityHost.scene_root().add_child(n)


## A full-screen themed Control on its own layer, as the HUD bits' capture drivers stage them.
func _hud_root() -> Control:
	var layer := CanvasLayer.new()
	_host(layer)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.theme = load(THEME_PATH) as Theme
	layer.add_child(root)
	return root


func _overlay() -> CutsceneOverlay:
	DialogueBacklog.forget()
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER_CONFIG))
	var overlay := CutsceneOverlay.new(cfg)
	_host(overlay)
	overlay.set_letterbox(1.0)
	overlay.box.visible = true
	overlay.box.set_process(false)
	(overlay.box.get_node(^"DialogueAssist") as DialogueAssist).set_process(false)
	return overlay


## Every op of kind `op` in the compiled dialogue.
func _dialogue_ops(op: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for f in DirAccess.get_files_at(COMPILED_DIALOGUE):
		if f.get_extension() != "json":
			continue
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(COMPILED_DIALOGUE.path_join(f)))
		if typeof(parsed) != TYPE_DICTIONARY:
			continue
		for node: Variant in ((parsed as Dictionary).get("nodes", {}) as Dictionary).values():
			for o: Variant in (node as Dictionary).get("ops", []):
				if typeof(o) == TYPE_DICTIONARY and str((o as Dictionary).get("op", "")) == op:
					out.append(o as Dictionary)
	return out


## The loc keys starting with `prefix`, in every loc CSV.
func _keys_with_prefix(prefix: String) -> PackedStringArray:
	var out := PackedStringArray()
	for csv in PseudoLoc.source_csvs():
		var f := FileAccess.open(csv, FileAccess.READ)
		while f != null and not f.eof_reached():
			var row := f.get_csv_line()
			if row.size() > 0 and row[0].begins_with(prefix) and not out.has(row[0]):
				out.append(row[0])
	return out


func _english(key: String) -> String:
	TranslationServer.set_locale(str(PseudoLoc.config()["source_locale"]))
	var s := tr(key)
	TranslationServer.set_locale(PseudoLoc.locale())
	return s


## Frees everything this test added under the test scene (the runner's own children stay).
func _clear() -> void:
	var host := ParityHost.scene_root()
	if host != (Engine.get_main_loop() as SceneTree).root:
		for c in host.get_children():
			if not _kept.has(c):
				host.remove_child(c)
				c.free()
	(Engine.get_main_loop() as SceneTree).paused = false


## Prints the warnings, asserts no failure, and puts English and the player's state back (the
## runner has no after_each).
func _done(group: String) -> void:
	_clear()
	for w in warnings_seen:
		print("    WARN %s" % w)
	assert_eq(
		failures_seen,
		PackedStringArray(),
		"%s: text does not fit in the pseudo-locale:\n%s" % [group, "\n".join(failures_seen)]
	)
	PseudoLoc.disable()
	InputDriver.root().content_scale_aspect = _was_aspect
	UiSettings.set_shared(null)
	Game.state = _saved_state
	SaveSystem.save_dir = _saved_dir
