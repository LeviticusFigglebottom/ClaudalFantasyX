class_name CreditsRollShot
extends Control
## Capture driver for the closing credits (M5-A3P-1700, tests/screenshots/shots.json): the roll at a fixed point of its
## climb, the black behind it and the hint at the foot, once seen (the skip offered too), still.

## How far the roll is: a fraction of it (0..1).
@export var at: float = 0.5

var roll: CreditsRoll


func _ready() -> void:
	roll = CreditsRoll.new()
	roll.model = CreditsRollModel.new({}, true)
	roll.change_scene = func(_p: String) -> void: pass
	roll.set_flag = func(_f: StringName) -> void: pass
	roll.set_process(false)
	add_child(roll)
	roll.advance(float(roll.model.data.get("lead_in_sec", 0.0)) + 0.01)
	roll.advance(at * float(roll.model.data.get("roll_sec", 0.0)))
