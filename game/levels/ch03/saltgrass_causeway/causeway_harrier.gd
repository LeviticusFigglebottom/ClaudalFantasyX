class_name CausewayHarrier
extends Node3D
## The gull harrier (B06's set fight, ch03_causeway_harrier) circling over the causeway ahead of its fight, so C07
## ("the flier against the cumulus") holds its subject. It is the battle creature's own model on its idle loop, on a
## slow banked circle around this node; it is gone once the fight is won (ch03_harrier_won).

const MODEL := "res://assets/creatures/gull_harrier/gull_harrier.glb"
const CLIP := &"idle"
const WON := &"ch03_harrier_won"

@export var radius_m := 3.0
@export var period_sec := 8.0
@export var bank_deg := 18.0

var model: Node3D
var _t := 0.0


func _ready() -> void:
	visible = not bool(Game.get_flag(WON))
	set_process(visible)
	if not visible:
		return
	model = (load(MODEL) as PackedScene).instantiate() as Node3D
	add_child(model)
	for n in model.find_children("*", "AnimationPlayer", true, false):
		var player := n as AnimationPlayer
		if player.has_animation(CLIP):
			player.get_animation(CLIP).loop_mode = Animation.LOOP_LINEAR
			player.play(CLIP)
		break
	place(0.0)


func _process(delta: float) -> void:
	_t += delta
	place(_t)


## Puts the bird `t` seconds into its circle: on the ring, facing along it (the model's front is +Z), banked in.
func place(t: float) -> void:
	if model == null:
		return
	var a := TAU * t / period_sec
	var ahead := Vector3(-sin(a), 0.0, cos(a))
	var facing := Basis.looking_at(ahead, Vector3.UP, true)
	model.transform = Transform3D(Basis(ahead, deg_to_rad(bank_deg)) * facing, Vector3(cos(a), 0.0, sin(a)) * radius_m)
