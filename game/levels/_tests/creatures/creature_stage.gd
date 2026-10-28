class_name CreatureStage
extends Node3D
## Review and capture stage for the battle creatures (M2-CRE-09, docs/kb/art/creatures/pipeline.md "Review").
## Shows one creature (or a lineup) in the battle sandbox's noon light, holds `clip` at `clip_time`, and frames
## the camera on the creatures' bounds from a named view (creature_stage.json). `scale_bars` adds thin bars at
## the heroes' heights beside the lineup. `show_floor` false hides the ground disc, for a creature that lives below
## y 0 (the Wakefin under its waterline, M3-CRE-635).

const CONFIG_PATH := "res://game/levels/_tests/creatures/creature_stage.json"

## Creature actor scenes, left to right.
@export var creatures: Array[PackedScene] = []
@export var clip: StringName = &"idle"
@export var clip_time: float = 0.0
@export var view: StringName = &"three_quarter"
@export var scale_bars := false
## Extra yaw for every creature (degrees); 0 shows each facing the camera's default +Z.
@export var creature_yaw_deg: float = 0.0
## A boss phase to show (CreatureActor.enter_phase, applied at once), and breakable parts to show broken.
@export var phase: StringName = &""
@export var broken_parts: Array[StringName] = []
## False hides the opaque ground disc, so what hangs below y 0 shows.
@export var show_floor := true

var actors: Array[CreatureActor] = []
var _cfg: Dictionary = {}

@onready var camera: Camera3D = $Camera


func _ready() -> void:
	_cfg = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH)) as Dictionary
	($GroundDisc as Node3D).visible = show_floor
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
		if phase != &"":
			a.enter_phase(phase, true)
		for part in broken_parts:
			a.set_part_broken(part, true)
		hold(a)
	if scale_bars:
		_add_scale_bars(x)
	frame_camera()


## Holds `clip` at `clip_time` (a paused AnimationPlayer: the capture is the same every run).
func hold(a: CreatureActor) -> void:
	if not CreatureFraming.hold(a, clip, clip_time):
		push_warning("CreatureStage: %s has no clip %s" % [a.creature_id, clip])


func frame_camera() -> void:
	var v: Dictionary = (_cfg.get("views", {}) as Dictionary).get(String(view), {})
	CreatureFraming.frame(
		camera,
		_bounds(get_children()),
		float(v.get("yaw_deg", 0.0)),
		float(v.get("pitch_deg", 10.0)),
		float(v.get("fov_deg", 30.0)),
		float(v.get("margin", 1.0))
	)


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


## World bounds of the creatures and scale bars (not the ground disc).
func _bounds(nodes: Array) -> AABB:
	return CreatureFraming.bounds(nodes, PackedStringArray(["GroundDisc"]))
