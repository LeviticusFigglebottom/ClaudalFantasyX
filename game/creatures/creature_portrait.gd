class_name CreaturePortrait
extends SubViewportContainer
## A live 3D portrait of a battle creature for the UI (M2-CRE-10): the bestiary page or the Read panel instances
## creature_portrait.tscn and calls show_enemy(id). It renders the enemy's model (enemies.json `model`) in its own
## small world with a transparent background, held at creatures.json's `portrait` clip and time and framed from its
## yaw and pitch, so no portrait image is ever stored: a model change updates every portrait. An enemy without a
## model shows nothing (show_enemy returns false and the control hides its picture).
## M3-CRE-618: the key and the rim are placed from the camera, not the world, so every creature's portrait yaw gets
## the same lighting: the key from over the camera's left shoulder, the rim from behind the creature (rim_side_deg
## to the right of straight back, rim_elev_deg up), its strength from the row (`portrait.rim_energy`; the creatures
## whose albedo is darkest get more, so their silhouettes hold on the UI's deep panel) and, for those, a low kick
## from the other back side (`kick_energy`, `kick_elev_deg`) that grazes their lower edges.

## The enemy shown (&"" when none).
var enemy_id: StringName = &""
## Its actor in the portrait world (null when none).
var actor: CreatureActor

@onready var _viewport: SubViewport = $Viewport
@onready var _camera: Camera3D = $Viewport/Camera
@onready var _holder: Node3D = $Viewport/Holder
@onready var _key: DirectionalLight3D = $Viewport/Key
@onready var _rim: DirectionalLight3D = $Viewport/Rim
@onready var _kick: DirectionalLight3D = $Viewport/Kick


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
	_light(cfg)
	_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	return true


## Places the key and the rim from the camera (see the class note). A DirectionalLight3D shines along its -Z.
func _light(cfg: Dictionary) -> void:
	var view := _camera.global_basis
	var side := deg_to_rad(float(cfg.get("rim_side_deg", 0.0)))
	var elev := deg_to_rad(float(cfg.get("rim_elev_deg", 0.0)))
	# The rim travels from behind the creature toward the camera (+Z of the camera), turned aside and tipped down.
	var toward_cam := view.z.rotated(view.y, side)
	var rim_dir := toward_cam.rotated(toward_cam.cross(Vector3.UP).normalized(), -elev)
	_rim.global_basis = Basis.looking_at(rim_dir, Vector3.UP)
	_rim.light_energy = float(cfg.get("rim_energy", _rim.light_energy))
	var kick_toward := view.z.rotated(view.y, -side)
	var kick_elev := deg_to_rad(float(cfg.get("kick_elev_deg", 0.0)))
	_kick.global_basis = Basis.looking_at(
		kick_toward.rotated(kick_toward.cross(Vector3.UP).normalized(), -kick_elev), Vector3.UP
	)
	_kick.light_energy = float(cfg.get("kick_energy", 0.0))
	_kick.visible = _kick.light_energy > 0.0
	# The key comes over the camera's left shoulder: away from the camera, turned right and down.
	var key_dir := (-view.z).rotated(view.y, -side).rotated(view.x, -elev)
	_key.global_basis = Basis.looking_at(key_dir, Vector3.UP)
	_key.light_energy = float(cfg.get("key_energy", _key.light_energy))


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
