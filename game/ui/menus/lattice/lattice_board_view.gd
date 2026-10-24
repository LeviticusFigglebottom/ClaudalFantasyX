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
## reduced motion). A click on a node emits node_clicked.

signal node_clicked(node_id: StringName)

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

var _m: Dictionary = {}
var _pan_tween: Tween


func setup(metrics: Dictionary, with_model: LatticeMenuModel) -> void:
	_m = metrics
	model = with_model
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_STOP


## Where node `nid` sits on the board, in reference px (before the pan).
func board_point(nid: StringName) -> Vector2:
	var n := model.board().lattice_node(nid)
	return Vector2(n.position) * _num("unit_px") if n != null else Vector2.ZERO


## Where node `nid` is drawn inside this view.
func screen_point(nid: StringName) -> Vector2:
	return size * 0.5 + board_point(nid) - pan


## The node drawn nearest `local` (a point in this view), within pick_px; &"" for none.
func node_at(local: Vector2) -> StringName:
	var best := &""
	var best_d := _num("pick_px")
	for nid: StringName in model.board().nodes:
		var d := screen_point(nid).distance_to(local)
		if d <= best_d:
			best_d = d
			best = nid
	return best


## Pans so `nid` is in the middle (held inside the board's bounds); slides unless `animate` is false
## or motion is reduced.
func center_on(nid: StringName, animate: bool) -> void:
	var target := _clamped_pan(board_point(nid))
	if _pan_tween != null and _pan_tween.is_valid():
		_pan_tween.kill()
	if not animate or reduced_motion or not is_inside_tree():
		pan = target
		return
	_pan_tween = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	_pan_tween.tween_property(self, ^"pan", target, _num("pan_sec"))


func _gui_input(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed or mb.button_index != MOUSE_BUTTON_LEFT:
		return
	var nid := node_at(mb.position)
	if nid != &"":
		accept_event()
		node_clicked.emit(nid)


func _clamped_pan(target: Vector2) -> Vector2:
	var b := model.board()
	if b.nodes.is_empty():
		return Vector2.ZERO
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for nid: StringName in b.nodes:
		var p := board_point(nid)
		lo = lo.min(p)
		hi = hi.max(p)
	var margin := _num("pan_margin_px")
	var out := target
	for axis in 2:
		var half := size[axis] * 0.5
		if hi[axis] - lo[axis] + margin * 2.0 <= size[axis]:
			out[axis] = (lo[axis] + hi[axis]) * 0.5
		else:
			out[axis] = clampf(target[axis], lo[axis] - margin + half, hi[axis] + margin - half)
	return out


# --- Drawing ----------------------------------------------------------------------------------------


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), _role(&"line_gold", _num("frame_alpha")), false, _num("outline_px"))
	if model == null or model.board().nodes.is_empty():
		return
	var b := model.board()
	_draw_wash()
	_draw_edges()
	_draw_path()
	for nid: StringName in b.nodes:
		_draw_node(b.lattice_node(nid))
	_draw_markers()
	_draw_cursor()
	_draw_tag()


## Each region's faint ribbon of colour along its own edges.
func _draw_wash() -> void:
	var b := model.board()
	for a: StringName in b.nodes:
		var na := b.lattice_node(a)
		for nb in b.neighbors(a):
			if String(a) >= String(nb) or b.lattice_node(nb).region != na.region:
				continue
			var c := _faded(_region_color(na), _num("wash_alpha"))
			draw_line(screen_point(a), screen_point(nb), c, _num("wash_px"), true)


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
			draw_line(screen_point(a), screen_point(nb), c, w, true)


func _draw_path() -> void:
	var c := _role(&"focus") if path_ok else _role(&"danger")
	for i in range(1, path.size()):
		draw_line(screen_point(path[i - 1]), screen_point(path[i]), c, _num("path_px"), true)


func _draw_node(n: LatticeNode) -> void:
	_draw_shape(n, screen_point(n.id), model.node_state(n.id), _region_color(n))


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
	_hero_ring(screen_point(nid), _half_size(n), pad, c, glow)


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
	var at := screen_point(cursor)
	var half := _half_size(n) + Vector2.ONE * _num("cursor_pad_px")
	var shape := _lozenge(at, half.x, half.y)
	_outline(shape, _role(&"focus"), _num("cursor_px"))
	var tick := _num("cursor_tick_px")
	for v in shape:
		draw_line(v, v + (v - at).normalized() * tick, _role(&"focus_gold"), _num("outline_px") * 2.0, true)


func _draw_tag() -> void:
	if tag_text == "" or model.board().lattice_node(cursor) == null:
		return
	var font := get_theme_font(&"font", &"RankLabel")
	var fs := get_theme_font_size(&"font_size", &"RankLabel")
	var text_size := font.get_string_size(tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1.0, fs)
	var pad := _vec("tag_pad")
	var box := Rect2(screen_point(cursor) + _vec("tag_offset"), text_size + pad * 2.0)
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


func _vec(key: String) -> Vector2:
	var v: Array = _m.get(key, [0, 0])
	return Vector2(float(v[0]), float(v[1]))
