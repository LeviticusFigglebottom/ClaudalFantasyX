extends Node
## ADR 0041 placeholder audit, the runtime half (tools/placeholder_audit.py runs it and reads its JSON):
## `godot --headless --path . res://tools/placeholder/scan.tscn -- --out=<file.json>`.
## Loads every zone (locations.json, the test rooms excluded; the First Verse set) as the game loads it, again
## under each layout variant's flags and after each layout state's flag, and every battle arena an Act I encounter
## fights on (the Python half keeps the act it audits). Records what a player would see:
##   capsule    a visible StandIn mesh: a stage actor or NPC still drawn as its capsule (the actor's name)
##   greybox    a visible primitive mesh (box, capsule, cylinder, sphere, prism, torus) with a flat, untextured
##              material, or a visible CSG shape: greybox geometry (grouped by its top node under the zone)
##   named      a visible node whose name says placeholder, temp, greybox or proxy
## Then quits. One JSON object: {"items": [{"scene", "kind", "node", "group", "detail"}...], "scanned": [scene...]}.

const LOCATIONS := "res://game/data/world/locations.json"
const FIRST_PLAYABLE := "res://game/data/flow/first_playable.json"
const ARENAS := "res://game/data/battle/arenas.json"
const ENCOUNTERS := "res://game/data/battle/encounters.json"
const TEST_DIR := "res://game/levels/_tests/"
const CHAPTERS_DIR := "res://game/data/flow/chapters"
const REEFBALL_DIR := "res://game/data/reefball"
## Scenes a data file names that are part of the playable game: levels, and env-art's sets.
const SCENE_ROOTS: Array[String] = ["res://game/levels/", "res://assets/environments/"]
const STANDIN := "StandIn"
const PRIMITIVES: Array[String] = ["BoxMesh", "CapsuleMesh", "CylinderMesh", "SphereMesh", "PrismMesh", "TorusMesh"]
const NAME_RE := "(?i)(placeholder|(^|[_\\W])temp([_\\W]|$)|greybox|graybox|proxy)"

var items: Array[Dictionary] = []
## Every scene loaded, so the inventory can say what it covered.
var scanned: Array[String] = []
var _name_re := RegEx.new()


func _ready() -> void:
	_name_re.compile(NAME_RE)
	var out := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="):
			out = arg.trim_prefix("--out=")
	var state_was := Game.state
	for path in zone_scenes():
		_scan_zone(path)
	for path in arena_scenes():
		_scan_scene(path)
	Game.state = state_was
	var f := FileAccess.open(out, FileAccess.WRITE) if out != "" else null
	var text := JSON.stringify({"items": items, "scanned": scanned}, " ", true)
	if f != null:
		f.store_string(text)
		f.close()
	else:
		print(text)
	print("placeholder scan: %d items" % items.size())
	get_tree().quit(0)


## Every zone: each location scene but the test rooms, and the First Verse set (the Python half picks the act).
static func zone_scenes() -> Array[String]:
	var out: Array[String] = []
	for row: Variant in _json(LOCATIONS).get("locations", []):
		var p := str((row as Dictionary).get("scene", ""))
		if p != "" and not p.begins_with(TEST_DIR) and not out.has(p):
			out.append(p)
	_collect_scenes(_json(FIRST_PLAYABLE), out)
	# a chapter's `scene` steps (Ch7's Tidecup match), every act's: the Python half keeps the --act's chapters
	for file in DirAccess.get_files_at(CHAPTERS_DIR):
		if file.ends_with(".json"):
			_collect_scenes(_json(CHAPTERS_DIR.path_join(file)), out)
	for file in DirAccess.get_files_at(REEFBALL_DIR):  # the Tidecup's own arena
		if file.ends_with(".json"):
			_collect_scenes(_json(REEFBALL_DIR.path_join(file)), out)
	return out


## Every encounter's arena (an encounter with no arena fights on the sandbox's own; the Python half
## reports those).
static func arena_scenes() -> Array[String]:
	var scenes := ((_json(ARENAS).get("arenas", {}) as Dictionary).get("scenes", {})) as Dictionary
	var out: Array[String] = []
	for enc: Variant in _json(ENCOUNTERS).get("encounters", []):
		var id := str((enc as Dictionary).get("arena", ""))
		var p := str(scenes.get(id, ""))
		if p != "" and not out.has(p):
			out.append(p)
	return out


static func _collect_scenes(v: Variant, out: Array[String]) -> void:
	if v is Dictionary:
		for k: Variant in v:
			_collect_scenes(v[k], out)
	elif v is Array:
		for x: Variant in v:
			_collect_scenes(x, out)
	elif v is String:
		var s := v as String
		var rooted := SCENE_ROOTS.any(func(r: String) -> bool: return s.begins_with(r))
		if rooted and s.ends_with(".tscn") and not s.begins_with(TEST_DIR) and not s.contains("/shots/"):
			if not out.has(s):
				out.append(s)


func _scan_zone(path: String) -> void:
	scanned.append(path)
	if not ResourceLoader.exists(path):
		_add(path, "missing", "", "", "the scene file does not exist")
		return
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	var zone := (load(path) as PackedScene).instantiate()
	if "autoplay" in zone:
		zone.set(&"autoplay", false)
	var story := zone.get(&"story") as ZoneStory if "story" in zone else null
	if story != null:
		story.autostart = false
	add_child(zone)
	_walk(path, zone, "")
	if zone.has_method(&"apply_variant") and "layout" in zone:
		for row: Variant in (zone.get(&"layout") as Dictionary).get("variants", []):
			var flags: Array = ((row as Dictionary).get("when", {}) as Dictionary).get("set", [])
			if flags.is_empty():
				continue
			Game.state = GameStateData.new()
			Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
			for flag: Variant in flags:
				Game.set_flag(StringName(str(flag)))
			zone.call(&"apply_variant")
			_walk(path, zone, "variant " + ",".join(flags))
	_scan_states(path, zone)
	zone.free()


## The zone as each layout "states" row shows it (Ch4/Ch6/Ch8 zones' refresh_states: a flag shows or hides stage
## actors), the flags set in story order as a playthrough sets them: Ch6's Sefir stands on the reed bank only once
## the Inquisitor has yielded.
func _scan_states(path: String, zone: Node) -> void:
	if not zone.has_method(&"refresh_states") or not "layout" in zone:
		return
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	for row: Variant in (zone.get(&"layout") as Dictionary).get("states", []):
		var flag := str((row as Dictionary).get("flag", "")) if row is Dictionary else ""
		if flag == "":
			continue
		Game.set_flag(StringName(flag))
		zone.call(&"refresh_states")
		_walk(path, zone, "state " + flag)


func _scan_scene(path: String) -> void:
	scanned.append(path)
	if not ResourceLoader.exists(path):
		_add(path, "missing", "", "", "the scene file does not exist")
		return
	var scene := (load(path) as PackedScene).instantiate()
	add_child(scene)
	_walk(path, scene, "")
	scene.free()


func _walk(path: String, root: Node, when: String) -> void:
	for n in root.find_children("*", "GeometryInstance3D", true, false):
		var g := n as GeometryInstance3D
		if not g.is_visible_in_tree():
			continue
		var group := _group(root, g)
		var detail := when
		if g.name == STANDIN:
			_add(path, "capsule", String(root.get_path_to(g.get_parent())), String(g.get_parent().name), detail)
		elif g is CSGShape3D:
			_add(path, "greybox", String(root.get_path_to(g)), group, _join(detail, g.get_class()))
		elif g is MeshInstance3D and _flat_primitive(g as MeshInstance3D):
			_add(
				path,
				"greybox",
				String(root.get_path_to(g)),
				group,
				_join(detail, (g as MeshInstance3D).mesh.get_class())
			)
		elif _name_re.search(String(g.name)) != null:
			_add(path, "named", String(root.get_path_to(g)), group, detail)


## A primitive mesh drawn with a flat colour (no texture, no shader): greybox. A primitive with a shader or a
## texture is deliberate (a water plane, a VFX card) and not counted.
static func _flat_primitive(m: MeshInstance3D) -> bool:
	if m.mesh == null or not PRIMITIVES.has(m.mesh.get_class()):
		return false
	var mat := m.get_active_material(0)
	if mat == null:
		return true
	if mat is ShaderMaterial:
		return false
	var std := mat as BaseMaterial3D
	return std != null and std.albedo_texture == null


## The node's top-level ancestor under the root: the block, prop or actor it belongs to.
static func _group(root: Node, n: Node) -> String:
	var at := n
	while at.get_parent() != null and at.get_parent() != root:
		at = at.get_parent()
	return String(at.name)


static func _join(a: String, b: String) -> String:
	return b if a == "" else "%s; %s" % [a, b]


func _add(scene: String, kind: String, node: String, group: String, detail: String) -> void:
	items.append({"scene": scene, "kind": kind, "node": node, "group": group, "detail": detail})


static func _json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}
