class_name CreaturePortrait
extends SubViewportContainer
## A live 3D portrait of a battle creature for the UI (M2-CRE-10): the bestiary page or the Read panel instances
## creature_portrait.tscn and calls show_enemy(id). It renders the enemy's model (enemies.json `model`) in its own
## small world with a transparent background, held at creatures.json's `portrait` clip and time and framed from its
## yaw and pitch, so no portrait image is ever stored: a model change updates every portrait. An enemy without a
## model shows nothing (show_enemy returns false and the control hides its picture).

## The enemy shown (&"" when none).
var enemy_id: StringName = &""
## Its actor in the portrait world (null when none).
var actor: CreatureActor

@onready var _viewport: SubViewport = $Viewport
@onready var _camera: Camera3D = $Viewport/Camera
@onready var _holder: Node3D = $Viewport/Holder


## Shows enemy `id`'s creature; false (and an empty picture) when it has no model.
func show_enemy(id: StringName) -> bool:
	clear()
	var path := str(CreatureModels.models().get(String(id), ""))
	if path == "" or not ResourceLoader.exists(path):
		return false
	enemy_id = id
	actor = (load(path) as PackedScene).instantiate() as CreatureActor
	_holder.add_child(actor)
	var cfg: Dictionary = CreatureActor.row_for(actor.creature_id).get("portrait", {})
	CreatureFraming.hold(actor, StringName(str(cfg.get("clip", "idle"))), float(cfg.get("clip_time", 0.0)))
	CreatureFraming.frame_fit(
		_camera,
		CreatureFraming.bounds([actor]),
		float(cfg.get("yaw_deg", 0.0)),
		float(cfg.get("pitch_deg", 0.0)),
		float(cfg.get("fov_deg", 30.0)),
		float(cfg.get("margin", 1.0))
	)
	_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	return true


func clear() -> void:
	enemy_id = &""
	if actor != null and is_instance_valid(actor):
		_holder.remove_child(actor)
		actor.queue_free()
	actor = null
	if _viewport != null:
		_viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED


func has_creature() -> bool:
	return actor != null
