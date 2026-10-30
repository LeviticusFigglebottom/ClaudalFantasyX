class_name FieldShore
extends RefCounted
## Keeps the field hero on walkable ground at the water's edge (the human's playtest: on Oruvel's dock town after the
## underwater sequence you could step off a deck and walk around in the sea). Tuning: field_movement.json "shore".
##
## A step is refused (the hero stays where he stood, as at a wall) when the ground it lands over is under a zone
## WaterSurface and either
##   - it drops more than edge_drop_m from the ground he stood on (stepping off a dock, a pier or a hull's edge), or
##   - it lies more than deep_water_m under the surface and deeper than where he stood (wading out too deep; walking
##     back out of water is always allowed, so a spawn in the shallows never traps him).
## A safety catch: grounded more than deep_water_m under water anyway (a fall, a push), he is put back on the last
## spot he stood on dry or shallow ground. Zones with no WaterSurface are never touched, and a hero already more
## than underwater_m under the surface walks the seabed (Oruvel's underway) with no shore rule at all.

var cfg: Dictionary = {}
var last_safe := Vector3(NAN, NAN, NAN)
var _waters: Array[WaterSurface] = []
var _read := false


func _init(movement_data: Dictionary) -> void:
	cfg = movement_data.get("shore", {}) as Dictionary


func enabled() -> bool:
	return bool(cfg.get("enabled", false))


## The ground height under `at` (a ray from probe_up_m above down probe_down_m), or NAN when there is none.
func ground_y(body: CharacterBody3D, at: Vector3) -> float:
	var space := body.get_world_3d().direct_space_state if body.is_inside_tree() else null
	if space == null:
		return NAN
	var q := PhysicsRayQueryParameters3D.create(
		at + Vector3.UP * float(cfg.get("probe_up_m", 0.0)), at + Vector3.DOWN * float(cfg.get("probe_down_m", 0.0))
	)
	q.exclude = [body.get_rid()]
	q.collide_with_areas = false
	var hit := space.intersect_ray(q)
	return (hit["position"] as Vector3).y if not hit.is_empty() else NAN


## The rest level of the zone's water over `at` (the highest WaterSurface covering it), or NAN when none does.
func water_y(body: Node, at: Vector3) -> float:
	if not _read:
		_read = true
		var root := body.get_tree().current_scene if body.is_inside_tree() else null
		var base: Node = root if root != null and root.is_ancestor_of(body) else body.get_parent()
		for n in base.find_children("*", "Node3D", true, false) if base != null else []:
			if n is WaterSurface:
				_waters.append(n as WaterSurface)
	var best := NAN
	for w in _waters:
		if not is_instance_valid(w) or not w.is_visible_in_tree() or not covers(w, at):
			continue
		best = w.global_position.y if is_nan(best) else maxf(best, w.global_position.y)
	return best


## True when `w` lies over `at` (flat): a surface that follows the camera, or has no mesh, covers the whole zone.
static func covers(w: WaterSurface, at: Vector3) -> bool:
	if w.follow_target != null or w.surface_mesh == null:
		return true
	var box := w.global_transform * w.surface_mesh.get_aabb()
	return at.x >= box.position.x and at.x <= box.end.x and at.z >= box.position.z and at.z <= box.end.z


## True when a step from `from` to `to` must be refused (see the class comment).
func refuses(body: CharacterBody3D, from: Vector3, to: Vector3) -> bool:
	var water := water_y(body, to)
	if is_nan(water):
		return false
	var new_ground := ground_y(body, to)
	if is_nan(new_ground):
		return false  # no ground found (the ray began inside a terrain collider): not evidence of water
	var under := water - new_ground
	if under <= float(cfg.get("wade_m", 0.0)):
		return false
	var old_ground := ground_y(body, from)
	var old_under := water - old_ground if not is_nan(old_ground) else INF
	if old_under > float(cfg.get("underwater_m", INF)):
		return false  # he walks the seabed (Oruvel's underway): no shore to keep to down there
	if not is_nan(old_ground) and old_ground - new_ground > float(cfg.get("edge_drop_m", INF)):
		return true
	return under > float(cfg.get("deep_water_m", INF)) and under > old_under + 1e-4


## After a step: remembers a safe spot, or returns him to the last one when he stands in deep water anyway. Returns
## true when it moved him.
func settle(body: CharacterBody3D, grounded: bool) -> bool:
	if not grounded:
		return false
	var at := body.global_position
	var water := water_y(body, at)
	var under := water - at.y if not is_nan(water) else -INF
	if under <= float(cfg.get("deep_water_m", INF)):
		last_safe = at
		return false
	if is_nan(last_safe.x):
		return false
	body.global_position = last_safe
	body.velocity = Vector3.ZERO
	return true
