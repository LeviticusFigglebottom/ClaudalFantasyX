extends Node3D
## M3-CRE-615 review stage: an Act I zone scene with its WildlifeLayer, so the zone's wildlife data is seen in place
## before the zone owner adds the node. The shots (wildlife_zone_*) pick one of the Cameras.

@export_file("*.tscn") var zone_scene: String = ""
@export var zone_id: StringName = &""

var zone: Node3D
var layer: WildlifeLayer


func _ready() -> void:
	zone = (load(zone_scene) as PackedScene).instantiate() as Node3D
	add_child(zone)
	# a zone that builds its own layer (GreyboxZone, from its wildlife file) keeps it: never a second one
	layer = zone.get_node_or_null(^"WildlifeLayer") as WildlifeLayer
	if layer != null:
		return
	layer = WildlifeLayer.new()
	layer.zone_id = zone_id
	zone.add_child(layer)
