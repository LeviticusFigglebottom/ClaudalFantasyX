extends TestCase
## M2-UI-29 (resolution and aspect audit): every screen built at 16:9, 16:10 and 21:9 (and 43:18,
## 3440 x 1440) with the text size at 100 % and 130 %, through a real window resize (AspectHost).
## Per screen: no visible Control leaves the screen; no text runs out of its panel; scrims and
## backdrops cover the whole screen; a full-screen menu's frame stays centred; each HUD piece keeps
## its 16:9 margin to the edge it is pinned to. A screen also follows a live window change.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const BOX_SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const SET_PIECE_SEED := 20261027
## The dialogue box panel's width at 16:9 (dialogue_box.tscn: centred, offsets -800 to 800), its cap (M2-ARC-09).
const DIALOGUE_MAX_WIDTH_PX := 1600.0
const SEQUENCER_CONFIG := "res://game/data/cutscene/sequencer.json"
const LINE_KEY := &"DLG_CH02_BEACH_004"
const TEST_DIR := "user://test_aspect_saves"
const HALUNA := &"ch02/haluna"
const BEACH := Vector3(-8.0, 0.0, 6.0)
const MAP_FLAGS: Array[StringName] = [&"ch02_met_asha", &"ch02_tideline_won", &"ch02_ate_at_nemes"]
const REEFBALL_CHOICE := "res://game/ui/reefball/shots/reefball_hud_choice.tscn"
const REEFBALL_GOAL := "res://game/ui/reefball/shots/reefball_hud_goal.tscn"
## The checks for a full-screen menu's frame (UiFrame.centre: centred, reference-sized) and a cover.
const FRAME := "frame"
const COVER := "cover"

var _ui: UiSettings
var _saved_dir := ""


func before_each() -> void:
	_wipe()
	_saved_dir = SaveSystem.save_dir
	_ui = UiSettings.new()
	UiSettings.set_shared(_ui)


# --- The audit ------------------------------------------------------------------------------------


func test_each_window_lays_out_in_one_of_four_viewports() -> void:
	var want := {
		Vector2i(1920, 1080): Vector2(1920, 1080),
		Vector2i(1280, 720): Vector2(1920, 1080),
		Vector2i(3840, 2160): Vector2(1920, 1080),
		Vector2i(1920, 1200): Vector2(1920, 1200),
		Vector2i(1280, 800): Vector2(1920, 1200),
		Vector2i(2560, 1080): Vector2(2560, 1080),
		Vector2i(3440, 1440): Vector2(2580, 1080),
	}
	for w in AspectHost.WINDOWS:
		AspectHost.set_window(w)
		assert_eq(AspectHost.view().size, want[w] as Vector2, "window %s" % w)
	AspectHost.restore()


func test_title_and_settings() -> void:
	_sweep("title", _title, _framed)
	for row: StringName in [&"", SettingsMenu.ROW_GRAPHICS, SettingsMenu.ROW_AUDIO, SettingsMenu.ROW_ACCESSIBILITY]:
		_sweep("settings %s" % row, _settings.bind(row), _framed)
	_sweep("settings controls", _settings.bind(SettingsMenu.ROW_CONTROLS), _framed)
	SaveSystem.save_dir = _saved_dir


func test_field_menu_and_its_pages() -> void:
	_sweep("field menu", func() -> Node: return ParityHost.open_field_menu(_state()), _framed)
	for row: StringName in [
		FieldMenuModel.ROW_ITEMS,
		FieldMenuModel.ROW_EQUIP,
		FieldMenuModel.ROW_LATTICE,
		FieldMenuModel.ROW_STATUS,
		FieldMenuModel.ROW_FORMATION,
		FieldMenuModel.ROW_MAP,
		FieldMenuModel.ROW_BESTIARY,
		FieldMenuModel.ROW_CODEX,
	]:
		_sweep("field menu %s" % row, _field_page.bind(row), _framed)


func test_shop_inn_and_save() -> void:
	_sweep("shop", _shop, _framed)
	_sweep("inn", _inn, _framed)
	_sweep("reefball outfitter", _outfitter, _framed)
	_sweep("save", _save, _framed)
	SaveSystem.save_dir = _saved_dir


func test_dialogue_backlog_and_cutscene() -> void:
	_sweep("dialogue box", _box, _box_pieces)
	_sweep("backlog", _backlog, _framed)
	_sweep("cutscene", _cutscene, _cutscene_pieces)


func test_field_hud() -> void:
	_sweep("field hud", _field_hud, _field_hud_pieces)


## M3-C09-05: the held-input prompt keeps its bottom-centre place; the act card's black covers the
## screen and its words stay centred.
func test_hold_prompt_and_act_card() -> void:
	_sweep("hold prompt and act card", _cutscene_cards, _cutscene_card_pieces)


func test_battle_hud() -> void:
	for script: StringName in [BattleController.SCRIPT_PLAYER_PREVIEW, BattleController.SCRIPT_SWELL_RING]:
		_sweep("battle %s" % script, _battle.bind(script), _battle_pieces)


## M3-UI-100: a Ch8 set piece: the stair meter keeps its top-centre pin beside the timeline and help line.
func test_set_piece_hud() -> void:
	_sweep("battle set piece", _set_piece, _set_piece_pieces)


func test_battle_panels_and_pause() -> void:
	for script: StringName in [BattleCaptureScript.SCRIPT_READ_PANEL, BattleController.SCRIPT_DEFEAT]:
		_sweep("battle %s" % script, _battle.bind(script), _battle_pieces)
	_sweep("battle pause", func() -> Node: return BattlePauseMenu.open_in(ParityHost.scene_root()), _framed)


## The shrine travel list: a framed page, centred, its covers full screen.
## The options pass: the Accessibility page with its speed preview showing (the text speed row).
func test_speed_preview() -> void:
	_sweep("speed preview", _speed_preview, _framed)


func _speed_preview() -> Node:
	var page := AccessibilityMenu.new(UiSettings.shared(), "")
	ParityHost.scene_root().add_child(page)
	page.model.set_cursor(page.model.row_ids().find(UiSettings.TEXT_SPEED))
	return page


func test_shrine_travel() -> void:
	var saved_state := Game.state
	_sweep("shrine travel", _shrine_travel, _framed)
	Game.state = saved_state


func _shrine_travel() -> Node:
	Game.state = GameStateData.new()
	Game.state.attuned_shrines = [&"save_shrine_test", &"haluna_shrine"] as Array[StringName]
	var here := SaveShrine.new()
	here.network_id = &"save_shrine_test"
	here.opens_menu = false
	ParityHost.scene_root().add_child(here)
	return here.open_travel()


## M3-UI-205: the Kite's world map (list, chart and line in one centred frame).
func test_kite_map() -> void:
	_sweep("kite map", _kite_map, _framed)


func _kite_map() -> Node:
	var host := Node.new()
	ParityHost.scene_root().add_child(host)
	return KiteMapMenu.open_in(host, KiteMapShot.fixed_model())


## M3-UI-205: the field menu a row taller once the Kite flies (FieldMenu.grown_for).
func test_field_menu_with_the_kite() -> void:
	_sweep("field menu with the Kite", _field_menu_kite, _framed)


func _field_menu_kite() -> Node:
	var m := FieldMenuModel.new(_state(), ParityHost.HEROES, ParityHost.NAMES)
	m.kite = KiteMapShot.fixed_model()
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(m)
	ParityHost.scene_root().add_child(menu)
	return menu


## M3-UI-01: the Reefball HUD on a pass choice (menu and preview open) and just after a goal (banner).
func test_reefball_hud() -> void:
	for driver: String in [REEFBALL_CHOICE, REEFBALL_GOAL]:
		_sweep(driver.get_file().get_basename(), _reefball.bind(driver), _reefball_pieces)


## Built at 16:9, then the window changes under it: the frame recentres and the scrims follow.
func test_a_live_window_change_refits() -> void:
	AspectHost.set_window(AspectHost.ASPECTS[0])
	var menu := ParityHost.open_field_menu(_state())
	for w in AspectHost.ASPECTS:
		AspectHost.set_window(w)
		_check_pieces("field menu after a resize to %s" % w, _framed.call(menu) as Array, {}, false)
	ParityHost.free_field_menu(menu)
	_wipe()
	var ctl := _battle(BattleController.SCRIPT_PLAYER_PREVIEW) as BattleHud
	var ref := _measure(_battle_pieces.call(ctl) as Array)
	for w in AspectHost.ASPECTS:
		AspectHost.set_window(w)
		_check_pieces("battle hud after a resize to %s" % w, _battle_pieces.call(ctl) as Array, ref, true)
	_wipe()
	AspectHost.restore()


# --- Unit checks of the helpers -------------------------------------------------------------------


func test_pinned_rect_keeps_the_margin_to_its_pin() -> void:
	var ref := UiFrame.reference_size()
	var wide := ref + Vector2(640, 120)
	var sec := {"rect": [1272, 800, 600, 232], "pin": "bottom_right"}
	var r := HudLayout.pinned_rect(sec, wide)
	assert_eq(wide.x - r.end.x, ref.x - 1872.0, "right margin")
	assert_eq(wide.y - r.end.y, ref.y - 1032.0, "bottom margin")
	var mid := HudLayout.pinned_rect({"rect": [560, 48, 800, 48], "pin": "top"}, wide)
	assert_eq(mid.get_center().x, wide.x * 0.5, "centred across")
	assert_eq(mid.position.y, 48.0, "top margin")
	assert_eq(HudLayout.pinned_rect({"rect": [48, 48, 10, 10]}, wide).position, Vector2(48, 48), "top_left default")


func test_fit_line_shrinks_only_the_extra_text_size() -> void:
	var host := Control.new()
	host.theme = UiSettings.new().theme_for(load(UiSettings.BASE_THEME_PATH) as Theme)
	var big := AspectHost.settings_at(AspectHost.TEXT_SCALES[-1])
	host.theme = big.theme_for(load(UiSettings.BASE_THEME_PATH) as Theme)
	ParityHost.scene_root().add_child(host)
	var l := Label.new()
	l.theme_type_variation = &"HelpLabel"
	host.add_child(l)
	l.text = tr("BATTLE_PAUSE_HELP")
	var scaled := l.get_theme_font_size(&"font_size")
	var base := UiFrame.base_font_size(l)
	assert_true(scaled > base, "the largest text scale is larger")
	var need := l.get_theme_font(&"font").get_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, scaled).x
	UiFrame.fit_line(l, need * 0.9)
	var fitted := l.get_theme_font_size(&"font_size")
	assert_true(fitted < scaled and fitted >= base, "shrunk, never below the 100 percent size: %d" % fitted)
	UiFrame.fit_line(l, need * 0.1)
	assert_eq(l.get_theme_font_size(&"font_size"), base, "the 100 % size is the floor")
	UiFrame.fit_line(l, need * 2.0)
	assert_eq(l.get_theme_font_size(&"font_size"), scaled, "room enough: the full size again")
	host.free()


# --- Sweep ----------------------------------------------------------------------------------------


## Builds `build` (a Callable returning the screen's root) at each audited aspect and text scale and
## checks it; `pieces` (Callable(root) -> [[label, Control, pin], ...]) names what keeps its place.
func _sweep(screen: String, build: Callable, pieces: Callable) -> void:
	for t in AspectHost.TEXT_SCALES:
		var ref := {}
		for w in AspectHost.ASPECTS:
			_wipe()
			_ui = AspectHost.settings_at(t)
			UiSettings.set_shared(_ui)
			AspectHost.set_window(w)
			var root: Node = build.call()
			if root == null:
				fail("%s: did not build" % screen)
				break
			AspectHost.settle(ParityHost.scene_root())
			var tag := "%s at %s, text %d%%" % [screen, AspectHost.view().size, roundi(t * 100.0)]
			for b in AspectHost.outside(root):
				fail("%s: %s leaves the screen" % [tag, b])
			for b in AspectHost.spilling(root):
				fail("%s: %s" % [tag, b])
			var ps: Array = pieces.call(root)
			assert_false(ps.is_empty(), "%s: nothing to check" % tag)
			if ref.is_empty():
				ref = _measure(ps)
			_check_pieces(tag, ps, ref, true)
	_wipe()
	AspectHost.restore()
	UiSettings.set_shared(UiSettings.new())


## Each piece's margins now, by label.
func _measure(ps: Array) -> Dictionary:
	var out := {}
	for p: Array in ps:
		out[p[0]] = AspectHost.margins(p[1] as Control)
	return out


func _check_pieces(tag: String, ps: Array, ref: Dictionary, need_ref: bool) -> void:
	for p: Array in ps:
		var what := str(p[0])
		var c := p[1] as Control
		var pin := str(p[2])
		if pin == COVER:
			assert_true(AspectHost.covers(c), "%s: %s covers the screen (%s)" % [tag, what, AspectHost.rect_of(c)])
		elif pin == FRAME:
			var r := AspectHost.rect_of(c)
			assert_true(AspectHost.centred(c), "%s: %s is centred (%s)" % [tag, what, AspectHost.margins(c)])
			assert_eq(r.size, UiFrame.reference_size(), "%s: %s is the reference frame" % [tag, what])
		elif ref.has(what):
			var want: Array = ref[what]
			assert_true(
				AspectHost.keeps_pin(AspectHost.margins(c), want, HudLayout.PINS[pin] as Vector2),
				"%s: %s keeps its %s margins (%s, at 16:9 %s)" % [tag, what, pin, AspectHost.margins(c), want]
			)
		elif need_ref:
			fail("%s: no 16:9 reference for %s" % [tag, what])


# --- Pieces ---------------------------------------------------------------------------------------


## A full-screen menu: its frame (and every frame under it) centred, their covers full screen.
func _framed(root: Node) -> Array:
	var out: Array = []
	var frames: Array[Node] = [root]
	frames.append_array(root.find_children("*", "Control", true, false))
	var i := 0
	for n in frames:
		if not n is Control or not n.has_meta(UiFrame.META_COVERS) or not (n as Control).is_visible_in_tree():
			continue
		out.append(["frame %d" % i, n, FRAME])
		for c: Variant in n.get_meta(UiFrame.META_COVERS) as Array:
			if is_instance_valid(c) and (c as Control).is_visible_in_tree():
				out.append(["cover %s" % (c as Control).name, c, COVER])
		i += 1
	if out.is_empty():
		fail("%s is not a centred frame (UiFrame.centre)" % root.name)
	return out


func _box_pieces(box: Node) -> Array:
	_box_width_capped(box.get_node(^"Panel") as Control)
	return [["box panel", box.get_node(^"Panel"), "bottom"]]


## M2-ARC-09: the box's panel is never wider than at 16:9 (centred at the bottom on wider screens).
func _box_width_capped(panel: Control) -> void:
	assert_true(
		panel.size.x <= DIALOGUE_MAX_WIDTH_PX + 0.5,
		"the dialogue box is at most %d px wide (%s)" % [DIALOGUE_MAX_WIDTH_PX, panel.size.x]
	)


func _cutscene_pieces(o: Node) -> Array:
	var overlay := o as CutsceneOverlay
	_box_width_capped(overlay.box.get_node(^"Panel") as Control)
	return [
		["letterbox top", overlay.bar_top, "top"],
		["letterbox bottom", overlay.bar_bottom, "bottom"],
		["box panel", overlay.box.get_node(^"Panel"), "bottom"],
		["choices", overlay.choices, "bottom_right"],
		["skip prompt", overlay.skip_prompt, "bottom_right"],
	]


func _field_hud_pieces(root: Node) -> Array:
	var out: Array = []
	for c in root.get_children():
		if c is ObjectiveHud:
			out.append(["objective line", (c as ObjectiveHud)._panel, "top_left"])
		elif c is TipCard:
			out.append(["tip card", (c as TipCard)._panel, "top_right"])
		elif c is AreaTitleCard:
			out.append(["area title", (c as AreaTitleCard)._name, "top"])
		elif c is CodexNotice:
			out.append(["codex notice", (c as CodexNotice)._panel, "bottom_right"])
	return out


func _cutscene_card_pieces(root: Node) -> Array:
	var out: Array = []
	for c in root.get_children():
		if c is HoldPrompt:
			out.append(["hold prompt", (c as HoldPrompt).plate(), "bottom"])
		elif c is ActCard:
			out.append(["act card black", (c as ActCard).backing(), COVER])
			out.append(["act card title", (c as ActCard).title_label(), "center"])
	return out


func _battle_pieces(h: Node) -> Array:
	var hud := h as BattleHud
	var out: Array = [
		["timeline", hud.timeline, "top_right"],
		["party bars", hud.party, "bottom_right"],
	]
	for extra: Array in [
		["help line", hud._help_panel, "top"],
		["target info", hud.target_cursor._info, "top_left"],
		["command menu", hud.commands.top_page(), "bottom_left"],
		["swell panel", hud.swell_ring, "bottom_left"],
	]:
		if extra[1] != null and (extra[1] as Control).is_visible_in_tree():
			out.append(extra)
	for panel: Control in [hud.read_panel(), hud.result]:
		if panel.is_visible_in_tree():
			out.append_array(_framed(panel))
	return out


# --- Screens --------------------------------------------------------------------------------------


func _state() -> GameStateData:
	var s := GameStateData.new()
	s.party_ids = ParityHost.HEROES.duplicate()
	s.inventory = {"salt_tonic": 3, "quiet_tea": 2, "crab_carapace": 7}
	return s


func _title() -> Node:
	SaveSystem.save_dir = TEST_DIR
	var menu := TitleMenu.new()
	menu.save_system = SaveSystem
	ParityHost.scene_root().add_child(menu)
	return menu


func _settings(row: StringName) -> Node:
	var hub := SettingsMenu.new()
	hub.ui_settings = _ui
	hub.save_path = ""
	var vp := SubViewport.new()
	hub.graphics_viewport = vp
	ParityHost.scene_root().add_child(vp)
	ParityHost.scene_root().add_child(hub)
	return hub.open_page(row) if row != &"" else hub


## The field menu's page for root row `row`, opened by Confirm on it (a hero first if it asks).
func _field_page(row: StringName) -> Node:
	var on := MAP_FLAGS
	var map := MapModel.new(HALUNA, BEACH, PI * 0.5, func(f: StringName) -> bool: return on.has(f))
	var menu := ParityHost.open_field_menu(_state(), ParityHost.HEROES, map)
	var d := InputDriver.new(InputDriver.Kind.KEYS)
	ParityHost.choose(d, menu.root_page(), ParityHost.row_of(menu.root_page(), row))
	if menu.child == null and menu.detail_page().visible:
		ParityHost.choose(d, menu.detail_page(), 0)
	for page: Node in [menu.child, menu.bestiary, menu.codex_menu, menu.map_menu]:
		if page != null:
			return page
	return null


func _shop() -> Node:
	var db := ItemDB.load_default()
	var flags := FlagReader.new()
	flags.values["ch02_met_asha"] = true
	var menu := (load(ShopMenu.SCENE_PATH) as PackedScene).instantiate() as ShopMenu
	menu.pause_tree = false
	var goods := PartyGoods.from_state(db, _state())
	menu.configure(ShopMenuModel.new(db, Shop.new(db, &"haluna_market"), goods, flags, ParityHost.NAMES))
	ParityHost.scene_root().add_child(menu)
	return menu


func _inn() -> Node:
	var db := ItemDB.load_default()
	var menu := (load(InnMenu.SCENE_PATH) as PackedScene).instantiate() as InnMenu
	menu.pause_tree = false
	var heal := func(_source: StringName) -> void: pass
	menu.configure(
		InnMenuModel.new(Inn.new(db, &"haluna_inn"), PartyGoods.from_state(db, _state()), FlagReader.new(), heal)
	)
	ParityHost.scene_root().add_child(menu)
	return menu


func _outfitter() -> Node:
	var menu := (load(ReefballOutfitterMenu.SCENE_PATH) as PackedScene).instantiate() as ReefballOutfitterMenu
	menu.pause_tree = false
	var none := func(_f: StringName) -> Variant: return ""
	var keep := func(_f: StringName, _v: Variant) -> void: pass
	menu.configure(
		ReefballOutfitterModel.new(
			ReefballDB.load_default(), PartyGoods.from_state(ItemDB.load_default(), _state()).wallet, none, keep
		)
	)
	ParityHost.scene_root().add_child(menu)
	return menu


func _save() -> Node:
	SaveSystem.save_dir = TEST_DIR
	var menu := SaveMenu.open_in(ParityHost.scene_root(), SaveMenuModel.Mode.SAVE, {}, "", SaveSystem)
	menu.animate = false
	menu.pause_tree = false
	(Engine.get_main_loop() as SceneTree).paused = false
	return menu


func _box() -> Node:
	var box := (load(BOX_SCENE) as PackedScene).instantiate() as DialogueBox
	ParityHost.scene_root().add_child(box)
	_say(box)
	return box


func _say(box: DialogueBox) -> void:
	box.visible = true
	box.set_process(false)
	(box.get_node(^"DialogueAssist") as DialogueAssist).set_process(false)
	box.show_text(&"rhen", LINE_KEY)
	box.skip_reveal()


func _backlog() -> Node:
	var box := _box() as DialogueBox
	var assist := box.get_node(^"DialogueAssist") as DialogueAssist
	assist.backlog = DialogueBacklog.new(int(DialogueAssist.load_data()["max_lines"]))
	for i in 12:
		box.show_text(&"rhen" if i % 2 == 0 else &"", LINE_KEY)
		box.skip_reveal()
	return assist.open_backlog()


func _cutscene() -> Node:
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER_CONFIG))
	var overlay := CutsceneOverlay.new(cfg)
	ParityHost.scene_root().add_child(overlay)
	_say(overlay.box)
	overlay.set_letterbox(1.0)
	var options: Array[DialogueOption] = []
	for i in 3:
		var o := DialogueOption.new()
		o.index = i
		o.text_key = LINE_KEY
		options.append(o)
	overlay.choices.show_options(options)
	overlay.set_skip_progress(0.5)
	return overlay


## The field's HUD pieces on one themed layer, each held in: the objective line, a tip card, the
## area title and the codex notice.
## The held-input prompt over an act card (both up at once, held in, so each is measured).
func _cutscene_cards() -> Node:
	var layer := CanvasLayer.new()
	ParityHost.scene_root().add_child(layer)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root)
	_ui.follow(root)
	FieldInput.ensure_actions()
	var card := ActCard.new()
	root.add_child(card)
	card.show_act(2)
	card.advance(float(ActCard.load_data()["in_sec"]))
	card.set_process(false)
	var prompt := HoldPrompt.new()
	prompt.action = FieldInput.INTERACT
	root.add_child(prompt)
	prompt.show_prompt("FIELD_PROMPT_CH09_RAISE_STAFF")
	prompt.advance(float(HoldPrompt.load_data()["fade_sec"]))
	prompt.set_process(false)
	return root


func _field_hud() -> Node:
	var layer := CanvasLayer.new()
	ParityHost.scene_root().add_child(layer)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root)
	_ui.follow(root)
	var hud := ObjectiveHud.new()
	hud.tracker = ObjectiveTracker.new(func(f: StringName) -> bool: return f == MAP_FLAGS[0])
	hud.zone = HALUNA
	root.add_child(hud)
	hud.show_now()
	hud.advance(float(ObjectiveHud.load_data()["in_sec"]))
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()
	var seen := {MAP_FLAGS[0]: true}
	var card := TipCard.new()
	card.tips = TutorialTips.new(
		func(f: StringName) -> bool: return bool(seen.get(f, false)),
		func(f: StringName) -> void: seen[f] = true,
		func() -> bool: return true
	)
	root.add_child(card)
	card.advance(0.0)
	card.advance(float(TutorialTips.load_data()["fade_sec"]))
	card.set_process(false)
	AreaTitleCard.forget()
	var title := AreaTitleCard.new()
	title.location = HALUNA
	root.add_child(title)
	title.advance(0.0)
	title.advance(float(AreaTitleCard.load_data()["in_sec"]))
	title.set_process(false)
	var notice := CodexNotice.new()
	root.add_child(notice)
	notice.set_process(false)
	notice._apply(1.0)
	return root


## A Reefball HUD capture driver (M3-UI-01), on its own layer as a match scene would hold it.
func _reefball(path: String) -> Node:
	var layer := CanvasLayer.new()
	ParityHost.scene_root().add_child(layer)
	var shot := (load(path) as PackedScene).instantiate() as ReefballHudShot
	shot.fresh_settings = false
	layer.add_child(shot)
	return shot.hud


func _reefball_pieces(h: Node) -> Array:
	return (h as ReefballHud).pieces()


func _battle(script: StringName) -> Node:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ParityHost.scene_root().add_child(ctl)
	ctl.hud.apply_settings(_ui)
	ctl.run_script(script)
	return ctl.hud


func _set_piece() -> Node:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ParityHost.scene_root().add_child(ctl)
	ctl.hud.apply_settings(_ui)
	var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var reserve: Array[StringName] = [&"ysolde", &"kerrid"]
	ctl.start_battle(party, reserve, &"ch08_stair_hold_1", SET_PIECE_SEED)
	ctl.engine.objective_count = 2
	ctl.set_piece.refresh()
	return ctl.hud


func _set_piece_pieces(h: Node) -> Array:
	var out := _battle_pieces(h)
	out.append(["stair meter", h.get_node(^"ObjectiveMeter"), "top"])
	return out


## Frees everything an earlier screen left under the test scene, and unpauses.
func _wipe() -> void:
	FlowRouting.record = Callable()
	var host := ParityHost.scene_root()
	var tree := Engine.get_main_loop() as SceneTree
	if host != tree.root:
		for c in host.get_children():
			host.remove_child(c)
			c.free()
	tree.paused = false
	InputDriver.park_pointer()
