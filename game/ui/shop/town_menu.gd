class_name TownMenu
extends Control
## What the shop and inn menus share (M2-UI-06): a scrimmed panel titled with the shop or inn's
## name, the purse on the right of the title row, a help line at the foot, and the line about
## the highlighted row with a status line under it (the deal's cost, or why it is refused, in
## the danger color). Like FieldMenu and SaveMenu it brings its own CanvasLayer (open_in) and
## pauses the tree while open, so the field stays still and the player can't walk off mid-deal.
## Subclasses: ShopMenu, InnMenu. Layout: game/data/ui/shop_menu.json (1920 x 1080 reference).

signal closed
## The close transition has finished (at once under Reduced motion): host_in's layer frees itself (MenuMotion).
signal gone

const DATA_PATH := "res://game/data/ui/shop_menu.json"
const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")

## Pause the tree while open (the field must not move under a menu).
@export var pause_tree := true

var _d: Dictionary = {}
var _title: Label
var _purse: Label
var _desc: Label
var _status: Label
var _help: Label
var _owns_pause := false
var _is_closed := false
var _refused := false
var _motion: MenuMotion


## Puts `menu` on its own CanvasLayer under `host`; the layer frees itself when the menu closes.
static func host_in(host: Node, menu: TownMenu, section: String) -> void:
	var layer := CanvasLayer.new()
	layer.layer = int(load_data(section).get("canvas_layer", 1))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(menu)
	menu.gone.connect(layer.queue_free)
	host.add_child(layer)


static func load_data(section: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get(section)) != TYPE_DICTIONARY:
		push_error("TownMenu: could not read '%s' from %s" % [section, DATA_PATH])
		return {}
	return (parsed as Dictionary)[section] as Dictionary


func _ready() -> void:
	_d = load_data(_section())
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	UiSettings.shared().follow(self)  # the player's text size and palette (M2-UI-28 found it missing)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_build_frame()
	_build()
	UiFrame.centre(self)  # M2-UI-29
	_render()
	if pause_tree and not get_tree().paused:
		get_tree().paused = true
		_owns_pause = true
	# The shop and the inn move like every other menu (the "parts look primitive" pass): over the open world.
	MenuMotion.follow_reduced_motion(self)
	_motion = MenuMotion.new(self)
	_motion.gone.connect(gone.emit)
	_motion.play_in()


func _exit_tree() -> void:
	_restore_pause()


func is_open() -> bool:
	return not _is_closed


func close() -> void:
	if _is_closed:
		return
	_is_closed = true
	_restore_pause()
	if _motion != null:
		_motion.play_out()
	else:
		visible = false
		gone.emit()
	closed.emit()


## The open and close transitions (null before _ready). Tests drive them with motion().finish().
func motion() -> MenuMotion:
	return _motion


func _unhandled_input(event: InputEvent) -> void:
	if is_open() and handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the menu used it. Tests call this directly.
func handle_input(_event: InputEvent) -> bool:
	return false


func title_text() -> String:
	return _title.text


func purse_text() -> String:
	return _purse.text


func desc_text() -> String:
	return _desc.text


func status_text() -> String:
	return _status.text


## True when the status line is a refusal (drawn in the danger color).
func status_is_refusal() -> bool:
	return _refused and _status.text != ""


func help_text() -> String:
	return _help.text


# --- for subclasses ------------------------------------------------------------------------------


## The shop_menu.json section this menu reads.
func _section() -> String:
	return ""


## Builds the pages (after the frame).
func _build() -> void:
	pass


## Redraws the lines from the current state.
func _render() -> void:
	pass


func _set_status(line: Dictionary) -> void:
	_status.text = str(line.get("text", ""))
	_refused = not bool(line.get("ok", true))
	var role := &"danger" if _refused else &"text_dim"
	_status.add_theme_color_override(&"font_color", _c(role))
	_fit_desc()


## The line about the row is as tall as its text needs, up to the data "desc" height, and the
## status sits "status" "gap" under it (M2-UI-15: a fixed height cut long lines short or left a
## hole). Every page renders through _set_status, so this runs after each redraw.
func _fit_desc() -> void:
	var gap := HudLayout.num(_d.get("status", {}), "gap")
	var cap := HudLayout.num(_d.get("desc", {}), "height")
	# The Act I UI pass (2026-10-30): at 130 % a two-line line and a two-line refusal ran into the help line. The
	# column from the line's top to the help is shared: the status keeps its lines, the line gets the rest.
	_status.remove_theme_font_size_override(&"font_size")
	var status_h := ceilf(HudLayout.lines_height(_status)) if _status.text != "" else 0.0
	var room := _help.position.y - _desc.position.y - gap - status_h
	cap = maxf(minf(cap, room), 0.0)
	_desc.size.y = cap  # measure the wrap at full height: the label's own line metrics
	HudLayout.fit_lines(_desc, cap)  # a line too long for the cap at 130 % shrinks a little first
	_desc.size.y = minf(ceilf(HudLayout.lines_height(_desc)), cap) if _desc.text != "" else 0.0
	_status.position.y = _desc.position.y + _desc.size.y + gap
	# M4-A2P-1700: the status gets the column down to the help line, not the one line it was built with, or its
	# wrapped second line is trimmed to an ellipsis ("The door is barred. No rooms for…" at 130 %).
	_status.size.y = maxf(_help.position.y - _status.position.y, 0.0)
	HudLayout.fit_lines(_status, _status.size.y)


## Puts the line and the status under `top` (a y in reference pixels).
func _place_lines(top: float) -> void:
	_desc.position.y = top
	_status.position.y = top + _desc.size.y


func _page(metrics: Dictionary, pid: StringName, title: String, rows: int) -> MenuPage:
	var page := MenuPage.new()
	HudLayout.place(page, metrics)
	page.size.y = MenuPage.height_for(metrics, rows, title != "")
	add_child(page)
	page.setup(metrics, pid, title, [])
	return page


func _restore_pause() -> void:
	if _owns_pause and is_inside_tree():
		get_tree().paused = false
	_owns_pause = false


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _build_frame() -> void:
	var scrim := ColorRect.new()
	scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = SCRIM_SHADER
	mat.set_shader_parameter(&"tint", _c(&"scrim"))
	scrim.material = mat
	add_child(scrim)
	var pm: Dictionary = _d.get("panel", {})
	var panel := Panel.new()
	HudLayout.place(panel, pm)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(panel)
	var pr := HudLayout.rect_of(pm)
	var pad := HudLayout.num(pm, "pad")
	var title_h := HudLayout.num(pm, "title_height")
	_title = _label(&"BannerLabel", Rect2(pr.position + Vector2(pad, pad), Vector2(pr.size.x - pad * 2.0, title_h)))
	_purse = _label(&"HudNumber", HudLayout.rect_of(_d.get("purse", {})))
	_purse.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_purse.add_theme_color_override(&"font_color", _c(&"text_dim"))
	var help_h := HudLayout.num(pm, "help_height")
	var help_at := Vector2(pr.position.x + pad, pr.end.y - pad - help_h)
	_help = HudLayout.wrap_upward(_label(&"HelpDimLabel", Rect2(help_at, Vector2(pr.size.x - pad * 2.0, help_h))))
	var dr := HudLayout.rect_of(_d.get("detail", {}))
	_desc = _label(&"BodyLabel", Rect2(dr.position, Vector2(dr.size.x, HudLayout.num(_d.get("desc", {}), "height"))))
	_desc.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_desc.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS  # long translations (M2-UI-15)
	var sh := HudLayout.num(_d.get("status", {}), "height")
	_status = _label(&"BodyLabel", Rect2(dr.position + Vector2(0.0, _desc.size.y), Vector2(dr.size.x, sh)))
	_status.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_status.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
