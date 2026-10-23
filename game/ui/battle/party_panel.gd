class_name PartyPanel
extends Control
## Bottom-right party bars (docs/kb/art/ui.md §6.2): the three active fighters only; reserves
## appear in the swap menu. A view over BattleCombatant data: refresh() re-reads, never writes.

var _m: Dictionary = {}
var _rows: Array[PartyRow] = []


func _ready() -> void:
	_m = HudLayout.section(&"party")
	HudLayout.place(self, _m)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var bg := Panel.new()
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)


## Rebuilds the rows for `members` (labels: id -> display name; tints: id -> portrait Color).
func show_members(members: Array[BattleCombatant], labels: Dictionary, tints: Dictionary = {}) -> void:
	for r in _rows:
		r.queue_free()
	_rows.clear()
	var h := HudLayout.num(_m, "row_height")
	var gap := HudLayout.num(_m, "row_gap")
	var inset := float(get_theme_constant(&"inner_rule_inset_px", HymnThemeBuilder.PALETTE_TYPE)) * 2.0
	var used := h * members.size() + gap * maxi(members.size() - 1, 0)
	var y0 := (size.y - used) * 0.5
	for i in members.size():
		var row := PartyRow.new()
		row.position = Vector2(inset, y0 + i * (h + gap))
		row.size = Vector2(size.x - inset * 2.0, h)
		add_child(row)
		var cid := members[i].id
		row.setup(_m, members[i], str(labels.get(cid, String(cid))), tints.get(cid, Color.WHITE) as Color)
		_rows.append(row)


func refresh(animate: bool = false, drain_sec: float = 0.0) -> void:
	for r in _rows:
		r.refresh(animate, drain_sec)


## Highlights the fighter acting now. `auto` (&"berserk"/&"confuse") marks a turn that plays itself.
func set_current(cid: StringName, auto: StringName = &"") -> void:
	for r in _rows:
		r.is_current = r.combatant != null and r.combatant.id == cid
		r.auto_reason = auto if r.is_current else &""
		r.queue_redraw()


func set_targeted(ids: Array[StringName]) -> void:
	for r in _rows:
		r.is_targeted = r.combatant != null and ids.has(r.combatant.id)
		r.queue_redraw()


func row_for(cid: StringName) -> PartyRow:
	for r in _rows:
		if r.combatant != null and r.combatant.id == cid:
			return r
	return null


func rows() -> Array[PartyRow]:
	return _rows.duplicate()
