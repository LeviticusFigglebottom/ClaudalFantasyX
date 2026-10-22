class_name PartyRow
extends Control
## One active fighter in the PartyPanel: name, status strip, HP and MP numbers with bars.
## Reads a BattleCombatant; never writes to it.

var combatant: BattleCombatant
var is_current := false
var is_targeted := false

var _m: Dictionary = {}
var _name: Label
var _hp_label: Label
var _mp_label: Label
var _hp: HudGauge
var _mp: HudGauge
var _status_strip: HBoxContainer
var _statuses: Array[StringName] = []


func setup(metrics: Dictionary, c: BattleCombatant, label: String) -> void:
	_m = metrics
	combatant = c
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var pad := HudLayout.num(_m, "pad_x")
	var gap := HudLayout.num(_m, "column_gap")
	var strip := HudLayout.num(_m, "status_strip_px")
	var name_w := HudLayout.num(_m, "name_width")
	var hp_x := pad + name_w + gap
	var hp_w := HudLayout.num(_m, "hp_width")
	var mp_x := hp_x + hp_w + gap
	var mp_w := HudLayout.num(_m, "mp_width")
	var h := HudLayout.num(_m, "row_height")
	var bar_y := h - strip * 0.5 - HudLayout.num(_m, "hp_bar_px")
	_name = _label(&"HudName", Rect2(pad, strip * 0.5, name_w, h - strip * 0.5 * 2.0))
	_name.text = label
	_name.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_name.clip_text = true
	_status_strip = HBoxContainer.new()
	_status_strip.position = Vector2(hp_x, 0.0)
	_status_strip.size = Vector2(hp_w + gap + mp_w, strip)
	_status_strip.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "status_gap")))
	_status_strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_status_strip)
	var num_h := bar_y - strip
	_hp_label = _label(&"HudNumber", Rect2(hp_x, strip, hp_w, num_h))
	_mp_label = _label(&"HudNumber", Rect2(mp_x, strip, mp_w, num_h))
	_hp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_mp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_hp = HudGauge.new(&"hp")
	_hp.low_fraction = HudLayout.num(_m, "low_hp_fraction")
	_hp.hatch_px = HudLayout.num(_m, "hatch_px")
	_hp.position = Vector2(hp_x, bar_y)
	_hp.size = Vector2(hp_w, HudLayout.num(_m, "hp_bar_px"))
	add_child(_hp)
	_mp = HudGauge.new(&"mp")
	_mp.position = Vector2(mp_x, bar_y + HudLayout.num(_m, "hp_bar_px") - HudLayout.num(_m, "mp_bar_px"))
	_mp.size = Vector2(mp_w, HudLayout.num(_m, "mp_bar_px"))
	add_child(_mp)
	refresh(false)


## Re-reads HP, MP and statuses. `animate` drains the bars instead of snapping.
func refresh(animate: bool, drain_sec: float = 0.0) -> void:
	if combatant == null:
		return
	var sec := drain_sec if animate else 0.0
	_hp.set_value(combatant.hp, combatant.max_hp, sec)
	_mp.set_value(combatant.mp, combatant.max_mp, sec)
	_hp_label.text = "%d/%d" % [combatant.hp, combatant.max_hp]
	_mp_label.text = "%d" % combatant.mp
	var low := _hp.is_low() or not combatant.is_alive()
	var danger := get_theme_color(&"danger", HymnThemeBuilder.PALETTE_TYPE)
	if low:
		_hp_label.add_theme_color_override(&"font_color", danger)
	else:
		_hp_label.remove_theme_color_override(&"font_color")
	_sync_statuses()
	queue_redraw()


func hp_text() -> String:
	return _hp_label.text


func status_ids() -> Array[StringName]:
	return _statuses.duplicate()


func _sync_statuses() -> void:
	var ids: Array[StringName] = []
	for sid: StringName in combatant.statuses:
		if ids.size() < int(HudLayout.num(_m, "max_status_icons")):
			ids.append(sid)
	if ids == _statuses:
		return
	_statuses = ids
	for ch in _status_strip.get_children():
		ch.queue_free()
	var px := HudLayout.num(_m, "status_icon_px")
	for sid in ids:
		var g := StatusGlyph.new(sid)
		g.custom_minimum_size = Vector2(px, px)
		_status_strip.add_child(g)


func _draw() -> void:
	if is_current or is_targeted:
		var raised := get_theme_color(&"panel_raised", HymnThemeBuilder.PALETTE_TYPE)
		draw_rect(Rect2(Vector2.ZERO, size), raised)
		var edge := get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE)
		var w := float(get_theme_constant(&"focus_px", HymnThemeBuilder.PALETTE_TYPE))
		if is_targeted:
			draw_rect(Rect2(Vector2.ONE * w * 0.5, size - Vector2.ONE * w), edge, false, w)
		else:
			draw_rect(Rect2(0, 0, w, size.y), edge)
	if combatant != null and not combatant.is_alive():
		_name.modulate = Color(1, 1, 1, get_theme_color(&"text_disabled", HymnThemeBuilder.PALETTE_TYPE).a)
	elif _name != null:
		_name.modulate = Color.WHITE


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
