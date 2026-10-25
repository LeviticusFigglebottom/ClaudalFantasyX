class_name ZoneMapView
extends Control
## The zone schematic (M2-UI-18): a MapModel drawn with _draw. Shapes come from ZoneMapShapes
## (the zone's own layout or trial data), places from zone_maps.json, the objective from
## ObjectiveTracker and the player from the field. World (x, z) maps to the control through
## MapModel.fit: the zone's bounds at one scale, centred and letterboxed; what lies past the
## bounds still draws, clipped to the control. North is up.
##
## Draw order: sea, seas (a greybox zone's open water), land, floors, sand, pads, lanes, water,
## channels, rims, buildings, structures, walls, foam; then the compass, the places (glyphs) with
## the highlighted place's ring, the objective's gold diamond framing its place's glyph, and the
## player's arrow on top. Colours are theme roles only (map_* and the UI roles). The objective's
## ring swells over pulse_sec from its own clock; under reduced motion it holds.
## Mouse: hovering or clicking a place emits poi_hovered / poi_clicked.

signal poi_hovered(poi_id: StringName)
signal poi_clicked(poi_id: StringName)

var model: MapModel
var shapes: ZoneMapShapes
## Metrics: zone_map_menu.json "map".
var metrics: Dictionary = {}
## The place under the legend's cursor (&"" = none).
var highlight: StringName = &""
var reduced_motion := false

var _xf := Transform2D.IDENTITY
var _t := 0.0
var _pieces: Dictionary = {}
var _greybox: Dictionary = {}


## Shows `with_model`. `map_metrics`: zone_map_menu.json "map"; `pieces`: its "pieces";
## `greybox`: its "greybox" block (how a greybox zone's blocks are read).
func setup(with_model: MapModel, map_metrics: Dictionary, pieces: Dictionary, greybox: Dictionary = {}) -> void:
	model = with_model
	metrics = map_metrics
	_pieces = pieces
	_greybox = greybox
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	_layout()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and model != null:
		_layout()
	elif what == NOTIFICATION_THEME_CHANGED:
		queue_redraw()


func _process(delta: float) -> void:
	_t += delta
	if not reduced_motion and objective_marker_at().is_finite():
		queue_redraw()


## Rebuilds the transform and the shapes for the control's current size.
func _layout() -> void:
	_xf = MapModel.fit(model.bounds(), Rect2(Vector2.ZERO, size))
	var margin := float(metrics.get("view_margin_m", 0.0))
	var seen := _xf.affine_inverse() * Rect2(Vector2.ZERO, size)
	shapes = ZoneMapShapes.build(
		model.shape_kind(), model.shape_source(), seen.grow(margin), metrics, _pieces, _greybox, model.shape_hints()
	)
	queue_redraw()


## World (x, z) -> this control's local px.
func map_point(world: Vector2) -> Vector2:
	return _xf * world


## Metres -> px at the map's scale.
func map_scale() -> float:
	return _xf.x.x


func poi_marker_at(poi_id: StringName) -> Vector2:
	var i := model.poi_index(poi_id)
	return map_point(model.pois()[i]["at"]) if i >= 0 else Vector2.INF


## Where the objective's marker is drawn (Vector2.INF when there is none).
func objective_marker_at() -> Vector2:
	if model == null:
		return Vector2.INF
	var at := model.objective_at()
	return map_point(at) if at.is_finite() else Vector2.INF


## Where the player's arrow is drawn (Vector2.INF when the player is not known).
func player_marker_at() -> Vector2:
	return map_point(model.player_at) if model != null and model.has_player() else Vector2.INF


## The objective's pulse, 0..1 (-1 while held under reduced motion).
func pulse_phase() -> float:
	var sec := float(metrics.get("pulse_sec", 0.0))
	if reduced_motion or sec <= 0.0:
		return -1.0
	return fposmod(_t / sec, 1.0)


## The place whose glyph is under local point `p`, or &"".
func poi_at_point(p: Vector2) -> StringName:
	var reach := float(metrics.get("highlight_px", 0.0))
	var best: StringName = &""
	var best_d := INF
	for poi in model.pois():
		var d := map_point(poi["at"]).distance_to(p)
		if d <= reach and d < best_d:
			best = poi["id"]
			best_d = d
	return best


func _gui_input(event: InputEvent) -> void:
	var motion := event as InputEventMouseMotion
	if motion != null:
		var id := poi_at_point(motion.position)
		if id != &"" and id != highlight:
			poi_hovered.emit(id)
		return
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		var hit := poi_at_point(mb.position)
		if hit != &"":
			poi_clicked.emit(hit)
			accept_event()


# --- Drawing -------------------------------------------------------------------------------------


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _m(key: String) -> float:
	return float(metrics.get(key, 0.0))


func _draw() -> void:
	if model == null or shapes == null:
		return
	if shapes.sea:
		draw_rect(Rect2(Vector2.ZERO, size), _c(&"map_sea"))
	_fill(shapes.seas, _c(&"map_sea"))
	_fill(shapes.land, _c(&"map_land"))
	_fill(shapes.floors, _c(&"map_floor"))
	_fill(shapes.sand, _c(&"map_sand"))
	_fill(shapes.pads, _c(&"map_pad"))
	_strokes(shapes.lanes, _c(&"map_lane"), shapes.lane_width_m * map_scale())
	_fill(shapes.water, _c(&"map_water"))
	_strokes(shapes.channels, _c(&"map_water"), shapes.channel_width_m * map_scale())
	_strokes(shapes.rims, _c(&"map_wall"), _m("wall_px"), true)
	_fill(shapes.buildings, _c(&"map_roof"))
	_fill(shapes.structures, _c(&"map_wall"))
	_strokes(shapes.walls, _c(&"map_wall"), _m("wall_px"))
	_strokes(shapes.foam, _c(&"map_foam"), _m("foam_px"))
	_draw_compass()
	_draw_pois()
	var goal := objective_marker_at()
	if goal.is_finite():
		MapGlyphs.draw_objective(
			self,
			goal,
			_m("objective_px"),
			_m("objective_line_px"),
			_c(&"focus_gold"),
			_c(&"map_glyph_back"),
			pulse_phase(),
			_m("pulse_px"),
			true
		)
	var me := player_marker_at()
	if me.is_finite():
		var ahead := map_point(model.player_at + model.player_facing()) - me
		MapGlyphs.draw_player(self, me, ahead, _m("player_px"), _m("player_outline_px"), _c(&"focus"), _c(&"outline"))


func _fill(polys: Array[PackedVector2Array], color: Color) -> void:
	for poly in polys:
		var pts := _xf * poly
		if pts.size() >= 3:
			draw_colored_polygon(pts, color)


## Polylines `width` px wide (translucent roles, so no join discs: they would double the alpha);
## `closed` draws back to the first point.
func _strokes(lines: Array[PackedVector2Array], color: Color, width: float, closed: bool = false) -> void:
	for line in lines:
		var pts := _xf * line
		if closed and pts.size() > 2:
			pts.append(pts[0])
		if pts.size() < 2:
			continue
		draw_polyline(pts, color, maxf(width, 1.0), true)


func _draw_pois() -> void:
	var px := _m("glyph_px")
	for poi in model.pois():
		var at := map_point(poi["at"])
		if poi["id"] == highlight:
			draw_arc(
				at, _m("highlight_px"), 0.0, TAU, int(_m("circle_segments")), _c(&"focus"), _m("glyph_line_px"), true
			)
		MapGlyphs.draw_poi(
			self, poi["kind"], at, px, _m("glyph_line_px"), _c(&"text"), _c(&"map_glyph_back"), _c(&"gauge_border")
		)


## North, in the top-right corner: a thin ring with a filled tick at its top and the letter N above
## (a ring, not an arrow, so it is never taken for the player).
func _draw_compass() -> void:
	var px := _m("compass_px")
	var c := Vector2(size.x - _m("compass_inset"), _m("compass_inset") + px * 0.5)
	var r := px * 0.5
	draw_arc(c, r, 0.0, TAU, int(_m("circle_segments")), _c(&"text_dim"), 1.0, true)
	draw_line(c + Vector2(0.0, r), c + Vector2(0.0, -r), _c(&"text_dim"), 1.0, true)
	var tick := PackedVector2Array(
		[c + Vector2(0.0, -r * 1.5), c + Vector2(r * 0.4, -r * 0.5), c + Vector2(-r * 0.4, -r * 0.5)]
	)
	draw_colored_polygon(tick, _c(&"text_dim"))
	var font := get_theme_default_font()
	var fs := get_theme_default_font_size()
	var letter := tr("MAP_NORTH")
	var w := font.get_string_size(letter, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	draw_string(font, c + Vector2(-w * 0.5, -px * 0.75), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, _c(&"text_dim"))
