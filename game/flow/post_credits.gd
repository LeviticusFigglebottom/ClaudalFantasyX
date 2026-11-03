class_name PostCredits
extends Node
## M5-A3P-1701 / 1203: the credits' next_scene (credits.json). It travels to `location` at `spawn`, where the
## zone's arrival row on credits_seen plays E7, the first lamp (ch01.json Oruvel), and then opens the title.

@export var location: StringName = &"ch01/oruvel"
@export var spawn: StringName = &"KellRun"


func _ready() -> void:
	FlowRouting.go_to.call_deferred(location, spawn)
