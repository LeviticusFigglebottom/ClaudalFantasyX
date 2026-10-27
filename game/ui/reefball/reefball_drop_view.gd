class_name ReefballDropView
extends Panel
## The drop on the Reefball HUD (M3-UI-01): the water's depth bands from the ring at the top to the
## weep at the bottom, each diver as a dot in its band (the player's side on the left half, the
## other side on the right), the float holder ringed, the fetch depth as a dashed line, and the
## choice under the cursor marked: the diver it would reach (a pass's receiver) and the opponent who
## takes the float on a miss. A view only: ReefballHud hands it plain data from the engine.
## Metrics: game/data/ui/reefball_hud.json "drop".
## A dot is {id, side (0 = the player's, 1 = the other), depth, resting}.

var dots: Array[Dictionary] = []
var holder: StringName = &""
## The diver the choice under the cursor reaches (&"" when none).
var target: StringName = &""
## The opponent who takes the float if that choice misses (&"" when it cannot miss).
var taker: StringName = &""
## The first band whose float counts as fetched (ReefballMatch.fetch_depth()).
var fetch_depth := -1

var _m: Dictionary = {}
var _labels: Array[Label] = []
var _canvas: Control


func setup(metrics: Dictionary, band_names: PackedStringArray) -> void:
	_m = metrics
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	HudLayout.place(self, _m)
	_canvas = Control.new()
	_canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_canvas.draw.connect(_draw_drop)
	add_child(_canvas)
	for n in band_names:
		var l := Label.new()
		l.theme_type_variation = &"DimLabel"
		l.text = n
		l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(l)
		_labels.append(l)
	_layout_labels()


## Shows the divers, the holder and the cursor's marks.
func show_state(
	new_dots: Array[Dictionary], new_holder: StringName, new_fetch: int, new_target: StringName, new_taker: StringName
) -> void:
	dots = new_dots
	holder = new_holder
	fetch_depth = new_fetch
	target = new_target
	taker = new_taker
	_canvas.queue_redraw()


func band_count() -> int:
	return _labels.size()


## The rect of band `i` in this panel's coordinates.
func band_rect(i: int) -> Rect2:
	var pad := HudLayout.num(_m, "pad")
	var inner := Rect2(Vector2(pad, pad), HudLayout.rect_of(_m).size - Vector2(pad, pad) * 2.0)
	var h := inner.size.y / float(maxi(1, _labels.size()))
	return Rect2(inner.position + Vector2(0.0, h * i), Vector2(inner.size.x, h))


## Where diver `id`'s dot is drawn (its centre), or Vector2(-1, -1) when it is not shown.
func dot_centre(id: StringName) -> Vector2:
	var count := {0: {}, 1: {}}
	for d in dots:
		var side := int(d.get("side", 0))
		var depth := int(d.get("depth", 0))
		var k: int = (count[side] as Dictionary).get(depth, 0)
		(count[side] as Dictionary)[depth] = k + 1
		if StringName(str(d.get("id", ""))) == id:
			return _slot(side, depth, k)
	return Vector2(-1.0, -1.0)


func _slot(side: int, depth: int, k: int) -> Vector2:
	var band := band_rect(depth)
	var lw := HudLayout.num(_m, "label_width")
	var half := (band.size.x - lw) * 0.5
	var px := HudLayout.num(_m, "dot_px")
	var step := px + HudLayout.num(_m, "dot_gap")
	var x0 := band.position.x + lw + half * side + step * 0.5
	return Vector2(x0 + step * k, band.get_center().y)


func _layout_labels() -> void:
	var lw := HudLayout.num(_m, "label_width")
	for i in _labels.size():
		var r := band_rect(i)
		_labels[i].position = r.position + Vector2(HudLayout.num(_m, "dot_gap"), 0.0)
		_labels[i].size = Vector2(lw - HudLayout.num(_m, "dot_gap"), r.size.y)


func _draw_drop() -> void:
	var line := HudLayout.num(_m, "line_px")
	for i in _labels.size():
		var r := band_rect(i)
		var alpha := HudLayout.num(_m, "ring_band_alpha" if i == 0 else "band_alpha")
		var back := _c(&"panel_raised" if i % 2 == 0 else &"panel_low")
		_canvas.draw_rect(r, Color(back, alpha))
		if i == 0:
			_canvas.draw_line(r.position, Vector2(r.end.x, r.position.y), _c(&"line_gold"), line)
	if fetch_depth > 0 and fetch_depth < _labels.size():
		_dashed(band_rect(fetch_depth).position.y)
	var px := HudLayout.num(_m, "dot_px")
	var ring := HudLayout.num(_m, "ring_px")
	for d in dots:
		var id := StringName(str(d.get("id", "")))
		var side := int(d.get("side", 0))
		var at := dot_centre(id)
		var col := _c(StringName(str(_m["ours_role" if side == 0 else "theirs_role"])))
		if bool(d.get("resting", false)):
			col.a = HudLayout.num(_m, "resting_alpha")
		_canvas.draw_circle(at, px * 0.5, col)
		var mark := &""
		if id == holder:
			mark = StringName(str(_m["holder_role"]))
		elif id == target:
			mark = StringName(str(_m["target_role"]))
		elif id == taker:
			mark = StringName(str(_m["taker_role"]))
		if mark != &"":
			_canvas.draw_arc(at, px * 0.5 + ring * 1.5, 0.0, TAU, 32, _c(mark), ring, true)


## The fetch depth: a dashed tide line across the dot columns at `y`.
func _dashed(y: float) -> void:
	var band := band_rect(0)
	var x := band.position.x + HudLayout.num(_m, "label_width")
	var dash := HudLayout.num(_m, "dash_px")
	var col := _c(StringName(str(_m["fetch_role"])))
	while x < band.end.x:
		_canvas.draw_line(Vector2(x, y), Vector2(minf(x + dash, band.end.x), y), col, HudLayout.num(_m, "line_px"))
		x += dash * 2.0


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
