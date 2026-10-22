class_name BattleHud
extends Control
## The battle HUD (SPEC §7.6, docs/kb/art/ui.md §6): timeline right, party bars bottom right,
## commands bottom left, target info and help line on top. A view only: BattleController feeds
## it engine data and routes its menu signals; nothing here changes combat state.

## Damage numbers spawned this battle (tests read it).
var damage_numbers_shown := 0

var _damage_m: Dictionary = {}

@onready var timeline: TurnTimeline = %TurnTimeline
@onready var party: PartyPanel = %PartyPanel
@onready var commands: CommandMenu = %CommandMenu
@onready var target_cursor: TargetCursor = %TargetCursor
@onready var result: BattleResultPanel = %ResultPanel
@onready var _help_panel: PanelContainer = %HelpLine
@onready var _help_label: Label = %HelpText
@onready var _damage_layer: Control = %DamageLayer


func _ready() -> void:
	_damage_m = HudLayout.section(&"damage")
	HudLayout.place(_help_panel, HudLayout.section(&"help_line"))
	set_help("")


func set_help(text: String) -> void:
	_help_label.text = text
	_help_panel.visible = text != ""


func help_text() -> String:
	return _help_label.text if _help_panel.visible else ""


## Pops a number at `at` (HUD coordinates). `stack` offsets simultaneous numbers on one target.
func pop_number(text: String, at: Vector2, kind: StringName, on_ally: bool, crit: bool, stack: int = 0) -> void:
	var n := DamageNumber.new()
	_damage_layer.add_child(n)
	n.pop(text, at - Vector2(0.0, HudLayout.num(_damage_m, "stack_px") * stack), kind, on_ally, crit, _damage_m)
	damage_numbers_shown += 1


func set_combat_ui_visible(on: bool) -> void:
	for c: CanvasItem in [timeline, party, commands, _help_panel]:
		c.visible = on
	if not on:
		target_cursor.clear()
		target_cursor.show_actor(Vector2.ZERO, false)
