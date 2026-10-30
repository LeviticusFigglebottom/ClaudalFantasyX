class_name DockProbe
extends Node
## Human playtest check (b), 2026-10-30 (cloud QA pass 6): Oruvel's moorings, as played.
##   godot --headless --path . --audio-driver Dummy res://tools/gpu_bench/dock_probe.tscn -- --out=/abs/dir \
##     [--location=ch01/oruvel --chapter=ch01 --spawn=ScaleHull --step=2.0]
## 1. Every mesh's world AABB (MeshInstance3D, and each MultiMesh instance) goes to <out>/meshes.json: the
##    boat-vs-dock overlap check is done on it offline (tools/gpu_bench/dock_overlaps.py).
## 2. Every walkable deck collider (a box whose top is near deck height) has its four edges walked: the hero is put
##    INSET_M inside the edge every --step metres and the field controller's stick drives him straight out for
##    PUSH_S seconds at a run. Where he ends is recorded: on a deck (a floor at deck height under him), in the
##    water (below WATER_Y) or still falling. <out>/edges.json; one DOCK_EDGE line per edge.

const CHAPTER_SELECT := "res://game/data/debug/chapter_select.json"
const DECK_TOP_MIN := -0.7
const DECK_TOP_MAX := 0.9
const MIN_EDGE_M := 0.8
const INSET_M := 0.7
const PUSH_S := 1.6
const WATER_Y := -0.45
const TIME_SCALE := 3.0
const RAY_UP := 2.0
const RAY_DOWN := 6.0

var _opts: Dictionary = {}


func _ready() -> void:
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := DockProbe.new()
		driver.name = "DockProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_opts[kv[0]] = kv[1] if kv.size() > 1 else "true"
	var out_dir := str(_opts.get("out", "user://dock_probe"))
	DirAccess.make_dir_recursive_absolute(out_dir)
	var saves := get_tree().root.get_node_or_null(^"SaveSystem")
	if saves != null and saves.has_method(&"hold_autosave"):
		saves.call(&"hold_autosave", self)
	for start: Dictionary in DebugReadouts.chapter_starts(CHAPTER_SELECT):
		if str(start["id"]) == str(_opts.get("chapter", "ch01")):
			DebugReadouts.apply_chapter_start(start)
	var router := get_tree().root.get_node(^"SceneRouter")
	FlowRouting.go_to(StringName(str(_opts.get("location", "ch01/oruvel"))), StringName(str(_opts.get("spawn", ""))))
	var t := Time.get_ticks_msec()
	while (_player() == null or bool(router.call(&"is_busy"))) and Time.get_ticks_msec() - t < 60000:
		await get_tree().process_frame
	await get_tree().create_timer(2.0).timeout
	var zone := get_tree().current_scene
	_write(out_dir.path_join("meshes.json"), _meshes(zone))
	var edges := await _walk_edges(zone)
	_write(out_dir.path_join("edges.json"), edges)
	get_tree().quit()


func _meshes(root: Node) -> Array:
	var out: Array = []
	for n in root.find_children("*", "GeometryInstance3D", true, false):
		var gi := n as GeometryInstance3D
		if not gi.is_visible_in_tree():
			continue
		var path := str(root.get_path_to(gi))
		if gi is MeshInstance3D and (gi as MeshInstance3D).mesh != null:
			var mi := gi as MeshInstance3D
			out.append(
				{"path": path, "mesh": mi.mesh.resource_path, "aabb": _aabb(mi.global_transform * mi.get_aabb())}
			)
		elif gi is MultiMeshInstance3D and (gi as MultiMeshInstance3D).multimesh != null:
			var mm := (gi as MultiMeshInstance3D).multimesh
			if mm.mesh == null:
				continue
			for i in mm.instance_count:
				var xf := gi.global_transform * mm.get_instance_transform(i)
				out.append(
					{"path": "%s#%d" % [path, i], "mesh": mm.mesh.resource_path, "aabb": _aabb(xf * mm.mesh.get_aabb())}
				)
	return out


static func _aabb(b: AABB) -> Array:
	return [b.position.x, b.position.y, b.position.z, b.end.x, b.end.y, b.end.z]


## The deck colliders: box shapes on static bodies whose top is near deck height.
func _decks(root: Node) -> Array:
	var out: Array = []
	for n in root.find_children("*", "CollisionShape3D", true, false):
		var cs := n as CollisionShape3D
		if cs.disabled or not (cs.shape is BoxShape3D) or not (cs.get_parent() is StaticBody3D):
			continue
		var size := (cs.shape as BoxShape3D).size
		var xf := cs.global_transform
		var top := (xf * Vector3(0, size.y * 0.5, 0)).y
		if top < DECK_TOP_MIN or top > DECK_TOP_MAX:
			continue
		out.append({"path": str(root.get_path_to(cs)), "xf": xf, "size": size, "top": top})
	return out


func _walk_edges(root: Node) -> Array:
	var p := _player()
	var results: Array = []
	if p == null:
		return results
	p.motor.latch_on_cut = false
	p.motor.latch_on_blend = false
	p.accepts_input = true
	var step_m := float(_opts.get("step", 2.0))
	Engine.time_scale = TIME_SCALE
	var scene := get_tree().current_scene
	for d: Dictionary in _decks(root):
		var xf: Transform3D = d["xf"]
		var size: Vector3 = d["size"]
		var hx := size.x * 0.5
		var hz := size.z * 0.5
		# [edge name, local outward normal, local edge start, local edge end]
		var sides := [
			["+x", Vector3(1, 0, 0), Vector3(hx, 0, -hz), Vector3(hx, 0, hz)],
			["-x", Vector3(-1, 0, 0), Vector3(-hx, 0, -hz), Vector3(-hx, 0, hz)],
			["+z", Vector3(0, 0, 1), Vector3(-hx, 0, hz), Vector3(hx, 0, hz)],
			["-z", Vector3(0, 0, -1), Vector3(-hx, 0, -hz), Vector3(hx, 0, -hz)],
		]
		for s: Array in sides:
			var a: Vector3 = s[2]
			var b: Vector3 = s[3]
			var length := a.distance_to(b)
			if length < MIN_EDGE_M:
				continue
			var n := int(maxf(1.0, floor(length / step_m)))
			var normal_w := (xf.basis * (s[1] as Vector3)).normalized()
			normal_w.y = 0.0
			normal_w = normal_w.normalized()
			var samples: Array = []
			for k in n:
				var f := (k + 0.5) / float(n)
				var local := a.lerp(b, f) - (s[1] as Vector3) * INSET_M
				local.y = size.y * 0.5
				var start := xf * local
				var r := await _push(p, start + Vector3(0, 0.05, 0), normal_w)
				if get_tree().current_scene != scene:
					results.append({"error": "scene changed during the walk", "at": d["path"]})
					Engine.time_scale = 1.0
					return results
				samples.append(r)
			var off := samples.filter(func(r: Dictionary) -> bool: return r["end"] != "deck")
			results.append({"deck": d["path"], "edge": s[0], "top": d["top"], "samples": samples, "off": off.size()})
			print("DOCK_EDGE %s %s samples %d off %d" % [d["path"], s[0], samples.size(), off.size()])
	Engine.time_scale = 1.0
	return results


func _push(p: FieldController, start: Vector3, dir: Vector3) -> Dictionary:
	p.velocity = Vector3.ZERO
	p.global_position = start
	p.motor.velocity = Vector3.ZERO
	await get_tree().physics_frame
	await _hold(p, dir, PUSH_S)
	var end := p.global_position
	var floor_y := _floor_under(end)
	var where := "deck"
	if end.y < WATER_Y:
		where = "water"
	elif is_nan(floor_y) or floor_y < DECK_TOP_MIN:
		where = "falling"
	# Off the deck: can he climb back? Run straight back the way he came.
	var back := ""
	if where != "deck":
		await _hold(p, -dir, PUSH_S * 2.0)
		back = "climbs back" if p.global_position.y > WATER_Y else "stuck below the deck"
	return {
		"back": back,
		"start": [snappedf(start.x, 0.01), snappedf(start.z, 0.01)],
		"end_pos": [snappedf(end.x, 0.01), snappedf(end.y, 0.01), snappedf(end.z, 0.01)],
		"moved": snappedf(Vector2(end.x - start.x, end.z - start.z).length(), 0.01),
		"end": where,
	}


## Holds the stick toward world direction `dir` for `secs` (game time), then lets go.
func _hold(p: FieldController, dir: Vector3, secs: float) -> void:
	var t := 0.0
	while t < secs:
		var yaw := p.director.camera_yaw() if p.director != null else 0.0
		var local := Basis(Vector3.UP, -yaw) * dir
		# Input.get_vector convention: x right, y back. Stick up (-y) = camera forward (-z).
		p.input_override = Vector2(local.x, local.z).normalized()
		await get_tree().physics_frame
		t += get_physics_process_delta_time()  # already scaled by Engine.time_scale
	p.input_override = Vector2(NAN, NAN)
	await get_tree().physics_frame


func _floor_under(at: Vector3) -> float:
	var space := (get_tree().current_scene as Node3D).get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(at + Vector3.UP * RAY_UP, at + Vector3.DOWN * RAY_DOWN)
	var p := _player()
	if p != null:
		q.exclude = [p.get_rid()]
	var hit := space.intersect_ray(q)
	return (hit["position"] as Vector3).y if not hit.is_empty() else NAN


func _player() -> FieldController:
	var cur := get_tree().current_scene
	if cur == null:
		return null
	if cur.get(&"player") is FieldController:
		return cur.get(&"player") as FieldController
	var found := cur.find_children("*", "FieldController", true, false)
	return found[0] as FieldController if not found.is_empty() else null


func _write(path: String, data: Variant) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify(data, " "))
	f.close()
	print("DOCK_PROBE wrote %s" % path)
