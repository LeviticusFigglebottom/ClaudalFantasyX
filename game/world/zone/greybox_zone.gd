class_name GreyboxZone
extends Node3D
## A playable greybox zone built from a layout file (M3-ARC-01; docs/kb/tech/chapter_flow.md). A zone
## scene is only this root with `location_id` and `layout_path`; everything else is built from data:
##   the player (a FieldController stand-in), the field camera and its director (a hub orbit), a
##   CutsceneStage (Shots, Actors, Marks), the ZoneStory that plays the chapter data, a sun and an
##   environment, the greybox blocks (solid ones collide; "emission" makes one glow), Spawns/
##   markers, the triggers and interactables (Interactable areas that carry the story payloads),
##   camera volumes with their rails (fixed, pan_follow or dolly shots; M2-FP-25) and the field
##   encounters (FieldEncounters, with its "Encounter" return spawn).
## Defaults (sizes, colours, the camera) come from game/data/world/greybox_defaults.json; the layout
## overrides any of them. Env-art's kit swaps in later by replacing the blocks, not the story.
##
## The build runs once, when the scene is instantiated (off the tree, as SceneRouter does on its
## loader thread), or on entering the tree for a zone made with new() (tests call build() first).

const DEFAULTS_PATH := "res://game/data/world/greybox_defaults.json"
const SPAWNS := &"Spawns"
const GREYBOX := &"Greybox"
const TRIGGERS := &"Triggers"
const ACTIVATION_TOUCH := "touch"
const RAILS := &"Rails"
const VOLUMES := &"CameraVolumes"
const SHOT_MODES := {
	"fixed": CameraShot.Mode.FIXED, "pan_follow": CameraShot.Mode.PAN_FOLLOW, "dolly": CameraShot.Mode.DOLLY
}

## The location this zone is in locations.json; ZoneStory reads its block of the chapter data by it.
@export var location_id: StringName = &""
## The layout file (blocks, spawns, marks, actors, shots, triggers).
@export_file("*.json") var layout_path: String = ""
## Overrides the chapter file ZoneStory reads (tests point it at a fixture). Empty = the registry's.
@export_file("*.json") var chapter_path: String = ""

var player: FieldController
var director: FieldCameraDirector
var field_camera: Camera3D
var stage: CutsceneStage
var story: ZoneStory
var sun: DirectionalLight3D
## The final zone scene a layout's "dressing" instanced (M2-FP-108); null for a pure greybox.
var dressing: Node3D
var encounters: FieldEncounters
var layout: Dictionary = {}
var defaults: Dictionary = {}

var _built := false


func _notification(what: int) -> void:
	if what == NOTIFICATION_SCENE_INSTANTIATED:
		build()


func _enter_tree() -> void:
	build()


## Builds the zone from its layout (once).
func build() -> void:
	if _built:
		return
	_built = true
	defaults = read_json(DEFAULTS_PATH)
	layout = read_json(layout_path) if layout_path != "" else {}
	_build_dressing()
	_build_lighting()
	_build_blocks()
	var spawns: Dictionary = (layout.get("spawns", {}) as Dictionary).duplicate()
	if layout.has("encounters"):
		spawns[String(FieldEncounters.RETURN_SPAWN)] = [0, 0, 0, 0]
	_build_markers(SPAWNS, spawns)
	_build_player()
	_build_stage()
	_build_wildlife()
	_build_triggers()
	_build_camera_volumes()
	story = ZoneStory.new()
	story.name = "ZoneStory"
	add_child(story)
	if layout.has("encounters"):
		encounters = FieldEncounters.new()
		encounters.name = "Encounters"
		add_child(encounters)


func _ready() -> void:
	_build_villagers()
	if encounters != null:
		encounters.setup(self, layout.get("encounters", {}), defaults.get("encounters", {}))


## Moves the player to Spawns/<spawn> facing `yaw_deg` and snaps the camera. The "Encounter" spawn
## is where the last field encounter here left Rhen (FieldEncounters.return_points).
func place_at(spawn: StringName, yaw_deg: float = 0.0) -> bool:
	var marker := spawn_marker(spawn)
	if marker == null:
		push_warning("GreyboxZone %s: no spawn '%s'" % [location_id, spawn])
		return false
	player.position = marker.position
	if spawn == FieldEncounters.RETURN_SPAWN and FieldEncounters.return_points.has(String(location_id)):
		player.position = FieldEncounters.return_points[String(location_id)]
	player.rotation.y = deg_to_rad(yaw_deg)
	player.velocity = Vector3.ZERO
	if encounters != null:
		encounters.reanchor()  # the jump to a spawn is never walking (M2-FP-28)
	if player.motor != null:
		player.motor.facing_yaw = player.rotation.y
	if director.is_inside_tree():
		director.snap()
	return true


func spawn_marker(spawn: StringName) -> Marker3D:
	return get_node_or_null(NodePath("%s/%s" % [SPAWNS, spawn])) as Marker3D


func spawn_yaw_deg(spawn: StringName) -> float:
	var marker := spawn_marker(spawn)
	return rad_to_deg(marker.rotation.y) if marker != null else 0.0


func spawn_names() -> Array[StringName]:
	var out: Array[StringName] = []
	for m in get_node(NodePath(String(SPAWNS))).get_children():
		out.append(StringName(m.name))
	return out


## Shows or hides a stage actor (story steps `{"zone": "show_actor", "args": [id, bool]}`).
func show_actor(id: String, shown: bool) -> void:
	var a := stage.actor(StringName(id))
	if a != null and not a is FieldController:
		a.visible = shown


## The layout value `key`, else the default's.
func setting(key: String) -> Variant:
	return layout.get(key, defaults.get(key))


static func read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("GreyboxZone: no file %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("GreyboxZone: %s is not a JSON object" % path)
		return {}
	return parsed as Dictionary


## M2-FP-108: a layout "dressing" {scene, adopt} instances a final zone scene (env-art's route: its own sky,
## sun and sea) and dresses it here, off the tree, through the adopt script's static adopt(dresser), whose
## dresser then skips dressing again in _ready. The greybox lighting is not built over it.
func _build_dressing() -> void:
	var spec: Dictionary = layout.get("dressing", {})
	var packed := load(str(spec.get("scene", ""))) as PackedScene if spec.has("scene") else null
	if packed == null:
		return
	dressing = packed.instantiate() as Node3D
	dressing.name = "Dressing"
	add_child(dressing)
	var dresser := dressing.get_node_or_null(^"Dresser")
	var adopt := load(str(spec.get("adopt", ""))) as Script if spec.has("adopt") else null
	if dresser != null and adopt != null:
		var adopted: Node = adopt.call(&"adopt", dresser)
		adopted.call(&"dress")
	sun = dressing.get_node_or_null(^"Sun") as DirectionalLight3D


func _build_lighting() -> void:
	if dressing != null:
		return
	var s: Dictionary = _merged("sun")
	sun = DirectionalLight3D.new()
	sun.name = "Sun"
	sun.rotation_degrees = Vector3(float(s.get("pitch_deg", 0.0)), float(s.get("yaw_deg", 0.0)), 0.0)
	sun.light_energy = float(s.get("energy", 1.0))
	sun.light_color = Color.html(str(s.get("color", "#ffffff")))
	sun.shadow_enabled = true
	add_child(sun)
	var e: Dictionary = _merged("environment")
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color.html(str(e.get("background", "#000000")))
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.html(str(e.get("ambient_color", "#ffffff")))
	env.ambient_light_energy = float(e.get("ambient_energy", 1.0))
	var we := WorldEnvironment.new()
	we.name = "WorldEnvironment"
	we.environment = env
	add_child(we)


func _build_blocks() -> void:
	var root := Node3D.new()
	root.name = String(GREYBOX)
	add_child(root)
	var mats: Dictionary = {}
	for b: Dictionary in layout.get("blocks", []):
		var size := _vec3(b.get("size", [1, 1, 1]))
		var color := str(b.get("color", setting("block_color")))
		var glow := str(b.get("emission", ""))
		var mat_key := color + glow + str(b.get("emission_energy", ""))
		if not mats.has(mat_key):
			var m := StandardMaterial3D.new()
			m.albedo_color = Color.html(color)
			if glow != "":
				m.emission_enabled = true
				m.emission = Color.html(glow)
				m.emission_energy_multiplier = float(b.get("emission_energy", 1.0))
			mats[mat_key] = m
		var mesh := BoxMesh.new()
		mesh.size = size
		mesh.material = mats[mat_key]
		var body: Node3D = StaticBody3D.new() if bool(b.get("solid", true)) else Node3D.new()
		body.name = str(b.get("id", "Block"))
		body.position = _vec3(b.get("pos", [0, 0, 0]))
		body.rotation_degrees = Vector3(float(b.get("pitch", 0.0)), float(b.get("yaw", 0.0)), 0.0)
		if bool(b.get("visible", true)):  # M2-FP-108: false = collision only, under a dressing
			var mi := MeshInstance3D.new()
			mi.name = "Mesh"
			mi.mesh = mesh
			body.add_child(mi)
		if body is StaticBody3D:
			var shape := BoxShape3D.new()
			shape.size = size
			var cs := CollisionShape3D.new()
			cs.name = "Shape"
			cs.shape = shape
			body.add_child(cs)
		root.add_child(body)


func _build_markers(folder: StringName, points: Dictionary, parent: Node = self) -> void:
	var root := Node3D.new()
	root.name = String(folder)
	parent.add_child(root)
	for id: String in points.keys():
		var p: Array = points[id]
		var m := Marker3D.new()
		m.name = id
		m.position = Vector3(float(p[0]), float(p[1]), float(p[2]))
		m.rotation_degrees.y = float(p[3]) if p.size() > 3 else 0.0
		root.add_child(m)


## M2-FP-102: ambient gulls, crabs and fish (M3-CRE-611) for any location with a wildlife file.
func _build_wildlife() -> void:
	if location_id == &"" or not FileAccess.file_exists(WildlifeConfig.zone_path(location_id)):
		return
	var w := WildlifeLayer.new()
	w.name = "WildlifeLayer"
	w.zone_id = location_id
	add_child(w)


## ADR 0152 (M3-CRE-657): the villagers and the crowd for any location with a villager zone file
## (game/data/world/npc/zones/). Added in _ready, after every child's (ZoneCast's casts included): the layer then
## replaces ZoneCast's stand-in villagers with the zone's crowd people and adopts the named ones' models.
func _build_villagers() -> void:
	if location_id == &"" or not FileAccess.file_exists(VillagerLayer.path_for(location_id)):
		return
	VillagerLayer.wire(self, location_id)


func _build_player() -> void:
	var d: Dictionary = _merged("player")
	player = FieldController.new()
	player.name = "Player"
	player.add_child(_capsule_shape(d))
	player.add_child(_capsule_mesh(d))
	field_camera = Camera3D.new()
	field_camera.name = "FieldCamera"
	field_camera.current = true
	director = FieldCameraDirector.new()
	director.name = "CameraDirector"
	var c: Dictionary = _merged("camera")
	var shot := CameraShot.new()
	shot.id = &"hub_orbit"
	shot.mode = CameraShot.Mode.ORBIT
	shot.target_offset = Vector3(0.0, float(c.get("target_height", 0.0)), 0.0)
	shot.fov_deg = float(c.get("fov_deg", CameraShot.USE_DEFAULT))
	shot.orbit_distance = float(c.get("orbit_distance", CameraShot.USE_DEFAULT))
	shot.orbit_height = float(c.get("orbit_height", CameraShot.USE_DEFAULT))
	director.hub_orbit_enabled = true
	director.initial_shot = shot
	add_child(player)
	add_child(field_camera)
	add_child(director)
	player.director_path = player.get_path_to(director)
	director.camera_path = director.get_path_to(field_camera)
	director.target_path = director.get_path_to(player)
	var spawns: Dictionary = layout.get("spawns", {})
	if not spawns.is_empty():
		player.position = _vec3(spawns.values()[0])


func _build_stage() -> void:
	stage = CutsceneStage.new()
	stage.name = "CutsceneStage"
	add_child(stage)
	_build_markers(&"Marks", layout.get("marks", {}), stage)
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	var base: Dictionary = _merged("actor")
	var actor_rows: Dictionary = layout.get("actors", {})
	for id: String in actor_rows.keys():
		var row: Dictionary = actor_rows[id]
		var d := base.duplicate()
		d.merge(row, true)
		var a := Node3D.new()
		a.name = id
		var at: Array = row.get("at", [0, 0, 0, 0])
		a.position = _vec3(at)
		a.rotation_degrees.y = float(at[3]) if at.size() > 3 else 0.0
		a.visible = not bool(row.get("hidden", false))
		a.add_child(_actor_body(id, row, d))
		actors.add_child(a)
	var shots := Node.new()
	shots.name = "Shots"
	stage.add_child(shots)
	var shot_rows: Dictionary = layout.get("shots", {})
	for id: String in shot_rows.keys():
		var row: Dictionary = shot_rows[id]
		var shot := CameraShot.new()
		shot.id = StringName(id)
		shot.mode = CameraShot.Mode.FIXED
		shot.position = _vec3(row.get("pos", [0, 0, 0]))
		shot.look_at = _vec3(row.get("look_at", [0, 0, -1]))
		shot.fov_deg = float(row.get("fov", setting("shot_fov_deg")))
		var sn := CutsceneShotNode.new()
		sn.name = id
		sn.shot = shot
		shots.add_child(sn)


func _build_triggers() -> void:
	var root := Node3D.new()
	root.name = String(TRIGGERS)
	add_child(root)
	for t: Dictionary in layout.get("triggers", []):
		var area := Interactable.new()
		area.name = str(t.get("id", "Trigger"))
		area.id = StringName(str(t.get("id", "")))
		area.activation = (
			Interactable.Activation.TOUCH
			if str(t.get("activation", ACTIVATION_TOUCH)) == ACTIVATION_TOUCH
			else Interactable.Activation.INTERACT
		)
		area.prompt_key = str(t.get("prompt_key", ""))
		area.requires_flag = StringName(str(t.get("requires_flag", "")))
		area.blocked_by_flag = StringName(str(t.get("blocked_by_flag", "")))
		area.sets_flag = StringName(str(t.get("sets_flag", "")))
		area.once = bool(t.get("once", false))
		area.payload = t.get("payload", {})
		area.position = _vec3(t.get("at", [0, 0, 0]))
		area.rotation_degrees.y = float(t.get("yaw", 0.0))
		var shape := BoxShape3D.new()
		var size := _vec3(t.get("size", [1, 1, 1]))
		if size.y <= 0.0:
			size.y = float(setting("trigger_height"))
		shape.size = size
		var cs := CollisionShape3D.new()
		cs.name = "Shape"
		cs.shape = shape
		cs.position.y = size.y * 0.5
		area.add_child(cs)
		root.add_child(area)


func _build_camera_volumes() -> void:
	var rails := Node3D.new()
	rails.name = String(RAILS)
	add_child(rails)
	var root := Node3D.new()
	root.name = String(VOLUMES)
	add_child(root)
	for v: Dictionary in layout.get("camera_volumes", []):
		var id := str(v.get("id", "Volume"))
		var shot := CameraShot.new()
		shot.id = StringName(id)
		shot.mode = SHOT_MODES.get(str(v.get("mode", "fixed")), CameraShot.Mode.FIXED)
		shot.position = _vec3(v.get("pos", [0, 0, 0]))
		shot.look_at = _vec3(v.get("look_at", [0, 0, -1]))
		shot.fov_deg = float(v.get("fov", setting("shot_fov_deg")))
		shot.target_offset = Vector3(0.0, float(_merged("camera").get("target_height", 0.0)), 0.0)
		if v.has("dolly"):
			shot.dolly_path = NodePath("%s/%s_dolly" % [RAILS, id])
			rails.add_child(_path(id + "_dolly", v["dolly"]))
		if v.has("track"):
			shot.track_path = NodePath("%s/%s_track" % [RAILS, id])
			rails.add_child(_path(id + "_track", v["track"]))
		var vol := CameraVolume.new()
		vol.name = id
		vol.shot = shot
		vol.shot_priority = int(v.get("priority", 0))
		vol.position = _vec3(v.get("at", [0, 0, 0]))
		var shape := BoxShape3D.new()
		shape.size = _vec3(v.get("size", [1, 1, 1]))
		var cs := CollisionShape3D.new()
		cs.name = "Shape"
		cs.shape = shape
		vol.add_child(cs)
		root.add_child(vol)


func _path(id: String, points: Array) -> Path3D:
	var curve := Curve3D.new()
	for p: Variant in points:
		curve.add_point(_vec3(p))
	var path := Path3D.new()
	path.name = id
	path.curve = curve
	return path


func _capsule_shape(d: Dictionary) -> CollisionShape3D:
	var shape := CapsuleShape3D.new()
	shape.radius = float(d.get("radius", 0.0))
	shape.height = float(d.get("height", 0.0))
	var cs := CollisionShape3D.new()
	cs.name = "Shape"
	cs.shape = shape
	cs.position.y = shape.height * 0.5
	return cs


## M2-FP-111: an actor row's "model" (a villager actor scene, e.g. Kell's) stands in its place idling and breathing,
## so the cutscene's @anim and talk clips have a body; without one (or when it can't load) it is the capsule.
func _actor_body(id: String, row: Dictionary, d: Dictionary) -> Node3D:
	var packed := load(str(row["model"])) as PackedScene if row.has("model") else null
	if packed == null:
		return _capsule_mesh(d)
	var body := packed.instantiate() as Node3D
	body.name = "Model"
	HeroMotion.play(body, &"idle", 0.0)
	HeroMotion.add_micro_motion(body, StringName(id))
	return body


func _capsule_mesh(d: Dictionary) -> MeshInstance3D:
	var mesh := CapsuleMesh.new()
	mesh.radius = float(d.get("radius", 0.0))
	mesh.height = float(d.get("height", 0.0))
	var m := StandardMaterial3D.new()
	m.albedo_color = Color.html(str(d.get("color", "#ffffff")))
	mesh.material = m
	var mi := MeshInstance3D.new()
	mi.name = "StandIn"
	mi.mesh = mesh
	mi.position.y = mesh.height * 0.5
	return mi


## The default block `key` with the layout's block of the same name merged over it.
func _merged(key: String) -> Dictionary:
	var out: Dictionary = (defaults.get(key, {}) as Dictionary).duplicate()
	out.merge(layout.get(key, {}), true)
	return out


static func _vec3(raw: Variant) -> Vector3:
	var a: Array = raw if raw is Array else [0, 0, 0]
	return Vector3(float(a[0]), float(a[1]), float(a[2]))
