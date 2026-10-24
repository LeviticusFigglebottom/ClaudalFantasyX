class_name FieldMenu
extends Control
## The field menu (M2-UI-04, SPEC §6.6): opened from the field with ui_cancel (Escape, B /
## Circle), it pauses the tree like SaveMenu and reaches the bestiary (BestiaryMenu), each
## hero's Swell fill mode (SPEC §6.2; BattleSwellCarry through FieldMenuModel) and the Settings
## hub (SettingsMenu: Graphics, Accessibility; M2-UI-09). It follows UiSettings (text size,
## palette, reduced motion).
## Layout: game/data/ui/field_menu.json (1920x1080 reference). Words: FieldMenuModel.
##
## Three levels: ROOT (Bestiary / Swell / Settings / Close) on the left; HEROES (each Swell hero and the mode
## in use) and MODES (one hero's unlocked modes, "In use" on the current one) on the right. The
## line under the right page says what the highlighted row means (pillar 4).
##
## Input (keyboard and controller through ui_*): ui_up / ui_down move, ui_accept chooses,
## ui_cancel goes back a level and closes from the root. Mouse: hover to move, click to choose.
## While the bestiary or the Settings hub is open it takes the input, and this menu hides until
## it closes.

signal closed

enum Level { ROOT, HEROES, MODES }

const SCENE_PATH := "res://game/ui/field_menu/field_menu.tscn"
const DATA_PATH := "res://game/data/ui/field_menu.json"
const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")
## The field action that opens the menu (FieldController).
const OPEN_ACTION := &"ui_cancel"

## Pause the tree while open (the field must not move under a menu).
@export var pause_tree := true

var model: FieldMenuModel
var level := Level.ROOT
## The hero whose modes are on show (MODES).
var hero: StringName = &""
## The bestiary opened from here (null when closed).
var bestiary: BestiaryMenu
## The Settings hub opened from here (null when closed).
var settings_menu: SettingsMenu

var _d: Dictionary = {}
var _root: MenuPage
var _detail: MenuPage
var _desc: Label
var _help: Label
var _owns_pause := false
var _is_closed := false
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
	menu.closed.connect(layer.queue_free)
	host.add_child(layer)
	return menu


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("field_menu")) != TYPE_DICTIONARY:
		push_error("FieldMenu: could not read 'field_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["field_menu"] as Dictionary


## Sets the model before the menu enters the tree (null = the live game).
func configure(with_model: FieldMenuModel = null) -> void:
	model = with_model


func _ready() -> void:
	if model == null:
		model = FieldMenuModel.from_game()
	_d = load_data()
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiSettings.shared().follow(self)
	_build()
	_root.replace_rows(model.root_rows())
	_render()
	if pause_tree and not get_tree().paused:
		get_tree().paused = true
		_owns_pause = true


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


## Goes back one level; closes from the root.
func back() -> void:
	match level:
		Level.ROOT:
			close()
		Level.HEROES:
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
	if settings_menu != null and settings_menu.is_open():
		settings_menu.close()
	_restore_pause()
	closed.emit()


## The root row under the cursor, the right page's rows and the lines on show (tests read these).
func root_page() -> MenuPage:
	return _root


func detail_page() -> MenuPage:
	return _detail


func desc_text() -> String:
	return _desc.text


func help_text() -> String:
	return _help.text


func _accept_root(id: StringName) -> void:
	match id:
		FieldMenuModel.ROW_BESTIARY:
			_open_bestiary()
		FieldMenuModel.ROW_SWELL:
			if not model.swell_heroes().is_empty():
				_open_heroes(&"")
		FieldMenuModel.ROW_SETTINGS:
			_open_settings()
		FieldMenuModel.ROW_CLOSE:
			close()


## True while the bestiary or the Settings hub is open over this menu (it has the input).
func _child_open() -> bool:
	return (bestiary != null and bestiary.is_open()) or (settings_menu != null and settings_menu.is_open())


func _open_settings() -> void:
	settings_menu = SettingsMenu.open_in(self)
	visible = false
	settings_menu.closed.connect(_on_settings_closed)


func _on_settings_closed() -> void:
	settings_menu = null
	visible = true
	_root.replace_rows(model.root_rows())  # in the text size or palette just chosen
	_render()


func _open_bestiary() -> void:
	bestiary = BestiaryMenu.open_in(self)
	visible = false
	bestiary.closed.connect(_on_bestiary_closed)


func _on_bestiary_closed() -> void:
	bestiary = null
	visible = true


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
	_detail.set_header(model.modes_title(hero) if level == Level.MODES else model.heroes_title())
	_place_detail(at_root)
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


## The right page is as tall as its rows; the line sits under it (at its top on the root).
func _place_detail(at_root: bool) -> void:
	var dm: Dictionary = _d.get("detail", {})
	var em: Dictionary = _d.get("desc", {})
	var top := HudLayout.rect_of(dm).position.y
	_detail.size.y = MenuPage.height_for(dm, maxi(_detail.row_count(), 1), true)
	_desc.position.y = top if at_root else top + _detail.size.y + HudLayout.num(em, "gap")


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
	var help_h := HudLayout.num(pm, "help_height")
	var help_at := Vector2(pr.position.x + pad, pr.end.y - pad - help_h)
	_help = _label(&"HelpDimLabel", Rect2(help_at, Vector2(pr.size.x - pad * 2.0, help_h)))
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


## A MenuPage at its block's rect, as tall as `rows` rows need (0 = the root's three).
func _page(metrics: Dictionary, pid: StringName, title: String, rows: int) -> MenuPage:
	var page := MenuPage.new()
	HudLayout.place(page, metrics)
	var count := rows if rows > 0 else FieldMenuModel.ROOT_IDS.size()
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
