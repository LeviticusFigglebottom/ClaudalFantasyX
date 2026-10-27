class_name AreaTitleCard
extends Control
## The area title card (M2-UI-21, intro audit 4): the location's name, in the title serif over a
## soft band with a centred gold rule (drawn here, heavier than OrnamentRule so it reads over the
## field), when the field first takes input in a location other than the last one carded. It fades
## in (rising a little; reduced motion: no rise), holds, and fades out. A cutscene or a
## conversation at the start delays it; a menu hides it. The location comes from
## game/data/world/locations.json by the current scene's path. Layout: area_title.json.

enum Phase { WAITING, IN, HOLD, OUT, DONE }

const DATA_PATH := "res://game/data/ui/area_title.json"

## The location carded last this session (&"" after the title screen, so every start shows one).
static var last_shown: StringName = &""

## The player whose input state gates the card (null in tests and shots).
var controller: FieldController
## The location to card (found from the scene when left empty).
var location: StringName = &""
var phase := Phase.DONE

var _d: Dictionary = {}
var _name: Label
var _t := 0.0


## Adds the card (on its own CanvasLayer) under field controller `c`, and returns it.
static func attach(c: FieldController) -> AreaTitleCard:
	var layer := CanvasLayer.new()
	layer.name = &"AreaTitleLayer"
	layer.layer = int(load_data().get("canvas_layer", 1))
	var card := AreaTitleCard.new()
	card.controller = c
	layer.add_child(card)
	c.add_child(layer)
	return card


## Forgets the last location (the title screen calls it, so the next start shows its card).
static func forget() -> void:
	last_shown = &""


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("area_title")) != TYPE_DICTIONARY:
		push_error("AreaTitleCard: could not read 'area_title' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["area_title"] as Dictionary


## The locations.json id whose scene is `scene_path` (&"" when none).
static func location_for_scene(scene_path: String, registry: LocationRegistry = null) -> StringName:
	var r := registry if registry != null else LocationRegistry.load_default()
	for id in r.location_ids():
		if r.scene_of(id) == scene_path:
			return id
	return &""


func _ready() -> void:
	name = &"AreaTitleCard"
	_d = load_data()
	process_mode = Node.PROCESS_MODE_ALWAYS  # so it can hide itself while a menu pauses the tree
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	if location == &"" and get_tree().current_scene != null:
		location = location_for_scene(get_tree().current_scene.scene_file_path)
	_build()
	var skip := (_d.get("skip_locations", []) as Array).has(String(location))
	phase = Phase.DONE if location == &"" or skip or location == last_shown else Phase.WAITING
	_apply()


func _process(delta: float) -> void:
	advance(delta)


## True while the card may be seen: the field takes input and no menu pauses the tree.
func allowed() -> bool:
	if controller != null and (not is_instance_valid(controller) or not controller.accepts_input):
		return false
	return not (is_inside_tree() and get_tree().paused)


## Steps the card by `delta` seconds (from _process; tests call it directly).
func advance(delta: float) -> void:
	if phase == Phase.DONE:
		return
	if not allowed():
		if phase != Phase.WAITING:
			phase = Phase.DONE  # a menu or a scene took over: the moment has passed
		_apply()
		return
	if phase == Phase.WAITING:
		phase = Phase.IN
		_t = 0.0
		last_shown = location
	else:
		_t += delta
	match phase:
		Phase.IN:
			if _t >= _num("in_sec"):
				phase = Phase.HOLD
				_t = 0.0
		Phase.HOLD:
			if _t >= _num("hold_sec"):
				phase = Phase.OUT
				_t = 0.0
		Phase.OUT:
			if _t >= _num("out_sec"):
				phase = Phase.DONE
	_apply()


func is_showing() -> bool:
	return phase == Phase.IN or phase == Phase.HOLD or phase == Phase.OUT


func name_text() -> String:
	return _name.text


## 0..1: how far the card is in.
func visibility() -> float:
	match phase:
		Phase.IN:
			return clampf(_t / maxf(_num("in_sec"), 0.001), 0.0, 1.0)
		Phase.HOLD:
			return 1.0
		Phase.OUT:
			return 1.0 - clampf(_t / maxf(_num("out_sec"), 0.001), 0.0, 1.0)
	return 0.0


func _apply() -> void:
	if _name == null:
		return
	var v := visibility()
	visible = v > 0.0
	modulate.a = v
	var rise := 0.0
	if phase == Phase.IN and not UiSettings.shared().reduced_motion():
		rise = _num("drift_px") * (1.0 - v)
	position.y = rise
	queue_redraw()


func _draw() -> void:
	var band := HudLayout.pinned_rect(_d.get("band", {}), size)  # centred at any aspect (M2-UI-29)
	var deep := get_theme_color(&"panel_deep", HymnThemeBuilder.PALETTE_TYPE)
	var mid := Color(deep, _num("band_alpha"))
	var clear := Color(deep, 0.0)
	var feather := _num("band_feather_px")
	var cx := band.get_center().x
	# Three strips (top feather, core, bottom feather), each fading out to both ends.
	var ys := [band.position.y, band.position.y + feather, band.end.y - feather, band.end.y]
	var tops := [clear, mid, mid]
	var bottoms := [mid, mid, clear]
	for i in 3:
		for side in [band.position.x, band.end.x]:
			var pts := PackedVector2Array(
				[Vector2(side, ys[i]), Vector2(cx, ys[i]), Vector2(cx, ys[i + 1]), Vector2(side, ys[i + 1])]
			)
			draw_polygon(pts, PackedColorArray([clear, tops[i], bottoms[i], clear]))
	_draw_rule(HudLayout.pinned_rect(_d.get("rule", {}), size))


## A centred gold rule (the OrnamentRule shape, heavier so it reads over the field): a diamond in
## the middle and a line fading out both ways.
func _draw_rule(r: Rect2) -> void:
	var gold := get_theme_color(&"ornament_gold", HymnThemeBuilder.PALETTE_TYPE)
	var clear := Color(gold, 0.0)
	var w := _num("rule_px")
	var node := _num("rule_node_px")
	var c := r.get_center()
	for end in [r.position.x, r.end.x]:
		var from := Vector2(c.x + signf(end - c.x) * node * 1.5, c.y)
		draw_polyline_colors(PackedVector2Array([from, Vector2(end, c.y)]), PackedColorArray([gold, clear]), w, true)
	draw_colored_polygon(SwellRingView.diamond(c, node), gold)


func _build() -> void:
	_name = Label.new()
	_name.theme_type_variation = &"TitleLabel"
	HudLayout.place(_name, _d.get("name", {}))
	_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_name.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var shadow := _num("shadow_px")
	_name.add_theme_color_override(&"font_shadow_color", get_theme_color(&"shadow", HymnThemeBuilder.PALETTE_TYPE))
	_name.add_theme_constant_override(&"shadow_offset_x", int(shadow))
	_name.add_theme_constant_override(&"shadow_offset_y", int(shadow))
	var key := LocationRegistry.load_default().name_key_of(location) if location != &"" else ""
	_name.text = tr(key) if key != "" else ""
	add_child(_name)


func _num(key: String) -> float:
	return HudLayout.num(_d, key)
