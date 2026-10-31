class_name BattleBossLight
extends RefCounted
## The PC's GPU QA row 61 (passes 5, 7 and the big38 sign-off): at its rest frame the Undertow's Reach was a dark mass
## against the night sky, and framing alone could not make it read. A boss with an effects.json boss_rim_lights row
## gets its lights: OmniLight3Ds placed along the lens-to-boss line from its body's centre (behind_m: a rim behind it,
## or on the lens's side for a key), up_m higher, in a light_color palette swatch, at energy over range_m, no shadows.
## They are children of the boss's stand-in, so they move and go with the boss. Used by BattleStage at spawn and by
## the arena previews.

const NODE_NAME := &"BossRimLight"


## Lights `f` (enemy `enemy_id`, its base id) for the lens at `cam_pos` (global): one OmniLight3D per entry of its
## row's `lights` (behind_m < 0 stands on the lens's side: a key light). Returns them; none when the enemy has no row.
static func apply(f: Node3D, enemy_id: StringName, cam_pos: Vector3) -> Array[OmniLight3D]:
	var out: Array[OmniLight3D] = []
	var row := (BattleVfx.load_data().get("boss_rim_lights", {}) as Dictionary).get(String(enemy_id), {}) as Dictionary
	if row.is_empty() or f == null or not f.is_inside_tree():
		return out
	for n in f.get_children():
		if String(n.name).begins_with(NODE_NAME):
			n.free()
	var centre := _body_centre(f)  # a colossus's body is metres over its stand-in's head (the Reach's arm)
	var away := Vector3(centre.x - cam_pos.x, 0.0, centre.z - cam_pos.z)
	away = away.normalized() if away.length() > 0.01 else Vector3.FORWARD
	for l: Dictionary in row.get("lights", []):
		var light := OmniLight3D.new()
		light.name = "%s%d" % [NODE_NAME, out.size()]
		light.light_color = Color(str(l.get("color", "#FFFFFF")))
		light.light_energy = float(l.get("energy", 1.0))
		light.omni_range = float(l.get("range_m", 10.0))
		light.shadow_enabled = false
		f.add_child(light)
		light.global_position = centre + away * float(l.get("behind_m", 0.0)) + Vector3.UP * float(l.get("up_m", 0.0))
		out.append(light)
	return out


## The centre of `f`'s visible meshes (global), else its position.
static func _body_centre(f: Node3D) -> Vector3:
	var box := AABB()
	var first := true
	for n in f.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null or not mi.is_visible_in_tree():
			continue
		var b := mi.global_transform * mi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return f.global_position if first else box.get_center()
