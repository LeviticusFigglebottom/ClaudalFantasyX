class_name CreatureStage
extends Node3D
## Review and capture stage for the battle creatures (M2-CRE-09, docs/kb/art/creatures/pipeline.md "Review").
## Shows one creature (or a lineup) in the battle sandbox's noon light, holds `clip` at `clip_time`, and frames
## the camera on the creatures' bounds from a named view (creature_stage.json). `scale_bars` adds thin bars at
## the heroes' heights beside the lineup.

const CONFIG_PATH := "res://game/levels/_tests/creatures/creature_stage.json"

## Creature actor scenes, left to right.
@export var creatures: Array[PackedScene] = []
@export var clip: StringName = &"idle"
@export var clip_time: float = 0.0
@export var view: StringName = &"three_quarter"
@export var scale_bars := false
## Extra yaw for every creature (degrees); 0 shows each facing the camera's default +Z.
@export var creature_yaw_deg: float = 0.0

var actors: Array[CreatureActor] = []
var _cfg: Dictionary = {}

@onready var camera: Camera3D = $Camera


func _ready() -> void:
	_cfg = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH)) as Dictionary
	var x := 0.0
	var gap := float(_cfg.get("lineup_gap_m", 0.5))
	for packed in creatures:
		var a := packed.instantiate() as CreatureActor
		add_child(a)
		a.rotation.y = deg_to_rad(creature_yaw_deg)
		var w := _bounds([a]).size.x
		a.position.x = x + w * 0.5 - _bounds([a]).get_center().x
		x += w + gap
		actors.append(a)
		hold(a)
	if scale_bars:
		_add_scale_bars(x)
	frame_camera()


## Holds `clip` at `clip_time` (a paused AnimationPlayer: the capture is the same every run).
func hold(a: CreatureActor) -> void:
	var players := a.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		return
	var p := players[0] as AnimationPlayer
	if not p.has_animation(clip):
		push_warning("CreatureStage: %s has no clip %s" % [a.creature_id, clip])
		return
	p.play(clip, 0.0)
	p.seek(clip_time, true)
	p.pause()


func frame_camera() -> void:
	var v: Dictionary = (_cfg.get("views", {}) as Dictionary).get(String(view), {})
	var box := _bounds(get_children())
	var c := box.get_center()
	var radius := box.size.length() * 0.5 * float(v.get("margin", 1.2))
	camera.fov = float(v.get("fov_deg", 30.0))
	var dist := radius / sin(deg_to_rad(camera.fov * 0.5))
	var yaw := deg_to_rad(float(v.get("yaw_deg", 0.0)))
	var pitch := deg_to_rad(float(v.get("pitch_deg", 10.0)))
	var dir := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
	camera.position = c + dir * dist
	camera.look_at(c, Vector3.UP)


func _add_scale_bars(x0: float) -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color.html(str(_cfg.get("scale_bar_color", "#808080")))
	var x := x0
	for bar: Variant in _cfg.get("scale_bars", []):
		var h := float((bar as Dictionary).get("height_m", 1.7))
		var m := MeshInstance3D.new()
		var cyl := CylinderMesh.new()
		cyl.top_radius = float(_cfg.get("scale_bar_radius_m", 0.05))
		cyl.bottom_radius = cyl.top_radius
		cyl.height = h
		cyl.material = mat
		m.mesh = cyl
		m.name = "Bar_%s" % str((bar as Dictionary).get("name", ""))
		m.position = Vector3(x, h * 0.5, 0.0)
		add_child(m)
		x += float(_cfg.get("scale_bar_gap_m", 0.4))


## World bounds of every visible mesh under `nodes` (skinned meshes at their rest bounds).
func _bounds(nodes: Array) -> AABB:
	var box := AABB()
	var first := true
	for n: Variant in nodes:
		if not n is Node:
			continue
		var list: Array = (n as Node).find_children("*", "MeshInstance3D", true, false)
		if n is MeshInstance3D:
			list.append(n)
		for m: MeshInstance3D in list:
			if m.mesh == null or not m.is_visible_in_tree() or m.name == "GroundDisc":
				continue
			var b := m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
	return box
