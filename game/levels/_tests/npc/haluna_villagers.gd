extends Node3D
## M3-CRE-613 review stage: a real zone with a VillagerLayer, so the villagers are seen in place. In Haluna:
## the dock pair chatting and mending, the vendor at the stall, Reed sweeping the chapel court, the child on the
## lane (npc_haluna_*); on the wake night, the feast tables (npc_wake_*). The shots pick one of the Cameras.

@export_file("*.tscn") var zone_scene: String = "res://game/levels/ch02/haluna/haluna.tscn"
@export var zone_id: StringName = &"ch02/haluna"

var zone: Node3D
var layer: VillagerLayer


func _ready() -> void:
	zone = (load(zone_scene) as PackedScene).instantiate() as Node3D
	add_child(zone)
	layer = VillagerLayer.new()
	layer.zone_id = zone_id
	zone.add_child(layer)
