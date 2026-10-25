extends Node3D
## M3-CRE-613 review stage: the real Haluna zone with a VillagerLayer, so the villagers are seen in place:
## the dock pair chatting and mending, the vendor at the stall, Reed sweeping the chapel court, the child
## on the lane. The shots (npc_haluna_*) pick one of the Cameras.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"

@export var zone_id: StringName = &"ch02/haluna"

var zone: Node3D
var layer: VillagerLayer


func _ready() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	add_child(zone)
	layer = VillagerLayer.new()
	layer.zone_id = zone_id
	zone.add_child(layer)
