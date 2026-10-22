class_name TargetCursor
extends Control
## Target feedback in screen space (docs/kb/art/ui.md §6.4): a chevron above each chosen
## target (ui_danger for foes, ui_focus for allies: the shape is shared, the color and the
## target info panel say which side), the target info panel at the top left, and the lamp mote
## over the fighter whose turn it is. The 3D ground ring is drawn by the battle scene.

## Target entries: {id, label, screen_pos: Vector2, hostile: bool, combatant: BattleCombatant,
## revealed: bool}. HP is shown for allies and for foes that have been Read (M1-CMB-03).
var targets: Array[Dictionary] = []

var _m: Dictionary = {}
var _marker_m: Dictionary = {}
var _info: PanelContainer
var _info_name: Label
var _info_hp: Label
var _info_gauge: HudGauge
var _info_status: HBoxContainer
var _info_note: Label
var _actor_pos := Vector2.ZERO
var _actor_mote: LampMote
var _t := 0.0


func _ready() -> void:
	_m = HudLayout.section(&"target_info")
	_marker_m = HudLayout.section(&"actor_marker")
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build_info()
	_actor_mote = LampMote.new()
	var px := HudLayout.num(_marker_m, "size_px")
	_actor_mote.size = Vector2(px, px)
	_actor_mote.period_sec = HudLayout.num(_marker_m, "bob_sec")
	_actor_mote.visible = false
	add_child(_actor_mote)
	clear()


func _process(delta: float) -> void:
	_t += delta
	if not targets.is_empty() or _actor_mote.visible:
		queue_redraw()


func show_targets(entries: Array[Dictionary]) -> void:
	targets = entries
	_info.visible = not entries.is_empty()
	if entries.is_empty():
		queue_redraw()
		return
	var first: Dictionary = entries[0]
	var c: BattleCombatant = first.get("combatant")
	var hostile := bool(first.get("hostile", false))
	_info_name.text = str(first.get("label", "")) if entries.size() == 1 else str(first.get("group_label", ""))
	var role := &"danger" if hostile else &"text"
	_info_name.add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))
	var show_hp := entries.size() == 1 and c != null and (not hostile or bool(first.get("revealed", false)))
	_info_gauge.visible = show_hp
	_info_hp.visible = show_hp
	_info_note.visible = entries.size() == 1 and hostile and not show_hp
	if show_hp:
		_info_gauge.set_value(c.hp, c.max_hp)
		_info_hp.text = "%d/%d" % [c.hp, c.max_hp]
	_sync_status(c if entries.size() == 1 else null)
	queue_redraw()


func clear() -> void:
	show_targets([])


func targeted_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for e in targets:
		out.append(StringName(str(e.get("id", ""))))
	return out


func info_text() -> String:
	return _info_name.text if _info.visible else ""


## Places the breathing mote above the acting fighter; pass `visible_on = false` to hide it.
func show_actor(screen_pos: Vector2, visible_on: bool = true) -> void:
	_actor_mote.visible = visible_on
	_actor_pos = screen_pos
	var px := HudLayout.num(_marker_m, "mote_px")
	_actor_mote.size = Vector2(px, px)
	_actor_mote.position = screen_pos - Vector2(px, px) * 0.5
	queue_redraw()


func _draw() -> void:
	var px := HudLayout.num(_marker_m, "size_px")
	var bob := sin(_t * TAU / maxf(HudLayout.num(_marker_m, "bob_sec"), 0.01)) * HudLayout.num(_marker_m, "bob_px")
	if _actor_mote.visible:
		# The acting fighter: a focus diamond inside the breathing mote (shape differs from the
		# target chevron, so "whose turn" and "who is targeted" never read alike).
		var c := _actor_pos + Vector2(0.0, bob * 0.5)
		var h := px * 0.5
		var dia := PackedVector2Array([c + Vector2(0, -h), c + Vector2(h, 0), c + Vector2(0, h), c + Vector2(-h, 0)])
		draw_colored_polygon(dia, get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE))
		var ring := dia.duplicate()
		ring.append(dia[0])
		draw_polyline(ring, get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE), 1.0, true)
	for e in targets:
		var p: Vector2 = e.get("screen_pos", Vector2.ZERO)
		var col := get_theme_color(
			&"danger" if bool(e.get("hostile", false)) else &"focus", HymnThemeBuilder.PALETTE_TYPE
		)
		var tip := p + Vector2(0.0, bob)
		var pts := PackedVector2Array([tip, tip + Vector2(-px, -px * 1.2), tip + Vector2(px, -px * 1.2)])
		draw_colored_polygon(pts, col)
		var outline := pts.duplicate()
		outline.append(pts[0])
		draw_polyline(outline, get_theme_color(&"outline", HymnThemeBuilder.PALETTE_TYPE), 1.0, true)


func _build_info() -> void:
	_info = PanelContainer.new()
	_info.theme_type_variation = &"PanelSmall"
	HudLayout.place(_info, _m)
	_info.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_info)
	var v := VBoxContainer.new()
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_info.add_child(v)
	var top := HBoxContainer.new()
	v.add_child(top)
	_info_name = Label.new()
	_info_name.theme_type_variation = &"HudName"
	_info_name.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(_info_name)
	_info_status = HBoxContainer.new()
	top.add_child(_info_status)
	var bottom := HBoxContainer.new()
	bottom.alignment = BoxContainer.ALIGNMENT_BEGIN
	v.add_child(bottom)
	_info_gauge = HudGauge.new(&"hp")
	_info_gauge.custom_minimum_size = Vector2(HudLayout.num(_m, "hp_bar_width"), HudLayout.num(_m, "hp_bar_px"))
	_info_gauge.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	bottom.add_child(_info_gauge)
	_info_hp = Label.new()
	_info_hp.theme_type_variation = &"HudNumber"
	bottom.add_child(_info_hp)
	_info_note = Label.new()
	_info_note.theme_type_variation = &"DimLabel"
	_info_note.text = tr("HUD_TARGET_UNREAD")
	bottom.add_child(_info_note)


func _sync_status(c: BattleCombatant) -> void:
	for ch in _info_status.get_children():
		ch.queue_free()
	if c == null:
		return
	var px := float(HudLayout.section(&"party").get("status_icon_px", 0))
	for sid: StringName in c.statuses:
		var g := StatusGlyph.new(sid)
		g.custom_minimum_size = Vector2(px, px)
		_info_status.add_child(g)
