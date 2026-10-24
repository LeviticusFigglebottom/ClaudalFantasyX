class_name ZoneMapMenu
extends Control
## The zone map page (M2-UI-18, SPEC §6.6), opened from the field menu's Map row: the current
## zone drawn from data (ZoneMapView), the pilgrimage strip (RouteStrip), the objective's line on
## top, a legend of places (a MenuPage) with each place's glyph, the line under the map that says
## where the highlighted place lies from the player, and the side errands. Words: MapModel.
## Layout: game/data/ui/zone_map_menu.json (1920x1080 reference). Field menu family: a tide-notch
## panel over the scrim and caustic backdrop, a banner title with its OrnamentRule, HelpDimLabel help.
##
## Input (keyboard and controller through ui_*): ui_up / ui_down choose a place (the map rings it),
## ui_cancel closes. Mouse: hover a legend row or a glyph on the map to choose it, the wheel steps.
## Open it with ZoneMapMenu.open_in(host, model) (its own CanvasLayer, between the field menu's
## and the bestiary's); it pauses the tree while open unless the opener already has.

signal closed

const SCENE_PATH := "res://game/ui/map/zone_map_menu.tscn"
const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")
const PAGE_ID := &"zone_map"
const PLAYER_GROUP := &"player"

@export var pause_tree := true

var model: MapModel

var _d: Dictionary = {}
var _view: ZoneMapView
var _route: RouteStrip
var _legend: MenuPage
var _legend_marks: Control
var _goal_mark: Control
var _objective: Label
var _poi_line: Label
var _errands: Label
var _errands_head: Label
var _help: Label
var _title: Label
var _owns_pause := false
var _is_closed := false


## Instances the page on its own CanvasLayer under `host` and opens it; the layer frees itself
## when the page closes.
static func open_in(host: Node, with_model: MapModel) -> ZoneMapMenu:
	var menu := (load(SCENE_PATH) as PackedScene).instantiate() as ZoneMapMenu
	menu.configure(with_model)
	var layer := CanvasLayer.new()
	layer.layer = int(MapModel.load_data().get("canvas_layer", 1))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(menu)
	menu.closed.connect(layer.queue_free)
	host.add_child(layer)
	return menu


## The live field's map: the zone of the running scene (ZoneMaps.zone_for_scene), and the player
## (the FieldController in group "player") where it stands and the way it faces. A scene with no
## map gives a model whose has_map() is false; a scene with no player, a map without the arrow.
static func live_model(from: Node) -> MapModel:
	var tree := from.get_tree()
	var maps := ZoneMaps.new()
	var scene := tree.current_scene
	var zone := maps.zone_for_scene(scene.scene_file_path) if scene != null else &""
	var player := tree.get_first_node_in_group(PLAYER_GROUP) as Node3D
	if player == null:
		var up := from
		while up != null and not up is FieldController:
			up = up.get_parent()
		player = up as Node3D
	if player == null or not player.is_inside_tree():
		return MapModel.new(zone, Vector3.INF, 0.0, Callable(), maps)
	return MapModel.new(zone, player.global_position, player.global_rotation.y, Callable(), maps)


func configure(with_model: MapModel) -> void:
	model = with_model


func _ready() -> void:
	_d = MapModel.load_data()
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiSettings.shared().follow(self)
	_build()
	UiFrame.centre(self)  # M2-UI-29
	_fill()
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


## Applies one input event. Returns true when the page used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif _wheel(event) != 0:
		_move(_wheel(event))
	elif event.is_action_pressed(&"ui_cancel"):
		close()
	elif event.is_action_pressed(&"ui_accept"):
		pass  # nothing to confirm: the map already rings the place under the cursor
	else:
		return false
	return true


## -1 / 1 for a mouse wheel turn up / down, else 0.
static func _wheel(event: InputEvent) -> int:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return 0
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		return -1
	return 1 if mb.button_index == MOUSE_BUTTON_WHEEL_DOWN else 0


## Puts the cursor on place `index` (the legend, the map's ring and the line follow).
func select(index: int) -> void:
	_legend.set_cursor(index, false)
	_show()


## The place under the cursor (&"" when the zone lists none).
func current_poi() -> StringName:
	return StringName(str(_legend.current_row().get("id", "")))


func view() -> ZoneMapView:
	return _view


func legend() -> MenuPage:
	return _legend


func route() -> RouteStrip:
	return _route


func objective_text() -> String:
	return _objective.text


func poi_line_text() -> String:
	return _poi_line.text


func errands_text() -> String:
	return _errands.text


func help_text() -> String:
	return _help.text


func title_text() -> String:
	return _title.text


func _move(delta: int) -> void:
	if _legend.move(delta):
		_show()


func _show() -> void:
	var pid := current_poi()
	_view.highlight = pid
	_view.queue_redraw()
	_poi_line.text = model.poi_line(pid)
	_legend_marks.queue_redraw()


func _fill() -> void:
	_title.text = model.zone_name()
	_objective.text = model.objective_line()
	_goal_mark.visible = model.objective_poi() != &""
	_errands.text = model.errands_text()
	_route.setup(model.route_stops(), _d.get("route", {}))
	_view.setup(model, _d.get("map", {}), _d.get("pieces", {}))
	_legend.replace_rows(model.poi_rows())
	_place_legend()
	select(model.first_index())


## The legend is as tall as its places (up to max_rows); the errands sit under it.
func _place_legend() -> void:
	var lm: Dictionary = _d.get("legend", {})
	var em: Dictionary = _d.get("errands", {})
	_legend.size.y = MenuPage.height_for(lm, maxi(_legend.row_count(), 1), true)
	_legend_marks.size = _legend.size
	var top := _legend.position.y + _legend.size.y + HudLayout.num(em, "gap")
	_errands_head.position.y = top
	_errands.position.y = top + HudLayout.num(em, "header_height")


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
	var title_h := HudLayout.num(pm, "title_height")
	_title = _label(&"BannerLabel", Rect2(pr.position + Vector2(pad, pad), Vector2(pr.size.x * 0.5 - pad, title_h)))
	var rule := OrnamentRule.new()  # ADR 0033: the gold rule under the title
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	rule.position = Vector2(_title.position.x, _title.position.y + title_h - node)
	rule.size = Vector2(_title.size.x * 0.6, node * 2.0)
	add_child(rule)
	_route = RouteStrip.new()
	HudLayout.place(_route, _d.get("route", {}))
	add_child(_route)
	_build_objective()
	var mm: Dictionary = _d.get("map", {})
	var frame := Panel.new()
	frame.theme_type_variation = &"PanelSmall"
	HudLayout.place(frame, mm)
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(frame)
	_view = ZoneMapView.new()
	var inset := HudLayout.num(mm, "inset")
	var mr := HudLayout.rect_of(mm).grow(-inset)
	_view.position = mr.position
	_view.size = mr.size
	_view.reduced_motion = UiSettings.shared().reduced_motion()
	_view.poi_hovered.connect(_on_map_poi)
	_view.poi_clicked.connect(_on_map_poi)
	add_child(_view)
	_poi_line = _label(&"MenuLabel", HudLayout.rect_of(_d.get("poi_line", {})))
	_poi_line.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	var lm: Dictionary = _d.get("legend", {})
	_legend = MenuPage.new()
	HudLayout.place(_legend, lm)
	add_child(_legend)
	_legend.reduced_motion = UiSettings.shared().reduced_motion()
	_legend.setup(lm, PAGE_ID, tr("MAP_PLACES"), [])
	_legend.row_hovered.connect(func(_i: int) -> void: _show())
	_legend.row_clicked.connect(select)
	_legend_marks = Control.new()
	_legend_marks.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_legend_marks.position = _legend.position
	_legend_marks.size = _legend.size
	_legend_marks.draw.connect(_draw_legend_marks)
	add_child(_legend_marks)
	var em: Dictionary = _d.get("errands", {})
	var er := HudLayout.rect_of(em)
	var eh := HudLayout.num(em, "header_height")
	_errands_head = _label(&"HeaderLabel", Rect2(er.position, Vector2(er.size.x, eh)))
	_errands_head.text = tr("MAP_ERRANDS")
	_errands = _label(&"DimLabel", Rect2(er.position + Vector2(0.0, eh), Vector2(er.size.x, er.size.y - eh)))
	_errands.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_errands.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var help_h := HudLayout.num(pm, "help_height")
	var help_at := Vector2(pr.position.x + pad, pr.end.y - pad - help_h)
	_help = _label(&"HelpDimLabel", Rect2(help_at, Vector2(pr.size.x - pad * 2.0, help_h)))
	_help.text = tr("MAP_HELP")


## The objective's line across the top, led by the map's objective marker (held still here).
func _build_objective() -> void:
	var om: Dictionary = _d.get("objective", {})
	var r := HudLayout.rect_of(om)
	var indent := HudLayout.num(om, "text_indent")
	_goal_mark = Control.new()
	_goal_mark.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_goal_mark.position = r.position
	_goal_mark.size = Vector2(indent, r.size.y)
	_goal_mark.draw.connect(
		func() -> void:
			var mm: Dictionary = _d.get("map", {})
			MapGlyphs.draw_objective(
				_goal_mark,
				_goal_mark.size * 0.5,
				HudLayout.num(om, "glyph_px"),
				HudLayout.num(mm, "objective_line_px"),
				_goal_mark.get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE),
				_goal_mark.get_theme_color(&"map_glyph_back", HymnThemeBuilder.PALETTE_TYPE),
				-1.0,
				0.0
			)
	)
	add_child(_goal_mark)
	_objective = _label(&"BodyLabel", Rect2(r.position + Vector2(indent, 0.0), Vector2(r.size.x - indent, r.size.y)))
	_objective.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS


## Each visible legend row's glyph at its right end, and the objective's marker beside its place.
func _draw_legend_marks() -> void:
	var lm: Dictionary = _d.get("legend", {})
	var mm: Dictionary = _d.get("map", {})
	var px := HudLayout.num(lm, "glyph_px")
	var x := _legend.size.x - HudLayout.num(lm, "glyph_inset")
	var top := HudLayout.num(lm, "header_height")
	var bottom := _legend.size.y - HudLayout.num(lm, "row_inset")
	var pois := model.pois()
	var goal := model.objective_poi()
	for i in pois.size():
		var y := _legend.row_rect(i).get_center().y
		if y < top or y > bottom:
			continue
		var at := Vector2(x, y)
		MapGlyphs.draw_poi(
			_legend_marks,
			pois[i]["kind"],
			at,
			px,
			HudLayout.num(mm, "glyph_line_px"),
			_c(&"text"),
			_c(&"map_glyph_back"),
			_c(&"gauge_border")
		)
		if pois[i]["id"] == goal:
			MapGlyphs.draw_objective(
				_legend_marks,
				at - Vector2(HudLayout.num(lm, "goal_gap"), 0.0),
				px * 0.75,
				HudLayout.num(mm, "glyph_line_px"),
				_c(&"focus_gold"),
				_c(&"map_glyph_back"),
				-1.0,
				0.0
			)


func _on_map_poi(poi_id: StringName) -> void:
	var i := model.poi_index(poi_id)
	if i >= 0 and is_open():
		select(i)


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
