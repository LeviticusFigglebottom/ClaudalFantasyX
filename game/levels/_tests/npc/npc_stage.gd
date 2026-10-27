extends Node3D
## M3-CRE-610 review stage: three FieldNpc villagers on a plain ground. The fisher walks a short route,
## the netmender idles, and Osu is spoken to by a stand-in player, so she turns to face it and talks.
## The screenshot (npc_stage_field) runs it at a fixed frame rate, so the frozen moment is deterministic.

@export var talker_path: NodePath = ^"Villagers/Osu"
@export var player_path: NodePath = ^"StandInPlayer"


func _ready() -> void:
	var talker := get_node_or_null(talker_path) as FieldNpc
	var player := get_node_or_null(player_path) as Node3D
	if talker != null and player != null:
		talker.begin_talk(player)
