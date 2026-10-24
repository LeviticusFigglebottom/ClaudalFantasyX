class_name UndertowEvents
extends Node
## The Undertow's events and its hold on the zone (M2-RND-05). UndertowStorm owns one as an internal
## child and calls build() on every rebuild and update() every frame; docs/kb/tech/undertow.md,
## "Storm events". Tunables: undertow.json "streamers", "bolts", "exposure_flash", "rain",
## "zone_shadow" and "reflection"; per-tier counts in "quality".
## - Streamers: km-scale ribbons of held light peeling off the wounds and sinking to the sea.
## - Bolts: a branching stroke at a site's flash when its strike shows one (always for force_flash),
##   and an exposure flash on the zone's Environment (photosensitivity-capped).
## - Rain: near-field curtains on the camera, heavier the deeper it is under the storm.
## - Zone shadow: the zone's key light and ambient dim when the storm stands between them and the
##   zone marker (the storm node), or the canopy is overhead.
## - Reflection: the storm's impostor in the zone water's reflection (the water shader's storm group).

const STREAMERS_NODE := "Streamers"
const BOLT_NODE := "Bolt"
const RAIN_NODE := "UndertowRain"
const SALT_BOLT := 11
const SALT_BOLT_SEED := 12
## _bolt_keys entry of a site with no stroke drawn.
const NO_STRIKE := -9223372036854775807
## The storm-local AABB head-room of a bolt mesh (m): its width grows by the pixel floor.
const BOLT_AABB_PAD_M := 400.0
## Reflection uniforms on the water (water_surface_body.gdshaderinc, storm group).
const PARAM_REFLECT := &"storm_reflect"

var storm: UndertowStorm
var streamers: MeshInstance3D
var streamer_material: ShaderMaterial
var bolts: Array[MeshInstance3D] = []
var bolt_materials: Array[ShaderMaterial] = []
var rain: Node3D
var rain_materials: Array[ShaderMaterial] = []
## Zone shadow in [0, 1] last frame (0 = in sunlight), and the sun energy the storm's own lighting
## uses (the zone's undimmed key).
var shadow: float = 0.0
## Exposure flashes fired and refused (photosensitivity: min interval) since the storm was built.
var flashes: int = 0
var flashes_suppressed: int = 0

var _prev_levels: PackedFloat32Array = PackedFloat32Array([0.0, 0.0, 0.0, 0.0])
var _bolt_keys: PackedInt64Array = PackedInt64Array([NO_STRIKE, NO_STRIKE, NO_STRIKE, NO_STRIKE])
var _sun_base: float = -1.0
var _sun_written: float = -1.0
var _ambient_base: float = -1.0
var _ambient_written: float = -1.0
var _exposure_base: float = -1.0
var _exposure_frames: int = 0
var _last_flash_s: float = -INF
var _rain_layers: int = -1
var _hidden_since_shown: bool = false


func _exit_tree() -> void:
	restore_zone()


## (Re)builds the parts for the storm's current tier. Safe to call again on a tier change.
func build(owner_storm: UndertowStorm) -> void:
	storm = owner_storm
	var plan := storm.state.quality_plan()
	var shaders := storm.state.config.get("shaders", {}) as Dictionary
	var prio := storm.state.config.get("render_priority", {}) as Dictionary
	_build_streamers(int(plan["streamers"]), str(shaders.get("streamer", "")), int(prio.get("streamers", 0)))
	_build_bolts(str(shaders.get("bolt", "")), int(prio.get("bolts", 0)))
	_build_rain(int(plan["rain_layers"]), str(shaders.get("rain", "")), int(prio.get("rain", 0)))


## Materials UndertowStorm pushes its static and dynamic uniforms into.
func materials() -> Array[ShaderMaterial]:
	var out: Array[ShaderMaterial] = []
	if streamer_material != null and streamers.visible:
		out.append(streamer_material)
	out.append_array(bolt_materials)
	return out


## Every material the events can draw with (prewarm and tests).
func all_materials() -> Array[ShaderMaterial]:
	var out := materials()
	out.append_array(rain_materials)
	return out


func update() -> void:
	if storm == null or not storm.is_inside_tree():
		return
	# A hidden storm (a zone between set pieces, gpu_bench --hide-storms) takes its events with it: this
	# Node breaks the visibility chain, so the rain and the zone hold are gated here.
	if not storm.is_visible_in_tree():
		if rain != null:
			rain.visible = false
		if _hidden_since_shown:
			return
		restore_zone()
		_hidden_since_shown = true
		return
	_hidden_since_shown = false
	_update_bolts()
	_update_exposure()
	_update_rain()
	_update_shadow()
	_push_reflection()


## The key light's energy before the zone shadow (what the storm's own lighting uses).
func sun_energy() -> float:
	if storm.sun == null:
		return 0.0
	return (
		_sun_base
		if _sun_base >= 0.0 and is_equal_approx(storm.sun.light_energy, _sun_written)
		else storm.sun.light_energy
	)


## Gives the zone back its light, exposure and reflection (the storm left the tree).
func restore_zone() -> void:
	if storm == null:
		return
	if storm.sun != null and _sun_base >= 0.0 and is_equal_approx(storm.sun.light_energy, _sun_written):
		storm.sun.light_energy = _sun_base
	var env := _environment()
	if env != null:
		if _ambient_base >= 0.0 and is_equal_approx(env.ambient_light_energy, _ambient_written):
			env.ambient_light_energy = _ambient_base
		if _exposure_frames > 0:
			env.tonemap_exposure = _exposure_base
	_exposure_frames = 0
	_sun_base = -1.0
	_ambient_base = -1.0
	if storm.water != null and storm.water.material != null:
		storm.water.material.set_shader_parameter(PARAM_REFLECT, 0.0)
		storm.water.material.set_shader_parameter(&"storm_body_ready", false)
		storm.water.material.set_shader_parameter(&"storm_body_tex", null)


# --- Streamers ---------------------------------------------------------------------------------


func _build_streamers(count: int, shader_path: String, prio: int) -> void:
	var cfg := _cfg("streamers")
	if streamers == null:
		streamers = MeshInstance3D.new()
		streamers.name = STREAMERS_NODE
		streamers.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		streamer_material = _material(shader_path, prio)
		streamers.material_override = streamer_material
		storm.visuals.add_child(streamers)
	streamers.visible = count > 0
	if count <= 0:
		return
	var reach_m := float(cfg.get("reach_m", 0.0))
	streamers.mesh = UndertowMeshBuilder.streamers(
		_streamer_anchors(count),
		reach_m,
		float(cfg.get("drop", 1.0)),
		float(cfg.get("twist_rad", 0.0)),
		float(cfg.get("width_m", 1.0)),
		int(cfg.get("segments", 1))
	)
	var reach := storm.state.wall_radius(0.0) + reach_m + float(cfg.get("width_m", 0.0))
	var top := storm.state.height_now()
	streamers.custom_aabb = AABB(Vector3(-reach, 0.0, -reach), Vector3(2.0 * reach, top, 2.0 * reach))
	streamer_material.set_shader_parameter(&"streamer_energy", float(cfg.get("energy", 0.0)))
	streamer_material.set_shader_parameter(&"streamer_mote_scale_m", float(cfg.get("mote_scale_m", 1.0)))
	streamer_material.set_shader_parameter(&"streamer_mote_cover", float(cfg.get("mote_cover", 0.0)))


## Anchors (radius, height, angle) on the wall's outer face inside the wounds' height window,
## spread round the storm by a golden-angle sequence with hashed jitter (deterministic).
func _streamer_anchors(count: int) -> PackedVector3Array:
	var w := storm.state.config.get("wounds", {}) as Dictionary
	var h_min := float(w.get("height_min", 0.0))
	var h_max := float(w.get("height_max", 1.0))
	var top := storm.state.height_now()
	var out := PackedVector3Array()
	for i in count:
		var h := lerpf(h_min, lerpf(h_min, h_max, 0.6), UndertowState.hash01(i, 0, SALT_BOLT_SEED))
		var a := fposmod(float(i) * 2.39996323 + UndertowState.hash01(i, 1, SALT_BOLT_SEED), TAU)
		out.append(Vector3(storm.state.wall_radius(h), h * top, a))
	return out


# --- Bolts and the exposure flash --------------------------------------------------------------


func _build_bolts(shader_path: String, prio: int) -> void:
	var cfg := _cfg("bolts")
	while bolts.size() < storm.state.flash_site_count():
		var mi := MeshInstance3D.new()
		mi.name = "%s%d" % [BOLT_NODE, bolts.size()]
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.visible = false
		var mat := _material(shader_path, prio)
		mat.set_shader_parameter(&"bolt_width_m", float(cfg.get("width_m", 1.0)))
		mat.set_shader_parameter(&"bolt_min_px", float(cfg.get("min_px", 0.0)))
		mat.set_shader_parameter(&"bolt_energy", float(cfg.get("energy", 0.0)))
		mi.material_override = mat
		storm.visuals.add_child(mi)
		bolts.append(mi)
		bolt_materials.append(mat)


## Whether site's current strike shows a bolt: forced strikes always, scheduled ones by bolts.chance
## (most of the storm's flashes stay inside the cloud), and only on the camera's half of the storm (a
## stroke behind the wall is hidden by it, and the body cannot occlude a transparent bolt).
func strike_shows_bolt(site: int, t: float) -> bool:
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	if cam != null:
		var s := storm.state.flash_sites(t)[site]
		var to_cam := cam.global_position - storm.storm_center()
		if s.x * to_cam.x + s.z * to_cam.z < 0.0:
			return false
	if storm.state.flash_is_forced(site, t):
		return true
	var chance := float(_cfg("bolts").get("chance", 0.0))
	return UndertowState.hash01(site, storm.state.flash_period(site, t), SALT_BOLT) < chance


## A strike's stroke in storm-local metres: from the cloud base over the site's wall angle down to the
## sea, beyond the wall's foot (cloud-to-sea; the site's in-cloud glow is undertow_lightning).
func bolt_ends(site: int, t: float) -> Array[Vector3]:
	var cfg := _cfg("bolts")
	var s := storm.state.flash_sites(t)[site]
	var a := atan2(s.z, s.x)
	var top_m := float(cfg.get("top_m", 0.0))
	var r := storm.state.wall_radius(top_m / maxf(storm.state.height_now(), 1.0))
	var k := storm.state.flash_period(site, t)
	var reach := float(cfg.get("sea_reach_m", 0.0)) * (0.5 + UndertowState.hash01(site, k, SALT_BOLT_SEED))
	var da := (UndertowState.hash01(site, k, SALT_BOLT) - 0.5) * float(cfg.get("spread_rad", 0.0))
	var top := Vector3(r * cos(a), top_m, r * sin(a))
	var bottom := Vector3((r + reach) * cos(a + da), 0.0, (r + reach) * sin(a + da))
	return [top, bottom]


func _update_bolts() -> void:
	var cfg := _cfg("bolts")
	var t := storm.state.time_s
	var threshold := float(cfg.get("threshold", 0.0))
	var levels := storm.state.flash_levels(t)
	for i in bolts.size():
		var level := levels[i]
		# The stroke is built on any frame of a live strike it was not built for yet: a capture or a cut
		# may make its camera current after the strike began (strike_shows_bolt asks the camera).
		var key := storm.state.flash_strike_id(i, t)
		var drawn := level > threshold and _bolt_keys[i] == key
		if level > threshold and not drawn and strike_shows_bolt(i, t):
			_strike(i, t)
			_bolt_keys[i] = key
			drawn = true
		if level > threshold and _prev_levels[i] <= threshold:
			_on_strike(level)
			storm.lightning_struck.emit(i, drawn)
		if level <= threshold * 0.25 and bolts[i].visible:
			bolts[i].visible = false
			_bolt_keys[i] = NO_STRIKE
		bolt_materials[i].set_shader_parameter(&"bolt_level", level)
		_prev_levels[i] = level


func _strike(site: int, t: float) -> void:
	var cfg := _cfg("bolts")
	var ends := bolt_ends(site, t)
	var seed := int(UndertowState.hash01(site, storm.state.flash_period(site, t), SALT_BOLT_SEED) * 2147483647.0)
	var mi := bolts[site]
	mi.mesh = UndertowMeshBuilder.bolt(
		seed,
		ends[0],
		ends[1],
		int(cfg.get("segments", 2)),
		int(storm.state.quality_plan()["bolt_branches"]),
		float(cfg.get("jag", 0.0))
	)
	mi.custom_aabb = mi.mesh.get_aabb().grow(BOLT_AABB_PAD_M)
	mi.visible = true


## The colour script's lightning frames (Ch8: 2.0x exposure for 2 frames) on the zone Environment,
## capped like battle flashes (battle_vfx.md): at least min_interval_s apart, and a gentler gain under
## reduced motion.
func _on_strike(_level: float) -> void:
	var cfg := _cfg("exposure_flash")
	var env := _environment()
	if not storm.exposure_flash or env == null or _exposure_frames > 0:
		return
	var now := Time.get_ticks_msec() / 1000.0
	if now - _last_flash_s < float(cfg.get("min_interval_s", 0.0)):
		flashes_suppressed += 1
		return
	var reduced := UiSettings.shared() != null and UiSettings.shared().reduced_motion()
	var gain := float(cfg.get("reduced_motion_gain" if reduced else "gain", 1.0))
	_exposure_base = env.tonemap_exposure
	env.tonemap_exposure = _exposure_base * gain
	_exposure_frames = int(cfg.get("frames", 0))
	_last_flash_s = now
	flashes += 1


func _update_exposure() -> void:
	if _exposure_frames <= 0:
		return
	_exposure_frames -= 1
	if _exposure_frames == 0:
		var env := _environment()
		if env != null:
			env.tonemap_exposure = _exposure_base


# --- Rain --------------------------------------------------------------------------------------


func _build_rain(layers: int, shader_path: String, prio: int) -> void:
	var cfg := _cfg("rain")
	if rain == null:
		rain = Node3D.new()
		rain.name = RAIN_NODE
		rain.top_level = true
		add_child(rain)
	if layers == _rain_layers:
		return
	_rain_layers = layers
	for c in rain.get_children():
		rain.remove_child(c)
		c.queue_free()
	rain_materials.clear()
	var radii := cfg.get("radii_m", []) as Array
	for i in mini(layers, radii.size()):
		var mi := MeshInstance3D.new()
		mi.name = "Layer%d" % i
		mi.mesh = UndertowMeshBuilder.unit_tube(1, int(cfg.get("segments", 3)))
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var r := float(radii[i])
		var h := float(cfg.get("height_m", 1.0))
		mi.custom_aabb = AABB(Vector3(-r, -0.5 * h, -r), Vector3(2.0 * r, h, 2.0 * r))
		var mat := _material(shader_path, prio + i)
		mat.set_shader_parameter(&"rain_radius_m", r)
		mat.set_shader_parameter(&"rain_height_m", h)
		for key: String in ["fall_m_s", "slant", "streak_m", "drop_m", "density", "alpha"]:
			mat.set_shader_parameter(StringName("rain_" + key), float(cfg.get(key, 0.0)))
		mi.material_override = mat
		rain.add_child(mi)
		rain_materials.append(mat)


## How hard it rains at the camera: storm.rain_amount when set (>= 0), else full within rain.full_m of
## the eye and nothing beyond rain.reach_m, none above rain.ceiling_m over the sea, times the storm's
## intensity.
func rain_amount(at: Vector3) -> float:
	if storm.rain_amount >= 0.0:
		return clampf(storm.rain_amount, 0.0, 1.0)
	var cfg := _cfg("rain")
	var c := storm.storm_center()
	var d := Vector2(at.x - c.x, at.z - c.z).length()
	var ceiling := float(cfg.get("ceiling_m", 0.0))
	var above := 1.0 - smoothstep(0.5 * ceiling, ceiling, at.y - c.y)
	var reach := 1.0 - smoothstep(float(cfg.get("full_m", 0.0)), float(cfg.get("reach_m", 0.0)), d)
	return reach * above * storm.intensity


func _update_rain() -> void:
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	rain.visible = cam != null and not rain_materials.is_empty()
	if not rain.visible:
		return
	rain.global_position = cam.global_position
	var amount := rain_amount(cam.global_position)
	rain.visible = amount > 0.0
	var cfg := _cfg("rain")
	var flash := 0.0
	for l in storm.state.flash_levels(storm.state.time_s):
		flash = maxf(flash, l)
	var base := Color.from_string(str(cfg.get("color", "")), Color.GRAY)
	var lit := base * storm.ambient_energy * (1.0 - shadow * float(_cfg("zone_shadow").get("ambient_dim", 0.0)))
	var col := (
		lit
		+ (
			Color.from_string(str(storm.state.config["colors"].get("lightning", "")), Color.WHITE)
			* (flash * float(cfg.get("flash_gain", 0.0)))
		)
	)
	# Every layer is a full-screen blend (about 0.06 ms at 1440p on the RX 9070 XT), so light rain
	# draws only the inner layers: all of them from half strength up.
	var layers := clampi(ceili(amount * 2.0 * rain_materials.size()), 1, rain_materials.size())
	var children := rain.get_children()
	for i in rain_materials.size():
		(children[i] as Node3D).visible = i < layers
		var m := rain_materials[i]
		m.set_shader_parameter(&"rain_amount", amount)
		m.set_shader_parameter(&"rain_time_s", storm.state.time_s)
		m.set_shader_parameter(&"col_rain", col)


# --- Zone shadow -------------------------------------------------------------------------------


## How deep the zone marker (the storm node) is in the storm's shadow, in [0, 1]: the canopy overhead,
## or the canopy or wall on the line to the sun. Times the storm's intensity.
func zone_shadow_at(at: Vector3, sun_dir: Vector3) -> float:
	var cfg := _cfg("zone_shadow")
	var sh := storm.state.config.get("shape", {}) as Dictionary
	var soft := float(cfg.get("soft_m", 1.0))
	var c := storm.storm_center()
	var canopy_r := float(sh.get("canopy_radius_m", 0.0))
	var over := 1.0 - smoothstep(canopy_r - soft, canopy_r + soft, Vector2(at.x - c.x, at.z - c.z).length())
	var k := over * float(cfg.get("overhead", 0.0))
	if sun_dir.y > 0.0:
		var heights := [
			[
				(
					float(sh.get("canopy_height_m", 0.0))
					* storm.state.height_now()
					/ maxf(float(sh.get("height_m", 1.0)), 1.0)
				),
				canopy_r
			],
			[0.5 * storm.state.height_now(), storm.state.wall_radius(0.5)],
		]
		for hr: Array in heights:
			var t := (c.y + float(hr[0]) - at.y) / sun_dir.y
			if t > 0.0:
				var q := at + sun_dir * t
				var d := Vector2(q.x - c.x, q.z - c.z).length()
				k = maxf(k, 1.0 - smoothstep(float(hr[1]) - soft, float(hr[1]) + soft, d))
	return clampf(k, 0.0, 1.0) * storm.intensity


func _update_shadow() -> void:
	var cfg := _cfg("zone_shadow")
	var sun := storm.sun
	if not storm.zone_shadow or sun == null:
		shadow = 0.0
		return
	if _sun_base < 0.0 or not is_equal_approx(sun.light_energy, _sun_written):
		_sun_base = sun.light_energy
	var sun_dir := sun.global_basis.z.normalized()
	shadow = zone_shadow_at(storm.global_position, sun_dir)
	_sun_written = _sun_base * (1.0 - float(cfg.get("sun_dim", 0.0)) * shadow)
	sun.light_energy = _sun_written
	var env := _environment()
	if env != null:
		if _ambient_base < 0.0 or not is_equal_approx(env.ambient_light_energy, _ambient_written):
			_ambient_base = env.ambient_light_energy
		_ambient_written = _ambient_base * (1.0 - float(cfg.get("ambient_dim", 0.0)) * shadow)
		env.ambient_light_energy = _ambient_written


# --- Reflection --------------------------------------------------------------------------------


## The water uniforms of the storm's reflection impostor (water_surface_body.gdshaderinc, storm group):
## two vertical cylinders (the wall, and the canopy's ring), with colours from the storm's lighting.
func reflection_parameters() -> Dictionary:
	var cfg := _cfg("reflection")
	var sh := storm.state.config.get("shape", {}) as Dictionary
	var colors := storm.state.config.get("colors", {}) as Dictionary
	var mood := storm.mood_parameters()
	var albedo := Color.from_string(str(colors.get("albedo", "")), Color.GRAY)
	var sun_col := mood["col_sun"] as Color
	var lit := albedo * sun_col * float(mood["sun_energy"]) * float(cfg.get("sun_gain", 0.0))
	var amb_top := (mood["col_ambient_top"] as Color) * float(mood["ambient_energy"])
	var amb_low := (mood["col_ambient_bottom"] as Color) * float(mood["ambient_energy"])
	var flash := 0.0
	for l in storm.state.flash_levels(storm.state.time_s):
		flash = maxf(flash, l)
	var lightning := Color.from_string(str(colors.get("lightning", "")), Color.WHITE)
	var wound := storm.state.dynamic_parameters()["col_wound"] as Color
	var h := storm.state.height_now()
	var canopy_h := float(sh.get("canopy_height_m", 0.0)) * h / maxf(float(sh.get("height_m", 1.0)), 1.0)
	return {
		PARAM_REFLECT: float(cfg.get("strength", 0.0)) * storm.intensity,
		&"storm_reflect_center": storm.storm_center(),
		&"storm_reflect_wall_m": Vector2(storm.state.wall_radius(0.0), storm.state.wall_radius(1.0)),
		&"storm_reflect_height_m": h,
		&"storm_reflect_canopy":
		Vector3(float(sh.get("canopy_radius_m", 0.0)), canopy_h, float(sh.get("canopy_thickness_m", 0.0))),
		&"storm_reflect_soft_m": float(cfg.get("soft_m", 1.0)),
		&"storm_reflect_low": amb_low * float(cfg.get("low_gain", 0.0)),
		&"storm_reflect_high": lit + amb_top * float(cfg.get("low_gain", 0.0)),
		&"storm_reflect_glow":
		(
			lightning * flash * float(cfg.get("flash_gain", 0.0))
			+ wound * storm.wound_intensity * float(cfg.get("wound_gain", 0.0))
		),
		&"storm_reflect_haze": mood["col_haze"],
		&"storm_reflect_visibility_m": mood["haze_visibility_m"],
	}


func _push_reflection() -> void:
	if storm.water == null or storm.water.material == null:
		return
	var params := reflection_parameters()
	# The half-res body's frame (compute or SubViewport): the water reflects the storm's own pixels.
	var tex: Variant = null
	if storm.half_res != null and storm.half_res.composite_material != null:
		tex = storm.half_res.composite_material.get_shader_parameter(&"body_tex")
	params[&"storm_body_tex"] = tex
	params[&"storm_body_ready"] = tex != null
	for key: StringName in params:
		storm.water.material.set_shader_parameter(key, params[key])


# --- Internals ---------------------------------------------------------------------------------


func _environment() -> Environment:
	return storm.world_environment.environment if storm.world_environment != null else null


func _cfg(section: String) -> Dictionary:
	return storm.state.config.get(section, {}) as Dictionary


func _material(shader_path: String, priority: int) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(shader_path) as Shader
	m.render_priority = priority
	return m
