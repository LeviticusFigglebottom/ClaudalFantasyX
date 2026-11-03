class_name BattleStorm
extends Node3D
## FAST-TRACK 11-03 (the human's playtest: the storm fights used the normal sunny backdrop, and the Undertow was not
## in them). A fight listed in game/data/vfx/battle/storm_fights.json `fights` gets its arena's storm variant at
## spawn, battle-side (the arena scenes are untouched; docs/kb/tech/battle_status_looks.md "Storm fights"):
##   - the sky: the look's environment_res in place of the arena's Environment (a duplicate), else the arena's own
##     with its sky shader's sky_params set (overcast, no sun disc);
##   - the sun: energy scaled and recoloured (its swatch);
##   - rain streaks and wind-blown spray over the field (looping GPUParticles3D, fewer under reduced motion);
##   - the Undertow: an UndertowStorm at the look's undertow.json preset, in the battle camera's view (the rest
##     frame's look azimuth plus yaw_offset_deg), its own rain off and its lightning never flashing the screen.
## Presentation only: it never reads or writes combat state.

const DATA_PATH := "res://game/data/vfx/battle/storm_fights.json"
const DRAW_MATERIAL := "res://game/vfx/battle/materials/battle_spark_draw.tres"
const STORM_NODE := &"BattleUndertow"
const VISIBILITY_HALF_M := 40.0

static var _data_cache: Dictionary = {}

var look_id := &""
var look: Dictionary = {}
## Our own Undertow: the fallback for a storm fight whose arena has none (else null).
var undertow: UndertowStorm
## The arena's own Undertow when it has one (it then owns the sky and the vortex).
var arena_storm: UndertowStorm
var rain: GPUParticles3D
var wind: GPUParticles3D
var reduced_motion := false


static func load_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = parsed as Dictionary
		else:
			push_warning("BattleStorm: cannot read %s" % DATA_PATH)
	return _data_cache


## The storm look encounter `encounter` fights in (&"" for a fight with none).
static func look_for(encounter: StringName) -> StringName:
	return StringName(str((load_data().get("fights", {}) as Dictionary).get(String(encounter), "")))


## Builds the storm under the controller's stage when `engine`'s encounter is a storm fight (BattleVfx.attach);
## null otherwise. A retry of the same fight keeps the arena, so an old storm is replaced, never stacked.
static func attached_if_storm(controller: BattleController, engine: BattleEngine) -> BattleStorm:
	var old := controller.stage.get_node_or_null(^"BattleStorm")
	if old != null:
		controller.stage.remove_child(old)
		old.queue_free()
	var id := look_for(engine.encounter_id)
	if id == &"":
		return null
	var view := BattleStorm.new()
	view.name = "BattleStorm"
	view.look_id = id
	view.look = (load_data().get("looks", {}) as Dictionary).get(String(id), {}) as Dictionary
	var settings := UiSettings.shared()
	view.reduced_motion = settings != null and settings.reduced_motion()
	controller.stage.add_child(view)
	view.apply(controller, engine)
	return view


func apply(controller: BattleController, engine: BattleEngine) -> void:
	# The Lead (11-03, big47): ONE Undertow per fight. A storm arena (arenas.json storm.arenas) owns the static set:
	# its sky, wet surfaces and Undertow. Then this adds only the dynamic layer (wind and spray, and rain when the
	# arena's storm brings none); the full look is the fallback for a storm fight on an arena without one.
	arena_storm = arena_undertow(controller)
	if arena_storm == null:
		_sky(controller)
		_sun(controller)
	var centre := _field_centre(controller, engine)
	var wd: Array = look.get("wind_dir", [1.0, 0.0, 0.0])
	var wind_dir := Vector3(float(wd[0]), float(wd[1]), float(wd[2])).normalized()
	if look.has("rain") and (arena_storm == null or arena_storm.rain_amount == 0.0):
		rain = _rain(look["rain"] as Dictionary, centre, wind_dir)
		add_child(rain)
	if look.has("wind"):
		wind = _wind(look["wind"] as Dictionary, centre, wind_dir)
		add_child(wind)
	if str(look.get("preset", "")) != "" and arena_storm == null:
		undertow = _undertow(controller, centre)


## The arena's own Undertow (an UndertowStorm in the battle scene that is not this view's), or null.
static func arena_undertow(controller: BattleController) -> UndertowStorm:
	for n in controller.find_children("*", "UndertowStorm", true, false):
		if not String(controller.get_path_to(n)).contains(String(STORM_NODE)):
			return n as UndertowStorm
	return null


## Every Undertow the battle scene draws (tests: one per storm fight).
static func undertows_in(controller: BattleController) -> int:
	return controller.find_children("*", "UndertowStorm", true, false).size()


## Where the fight stands: the midpoint of every fighter on the stage (the stage's origin when there are none).
func _field_centre(controller: BattleController, e: BattleEngine) -> Vector3:
	var sum := Vector3.ZERO
	var n := 0
	if e != null:
		for c in e.party_active + e.enemies:
			if controller.stage.has_fighter(c.id):
				sum += controller.stage.stand_in(c.id).global_position
				n += 1
	return sum / float(n) if n > 0 else controller.stage.global_position


func _sky(controller: BattleController) -> void:
	var we := controller.get_node_or_null(^"WorldEnvironment") as WorldEnvironment
	if we == null or we.environment == null:
		return
	var res := str(look.get("environment_res", ""))
	if res != "" and ResourceLoader.exists(res):
		we.environment = (load(res) as Environment).duplicate(true) as Environment
	var params := look.get("sky_params", {}) as Dictionary
	if params.is_empty() or we.environment.sky == null:
		return
	var env := we.environment.duplicate(false) as Environment  # the arena's resource stays as authored
	var sky := env.sky.duplicate(false) as Sky
	var mat := sky.sky_material.duplicate(false) as ShaderMaterial if sky.sky_material is ShaderMaterial else null
	if mat == null:
		return
	var known := {}
	for u: Dictionary in mat.shader.get_shader_uniform_list():
		known[str(u["name"])] = true
	for k: String in params:
		if not known.has(k):
			continue
		var v: Variant = params[k]
		mat.set_shader_parameter(k, Color(str(v)) if typeof(v) == TYPE_STRING else v)
	sky.sky_material = mat
	env.sky = sky
	we.environment = env


func _sun(controller: BattleController) -> void:
	var row := look.get("sun", {}) as Dictionary
	var sun := controller.get_node_or_null(^"Sun") as DirectionalLight3D
	if row.is_empty() or sun == null:
		return
	sun.light_energy *= float(row.get("energy_scale", 1.0))
	if row.has("color"):
		sun.light_color = Color(str(row["color"]))


func _amount(n: float) -> int:
	var rm := load_data().get("reduced_motion", {}) as Dictionary
	return maxi(1, roundi(n * (float(rm.get("particle_scale", 1.0)) if reduced_motion else 1.0)))


func _speed(v: float) -> float:
	var rm := load_data().get("reduced_motion", {}) as Dictionary
	return v * (float(rm.get("speed_scale", 1.0)) if reduced_motion else 1.0)


## Rain: thin streaks falling across the field, slanted by the wind, standing upright to the camera.
func _rain(r: Dictionary, centre: Vector3, wind_dir: Vector3) -> GPUParticles3D:
	var p := GPUParticles3D.new()
	p.name = "Rain"
	p.amount = _amount(float(r.get("amount", 600)))
	p.lifetime = float(r.get("lifetime_s", 1.0))
	p.preprocess = p.lifetime
	p.local_coords = false
	p.position = centre + Vector3(0.0, float(r.get("height_m", 12.0)), 0.0)
	var mat := ParticleProcessMaterial.new()
	var box: Array = r.get("box_m", [30.0, 2.0, 30.0])
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	mat.emission_box_extents = Vector3(float(box[0]), float(box[1]), float(box[2])) * 0.5
	mat.direction = (Vector3.DOWN + wind_dir * float(r.get("slant", 0.2))).normalized()
	mat.spread = 2.0
	var v := _speed(float(r.get("speed_m_s", 12.0)))
	mat.initial_velocity_min = v * 0.85
	mat.initial_velocity_max = v
	mat.gravity = Vector3.ZERO
	p.process_material = mat
	var streak: Array = r.get("streak_m", [0.012, 0.5])
	var q := QuadMesh.new()
	q.size = Vector2(float(streak[0]), float(streak[1]))
	var m := StandardMaterial3D.new()
	var c := Color(str(r.get("color", "#FFFFFF")))
	m.albedo_color = Color(c.r, c.g, c.b, float(r.get("alpha", 0.3)))
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_FIXED_Y
	m.billboard_keep_scale = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	q.material = m
	p.draw_pass_1 = q
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var h := VISIBILITY_HALF_M
	p.visibility_aabb = AABB(Vector3(-h, -h, -h), Vector3(2.0 * h, 2.0 * h, 2.0 * h))
	p.emitting = true
	return p


## Wind: spray and grit blown low across the field along wind_dir.
func _wind(w: Dictionary, centre: Vector3, wind_dir: Vector3) -> GPUParticles3D:
	var p := GPUParticles3D.new()
	p.name = "Wind"
	p.amount = _amount(float(w.get("amount", 60)))
	p.lifetime = float(w.get("lifetime_s", 2.0))
	p.preprocess = p.lifetime
	p.local_coords = false
	p.position = centre + Vector3(0.0, float(w.get("height_m", 1.5)), 0.0) - wind_dir * 6.0
	var mat := ParticleProcessMaterial.new()
	var box: Array = w.get("box_m", [30.0, 3.0, 30.0])
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	mat.emission_box_extents = Vector3(float(box[0]), float(box[1]), float(box[2])) * 0.5
	mat.direction = wind_dir
	mat.spread = 8.0
	var sp: Array = w.get("speed_m_s", [5.0, 8.0])
	mat.initial_velocity_min = _speed(float(sp[0]))
	mat.initial_velocity_max = _speed(float(sp[1]))
	mat.gravity = Vector3(0.0, -0.4, 0.0)
	mat.turbulence_enabled = not reduced_motion and float(w.get("turbulence", 0.0)) > 0.0
	mat.turbulence_noise_strength = float(w.get("turbulence", 0.0))
	var size: Array = w.get("size_m", [0.03, 0.07])
	mat.scale_min = float(size[0])
	mat.scale_max = float(size[1])
	var c := Color(str(w.get("color", "#FFFFFF")))
	var e := float(w.get("energy", 1.0))
	var ramp := Gradient.new()
	ramp.set_color(0, Color(c.r * e, c.g * e, c.b * e, 0.0))
	ramp.set_color(1, Color(c.r * e, c.g * e, c.b * e, 0.0))
	ramp.add_point(0.2, Color(c.r * e, c.g * e, c.b * e, 0.8))
	ramp.add_point(0.75, Color(c.r * e, c.g * e, c.b * e, 0.6))
	var tex := GradientTexture1D.new()
	tex.gradient = ramp
	mat.color_ramp = tex
	p.process_material = mat
	var q := QuadMesh.new()
	q.material = load(DRAW_MATERIAL) as Material
	p.draw_pass_1 = q
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var h := VISIBILITY_HALF_M
	p.visibility_aabb = AABB(Vector3(-h, -h, -h), Vector3(2.0 * h, 2.0 * h, 2.0 * h))
	p.emitting = true
	return p


## The Undertow standing in the background: placed at the field, its approach azimuth the rest frame's look plus
## yaw_offset_deg, so it fills part of the sky behind the foes rather than behind the lens.
func _undertow(controller: BattleController, centre: Vector3) -> UndertowStorm:
	var s := UndertowStorm.new()
	s.name = String(STORM_NODE)
	s.preset = str(look.get("preset", ""))
	s.approach_azimuth_deg = rest_azimuth(controller) + float(look.get("yaw_offset_deg", 0.0))
	s.sea_level_from_water = false
	var sea := controller.get_node_or_null(^"Arena/Sea") as Node3D
	s.sea_level_y = sea.global_position.y if sea != null and sea.is_inside_tree() else 0.0
	s.position = Vector3(centre.x, 0.0, centre.z)
	s.rain_amount = 0.0  # the battle's own rain (above); the storm's near curtains are for the field camera
	s.exposure_flash = false  # the battle flash safety contract (effects.json safety): no screen-wide flashes
	s.zone_shadow = false  # the sun is set above; the storm must not take it back mid-fight
	s.sun = controller.get_node_or_null(^"Sun") as DirectionalLight3D
	s.world_environment = controller.get_node_or_null(^"WorldEnvironment") as WorldEnvironment
	add_child(s)
	var far := StormFarPlane.new()
	far.name = "FarPlane"
	s.add_child(far)  # the battle camera reaches past the storm (M3-ENV-1308)
	return s


## The azimuth (clockwise from north, -Z; UndertowStorm.direction_from_azimuth) the battle camera's rest frame
## looks along.
static func rest_azimuth(controller: BattleController) -> float:
	var cam := controller.stage.camera
	var dir := controller.stage.choreo.camera if controller.stage.choreo != null else null
	var xf := dir.default_transform if dir != null else (cam.global_transform if cam != null else Transform3D.IDENTITY)
	var fwd := -xf.basis.z
	return fposmod(rad_to_deg(atan2(fwd.x, -fwd.z)), 360.0)
