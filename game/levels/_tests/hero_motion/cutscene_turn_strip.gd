extends Node3D
## M2-HER-1104 cutscene turn strip (shot `hero_cutscene_turn_strip`): one hero turning through a cutscene
## turn, frozen at `frames` successive times and stood side by side, left to right, so one image shows
## the whole turn. Each copy's ROOT gets the sequencer's eased yaw at its time (the M2-FP-29 curve:
## Godot's ease() with `turn_ease` over turn_min_sec..turn_sec by angle, mirroring sequencer.json) and
## its body gets HeroIdleMicro, fed the root's turn rate at that instant, so the head and neck lead the
## body mid-turn and settle as it lands. The clip is held on its first frame: a pure function of the
## exports, deterministic. The review stage (`stage`) lends its lights, floor and hero materials.

@export var stage: AshaStage
@export var frames: int = 5
@export var spacing_m: float = 1.0
@export var start_yaw_deg: float = -60.0
@export var turn_deg: float = 120.0
@export var turn_ease: float = -2.0
@export var turn_min_sec: float = 0.25
@export var turn_max_sec: float = 0.45
@export var idle_clip: StringName = &"idle"
@export var actor_id: StringName = &"asha"
## Half-width of the central difference that reads the turn rate off the curve (a share of the turn).
@export var rate_probe: float = 0.001

var actors: Array[Node3D] = []


func _ready() -> void:
	if stage == null or stage.character_scene == null:
		push_warning("cutscene_turn_strip: no stage")
		return
	var source := stage.find_child(String(stage.character_name), true, false) as Node3D
	var dur := turn_duration()
	for i in frames:
		var u := float(i) / float(maxi(frames - 1, 1))
		var root := Node3D.new()
		root.name = "Frame%d" % i
		root.position = Vector3((float(i) - float(frames - 1) * 0.5) * spacing_m, 0.0, 0.0)
		root.rotation.y = yaw_at(u)
		add_child(root)
		var body := stage.character_scene.instantiate() as Node3D
		body.name = "Body"
		root.add_child(body)
		if source != null:
			_copy_materials(source, body)
		var ap := HeroMotion.player_of(body)
		if ap != null and ap.has_animation(idle_clip):
			ap.play(idle_clip, 0.0)
			ap.seek(0.0, true)
			ap.pause()
		var micro := HeroMotion.add_micro_motion(root, actor_id)
		if micro != null:
			micro.use_measured_rate = false
			micro.turn_rate = rate_at(u, dur)
		actors.append(root)
	if source != null:
		source.visible = false


## The turn's length for `turn_deg` (CutsceneMotion.turn_duration).
func turn_duration() -> float:
	return lerpf(turn_min_sec, turn_max_sec, clampf(absf(deg_to_rad(turn_deg)) / PI, 0.0, 1.0))


## The root's yaw (radians) a share `u` (0..1) through the turn (CutsceneMotion.eased).
func yaw_at(u: float) -> float:
	return deg_to_rad(start_yaw_deg + turn_deg * ease(clampf(u, 0.0, 1.0), turn_ease))


## The root's turn rate (radians per second) at share `u`, read off the curve.
func rate_at(u: float, dur: float) -> float:
	if dur <= 0.0:
		return 0.0
	var lo := clampf(u - rate_probe, 0.0, 1.0)
	var hi := clampf(u + rate_probe, 0.0, 1.0)
	if hi <= lo:
		return 0.0
	return (yaw_at(hi) - yaw_at(lo)) / ((hi - lo) * dur)


func _copy_materials(from: Node, to: Node) -> void:
	for mi: Node in from.find_children("*", "MeshInstance3D", true, false):
		var src := mi as MeshInstance3D
		var dst := to.get_node_or_null(from.get_path_to(src)) as MeshInstance3D
		if dst == null:
			continue
		for s: int in src.get_surface_override_material_count():
			dst.set_surface_override_material(s, src.get_surface_override_material(s))
		dst.cast_shadow = src.cast_shadow
