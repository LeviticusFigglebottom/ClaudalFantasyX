extends Control
## Screenshot fixture (M2-CRE-10): a CreaturePortrait for every enemy with a model, on the UI's deep panel colour,
## as the bestiary page would show them (the UI request is M2-UI-28).

const PORTRAIT := preload("res://game/creatures/creature_portrait.tscn")
## Every portrait fits the 1280 x 720 shot: 7 columns of 3 rows (21 creatures with models).
const CELL := Vector2(160, 160)

@onready var _grid: GridContainer = $Grid


func _ready() -> void:
	var ids: Array = CreatureModels.models().keys()
	ids.sort()
	for id: Variant in ids:
		var p := PORTRAIT.instantiate() as CreaturePortrait
		p.custom_minimum_size = CELL
		_grid.add_child(p)
		p.show_enemy(StringName(str(id)))
