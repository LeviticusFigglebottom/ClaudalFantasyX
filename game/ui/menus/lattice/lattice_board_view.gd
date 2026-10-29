class_name LatticeBoardView
extends Control
## The Lattice board as the Lattice page draws it (M2-MNU-01): our own look, from the UI's deep-blue,
## gold and thin-line language (docs/kb/tech/ui.md § Lattice page), drawn with _draw from the board's
## lattice-unit coordinates. Every node is a cut-gem lozenge (a gate a wide plate with a boom across
## it), every edge a thin gold rigging line; a node the hero woke burns like a lamp, one someone else
## woke glows dimly, and each region is washed faintly in its palette role. The hero hangs a lantern
## over the node they stand on; the cursor is a teal frame with gold ticks, and the planned path is a
## teal line with its cost tagged beside the cursor. Colours are theme roles (type Hymn) and every
## size is in lattice_menu.json "board". The camera pans to keep the cursor in view (no tween under
## reduced motion). A click on a node emits node_clicked (on release, so a press that moves drag_px or
## more pans the board instead: M2-UI-26); the wheel zooms between zoom_min and zoom_max about the
## pointer, every shape and line scaling with it.
## M3-MNU-04: the overview fits the whole board in the view (fit_zoom, centred; no second renderer)
## and names every hero under their node, with the initials of who woke it beside each woken node,
## so who stands where and who woke what reads without colour. Cursor moves keep the framing; a
## wheel turn or a drag hands the camera back to the player (overview off).

signal node_clicked(node_id: StringName)
## The overview was turned on or off (by set_overview, or a wheel turn or drag leaving it).
signal overview_changed(on: bool)

var model: LatticeMenuModel
var cursor: StringName = &""
## The planned walk (cheapest_path; [] when Confirm would not walk) and whether it can be paid.
var path: Array[StringName] = []
var path_ok := true
## The cost tag drawn beside the cursor ("" for none).
var tag_text := ""
var reduced_motion := false
## The board point (reference px) at the middle of the view.
var pan := Vector2.ZERO:
	set(value):
		pan = value
		queue_redraw()

## The board's scale on screen (1: as drawn at the reference; the wheel changes it).
var zoom := 1.0:
	set(value):
		zoom = value
		queue_redraw()

## M3-MNU-04: the whole board is framed (set_overview).
var overview := false

## The node waking (the bloom after Confirm wakes it or opens its gate; &"" when none) and how far
## the bloom has gone (0..1). Reduced motion plays none.
var waking: StringName = &""
var wake_t := 0.0:
	set(value):
		wake_t = value
		queue_redraw()

var _m: Dictionary = {}
## lattice_menu.json "overview".
var _o: Dictionary = {}
## The zoom to return to when the overview ends.
var _return_zoom := 1.0
var _pan_tween: Tween
var _wake_tween: Tween
## A left press on the board: where it went down, and whether it has moved far enough to pan.
var _pressing := false
var _dragging := false
var _press_at := Vector2.ZERO


func setup(metrics: Dictionary, with_model: LatticeMenuModel, overview_metrics: Dictionary = {}) -> void:
	_m = metrics
	_o = overview_metrics
	model = with_model
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_STOP


## Where node `nid` sits on the board, in reference px (before the pan).
func board_point(nid: StringName) -> Vector2:
	var n := model.board().lattice_node(nid)
	return Vector2(n.position) * _num("unit_px") if n != null else Vector2.ZERO


## Where node `nid` is drawn inside this view (at the current zoom).
func screen_point(nid: StringName) -> Vector2:
	return size * 0.5 + (board_point(nid) - pan) * zoom


## Where `nid` is drawn before the zoom's transform (_draw scales about the middle of the view).
func _draw_point(nid: StringName) -> Vector2:
	return size * 0.5 + board_point(nid) - pan


func zoom_min() -> float:
	return _num("zoom_min")


func zoom_max() -> float:
	return _num("zoom_max")


## Scales the board by `factor` (held between zoom_min and zoom_max), keeping the board point under
## `local` (a point in this view) where it is.
func zoom_by(factor: float, local: Vector2) -> void:
	var z := clampf(zoom * factor, zoom_min(), zoom_max())
	if is_equal_approx(z, zoom):
		return
	_stop_pan()
	_leave_overview()
	var anchor := pan + (local - size * 0.5) / zoom
	zoom = z
	pan = _clamped_pan(anchor - (local - size * 0.5) / z)


## The node drawn nearest `local` (a point in this view), within pick_px; &"" for none.
func node_at(local: Vector2) -> StringName:
	var best := &""
	var best_d := _num("pick_px") * zoom
	for nid: StringName in model.board().nodes:
		var d := screen_point(nid).distance_to(local)
		if d <= best_d:
			best_d = d
			best = nid
	return best


## Pans so `nid` is in the middle (held inside the board's bounds); slides unless `animate` is false
## or motion is reduced. In the overview the whole board stays framed, so nothing moves.
func center_on(nid: StringName, animate: bool) -> void:
	if overview:
		return
	_move_to(zoom, _clamped_pan(board_point(nid)), animate)


## The board's node centres, in reference px (an empty rect for an empty board).
func board_bounds() -> Rect2:
	var b := model.board()
	if b.nodes.is_empty():
		return Rect2()
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for nid: StringName in b.nodes:
		var p := board_point(nid)
		lo = lo.min(p)
		hi = hi.max(p)
	return Rect2(lo, hi - lo)


## The zoom that fits every node in the view, margin_px inside each side (held between zoom_min and
## zoom_max).
func fit_zoom() -> float:
	var r := board_bounds()
	var room := size - Vector2.ONE * HudLayout.num(_o, "margin_px") * 2.0
	var z := minf(room.x / maxf(r.size.x, 1.0), room.y / maxf(r.size.y, 1.0))
	return clampf(z, zoom_min(), zoom_max())


## Turns the overview on (the whole board, fitted and centred) or off (back to the zoom it had, on
## the cursor). Moves over pan_sec unless `animate` is false or motion is reduced.
func set_overview(on: bool, animate: bool) -> void:
	if on == overview:
		return
	overview = on
	if on:
		_return_zoom = zoom
		var z := fit_zoom()
		_move_to(z, _clamped_pan(board_bounds().get_center(), z), animate)
	else:
		_move_to(_return_zoom, _clamped_pan(board_point(cursor), _return_zoom), animate)
	overview_changed.emit(on)


func _move_to(z: float, target: Vector2, animate: bool) -> void:
	_stop_pan()
	if not animate or reduced_motion or not is_inside_tree():
		zoom = z
		pan = target
		return
	_pan_tween = create_tween().set_parallel().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	_pan_tween.tween_property(self, ^"pan", target, _num("pan_sec"))
	_pan_tween.tween_property(self, ^"zoom", z, _num("pan_sec"))


## The player took the camera (a wheel turn or a drag): the overview ends where the board is.
func _leave_overview() -> void:
	if overview:
		overview = false
		overview_changed.emit(false)


func _gui_input(event: InputEvent) -> void:
	var mm := event as InputEventMouseMotion
	if mm != null:
		if not _pressing or mm.button_mask & MOUSE_BUTTON_MASK_LEFT == 0:
			return
		if not _dragging and mm.position.distance_to(_press_at) >= _num("drag_px"):
			_dragging = true
			_stop_pan()
			_leave_overview()
		if _dragging:
			pan = _clamped_pan(pan - mm.relative / zoom)
			accept_event()
		return
	var mb := event as InputEventMouseButton
	if mb == null:
		return
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP or mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		if mb.pressed:
			var step := _num("zoom_step")
			zoom_by(step if mb.button_index == MOUSE_BUTTON_WHEEL_UP else 1.0 / step, mb.position)
		accept_event()
		return
	if mb.button_index != MOUSE_BUTTON_LEFT:
		return
	accept_event()
	if mb.pressed:
		_pressing = true
		_dragging = false
		_press_at = mb.position
		return
	var clicked := _pressing and not _dragging
	_pressing = false
	_dragging = false
	var nid := node_at(mb.position) if clicked else &""
	if nid != &"":
		node_clicked.emit(nid)


func _stop_pan() -> void:
	if _pan_tween != null and _pan_tween.is_valid():
		_pan_tween.kill()


## `target` held so the board stays in view at zoom `z` (the current zoom when < 0).
func _clamped_pan(target: Vector2, z: float = -1.0) -> Vector2:
	if model.board().nodes.is_empty():
		return Vector2.ZERO
	var bounds := board_bounds()
	var lo := bounds.position
	var hi := bounds.end
	var margin := _num("pan_margin_px")
	var out := target
	var seen := size / (z if z > 0.0 else zoom)
	for axis in 2:
		var half := seen[axis] * 0.5
		if hi[axis] - lo[axis] + margin * 2.0 <= seen[axis]:
			out[axis] = (lo[axis] + hi[axis]) * 0.5
		else:
			out[axis] = clampf(target[axis], lo[axis] - margin + half, hi[axis] + margin - half)
	return out


# --- Drawing ----------------------------------------------------------------------------------------


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), _role(&"line_gold", _num("frame_alpha")), false, _num("outline_px"))
	if model == null or model.board().nodes.is_empty():
		return
	draw_set_transform(size * 0.5 * (1.0 - zoom), 0.0, Vector2(zoom, zoom))  # the zoom, about the middle
	var b := model.board()
	_draw_wash()
	_draw_edges()
	_draw_path()
	for nid: StringName in b.nodes:
		_draw_node(b.lattice_node(nid))
	_draw_markers()
	if waking != &"":
		_draw_wake()
	_draw_cursor()
	if not overview:
		_draw_tag(_draw_point(cursor))
		return
	draw_set_transform(Vector2.ZERO)  # the overview's words keep their size
	_draw_tag(screen_point(cursor))
	_draw_overview_words()


## M3-MNU-04, in view space (the words keep their size at any zoom): each hero's name in a tag
## under their node (the hero on show framed in gold, others dim; tags on one node stack), and the
## initials of who woke each woken node beside it. Initials that would touch a name tag or other
## initials are left off (the node's fill still says it is woken), so the tags always read.
func _draw_overview_words() -> void:
	var font := get_theme_font(&"font", &"SmallLabel")
	var fs := get_theme_font_size(&"font_size", &"SmallLabel")
	var tags := _overview_tags(font, fs)
	var taken: Array[Rect2] = []
	for t: Dictionary in tags:
		taken.append(t["box"] as Rect2)
	var off := _ovec("initials_offset")
	for nid: StringName in model.board().nodes:
		var who := model.woken_initials(nid)
		if who == "":
			continue
		var n := model.board().lattice_node(nid)
		var at := screen_point(nid) + Vector2(_half_size(n).x * zoom + off.x, font.get_ascent(fs) + off.y)
		var r := Rect2(
			at - Vector2(0.0, font.get_ascent(fs)), font.get_string_size(who, HORIZONTAL_ALIGNMENT_LEFT, -1.0, fs)
		)
		if taken.any(func(o: Rect2) -> bool: return o.intersects(r)):
			continue
		taken.append(r)
		draw_string(font, at, who, HORIZONTAL_ALIGNMENT_LEFT, -1.0, fs, _role(&"text_dim"))
	var pad := _ovec("name_pad")
	for t: Dictionary in tags:
		var box := t["box"] as Rect2
		draw_rect(box, _role(&"panel_deep"))
		draw_rect(box, t["edge"] as Color, false, _num("outline_px"))
		draw_string(
			font,
			box.position + Vector2(pad.x, pad.y + font.get_ascent(fs)),
			str(t["text"]),
			0,
			-1.0,
			fs,
			_role(&"text")
		)


## The overview's name tags: [{box, text, edge}], one per hero under their node (stacked on a shared node).
func overview_tags() -> Array[Dictionary]:
	return _overview_tags(get_theme_font(&"font", &"SmallLabel"), get_theme_font_size(&"font_size", &"SmallLabel"))


func _overview_tags(font: Font, fs: int) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var stacked: Dictionary = {}
	var pad := _ovec("name_pad")
	for cid: StringName in model.heroes():
		var nid: StringName = model.progress().traveler(cid).position
		var n := model.board().lattice_node(nid)
		if n == null:
			continue
		var k := int(stacked.get(nid, 0))
		stacked[nid] = k + 1
		var text := model.hero_name(cid)
		var ts := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, fs)
		var top := _half_size(n).y * zoom + HudLayout.num(_o, "name_gap_px") + HudLayout.num(_o, "name_step_px") * k
		var box := Rect2(screen_point(nid) + Vector2(-ts.x * 0.5 - pad.x, top), ts + pad * 2.0)
		var edge := _role(&"focus_gold") if cid == model.hero() else _role(&"text_dim")
		out.append({"box": box, "text": text, "edge": edge})
	return out


## Each region's faint ribbon of colour along its own edges.
func _draw_wash() -> void:
	var b := model.board()
	for a: StringName in b.nodes:
		var na := b.lattice_node(a)
		for nb in b.neighbors(a):
			if String(a) >= String(nb) or b.lattice_node(nb).region != na.region:
				continue
			var c := _faded(_region_color(na), _num("wash_alpha"))
			draw_line(_draw_point(a), _draw_point(nb), c, _num("wash_px"), true)


func _draw_edges() -> void:
	var b := model.board()
	var p := model.progress()
	for a: StringName in b.nodes:
		for nb in b.neighbors(a):
			if String(a) >= String(nb):
				continue
			var lit := p.is_activated_by_anyone(a) and p.is_activated_by_anyone(nb)
			var c := _role(&"line_gold", _num("edge_lit_alpha") if lit else _num("edge_alpha"))
			var w := _num("edge_lit_px") if lit else _num("edge_px")
			draw_line(_draw_point(a), _draw_point(nb), c, w, true)


func _draw_path() -> void:
	var c := _role(&"focus") if path_ok else _role(&"danger")
	for i in range(1, path.size()):
		draw_line(_draw_point(path[i - 1]), _draw_point(path[i]), c, _num("path_px"), true)
	# Each step's marker: filled where the step costs movement (a node nobody has woken), a ring where
	# it is free (the way already woken), so the walk's cost reads along the line, not only in the tag.
	for i in range(1, path.size() - 1):
		var at := _draw_point(path[i])
		if is_paid_step(path[i]):
			draw_circle(at, _num("step_px"), c)
		else:
			draw_arc(at, _num("step_px"), 0.0, TAU, 16, c, _num("outline_px"), true)


## True when stepping onto `nid` costs movement (nobody has woken it; LatticeProgress.entry_cost).
func is_paid_step(nid: StringName) -> bool:
	return model.progress().entry_cost(nid) > model.rules().move_cost_activated


## The wake bloom on `nid` (LatticeMenu, after Confirm wakes a node or opens a gate): a ring grows
## from the node and fades over wake_sec. Nothing under reduced motion.
func play_wake(nid: StringName) -> void:
	if _wake_tween != null and _wake_tween.is_valid():
		_wake_tween.kill()
	waking = &""
	if reduced_motion or not is_inside_tree():
		return
	waking = nid
	wake_t = 0.0
	_wake_tween = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	_wake_tween.tween_property(self, ^"wake_t", 1.0, _num("wake_sec"))
	_wake_tween.tween_callback(func() -> void: waking = &"")


func is_waking() -> bool:
	return waking != &""


## Ends the bloom now (tests).
func finish_wake() -> void:
	if _wake_tween != null and _wake_tween.is_valid() and _wake_tween.is_running():
		_wake_tween.custom_step(_num("wake_sec") + 1.0)


func _draw_wake() -> void:
	var n := model.board().lattice_node(waking)
	if n == null:
		return
	var half := _half_size(n)
	var r := maxf(half.x, half.y) * (1.0 + _num("wake_grow") * wake_t)
	var c := _role(&"focus_gold", 1.0 - wake_t)
	draw_arc(_draw_point(waking), r, 0.0, TAU, 32, c, _num("wake_px"), true)


func _draw_node(n: LatticeNode) -> void:
	_draw_shape(n, _draw_point(n.id), model.node_state(n.id), _region_color(n))


## One node's shape at `at`, as it stands (`state`, LatticeMenuModel.STATE_*), edged in `region`.
func _draw_shape(n: LatticeNode, at: Vector2, state: StringName, region: Color) -> void:
	if n.is_gate():
		_draw_gate(n, at, state)
		return
	var hw := _num("node_half_w") * _scale_of(n)
	var hh := _num("node_half_h") * _scale_of(n)
	var line := _num("outline_px")
	if state == LatticeMenuModel.STATE_EMPTY:
		draw_colored_polygon(_lozenge(at, hw, hh), _role(&"panel_low"))
		_outline(_lozenge(at, hw, hh), _faded(region, 0.6), line)
		return
	var edge := region
	if state == LatticeMenuModel.STATE_MINE:
		_glow(at, hw, hh, _role(&"lamp_node_glow"))
		_gem(at, hw, hh, _role(&"focus_gold"))
		edge = _role(&"ornament_gold")
	elif state == LatticeMenuModel.STATE_TRODDEN:
		_gem(at, hw, hh, _role(&"focus_gold").darkened(_num("trodden_dark")))
	else:
		_gem(at, hw, hh, _role(&"panel_raised"))
	_outline(_lozenge(at, hw, hh), edge, line)
	if n.kind == LatticeNode.KIND_ABILITY:
		var k := _num("ability_inner")
		var inner := _role(&"panel_low") if state == LatticeMenuModel.STATE_MINE else edge
		_outline(_lozenge(at, hw * k, hh * k), inner, line)
	elif n.kind == LatticeNode.KIND_START:
		var bar := Vector2(hw + _num("start_bar_px"), 0.0)
		draw_line(at - bar, at + bar, edge, line * 2.0, true)


## A gate: a wide plate with one tick per Key level. Sealed, a boom runs straight through it; open,
## the boom is swung aside into two stubs and the plate is lit.
func _draw_gate(n: LatticeNode, at: Vector2, state: StringName) -> void:
	var hw := _num("gate_half_w")
	var hh := _num("gate_half_h")
	var line := _num("outline_px")
	var shape := _lozenge(at, hw, hh)
	var bar := _num("gate_bar_px")
	var open := state == LatticeMenuModel.STATE_GATE_OPEN
	var edge := _role(&"ornament_gold") if open else _role(&"text_dim")
	if open:
		draw_colored_polygon(shape, _role(&"focus_gold").darkened(_num("trodden_dark")))
		draw_line(at - Vector2(hw + bar, 0.0), at - Vector2(hw, 0.0), edge, line * 2.0, true)
		draw_line(at + Vector2(hw, 0.0), at + Vector2(hw + bar, 0.0), edge, line * 2.0, true)
	else:
		draw_colored_polygon(shape, _role(&"panel_low"))
		draw_line(at - Vector2(hw + bar, 0.0), at + Vector2(hw + bar, 0.0), edge, line * 2.0, true)
	_outline(shape, edge, line)
	var tick := _num("gate_tick_px")
	var gap := _num("gate_tick_gap")
	var x0 := -gap * (n.gate_level - 1) * 0.5
	var tc := _role(&"focus_gold") if open else _role(&"line_gold")
	for i in n.gate_level:
		var x := at.x + x0 + gap * i
		draw_line(Vector2(x, at.y - tick), Vector2(x, at.y - tick * 0.5), tc, line, true)
		draw_line(Vector2(x, at.y + tick * 0.5), Vector2(x, at.y + tick), tc, line, true)


## Where each hero stands: a ring of lamp-light round their node, gold for the hero on show, dim
## (one ring further out per hero) for the others.
func _draw_markers() -> void:
	var on_node: Dictionary = {}
	var shown := model.hero()
	for cid: StringName in model.heroes():
		if cid == shown:
			continue
		var nid: StringName = model.progress().traveler(cid).position
		var k := int(on_node.get(nid, 0)) + 1
		on_node[nid] = k
		_ring_at(nid, _num("marker_gap_px") + _num("other_marker_step_px") * k, _role(&"text_dim"), Color.TRANSPARENT)
	if shown != &"":
		_ring_at(model.position(), _num("marker_gap_px"), _role(&"focus_gold"), _role(&"lamp_node_glow"))


func _ring_at(nid: StringName, pad: float, c: Color, glow: Color) -> void:
	var n := model.board().lattice_node(nid)
	if n == null:
		return
	_hero_ring(_draw_point(nid), _half_size(n), pad, c, glow)


## The hero ring: a lozenge `pad` outside a node of half-size `half`, over a soft round glow.
func _hero_ring(at: Vector2, half: Vector2, pad: float, c: Color, glow: Color) -> void:
	if glow.a > 0.0:
		draw_circle(at, half.y + pad + _num("marker_px"), glow)
	_outline(_lozenge(at, half.x + pad, half.y + pad), c, _num("marker_line_px"))


func _half_size(n: LatticeNode) -> Vector2:
	if n.is_gate():
		return Vector2(_num("gate_half_w"), _num("gate_half_h"))
	return Vector2(_num("node_half_w"), _num("node_half_h")) * _scale_of(n)


func _draw_cursor() -> void:
	var n := model.board().lattice_node(cursor)
	if n == null:
		return
	var at := _draw_point(cursor)
	var half := _half_size(n) + Vector2.ONE * _num("cursor_pad_px")
	var shape := _lozenge(at, half.x, half.y)
	_outline(shape, _role(&"focus"), _num("cursor_px"))
	var tick := _num("cursor_tick_px")
	for v in shape:
		draw_line(v, v + (v - at).normalized() * tick, _role(&"focus_gold"), _num("outline_px") * 2.0, true)


## The cost tag beside the cursor drawn at `at` (the cursor's point in the current transform).
func _draw_tag(at: Vector2) -> void:
	if tag_text == "" or model.board().lattice_node(cursor) == null:
		return
	var font := get_theme_font(&"font", &"RankLabel")
	var fs := get_theme_font_size(&"font_size", &"RankLabel")
	var text_size := font.get_string_size(tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, fs)
	var pad := _vec("tag_pad")
	var box := Rect2(at + _vec("tag_offset"), text_size + pad * 2.0)
	var c := _role(&"focus") if path_ok else _role(&"danger")
	draw_rect(box, _role(&"panel_deep"))
	draw_rect(box, c, false, _num("outline_px"))
	draw_string(font, box.position + Vector2(pad.x, pad.y + font.get_ascent(fs)), tag_text, 0, -1.0, fs, c)


# --- Shapes -----------------------------------------------------------------------------------------


static func _lozenge(at: Vector2, hw: float, hh: float) -> PackedVector2Array:
	return PackedVector2Array(
		[at + Vector2(0.0, -hh), at + Vector2(hw, 0.0), at + Vector2(0.0, hh), at + Vector2(-hw, 0.0)]
	)


func _outline(shape: PackedVector2Array, c: Color, width: float) -> void:
	var closed := shape.duplicate()
	closed.append(shape[0])
	draw_polyline(closed, c, width, true)


## A cut gem: four facets, lit from the upper left (lighter) to the lower right (darker).
func _gem(at: Vector2, hw: float, hh: float, c: Color) -> void:
	var s := _num("facet_shade")
	var top := at + Vector2(0.0, -hh)
	var right := at + Vector2(hw, 0.0)
	var bottom := at + Vector2(0.0, hh)
	var left := at + Vector2(-hw, 0.0)
	draw_colored_polygon(PackedVector2Array([top, at, left]), c.lightened(s))
	draw_colored_polygon(PackedVector2Array([top, right, at]), c.lightened(s * 0.4))
	draw_colored_polygon(PackedVector2Array([left, at, bottom]), c.darkened(s * 0.4))
	draw_colored_polygon(PackedVector2Array([at, right, bottom]), c.darkened(s))


## Lamp-light: rings of soft glow, widest and faintest first.
func _glow(at: Vector2, hw: float, hh: float, c: Color) -> void:
	var rings := int(_num("glow_rings"))
	var step := _num("glow_step_px")
	var ring := _faded(c, _num("glow_alpha"))
	for i in range(rings, 0, -1):
		draw_colored_polygon(_lozenge(at, hw + step * i, hh + step * i), ring)


func _scale_of(n: LatticeNode) -> float:
	match n.kind:
		LatticeNode.KIND_ABILITY:
			return _num("ability_scale")
		LatticeNode.KIND_START:
			return _num("start_scale")
		LatticeNode.KIND_EMPTY:
			return _num("empty_scale")
	return 1.0


func _region_color(n: LatticeNode) -> Color:
	var roles: Dictionary = _m.get("region_roles", {})
	return _role(StringName(str(roles.get(String(n.region), _m.get("default_region_role", "text_dim")))))


func _role(role: StringName, alpha_scale: float = 1.0) -> Color:
	var c := get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
	c.a *= alpha_scale
	return c


static func _faded(c: Color, k: float) -> Color:
	var out := c
	out.a *= k
	return out


func _num(key: String) -> float:
	return HudLayout.num(_m, key)


func _ovec(key: String) -> Vector2:
	var v: Array = _o.get(key, [0, 0])
	return Vector2(float(v[0]), float(v[1]))


func _vec(key: String) -> Vector2:
	var v: Array = _m.get(key, [0, 0])
	return Vector2(float(v[0]), float(v[1]))


## M2-AUD-15 (audio listens, never edits; ADR 0031): true while the player drags the board (a pan by hand, not the
## camera following the cursor).
func is_dragging() -> bool:
	return _dragging
