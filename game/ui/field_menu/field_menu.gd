class_name FieldMenu
extends Control
## The field menu (M2-UI-04, SPEC §6.6): opened from the field with ui_cancel (Escape, B /
## Circle), it pauses the tree like SaveMenu and reaches the bestiary (BestiaryMenu), each
## hero's Swell fill mode (SPEC §6.2; BattleSwellCarry through FieldMenuModel) and the Settings
## hub (SettingsMenu: Graphics, Accessibility; M2-UI-09). It follows UiSettings (text size,
## palette, reduced motion).
## Layout: game/data/ui/field_menu.json (1920x1080 reference). Words: FieldMenuModel.
##
## Map (M2-UI-18) opens the zone map page (ZoneMapMenu) over it, like the bestiary; the zone and
## the player come from the field when the menu opens (ZoneMapMenu.live_model). Codex (M3-UI-03)
## opens the lore codex (CodexMenu) the same way, over the model's `codex` (null: the game's).
##
## Three levels: ROOT (Bestiary / Swell / Map / Settings / Close) on the left; HEROES (each Swell hero and the mode
## in use) and MODES (one hero's unlocked modes, "In use" on the current one) on the right. The
## line under the right page says what the highlighted row means (pillar 4).
##
## Input (keyboard and controller through ui_*): ui_up / ui_down move, ui_accept chooses,
## ui_cancel goes back a level and closes from the root. Mouse: hover to move, click to choose.
## While the bestiary, the codex, the map or the Settings hub is open it takes the input, and this menu hides
## until it closes.
##
## M2-MNU-01..04 (the Menus track): Items, Equip, Lattice and Status open the party's pages
## (FieldSubmenu children in game/ui/menus/, each over a PartySheet of this model's state and
## heroes) the same way. Quit asks first on the right page (Level.QUIT: Stay / Quit to the title,
## Stay under the cursor, the line saying what is lost) and then returns to the title (boot.tscn)
## through FlowRouting. M2-MNU-07 added Formation (FormationMenu, the same way); when it closes the
## heroes follow the saved line's order.
## M3-UI-205: once the Kite flies, Kite (after Map) opens its world map (KiteMapMenu) the same way; a
## flight closes this menu too, and the panel is a row taller while the row is there (grown_for).
## M2-MNU-303: the menu fades and rises in from the field and fades out when it closes (MenuMotion);
## a page over it keeps the backdrop still, and the menu's own content fades back in when it closes.

signal closed
## The close transition has finished (at once under Reduced motion): open_in's layer frees itself.
signal gone

enum Level { ROOT, HEROES, MODES, QUIT }

const SCENE_PATH := "res://game/ui/field_menu/field_menu.tscn"
const DATA_PATH := "res://game/data/ui/field_menu.json"
const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")
## The field action that opens the menu (FieldController).
const OPEN_ACTION := &"ui_cancel"
## Where Quit goes (EndCard's return scene: the title).
const TITLE_SCENE := "res://game/core/boot.tscn"

## Root row -> the party page it opens (a FieldSubmenu script with static create(PartySheet)).
const CHILD_PAGES := {
	FieldMenuModel.ROW_ITEMS: preload("res://game/ui/menus/items/items_menu.gd"),
	FieldMenuModel.ROW_EQUIP: preload("res://game/ui/menus/equip/equip_menu.gd"),
	FieldMenuModel.ROW_LATTICE: preload("res://game/ui/menus/lattice/lattice_menu.gd"),
	FieldMenuModel.ROW_STATUS: preload("res://game/ui/menus/status/status_menu.gd"),
	FieldMenuModel.ROW_FORMATION: preload("res://game/ui/menus/formation/formation_menu.gd"),
}

## Pause the tree while open (the field must not move under a menu).
@export var pause_tree := true

var model: FieldMenuModel
var level := Level.ROOT
## The hero whose modes are on show (MODES).
var hero: StringName = &""
## The bestiary opened from here (null when closed).
var bestiary: BestiaryMenu
## The lore codex opened from here (null when closed).
var codex_menu: CodexMenu
## The Settings hub opened from here (null when closed).
var settings_menu: SettingsMenu
## The zone map opened from here (null when closed).
var map_menu: ZoneMapMenu
## The Kite's world map opened from here (null when closed).
var kite_menu: KiteMapMenu
## The party page opened from here (Items, Equip, Lattice, Status; null when closed).
var child: FieldSubmenu

var _d: Dictionary = {}
var _root: MenuPage
var _detail: MenuPage
var _desc: Label
var _help: Label
var _objective_head: Label
var _objective: Label
var _save_head: Label
var _save_line: Label
var _save_hint: Label
var _party_cards: Array[PartyCard] = []
var _owns_pause := false
var _is_closed := false
var _motion: MenuMotion
## A line that stays on the description until the cursor moves ("Rhen's gauge now fills by ...").
var _notice := ""


## Instances the menu on its own CanvasLayer under `host` and opens it; the layer frees itself
## when the menu closes. `with_model` defaults to FieldMenuModel.from_game().
static func open_in(host: Node, with_model: FieldMenuModel = null) -> FieldMenu:
	var menu := (load(SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.configure(with_model)
	var layer := CanvasLayer.new()
	layer.layer = int(load_data().get("canvas_layer", 1))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(menu)
	menu.gone.connect(layer.queue_free)
	host.add_child(layer)
	return menu


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("field_menu")) != TYPE_DICTIONARY:
		push_error("FieldMenu: could not read 'field_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["field_menu"] as Dictionary


## The layout with `extra` more root rows (the Kite's, M3-UI-205): "extra_rows" grows each "grow" block by a
## row pitch per row and moves it up by half of that, and moves each "follow" block down by half, so the
## panel stays centred and the Objective block stays at the foot of the right column.
static func grown_for(d: Dictionary, extra: int) -> Dictionary:
	if extra <= 0:
		return d
	var out := d.duplicate(true)
	var em: Dictionary = out.get("extra_rows", {})
	var grow := HudLayout.num(out.get("root", {}), "row_pitch") * extra
	for key: Variant in em.get("grow", []):
		var b := out[key] as Dictionary
		var r := b["rect"] as Array
		b["rect"] = [r[0], float(r[1]) - grow * 0.5, r[2], float(r[3]) + grow]
		if b.has("max_rows"):
			b["max_rows"] = int(b["max_rows"]) + extra
	for key: Variant in em.get("follow", []):
		var b := out[key] as Dictionary
		var r := b["rect"] as Array
		b["rect"] = [r[0], float(r[1]) + grow * 0.5, r[2], r[3]]
	return out


## Sets the model before the menu enters the tree (null = the live game).
func configure(with_model: FieldMenuModel = null) -> void:
	model = with_model


func _ready() -> void:
	if model == null:
		model = FieldMenuModel.from_game()
	if model.map == null and model.live_map:
		model.map = ZoneMapMenu.live_model(self)
	_d = grown_for(load_data(), model.root_ids().size() - FieldMenuModel.ROOT_IDS.size())
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiSettings.shared().follow(self)
	_build()
	UiFrame.centre(self)  # the panel centred at 16:10 and 21:9, the scrim full screen (M2-UI-29)
	_root.replace_rows(model.root_rows())
	_render()
	if pause_tree and not get_tree().paused:
		get_tree().paused = true
		_owns_pause = true
	MenuMotion.follow_reduced_motion(self)
	_motion = MenuMotion.new(self)
	_motion.gone.connect(_on_motion_gone)
	_motion.play_in()


func _exit_tree() -> void:
	_restore_pause()


func is_open() -> bool:
	return not _is_closed


func _unhandled_input(event: InputEvent) -> void:
	if is_open() and handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the menu used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if not is_open() or _child_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## Chooses the highlighted row.
func accept() -> void:
	match level:
		Level.ROOT:
			_accept_root(StringName(str(_root.current_row().get("id", ""))))
		Level.HEROES:
			var cid := StringName(str(_detail.current_row().get("id", "")))
			if cid != &"":
				_open_modes(cid)
		Level.MODES:
			var mode := StringName(str(_detail.current_row().get("id", "")))
			_notice = model.choose_mode(hero, mode)
			_detail.replace_rows(model.mode_page_rows(hero))
			_render()
		Level.QUIT:
			if StringName(str(_detail.current_row().get("id", ""))) == FieldMenuModel.QUIT_GO:
				quit_to_title()
			else:
				back()


## Goes back one level; closes from the root.
func back() -> void:
	match level:
		Level.ROOT:
			close()
		Level.HEROES, Level.QUIT:
			level = Level.ROOT
			_render()
		Level.MODES:
			_open_heroes(hero)


func close() -> void:
	if _is_closed:
		return
	_is_closed = true
	if bestiary != null and bestiary.is_open():
		bestiary.close()
	if codex_menu != null and codex_menu.is_open():
		codex_menu.close()
	if settings_menu != null and settings_menu.is_open():
		settings_menu.close()
	if map_menu != null and map_menu.is_open():
		map_menu.close()
	if kite_menu != null and kite_menu.is_open():
		kite_menu.close()
	if child != null and child.is_open():
		child.close()
	_restore_pause()
	if _motion != null:
		_motion.play_out()
	else:
		gone.emit()
	closed.emit()


## The open, close and return transitions (null before _ready). Tests drive them with motion().finish().
func motion() -> MenuMotion:
	return _motion


## Closes the menu and returns to the title (FlowRouting waits for an idle router). Unsaved
## progress is lost, as the confirm said.
func quit_to_title() -> void:
	close()
	FlowRouting.change_scene(TITLE_SCENE)


## The root row under the cursor, the right page's rows and the lines on show (tests read these).
func root_page() -> MenuPage:
	return _root


func detail_page() -> MenuPage:
	return _detail


func desc_text() -> String:
	return _desc.text


## The root's Objective block ("" when hidden).
func objective_text() -> String:
	return _objective.text if _objective.visible else ""


## The party cards on the root (M2-MNU-304), one per place of the active line.
func party_cards() -> Array[PartyCard]:
	return _party_cards


## The root's Last saved line as shown ("" while hidden; M2-MNU-300).
func last_save_text() -> String:
	return _save_line.text if _save_line.visible else ""


func help_text() -> String:
	return _help.text


func _accept_root(id: StringName) -> void:
	match id:
		FieldMenuModel.ROW_BESTIARY:
			_open_bestiary()
		FieldMenuModel.ROW_CODEX:
			_open_codex()
		FieldMenuModel.ROW_SWELL:
			if not model.swell_heroes().is_empty():
				_open_heroes(&"")
		FieldMenuModel.ROW_MAP:
			if model.has_map():
				_open_map()
		FieldMenuModel.ROW_KITE:
			if model.has_kite():
				_open_kite()
		FieldMenuModel.ROW_SETTINGS:
			_open_settings()
		FieldMenuModel.ROW_QUIT:
			_open_quit()
		FieldMenuModel.ROW_CLOSE:
			close()
		_:
			if model.root_enabled(id) and CHILD_PAGES.has(id):
				_open_child(id)


## True while the bestiary, the codex, the map, the Settings hub or a party page is open over this
## menu (it has the input).
func _child_open() -> bool:
	return (
		(bestiary != null and bestiary.is_open())
		or (codex_menu != null and codex_menu.is_open())
		or (settings_menu != null and settings_menu.is_open())
		or (map_menu != null and map_menu.is_open())
		or (kite_menu != null and kite_menu.is_open())
		or (child != null and child.is_open())
	)


func _open_map() -> void:
	map_menu = ZoneMapMenu.open_in(self, model.map, true)  # over this menu: only its content moves
	visible = false
	map_menu.closed.connect(_on_map_closed)


func _on_map_closed() -> void:
	map_menu = null
	_come_back()


func _open_kite() -> void:
	var page := KiteMapMenu.create(model.kite)
	page.over_menu = true  # the same scrim and caustics: only the page's content moves
	kite_menu = FieldSubmenu.mount(page, self) as KiteMapMenu
	visible = false
	kite_menu.closed.connect(_on_kite_closed)


## Back from the Kite's map: after a flight this menu closes too (the party is leaving); else it returns.
func _on_kite_closed() -> void:
	var flew := kite_menu.flown != &""
	kite_menu = null
	if flew:
		close()
	else:
		_come_back()


## Opens the party page for root row `id` (CHILD_PAGES) over a PartySheet of this menu's state.
func _open_child(id: StringName) -> void:
	var sheet := PartySheet.new(model.state, model.heroes)
	var page := (CHILD_PAGES[id] as Script).call(&"create", sheet) as FieldSubmenu
	page.over_menu = true  # the same scrim and caustics: only the page's content moves
	child = FieldSubmenu.mount(page, self)
	visible = false
	child.closed.connect(_on_child_closed)


func _on_child_closed() -> void:
	if child is FormationMenu:
		_follow_formation()
	child = null
	_come_back()
	_refresh_party()  # an item, gear or the line may have changed
	_root.replace_rows(model.root_rows())
	_render()


## After the Formation page: the heroes follow the saved line's order (party_ids, then
## reserve_ids), so the other pages list them as the next fight has them. A stand-in party (nobody
## joined) is left as it is.
func _follow_formation() -> void:
	var joined := PartyGoods.joined_members(model.state)
	if not joined.is_empty():
		model.heroes = joined


func _open_quit() -> void:
	level = Level.QUIT
	_detail.replace_rows(model.quit_rows())
	_detail.set_cursor(0, false)  # Stay
	_notice = ""
	_render()


func _open_settings() -> void:
	settings_menu = SettingsMenu.open_in(self, true)
	visible = false
	settings_menu.closed.connect(_on_settings_closed)


func _on_settings_closed() -> void:
	settings_menu = null
	_come_back()
	_root.replace_rows(model.root_rows())  # in the text size or palette just chosen
	_render()


func _open_bestiary() -> void:
	bestiary = BestiaryMenu.open_in(self, null, true)
	visible = false
	bestiary.closed.connect(_on_bestiary_closed)


func _on_bestiary_closed() -> void:
	bestiary = null
	_come_back()


func _open_codex() -> void:
	codex_menu = CodexMenu.open_in(self, model.codex, true)
	visible = false
	codex_menu.closed.connect(_on_codex_closed)


func _on_codex_closed() -> void:
	codex_menu = null
	_come_back()


## The hero list, with the cursor on `on_hero` when given (coming back from its modes).
func _open_heroes(on_hero: StringName) -> void:
	level = Level.HEROES
	var rows := model.hero_rows()
	_detail.replace_rows(rows)
	_detail.set_cursor(0, false)
	for i in rows.size():
		if StringName(str(rows[i]["id"])) == on_hero:
			_detail.set_cursor(i, false)
	_notice = ""
	_render()


func _open_modes(cid: StringName) -> void:
	level = Level.MODES
	hero = cid
	var rows := model.mode_page_rows(cid)
	_detail.replace_rows(rows)
	_detail.set_cursor(0, false)
	var cur := StringName(str(model.current_mode_row(cid).get("id", "")))
	for i in rows.size():
		if StringName(str(rows[i]["id"])) == cur:
			_detail.set_cursor(i, false)
	_notice = ""
	_render()


func _move(delta: int) -> void:
	var page := _root if level == Level.ROOT else _detail
	if page.move(delta):
		_notice = ""
		_render()


func _render() -> void:
	var at_root := level == Level.ROOT
	_root.set_dimmed(not at_root)
	_detail.visible = not at_root
	match level:
		Level.MODES:
			_detail.set_header(model.modes_title(hero))
		Level.QUIT:
			_detail.set_header(model.quit_title())
		_:
			_detail.set_header(model.heroes_title())
	_place_detail(at_root)
	_objective.text = model.objective_line()
	_objective.visible = at_root and _objective.text != ""
	_objective_head.visible = _objective.visible
	_save_line.text = model.last_save_line()
	for l: Label in [_save_head, _save_line, _save_hint]:
		l.visible = at_root and _save_line.text != ""
	for card: PartyCard in _party_cards:
		card.visible = at_root and card.hero() != &""
	var id := StringName(str((_root if at_root else _detail).current_row().get("id", "")))
	match level:
		Level.ROOT:
			_desc.text = model.root_desc(id)
			_help.text = tr("FIELD_MENU_HELP_ROOT")
		Level.HEROES:
			_desc.text = model.hero_desc(id)
			_help.text = tr("FIELD_MENU_HELP_HEROES")
		Level.MODES:
			_desc.text = _notice if _notice != "" else model.mode_desc(hero, id)
			_help.text = tr("FIELD_MENU_HELP_MODES")
		Level.QUIT:
			_desc.text = model.quit_desc(id)
			_help.text = tr("FIELD_MENU_HELP_QUIT")
	_stack_info()


## Stacks the Last saved block and the objective down the right column from their data rects, a line each at the
## data's line height grown with the text size setting (the Act I UI pass of 2026-10-30: at 130% the hint sat on
## the date and the objective ran into the help; at 100% nothing moves). The objective takes the room left above
## the help line; when its wrapped lines need more, the save hint (a standing reminder) steps aside for it, and then
## the objective's font shrinks into what is left.
func _stack_info() -> void:
	_objective.remove_theme_font_size_override(&"font_size")
	if _save_hint.visible and not _stack_fits(true):
		_save_hint.visible = false
	if not _stack_fits(_save_hint.visible):  # still too long: the objective shrinks (to 80% at most) into the room
		HudLayout.fit_lines(_objective, _help.position.y - _objective.position.y)


## Places the blocks (with or without the save hint). True when the objective's lines fit above the help line.
func _stack_fits(with_hint: bool) -> bool:
	var sm: Dictionary = _d.get("last_save", {})
	var om: Dictionary = _d.get("objective", {})
	var grow := UiSettings.shared().text_scale()
	var y := HudLayout.rect_of(sm).position.y
	for l: Label in [_save_head, _save_line, _save_hint]:
		if l == _save_hint and not with_hint:
			continue
		var h := HudLayout.num(sm, "line_height") * grow
		l.position.y = y
		l.size.y = h
		y += h
	var orr := HudLayout.rect_of(om)
	var top := maxf(orr.position.y, y if _save_line.visible else orr.position.y)
	var head_h := HudLayout.num(om, "label_height") * grow
	_objective_head.position.y = top
	_objective_head.size.y = head_h
	_objective.position.y = top + head_h
	var room := maxf(_help.position.y - _objective.position.y, 0.0)
	_objective.size.y = room
	# a Label grows past `room` to its own minimum height (its wrapped lines with their spacing and margins)
	return not _objective.visible or _objective.get_combined_minimum_size().y <= room + 0.5


## The right page is as tall as its rows; the line sits under it (at its top on the root).
func _place_detail(at_root: bool) -> void:
	var dm: Dictionary = _d.get("detail", {})
	var em: Dictionary = _d.get("desc", {})
	var top := HudLayout.rect_of(dm).position.y
	_detail.size.y = MenuPage.height_for(dm, maxi(_detail.row_count(), 1), true)
	_desc.position.y = top if at_root else top + _detail.size.y + HudLayout.num(em, "gap")


## Shows the menu again when a page over it closes; its content fades back in over the still backdrop.
func _come_back() -> void:
	visible = true
	if is_open() and _motion != null:
		_motion.play_in(true, "return_sec")


func _on_motion_gone() -> void:
	gone.emit()


func _restore_pause() -> void:
	if _owns_pause and is_inside_tree():
		get_tree().paused = false
	_owns_pause = false


# --- Build ---------------------------------------------------------------------------------------


func _build() -> void:
	var scrim := ColorRect.new()
	scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = SCRIM_SHADER
	mat.set_shader_parameter(&"tint", get_theme_color(&"scrim", HymnThemeBuilder.PALETTE_TYPE))
	scrim.material = mat
	add_child(scrim)
	add_child(CausticBackdrop.new())  # ADR 0033
	var pm: Dictionary = _d.get("panel", {})
	var panel := Panel.new()
	HudLayout.place(panel, pm)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(panel)
	var pr := HudLayout.rect_of(pm)
	var pad := HudLayout.num(pm, "pad")
	var title := _label(&"BannerLabel", Rect2(pr.position + Vector2(pad, pad), Vector2(pr.size.x - pad * 2.0, 0.0)))
	title.size.y = HudLayout.num(pm, "title_height")
	title.text = tr("FIELD_MENU_TITLE")
	_title_rule(Rect2(title.position, Vector2(pr.size.x * 0.5, title.size.y)))
	if _heretics():  # Act II (M4-A2P-082): the act's one quiet reminder, never red
		var sub := _label(&"HelpDimLabel", Rect2(title.position, title.size))
		sub.text = tr("FIELD_MENU_SUBTITLE_HERETIC")
		sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		sub.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	var help_h := HudLayout.num(pm, "help_height")
	var help_at := Vector2(pr.position.x + pad, pr.end.y - pad - help_h)
	_help = HudLayout.wrap_upward(_label(&"HelpDimLabel", Rect2(help_at, Vector2(pr.size.x - pad * 2.0, help_h))))
	var rm: Dictionary = _d.get("root", {})
	_root = _page(rm, &"field_root", "", 0)
	_root.row_hovered.connect(_on_hovered.bind(Level.ROOT))
	_root.row_clicked.connect(_on_clicked.bind(Level.ROOT))
	var dm: Dictionary = _d.get("detail", {})
	_detail = _page(dm, &"field_detail", " ", int(HudLayout.num(dm, "max_rows")))
	_detail.row_hovered.connect(_on_hovered.bind(Level.HEROES))
	_detail.row_clicked.connect(_on_clicked.bind(Level.HEROES))
	var dr := HudLayout.rect_of(dm)
	_desc = _label(&"BodyLabel", Rect2(dr.position, Vector2(dr.size.x, HudLayout.num(_d.get("desc", {}), "height"))))
	_desc.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var om: Dictionary = _d.get("objective", {})
	var orr := HudLayout.rect_of(om)
	var head_h := HudLayout.num(om, "label_height")
	_objective_head = _label(&"DimLabel", Rect2(orr.position, Vector2(orr.size.x, head_h)))
	_objective_head.text = tr("OBJ_LABEL")
	_objective = _label(&"BodyLabel", Rect2(orr.position + Vector2(0.0, head_h), orr.size - Vector2(0.0, head_h)))
	_objective.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_objective.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_build_last_save(_d.get("last_save", {}))
	_build_party(_d.get("party", {}))


## M2-MNU-304: the active line as cards across the right column on the root, under the line about the
## highlighted row: portrait, name, HP and MP (the playtest's "parts look primitive").
func _build_party(pm: Dictionary) -> void:
	var at := HudLayout.rect_of(pm).position
	var step := HudLayout.num(pm, "card_w") + HudLayout.num(pm, "spacing")
	for i in FormationMenuModel.places():
		var card := PartyCard.new()
		card.setup(pm)
		card.position = at + Vector2(step * i, 0.0)
		add_child(card)
		_party_cards.append(card)
	_refresh_party()


## Fills the cards from the active line as the next fight has it (FormationMenuModel over a PartySheet).
func _refresh_party() -> void:
	var line := FormationMenuModel.new(PartySheet.new(model.state, model.heroes))
	for i in _party_cards.size():
		var cid := line.active[i] if i < line.active.size() else &""
		if cid == &"":
			_party_cards[i].show_hero(&"", "", {})
			continue
		_party_cards[i].show_hero(cid, line.sheet.hero_name(cid), line.vitals(cid))


## M2-MNU-300: the root's Last saved block above the objective: a dim head, the place and time, and the
## reminder that saving happens at shrines (there is no save row).
func _build_last_save(sm: Dictionary) -> void:
	var sr := HudLayout.rect_of(sm)
	var line_h := HudLayout.num(sm, "line_height")
	_save_head = _label(&"DimLabel", Rect2(sr.position, Vector2(sr.size.x, line_h)))
	_save_head.text = tr(FieldMenuModel.LAST_SAVE_HEAD_KEY)
	_save_line = _label(&"BodyLabel", Rect2(sr.position + Vector2(0.0, line_h), Vector2(sr.size.x, line_h)))
	_save_line.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_save_hint = _label(&"HelpDimLabel", Rect2(sr.position + Vector2(0.0, line_h * 2.0), Vector2(sr.size.x, line_h)))
	_save_hint.text = tr(FieldMenuModel.SAVE_HINT_KEY)
	_save_hint.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS


## A MenuPage at its block's rect, as tall as `rows` rows need (0 = the root's three).
func _page(metrics: Dictionary, pid: StringName, title: String, rows: int) -> MenuPage:
	var page := MenuPage.new()
	HudLayout.place(page, metrics)
	var count := rows if rows > 0 else model.root_ids().size()
	page.size.y = MenuPage.height_for(metrics, count, title != "")
	add_child(page)
	page.reduced_motion = UiSettings.shared().reduced_motion()
	page.setup(metrics, pid, title, [])
	return page


func _on_hovered(_index: int, page_level: Level) -> void:
	if (page_level == Level.ROOT) == (level == Level.ROOT):
		_notice = ""
		_render()


func _on_clicked(index: int, page_level: Level) -> void:
	if not is_open() or _child_open():
		return
	if page_level == Level.ROOT and level != Level.ROOT:
		level = Level.ROOT  # a click on the root page goes back to it
	elif page_level != Level.ROOT and level == Level.ROOT:
		return
	(_root if level == Level.ROOT else _detail).set_cursor(index, false)
	accept()


## True once the party are heretics (Act II, ch14_declared_heretics): the title row carries the subtitle.
func _heretics() -> bool:
	return model != null and model.state != null and bool(model.state.flags.get("ch14_declared_heretics", false))


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l


## The gold OrnamentRule under the menu's title (ADR 0033), across the left half of the panel.
func _title_rule(title: Rect2) -> void:
	var rule := OrnamentRule.new()
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	rule.position = Vector2(title.position.x, title.end.y - node)
	rule.size = Vector2(title.size.x, node * 2.0)
	add_child(rule)
