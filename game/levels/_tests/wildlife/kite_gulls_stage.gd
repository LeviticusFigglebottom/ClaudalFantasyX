extends Node3D
## M5-A3P-1808 review stage: a stand-in Kite under way on a wide turn, its gulls (kite_gulls.json, a `follow` flock)
## riding along with it. The camera is the Kite's, so the flock should hold its place round the hull while the sea
## slides past. The Kite moves before the layer steps (process_priority), so the perched birds never lag the rail.

## The stand-in's way: speed along a turn of this radius (review values, not game tuning).
@export var speed_mps := 9.0
@export var turn_radius_m := 120.0

var _angle := 0.0

@onready var kite: Node3D = $Kite


func _ready() -> void:
	process_priority = -1
	_place()


func _process(delta: float) -> void:
	_angle += speed_mps / turn_radius_m * delta
	_place()


func _place() -> void:
	var p := Vector3(turn_radius_m * (1.0 - cos(_angle)), 0.0, turn_radius_m * sin(_angle))
	kite.transform = Transform3D(Basis(Vector3.UP, _angle), p)
