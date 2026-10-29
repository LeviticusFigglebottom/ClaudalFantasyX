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
	# A zone that adds its own layer (Haluna, M2-FP-113) keeps it: a second one would show every villager twice
	# (M3-CRE-100). Only a zone without one gets one here.
	layer = zone.get_node_or_null(^"VillagerLayer") as VillagerLayer
	if layer == null:
		layer = VillagerLayer.new()
		layer.name = "VillagerLayer"
		layer.zone_id = zone_id
		zone.add_child(layer)
