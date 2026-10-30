extends SceneTree
## The zone life audit (creatures, 2026-10-29: the Act I final-quality audit). Loads each Act I zone that has villagers
## (game/data/world/npc/zones/) or wildlife (game/data/world/wildlife/) as the game does, lets it run RUN_FRAMES, and
## reports:
##   villagers  every FieldNpc in the zone: its AnimationPlayer playing a clip, and its pose moving over the run (a
##              frozen villager: no player, nothing playing, or a still skeleton);
##   wildlife   the zone's WildlifeLayer: built, and its animals' instance buffers changing over the run.
## godot --headless --path . -s tools/creatures/life_audit.gd [-- zone_id ...]

const NPC_DIR := "res://game/data/world/npc/zones/"
const WILDLIFE_DIR := "res://game/data/world/wildlife/"
const LOCATIONS := "res://game/data/world/locations.json"
const RUN_FRAMES := 90
const STILL_M := 0.0005


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var scenes := {}
	var locs: Variant = JSON.parse_string(FileAccess.get_file_as_string(LOCATIONS))
	for l: Dictionary in locs if locs is Array else (locs as Dictionary).get("locations", []):
		scenes[str(l.get("id", ""))] = str(l.get("scene", ""))
	var zones := {}
	for dir: String in [NPC_DIR, WILDLIFE_DIR]:
		for f: String in DirAccess.get_files_at(dir):
			if not f.ends_with(".json"):
				continue
			var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(dir + f))
			var zone := str(data.get("zone", "")) if data is Dictionary else ""
			if zone.begins_with("ch0"):  # Act I (Ch1-Ch9)
				zones[zone] = true
	var wanted := Array(OS.get_cmdline_user_args())
	var ids := zones.keys()
	ids.sort()
	for zone: String in ids:
		if not wanted.is_empty() and not wanted.has(zone):
			continue
		var path := str(scenes.get(zone, ""))
		if path == "" or not ResourceLoader.exists(path):
			print("%s: no scene" % zone)
			continue
		await _audit(zone, path)
	quit()


func _audit(zone: String, path: String) -> void:
	var node := (load(path) as PackedScene).instantiate() as Node3D
	root.add_child(node)
	await process_frame
	var npcs: Array[FieldNpc] = []
	for n: Node in node.find_children("*", "FieldNpc", true, false):
		npcs.append(n as FieldNpc)
	var before := _poses(npcs)
	var layers := node.find_children("*", "WildlifeLayer", true, false)
	var wild_before := _wild(layers)
	for i in RUN_FRAMES:
		await process_frame
	var after := _poses(npcs)
	var wild_after := _wild(layers)
	var frozen: Array[String] = []
	for i in npcs.size():
		var npc := npcs[i]
		if not npc.is_visible_in_tree():
			continue  # a villager this story state keeps hidden (gone home, not yet arrived)
		var anim := npc.anim
		if anim == null or not anim.is_playing() or anim.current_animation == "":
			frozen.append("%s (no clip playing)" % npc.name)
		elif before[i].distance_to(after[i]) < STILL_M:
			frozen.append("%s (pose still on %s)" % [npc.name, anim.current_animation])
	var wild := "no wildlife layer"
	if not layers.is_empty():
		wild = "wildlife moving" if wild_before != wild_after else "WILDLIFE STILL"
	print(
		(
			"%-34s villagers %2d, frozen %d%s; %s"
			% [zone, npcs.size(), frozen.size(), (": " + ", ".join(frozen)) if not frozen.is_empty() else "", wild]
		)
	)
	node.get_parent().remove_child(node)
	node.free()


## Each villager's head bone (or its actor's origin) in world space: a breathing, glancing villager moves it.
func _poses(npcs: Array[FieldNpc]) -> PackedVector3Array:
	var out := PackedVector3Array()
	for npc in npcs:
		var p := npc.global_position
		var skel := HeroMotion.skeleton_of(npc.actor) if npc.actor != null else null
		if skel != null:
			var b := skel.find_bone("DEF-spine.006")
			b = b if b >= 0 else skel.get_bone_count() - 1
			p = skel.global_transform * skel.get_bone_global_pose(b).origin
		out.append(p)
	return out


func _wild(layers: Array) -> int:
	var h := 0
	for l: Node in layers:
		for mm: MultiMeshInstance3D in l.find_children("*", "MultiMeshInstance3D", true, false):
			if mm.multimesh != null and mm.multimesh.instance_count > 0:
				h = hash([h, mm.multimesh.buffer])
	return h
