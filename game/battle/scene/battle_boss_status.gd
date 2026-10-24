class_name BattleBossStatus
extends PanelContainer
## The boss's standing read-out (M2-FP-11; battle_ctb.md "The Drownbell", "Status strip"): under the
## target info, top left, for as long as a boss with mechanics is on the field. Floats come and go
## (and are off with damage numbers); this stays, so the player can always see what the boss is
## building toward and what answers it (pillar 4). A view: it reads combatant state, never writes.
##   title    "<boss> · <phase>"  (enemies.json phase_name_key for the opening phase, then each
##            phase row's name_key)
##   charge   "<skill> comes on its next turn" / "... in N of its turns" (charge_left), in danger
##   weak     "<part> n/need" while a charge can still be broken
##   field    "<field>: n bound to it" while a field the boss raised is up (field_name_key)
## refresh() runs after every engine signal BattleBossHud listens to; hide_status() at the end.

const ROLE_DANGER := &"danger"
const ROLE_FOCUS := &"focus_gold"

var title: Label
var charge: Label
var weak: Label
var field: Label

var _m: Dictionary = {}


func _init() -> void:
	name = &"BossStatus"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(box)
	title = _label(box, &"HelpLabel")
	charge = _label(box, &"HelpLabel")
	weak = _label(box, &"HelpLabel")
	field = _label(box, &"DimLabel")


func _ready() -> void:
	_m = HudLayout.section(&"boss_status")
	HudLayout.place(self, _m)
	(get_child(0) as VBoxContainer).add_theme_constant_override(&"separation", int(HudLayout.num(_m, "line_gap")))


## The boss `engine` shows, or null: the first living enemy with a weak point or phases.
static func boss_of(engine: BattleEngine) -> BattleCombatant:
	for e in engine.enemies:
		if e.is_alive() and (not e.weak_point.is_empty() or not e.phases.is_empty()):
			return e
	return null


## Reads the boss's state off `engine` and shows it; hides when there is no boss.
func refresh(engine: BattleEngine, menus: BattleMenus) -> void:
	var b := boss_of(engine)
	if b == null or engine.outcome != &"":
		hide_status()
		return
	var row: Dictionary = engine.db.enemies.get(BattleEngine.enemy_id(b), {})
	var phase := _phase_key(b, row)
	title.text = " · ".join([menus.display_name(b), tr(phase)]) if phase != "" else menus.display_name(b)
	charge.visible = b.is_charging()
	weak.visible = b.is_charging() and not b.weak_point.is_empty()
	if b.is_charging():
		var skill := menus.skill_name(engine, b.charge_skill)
		charge.text = (
			tr("HUD_BOSS_CHARGE_NEXT_FMT").format({"skill": skill})
			if b.charge_left <= 1
			else tr("HUD_BOSS_CHARGE_IN_FMT").format({"skill": skill, "turns": b.charge_left})
		)
		_tint(charge, ROLE_DANGER)
		weak.text = (
			tr("HUD_WEAK_POINT_FMT")
			. format(
				{
					"part": tr(str(b.weak_point.get("name_key", ""))),
					"hits": b.weak_hits,
					"need": int(b.weak_point.get("hits", 1)),
				}
			)
		)
		_tint(weak, ROLE_FOCUS)
	var field_key := str(row.get("field_name_key", ""))
	var bound := 0
	for f: StringName in engine.fields:
		for e in engine.enemies:
			if e.is_alive() and e.field == f:
				bound += 1
	field.visible = field_key != "" and not engine.fields.is_empty()
	field.text = tr("HUD_BOSS_FIELD_FMT").format({"field": tr(field_key), "count": bound})
	visible = true
	# Fit the lines in force: a Control grows to its minimum size but never shrinks by itself.
	size = Vector2(size.x, 0.0)


func hide_status() -> void:
	visible = false


## The name key of the phase in force: the row's name_key, or phase_name_key before any row.
static func _phase_key(b: BattleCombatant, row: Dictionary) -> String:
	if b.phase_index >= 0 and b.phase_index < b.phases.size():
		return str((b.phases[b.phase_index] as Dictionary).get("name_key", ""))
	return str(row.get("phase_name_key", ""))


func _tint(l: Label, role: StringName) -> void:
	l.add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))


static func _label(box: VBoxContainer, variation: StringName) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(l)
	return l
