class_name CreatureFraming
extends RefCounted
## Camera framing shared by the creature review stage and CreaturePortrait (M2-CRE-09/10): a camera at a yaw and
## pitch around a creature's bounds, far enough that the bounds' sphere (times `margin`) fills the vertical FOV.


## World bounds of every visible MeshInstance3D under `nodes` (skinned meshes at their rest bounds), skipping
## nodes named in `skip`.
static func bounds(nodes: Array, skip: PackedStringArray = []) -> AABB:
	var box := AABB()
	var first := true
	for n: Variant in nodes:
		if not n is Node:
			continue
		var list: Array = (n as Node).find_children("*", "MeshInstance3D", true, false)
		if n is MeshInstance3D:
			list.append(n)
		for m: MeshInstance3D in list:
			if m.mesh == null or not m.is_visible_in_tree() or skip.has(String(m.name)):
				continue
			var b := m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
	return box


## Places `camera` looking at `box`'s centre from `yaw_deg` (0 = from +Z) and `pitch_deg` above, with `fov_deg`.
static func frame(camera: Camera3D, box: AABB, yaw_deg: float, pitch_deg: float, fov_deg: float, margin: float) -> void:
	var c := box.get_center()
	var radius := box.size.length() * 0.5 * margin
	camera.fov = fov_deg
	var dist := radius / sin(deg_to_rad(fov_deg * 0.5))
	var yaw := deg_to_rad(yaw_deg)
	var pitch := deg_to_rad(pitch_deg)
	var dir := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
	camera.position = c + dir * dist
	camera.look_at(c, Vector3.UP)


## Like frame(), but the distance fits every corner of `box` inside the view (vertical FOV `fov_deg`, `aspect`
## width over height), times `margin`: tall and wide creatures fill the frame alike (CreaturePortrait).
static func frame_fit(
	camera: Camera3D, box: AABB, yaw_deg: float, pitch_deg: float, fov_deg: float, margin: float, aspect: float = 1.0
) -> void:
	var c := box.get_center()
	var yaw := deg_to_rad(yaw_deg)
	var pitch := deg_to_rad(pitch_deg)
	var back := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
	var right := Vector3.UP.cross(back).normalized()
	var up := back.cross(right)
	var tv := tan(deg_to_rad(fov_deg * 0.5))
	var th := tv * aspect
	var dist := 0.0
	for i in 8:
		var p := box.get_endpoint(i) - c
		var z := p.dot(back)
		dist = maxf(dist, z + absf(p.dot(up)) * margin / tv)
		dist = maxf(dist, z + absf(p.dot(right)) * margin / th)
	camera.fov = fov_deg
	camera.position = c + back * dist
	camera.look_at(c, Vector3.UP)


## Holds `clip` at `time` on the creature's AnimationPlayer (paused), so a still is the same every run.
static func hold(actor: Node, clip: StringName, time: float) -> bool:
	var players := actor.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		return false
	var p := players[0] as AnimationPlayer
	if not p.has_animation(clip):
		return false
	p.play(clip, 0.0)
	p.seek(time, true)
	p.pause()
	return true
