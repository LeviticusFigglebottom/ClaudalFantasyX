class_name Act1ZoneRig
extends Node3D
## A shot rig for a dressed Act I zone (ADR 0200): instances the zone with its story held (no arrival
## cutscene, no player input), so the Cameras/* children frame the kit dressing as the player meets it.
## `flags` are set first, so a rig can show a later state (the states rows, the dusk light).
## `views`: {name: [pos [x, y, z], look_at [x, y, z], fov_deg]}, built as Cameras/<name> (Camera3D).

@export var zone_scene: PackedScene
@export var flags: PackedStringArray = []
@export var views: Dictionary = {}

var zone: GreyboxZone


func _ready() -> void:
	for f: String in flags:
		Game.set_flag(StringName(f))
	zone = zone_scene.instantiate() as GreyboxZone
	zone.story.autostart = false
	add_child(zone)
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	zone.director.auto_update = false
	var cams := Node3D.new()
	cams.name = "Cameras"
	add_child(cams)
	for view: String in views:
		var v: Array = views[view]
		var cam := Camera3D.new()
		cam.name = view
		cams.add_child(cam)
		cam.look_at_from_position(_vec(v[0]), _vec(v[1]))
		cam.fov = float(v[2])


static func _vec(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))
