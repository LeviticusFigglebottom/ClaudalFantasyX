class_name FieldSubmenu
extends Control
## The shared frame of the pages the field menu opens for the party (M2-MNU-01..04: Lattice,
## Equip, Items, Status): its own CanvasLayer over the field menu's, the scrim and caustic
## backdrop, the gold-ruled panel title and the help line, the tree paused while open, and
## UiSettings followed (text size, palette, reduced motion), as BestiaryMenu does.
##
## A page extends this, names its layout file (data_path / data_section), builds itself in
## _build_page() and reads input in handle_input(), calling super for Cancel (which closes).
## Open one with FieldSubmenu.mount(MyPage.new(...), host); the layer frees itself on close.
## Layouts are at the 1920 x 1080 reference, every rect a multiple of 3 (as field_menu.json).

signal closed

const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")
## Over the field menu (60), under the Settings hub (66), like the bestiary.
const DEFAULT_CANVAS_LAYER := 64

## Pause the tree while open (the field must not move under a menu). Captures turn it off.
@export var pause_tree := true

## This page's layout block (data_section of data_path).
var _d: Dictionary = {}
var _owns_pause := false
var _is_closed := false


## Puts `menu` on its own CanvasLayer under `host` and opens it; the layer frees itself when the
## menu closes.
static func mount(menu: FieldSubmenu, host: Node) -> FieldSubmenu:
	var layer := CanvasLayer.new()
	layer.layer = int(menu.load_layout().get("canvas_layer", DEFAULT_CANVAS_LAYER))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(menu)
	menu.closed.connect(layer.queue_free)
	host.add_child(layer)
	return menu


## The JSON file holding this page's layout (override).
func data_path() -> String:
	return ""


## The top-level key of this page's block in data_path() (override).
func data_section() -> String:
	return ""


func load_layout() -> Dictionary:
	var path := data_path()
	if path == "":
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	var section := data_section()
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get(section)) != TYPE_DICTIONARY:
		push_error("%s: could not read '%s' from %s" % [get_script().get_global_name(), section, path])
		return {}
	return (parsed as Dictionary)[section] as Dictionary


func _ready() -> void:
	_d = load_layout()
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiSettings.shared().follow(self)
	_build_backdrop()
	_build_page()
	if pause_tree and not get_tree().paused:
		get_tree().paused = true
		_owns_pause = true


func _exit_tree() -> void:
	_restore_pause()


func is_open() -> bool:
	return not _is_closed


func close() -> void:
	if _is_closed:
		return
	_is_closed = true
	_restore_pause()
	closed.emit()


func _unhandled_input(event: InputEvent) -> void:
	if is_open() and handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event; returns true when the page used it. Tests call it directly. The base
## closes on ui_cancel; pages handle their own keys first and call super for the rest.
func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_cancel"):
		close()
		return true
	return false


## Builds the page's own controls (override). `_d` holds its layout.
func _build_page() -> void:
	pass


# --- Helpers for pages ----------------------------------------------------------------------------


## The framed panel at `metrics.rect`, with a banner title under a gold rule and a dim help line at
## its foot (metrics: rect, pad, title_height, help_height). Returns the help label.
func _framed_panel(metrics: Dictionary, title_text: String) -> Label:
	var panel := Panel.new()
	HudLayout.place(panel, metrics)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(panel)
	var pr := HudLayout.rect_of(metrics)
	var pad := HudLayout.num(metrics, "pad")
	var title := _label(&"BannerLabel", Rect2(pr.position + Vector2(pad, pad), Vector2(pr.size.x - pad * 2.0, 0.0)))
	title.size.y = HudLayout.num(metrics, "title_height")
	title.text = title_text
	_title_rule(Rect2(title.position, Vector2(pr.size.x * 0.5, title.size.y)))
	var help_h := HudLayout.num(metrics, "help_height")
	var help_at := Vector2(pr.position.x + pad, pr.end.y - pad - help_h)
	return _label(&"HelpDimLabel", Rect2(help_at, Vector2(pr.size.x - pad * 2.0, help_h)))


## A MenuPage at its block's rect, as tall as `rows` rows (titled when `title` is not "").
func _menu_page(metrics: Dictionary, pid: StringName, title: String, rows: int) -> MenuPage:
	var page := MenuPage.new()
	HudLayout.place(page, metrics)
	page.size.y = MenuPage.height_for(metrics, maxi(rows, 1), title != "")
	add_child(page)
	page.reduced_motion = UiSettings.shared().reduced_motion()
	page.setup(metrics, pid, title, [])
	return page


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l


## A theme palette color (HymnThemeBuilder roles: focus_gold, text_dim, danger, swell, ...).
func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _build_backdrop() -> void:
	var scrim := ColorRect.new()
	scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = SCRIM_SHADER
	mat.set_shader_parameter(&"tint", _c(&"scrim"))
	scrim.material = mat
	add_child(scrim)
	add_child(CausticBackdrop.new())  # ADR 0033


## The gold OrnamentRule under a banner title (ADR 0033).
func _title_rule(title: Rect2) -> void:
	var rule := OrnamentRule.new()
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	rule.position = Vector2(title.position.x, title.end.y - node)
	rule.size = Vector2(title.size.x, node * 2.0)
	add_child(rule)


func _restore_pause() -> void:
	if _owns_pause and is_inside_tree():
		get_tree().paused = false
	_owns_pause = false
