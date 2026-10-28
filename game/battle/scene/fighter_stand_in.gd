class_name FighterStandIn
extends Node3D
## Stand-in for one fighter (M1-CMB-01): a primitive mesh from battle_sandbox.json and the
## ground-ring target highlight. Presentation only: it is told what to show.
## M2-UI-07: a spec with "scene" (a hero's battle-scale actor scene, e.g.
## res://game/characters/heroes/asha_battle.tscn) instances that scene instead of the primitive,
## standing on the ground at "hover", turned by "yaw_deg", playing its AnimationPlayer's "idle"
## clip while it waits. The head position still comes from the spec's "height" (the hero's real
## height). Flinch and KO move the actor as they moved the primitive; Petrify gives every surface
## the stone material; KO fades every surface. A missing scene falls back to the primitive.

const RING_SHADER := preload("res://game/battle/scene/ground_ring.gdshader")
const RING_NONE := &"none"
const RING_ALLY := &"ally"
const RING_FOE := &"foe"
## The clip an actor scene plays while it waits (character pipeline.md §13).
const IDLE_CLIP := &"idle"

var combatant_id: StringName = &""
var spec: Dictionary = {}

var _mesh: MeshInstance3D
## The hero actor scene's instance (null for a primitive stand-in).
var _actor: Node3D
## What flinch and KO move: the primitive mesh, or the actor.
var _body: Node3D
## The actor's surfaces (MeshInstance3D descendants), for stone and the KO fade.
var _surfaces: Array[MeshInstance3D] = []
var _stone_mat: StandardMaterial3D
var _ring: MeshInstance3D
var _ring_mat: ShaderMaterial
var _body_mat: StandardMaterial3D
var _ring_cfg: Dictionary = {}
var _spin := 0.0
var _rest := Vector3.ZERO
var _ko := false
var _stone := false
var _albedo := Color.WHITE
var _roughness := 1.0


func setup(cid: StringName, stand_in: Dictionary, ring_cfg: Dictionary) -> void:
	combatant_id = cid
	spec = stand_in
	_ring_cfg = ring_cfg
	name = String(cid).replace("#", "_")
	_build_body()
	_build_ring()


## True when the stand-in shows a hero actor scene rather than a primitive (M2-UI-07).
func has_actor() -> bool:
	return _actor != null


func actor() -> Node3D:
	return _actor


func _build_body() -> void:
	var path := str(spec.get("scene", ""))
	if path != "":
		if ResourceLoader.exists(path):
			_build_actor(load(path) as PackedScene)
			return
		push_warning("FighterStandIn: %s names a missing actor scene %s; using the primitive" % [combatant_id, path])
	_mesh = MeshInstance3D.new()
	_mesh.mesh = _make_mesh()
	_body_mat = StandardMaterial3D.new()
	_body_mat.albedo_color = Color.html(str(spec.get("color", "#B9AE98")))
	_body_mat.roughness = float(spec.get("roughness", 1.0))
	if spec.has("emission"):
		_body_mat.emission_enabled = true
		_body_mat.emission = Color.html(str(spec["emission"]))
		_body_mat.emission_energy_multiplier = float(spec.get("emission_energy", 1.0))
	_mesh.material_override = _body_mat
	_albedo = _body_mat.albedo_color
	_roughness = _body_mat.roughness
	_rest = Vector3(0.0, _base_height(), 0.0)
	_mesh.position = _rest
	add_child(_mesh)
	_body = _mesh


## The actor stands with its origin (its feet) on the ground at "hover", turned by "yaw_deg".
func _build_actor(packed: PackedScene) -> void:
	_actor = packed.instantiate() as Node3D
	_actor.rotation.y = deg_to_rad(float(spec.get("yaw_deg", 0.0)))
	_rest = Vector3(0.0, float(spec.get("hover", 0.0)), 0.0)
	_actor.position = _rest
	add_child(_actor)
	_body = _actor
	for n in _actor.find_children("*", "MeshInstance3D", true, false):
		_surfaces.append(n as MeshInstance3D)
	var players := _actor.find_children("*", "AnimationPlayer", true, false)
	if not players.is_empty():
		var player := players[0] as AnimationPlayer
		if player.has_animation(IDLE_CLIP):
			player.play(IDLE_CLIP)


func _process(delta: float) -> void:
	if _ring.visible:
		_spin += deg_to_rad(float(_ring_cfg.get("spin_deg_per_sec", 0.0))) * delta
		_ring_mat.set_shader_parameter(&"spin", _spin)


## World position just above the head (for damage numbers and markers).
func head_position(extra_m: float = 0.0) -> Vector3:
	var top := _base_height() + _height() * 0.5 + extra_m
	return global_position + Vector3(0.0, top, 0.0)


func set_ring(mode: StringName, color: Color) -> void:
	_ring.visible = mode != RING_NONE
	_ring_mat.set_shader_parameter(&"ring_color", color)


func ring_mode_visible() -> bool:
	return _ring.visible


## A small knock-back away from the camera's right, then back (no effect while KO'd), at the
## battle presentation speed `speed` (UiSettings.battle_speed, M2-UI-23).
func flinch(speed: float = 1.0) -> void:
	if _ko or _stone or not is_inside_tree():
		return
	var push := float(spec.get("recoil_m", 0.0))
	var sec := float(spec.get("recoil_sec", 0.0))
	var tw := create_tween().set_speed_scale(speed)
	tw.tween_property(_body, "position", _rest + Vector3(push * signf(-global_position.x), 0.0, 0.0), sec * 0.5)
	tw.tween_property(_body, "position", _rest, sec * 0.5)


## M2-CRE-03: a creature actor (CreatureActor, the enemies.json `model`) plays body clips; these are no-ops for
## a primitive or a hero actor. BattleActorMotion calls them.
func creature() -> CreatureActor:
	return _actor as CreatureActor


func play_action(skill_id: StringName, kind: StringName) -> bool:
	return creature() != null and creature().play_action(skill_id, kind)


func play_hit() -> bool:
	return creature() != null and creature().play_hit()


func enter_phase(phase_id: StringName) -> bool:
	return creature() != null and creature().enter_phase(phase_id)


func set_part_broken(skill_id: StringName, broken: bool) -> bool:
	return creature() != null and creature().set_part_broken(skill_id, broken)


## Petrify: the stand-in turns to matte stone (no glow) where it stands; it does not sink.
func set_stone(on: bool, stone_color: Color, stone_roughness: float) -> void:
	_stone = on
	if creature() != null:
		creature().set_frozen(on)
	if _actor != null:
		_set_actor_stone(on, stone_color, stone_roughness)
		return
	_body_mat.albedo_color = stone_color if on else _albedo
	_body_mat.roughness = stone_roughness if on else _roughness
	_body_mat.emission_enabled = spec.has("emission") and not on


func is_stone() -> bool:
	return _stone


func set_ko(ko: bool, sink_m: float, alpha: float) -> void:
	_ko = ko
	if creature() != null:  # it plays its own KO clip and fade, and does not sink
		creature().set_ko(ko, alpha)
		return
	# A model with a KO clip lies on the ground itself (M2-HER-1103): sinking it too puts it through the floor.
	var sink := sink_m if ko and not BattleClips.has_clip(self, BattleClips.KO) else 0.0
	_body.position = _rest - Vector3(0.0, sink, 0.0)
	_body.visible = not (ko and alpha <= 0.0)  # faded right out: hidden, so it casts no shadow either
	if _actor != null:
		for m in _surfaces:
			m.transparency = 1.0 - alpha if ko else 0.0
		return
	_body_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA if ko else BaseMaterial3D.TRANSPARENCY_DISABLED
	_body_mat.albedo_color.a = alpha if ko else 1.0


## Every actor surface takes one matte stone material (Petrify), and its own back when it ends.
func _set_actor_stone(on: bool, stone_color: Color, stone_roughness: float) -> void:
	if on and _stone_mat == null:
		_stone_mat = StandardMaterial3D.new()
	if on:
		_stone_mat.albedo_color = stone_color
		_stone_mat.roughness = stone_roughness
	for m in _surfaces:
		m.material_override = _stone_mat if on else null


func _height() -> float:
	return float(spec.get("height", 1.0))


func _radius() -> float:
	return float(spec.get("radius", 0.3))


func _base_height() -> float:
	return float(spec.get("hover", 0.0)) + _height() * 0.5


func _make_mesh() -> Mesh:
	match str(spec.get("shape", "capsule")):
		"box":
			var b := BoxMesh.new()
			b.size = Vector3(_radius() * 2.0, _height(), _radius() * 1.6)
			return b
		"cylinder":
			var c := CylinderMesh.new()
			c.top_radius = _radius() * 0.6
			c.bottom_radius = _radius()
			c.height = _height()
			return c
		"prism":
			var p := PrismMesh.new()
			p.size = Vector3(_radius() * 3.0, _height(), _radius() * 1.4)
			return p
	var cap := CapsuleMesh.new()
	cap.radius = _radius()
	cap.height = _height()
	return cap


func _build_ring() -> void:
	_ring = MeshInstance3D.new()
	var r := _radius() * float(_ring_cfg.get("radius_factor", 1.4))
	var soft := float(_ring_cfg.get("inner_soft_m", 0.25))
	var extent := r + soft
	var quad := PlaneMesh.new()
	quad.size = Vector2(extent * 2.0, extent * 2.0)
	_ring.mesh = quad
	_ring_mat = ShaderMaterial.new()
	_ring_mat.shader = RING_SHADER
	_ring_mat.set_shader_parameter(&"radius", r)
	_ring_mat.set_shader_parameter(&"extent", extent)
	_ring_mat.set_shader_parameter(&"line_width", float(_ring_cfg.get("line_width_m", 0.06)))
	_ring_mat.set_shader_parameter(&"inner_soft", soft)
	_ring_mat.set_shader_parameter(&"notches", float(_ring_cfg.get("notches", 6)))
	_ring_mat.render_priority = int(_ring_cfg.get("render_priority", 0))  # drawn over ground VFX (Pillar 4, M3-BPR-409)
	_ring.material_override = _ring_mat
	_ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_ring.position = Vector3(0.0, float(_ring_cfg.get("lift_m", 0.02)), 0.0)
	_ring.visible = false
	add_child(_ring)
