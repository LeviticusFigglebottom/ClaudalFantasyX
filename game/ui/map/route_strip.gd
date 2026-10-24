class_name RouteStrip
extends Control
## The pilgrimage strip on the map page (M2-UI-18): every stop of zone_maps.json "route" as a node
## on one line (Haluna, the Saltgrass Causeway, the Shell Shrine), its name under it. The stop the
## party stands in is a larger filled gold diamond with its name in full text colour; the others
## are small hollow diamonds in dim text (shape and weight, not hue alone). A stop with no map of
## its own draws the same; only "current" changes. Metrics: zone_map_menu.json "route".

var stops: Array[Dictionary] = []
var metrics: Dictionary = {}

var _labels: Array[Label] = []


func setup(route_stops: Array[Dictionary], route_metrics: Dictionary) -> void:
	stops = route_stops
	metrics = route_metrics
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	for l in _labels:
		l.queue_free()
	_labels.clear()
	for i in stops.size():
		var l := Label.new()
		l.theme_type_variation = &"SmallLabel"
		l.text = str(stops[i]["name"])
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.vertical_alignment = VERTICAL_ALIGNMENT_TOP
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		add_child(l)
		_labels.append(l)
	_place()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_place()
	elif what == NOTIFICATION_THEME_CHANGED:
		_place()


## The index of the stop the party is in (-1 when none is).
func current_index() -> int:
	for i in stops.size():
		if bool(stops[i]["current"]):
			return i
	return -1


## The centre of stop `i`'s node: the stops spread evenly, each in the middle of its share.
func node_at(i: int) -> Vector2:
	var share := size.x / maxf(stops.size(), 1.0)
	return Vector2(share * (i + 0.5), float(metrics.get("line_y", 0.0)))


func label_of(i: int) -> Label:
	return _labels[i]


func _place() -> void:
	var share := size.x / maxf(stops.size(), 1.0)
	var top := float(metrics.get("line_y", 0.0)) + float(metrics.get("current_px", 0.0))
	for i in _labels.size():
		_labels[i].position = Vector2(share * i, top)
		_labels[i].size = Vector2(share, float(metrics.get("label_height", 0.0)))
		var role := &"text" if bool(stops[i]["current"]) else &"text_dim"
		_labels[i].add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))
	queue_redraw()


func _draw() -> void:
	if stops.is_empty():
		return
	var line := float(get_theme_constant(&"line_px", HymnThemeBuilder.PALETTE_TYPE))
	var dim := get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE)
	var gold := get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	var small := float(metrics.get("node_px", 0.0))
	var big := float(metrics.get("current_px", 0.0))
	for i in stops.size() - 1:
		var a := node_at(i)
		var b := node_at(i + 1)
		var ra := big if bool(stops[i]["current"]) else small
		var rb := big if bool(stops[i + 1]["current"]) else small
		draw_line(
			a + Vector2(ra, 0.0),
			b - Vector2(rb, 0.0),
			get_theme_color(&"gauge_border", HymnThemeBuilder.PALETTE_TYPE),
			line
		)
	for i in stops.size():
		var at := node_at(i)
		if bool(stops[i]["current"]):
			draw_colored_polygon(SwellRingView.diamond(at, big), gold)
		else:
			var d := SwellRingView.diamond(at, small)
			d.append(d[0])
			draw_polyline(d, dim, line, true)
