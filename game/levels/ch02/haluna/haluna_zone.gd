class_name HalunaZone
extends Node3D
## The playable Haluna zone (M2-FP-02; README.md beside this file). It instances Environment's mood
## scene (terrain, kit dressing, sea, sun, the save shrine) without editing it, and adds what play
## needs: walk collision built at runtime (HalunaCollision), Rhen as a FieldController under the
## FieldCameraDirector's volumes (a hub orbit as the whole-zone fallback), spawns, three villagers,
## the battle and causeway triggers, and the CutsceneStage for Cutscene A.
##
## This script only places things. The story driver listens on FieldEvents for the NPC barks
## (`payload.dialogue`), the tideline battle (`payload.battle`) and the causeway head
## (`payload.cutscene`), and plays Cutscene A on `stage`.

## Spawn used at _ready (a loader then calls place_at with its own spawn).
@export var start_spawn: StringName = &"Shrine"
## Raised above the marker on placement so the capsule settles onto the ground.
@export var spawn_lift_m: float = 0.02
## A shadow_normal_bias for the zone sun in place of the mood scene's 1.0; 0 (the default, and
## haluna.tscn since M2-FP-11) leaves it. Close-ups no longer use the sun on faces: CutsceneKeyLight
## (M2-FP-10) keys the cast with bias 4.5 on a short-range light, and at the zone's 400 m cascade a
## higher sun bias only erased the nose shadow (docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md).
@export var face_key_shadow_normal_bias: float = 0.0

## True once prebuild() has dressed the mood scene and built the collision (M2-FP-05).
var prebuilt := false
## True once set_night() has run (M2-FP-15).
var is_night := false
## Wall time of prebuild(), for the README and tests.
var prebuild_msec := 0

@onready var player: FieldController = $Player
@onready var director: FieldCameraDirector = $CameraDirector
@onready var stage: CutsceneStage = $CutsceneStage
@onready var collision: HalunaCollision = $Collision
@onready var mood: Node3D = $HalunaMood
@onready var field_camera: Camera3D = $FieldCamera


## M2-FP-05: PackedScene.instantiate() sends NOTIFICATION_SCENE_INSTANTIATED to the zone root once
## every node exists, on the thread that instantiates it. SceneRouter instantiates on a
## WorkerThreadPool thread under its opaque fade, so the ~1.5 s of dressing and collision happen
## there, not in the frame that adds the zone to the tree (README, "Entry hitch"). An instance made
## on the main thread (ShaderPrewarm's off-tree material scan, tests, the screenshot capture) is not
## prebuilt here: it would only move the same cost into another main-thread frame, and the scan
## would pay it a second time. Such an instance dresses in _ready as before, or calls prebuild().
func _notification(what: int) -> void:
	if what == NOTIFICATION_SCENE_INSTANTIATED and OS.get_thread_caller_id() != OS.get_main_thread_id():
		prebuild()


## Dresses the mood scene, builds the walk collision and loads the cutscene cast's materials while
## the zone is still off the tree (thread-safe: nothing here touches a node in the tree). The mood scene's
## dresser is swapped to HalunaZoneDresser first so it does not dress again in _ready. Runs once,
## synchronously; the zone's _ready then only skips what was done here.
func prebuild() -> void:
	if prebuilt or is_inside_tree():
		return
	var t0 := Time.get_ticks_msec()
	# M2-ENV-05: the cast's materials (about a second of texture decoding) load on the loader's threads
	# while this thread dresses the zone and builds its collision.
	var cast: Array[HalunaActorPose] = []
	for actor in get_node(^"CutsceneStage").find_children("*", "", true, false):
		if actor is HalunaActorPose:
			cast.append(actor as HalunaActorPose)
			(actor as HalunaActorPose).request_materials()
	var dresser := get_node(^"HalunaMood/Dresser") as HalunaDresser
	HalunaZoneDresser.adopt(dresser).dress()
	(get_node(^"Collision") as HalunaCollision).build()
	_add_life()
	for actor in cast:
		actor.assign_materials()
	# The sea builds its ocean grid in _ready (~40 ms) unless handed one: hand it the same grid.
	var water := get_node_or_null(^"HalunaMood/Water") as WaterSurface
	if water != null and water.surface_mesh == null:
		water.surface_mesh = WaterMeshBuilder.build(
			water.core_half_extent_m, water.core_cell_m, water.outer_half_extent_m, water.cell_growth
		)
	prebuild_msec = Time.get_ticks_msec() - t0
	prebuilt = true


## The village alive: creatures' VillagerLayer owns the villagers (M3-CRE-613, ch02_haluna.json: routes, chats,
## work, storms), HalunaVillagers dresses the three shop bodies it doesn't cover yet (M2-FP-113), and the
## WildlifeLayer brings the gulls, crabs and fish (M3-CRE-611).
func _add_life() -> void:
	if get_node_or_null(^"VillagerLayer") == null:
		var villagers := VillagerLayer.new()
		villagers.name = "VillagerLayer"
		villagers.zone_id = &"ch02/haluna"
		add_child(villagers)
	HalunaVillagers.populate(self)
	if get_node_or_null(^"WildlifeLayer") == null:
		var w := WildlifeLayer.new()
		w.name = "WildlifeLayer"
		w.zone_id = &"ch02/haluna"
		add_child(w)


func _ready() -> void:
	if not prebuilt:
		# Not prebuilt (instanced on the main thread): the mood dressed itself in its own _ready.
		collision.build()
		_add_life()
	field_camera.make_current()
	# After Cutscene A the girl and the guardian have walked up to the village.
	_apply_face_key_bias()
	var intro_flag := StringName(
		str(FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA).get("intro_flag", ""))
	)
	set_beach_cast_visible(intro_flag == &"" or not bool(Game.get_flag(intro_flag)))
	place_at(start_spawn, spawn_yaw_deg(start_spawn))


## The zone's own wind variant (zone_weather.json, this scene's row "variants"), e.g. the night land
## breeze. The WeatherClock owner wrote the row's wind on the swap; a variant replaces it in place until
## the next swap. False when the data has no such variant.
func apply_wind_variant(variant: StringName) -> bool:
	var row: Dictionary = WeatherClock.zone_row(scene_file_path)
	var v: Variant = (row.get("variants", {}) as Dictionary).get(String(variant))
	if not v is Dictionary:
		return false
	ShaderGlobals.set_value(&"hymn_wind", WeatherClock.wind_vector(v as Dictionary))
	return true


## Moves the player to Spawns/<spawn>, facing `yaw_deg`, and snaps the camera (teleport-style).
func place_at(spawn: StringName, yaw_deg: float = 0.0) -> bool:
	var marker := spawn_marker(spawn)
	if marker == null:
		push_warning("HalunaZone: no spawn '%s'" % spawn)
		return false
	player.global_position = marker.global_position + Vector3.UP * spawn_lift_m
	player.rotation.y = deg_to_rad(yaw_deg)
	player.velocity = Vector3.ZERO
	if player.motor != null:
		player.motor.facing_yaw = player.rotation.y
	director.snap()
	return true


func spawn_marker(spawn: StringName) -> Marker3D:
	return get_node_or_null(NodePath("Spawns/%s" % spawn)) as Marker3D


## The facing authored on a spawn marker, in degrees (what WorldReturn passes to place_at).
func spawn_yaw_deg(spawn: StringName) -> float:
	var marker := spawn_marker(spawn)
	return rad_to_deg(marker.rotation.y) if marker != null else 0.0


func spawn_names() -> Array[StringName]:
	var out: Array[StringName] = []
	for m in get_node(^"Spawns").get_children():
		out.append(StringName(m.name))
	return out


## Shows or hides Cutscene A's cast (Actors under the stage); the player is never touched.
func set_beach_cast_visible(on: bool) -> void:
	var actors := stage.get_node_or_null(CutsceneStage.ACTORS)
	if actors == null:
		return
	for a in actors.get_children():
		(a as Node3D).visible = on


func _apply_face_key_bias() -> void:
	var sun: Variant = mood.get(&"sun")
	if face_key_shadow_normal_bias > 0.0 and sun is DirectionalLight3D:
		(sun as DirectionalLight3D).shadow_normal_bias = face_key_shadow_normal_bias


## M2-FP-15: Haluna at night for B11. `night` is first_playable.json haluna.night: the world's own
## night mood (HalunaMood `mood`, M2-ENV-02: moon, star sky, sea-glow, the houses' oil lamps), plus
## the zone's practicals, warm lanterns at the given points (the dock). `hide` lists node paths (the
## dock villagers) that are gone home at night.
func set_night(night: Dictionary, hide: Array = []) -> void:
	mood.set(&"mood", StringName(str(night.get("mood", "night"))))
	apply_wind_variant(&"night")
	var lamps := Node3D.new()
	lamps.name = "NightLamps"
	add_child(lamps)
	for p: Array in night.get("lamps", []):
		var lamp := OmniLight3D.new()
		lamp.position = Vector3(float(p[0]), float(p[1]), float(p[2]))
		lamp.light_color = Color.html(str(night.get("lamp_color", "#FFFFFF")))
		lamp.light_energy = float(night.get("lamp_energy", 1.0))
		lamp.omni_range = float(night.get("lamp_range_m", 1.0))
		lamps.add_child(lamp)
	# Hidden and stopped, not freed: creatures' VillagerLayer keeps ticking the villagers and the stand-ins it
	# carries (the dock's), so freeing them left it moving freed nodes every frame.
	for path: Variant in hide:
		var n := get_node_or_null(NodePath(str(path)))
		if n != null:
			n.process_mode = Node.PROCESS_MODE_DISABLED
			if n is Node3D:
				(n as Node3D).visible = false
	is_night = true


## Puts the cast where `cast` says ([x, y, z, yaw°] per actor id) and shows them, and adds the scene's
## marks (id -> [x, y, z]) to the stage (M2-FP-15, B11 on the dock).
func place_cast(cast: Dictionary, marks: Dictionary) -> void:
	for id: String in cast.keys():
		var a := stage.actor(StringName(id))
		var p: Array = cast[id]
		if a == null or a is FieldController:
			continue
		a.global_position = Vector3(float(p[0]), float(p[1]), float(p[2]))
		a.rotation.y = deg_to_rad(float(p[3]))
		a.visible = true
	var folder := stage.get_node_or_null(CutsceneStage.MARKS)
	for id: String in marks.keys():
		if folder == null or folder.has_node(NodePath(id)):
			continue
		var m := Marker3D.new()
		m.name = id
		var q: Array = marks[id]
		folder.add_child(m)
		m.global_position = Vector3(float(q[0]), float(q[1]), float(q[2]))
