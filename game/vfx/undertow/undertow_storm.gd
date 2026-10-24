@tool
class_name UndertowStorm
extends Node3D
## The Undertow: a colossal storm of the unreleased dead (M1-RND-03, SPEC §8.2 item 9).
## Docs: docs/kb/tech/undertow.md. Tunables: game/data/vfx/undertow.json. Logic: UndertowState.
##
## Place one per zone or cutscene. This node marks the point the storm approaches (a village, the
## Kite); the storm itself sits approach_distance_m away along approach_azimuth_deg. Its sea level is
## sea_level() (the zone water's rest plane, or sea_level_y), never the node's Y, so the marker may sit
## on a headland. Keep the node unrotated and unscaled: the storm is built in world axes.
## @tool: in the editor it builds at editor_preview_quality (Low shells by default, no raymarch) with
## its clock stopped, plus a footprint gizmo (eye, wall, funnel, lid and bound circles, eye axis).
## It builds, under a top-level child:
##   Sea     the maelstrom funnel disc (every tier); SeaLid, a depth-only disc that keeps the zone's
##           WaterSurface from drawing over the funnel (no rebuild when the storm moves)
##   Body    raymarched volume on a proxy cylinder (Medium+), or Shell* lathe shells (Low)
##   Spray*  spray curtains where the sea is torn into the wall (every tier)
##
## API (typed; everything but the meshes is headless-testable):
##   intensity, rotation_rad_s, wound_intensity, approach_distance_m, approach_azimuth_deg
##   get_time() / set_time(t) / playing / time_scale the storm clock (never TIME)
##   set_quality(id) / get_quality() / apply_graphics_settings(gs)
##   force_flash(site, start_s)                     time a lightning stroke in a cutscene
##   site_facing(point)                             the site to strike so its bolt lands in view
##   storm_center() / sea_level() / sea_height_at(world_xz)   placement and the funnel for floaters
##   look                                           named look from undertow.json ("day_storm")
##   preset / apply_preset(id)                      chapter preset from undertow.json "presets" (M2-RND-05)
##   unbinding                                      the Letting, 0 held .. 1 released (Ch21; M2-RND-05)
##   rain_amount, zone_shadow, exposure_flash, world_environment   storm events on the zone (M2-RND-05,
##                                                  UndertowEvents: streamers, bolts, rain, shadow, reflection)
##   lightning_struck(site, bolt)                   a strike began (bolt: a stroke is drawn)
##   refresh()                                      re-apply after changing tunables at runtime
##   on_viewport_state_changed()                    re-reads the viewport's AA now (M1-RND-16: a
##                                                  GraphicsSettings.push_override at a cut calls it
##                                                  through VIEWPORT_STATE_GROUP, so the temporal
##                                                  jitter gate follows the override frame-exactly)

signal quality_changed(tier: String)
## A lightning strike began at `site` (M2-RND-05); `bolt` is whether it draws a stroke (else in-cloud).
signal lightning_struck(site: int, bolt: bool)

const VISUALS_NODE := "UndertowVisuals"
const SEA_NODE := "Sea"
const LID_NODE := "SeaLid"
const BODY_NODE := "Body"
const SHELL_NODE := "Shell"
const SPRAY_NODE := "Spray"
const EVENTS_NODE := "Events"
const PARAM_DEEP := &"col_deep"
const PARAM_STORM_CENTER_XZ := &"storm_center_xz"
const PARAM_STORM_REACH := &"storm_reach_m"
const PARAM_FOAM := &"col_foam"
const PARAM_SEA_GLOW := &"sea_glow_energy"
## 3D scaling modes that accumulate history like TAA (M1-RND-15).
const TEMPORAL_SCALING_MODES: Array[int] = [
	Viewport.SCALING_3D_MODE_FSR2,
	Viewport.SCALING_3D_MODE_METALFX_TEMPORAL,
]
const PARAM_NOISE_TEX := &"noise_tex"
## Radial segments of the raymarch proxy (the shader clips rays analytically; this only has to
## cover the silhouette).
const PROXY_SEGMENTS := 48
## Sea disc AABB head-room above sea level (m) for the lip and swell.
const SEA_AABB_TOP_M := 200.0
const GIZMO_NODE := "EditorFootprint"
const GIZMO_SEGMENTS := 96
const GIZMO_COLOR := Color(0.25, 0.88, 0.78)

@export_range(0.0, 1.0, 0.01) var intensity: float = 1.0:
	set(value):
		state.intensity = value
		intensity = state.intensity
@export_range(0.0, 0.12, 0.001, "suffix:rad/s") var rotation_rad_s: float = 0.012:
	set(value):
		state.rotation_rad_s = value
		rotation_rad_s = state.rotation_rad_s
@export_range(0.0, 4.0, 0.01) var wound_intensity: float = 1.0:
	set(value):
		state.wound_intensity = value
		wound_intensity = state.wound_intensity
@export_range(0.0, 60000.0, 1.0, "suffix:m") var approach_distance_m: float = 0.0:
	set(value):
		state.approach_distance_m = value
		approach_distance_m = state.approach_distance_m
		_place()
## Direction from this node toward the storm: azimuth clockwise from north (-Z), degrees.
@export_range(0.0, 360.0, 0.1, "suffix:deg") var approach_azimuth_deg: float = 0.0:
	set(value):
		approach_azimuth_deg = value
		_place()
## Graphics preset id ("low" .. "ultra"); empty = undertow.json default_quality. Setting it at
## runtime switches the tier (same as set_quality).
@export var quality: String = "":
	set(value):
		quality = value
		if is_inside_tree() and not Engine.is_editor_hint() and value != state.get_quality():
			set_quality(value)
## Named look from undertow.json "looks" ("" = the tunables): e.g. "day_storm" for daylight shots.
@export var look: String = "":
	set(value):
		look = value
		state.look = value
		_push_static()
## Tier the editor previews (the raymarched tiers are heavy for a viewport that redraws constantly).
@export var editor_preview_quality: String = "low"
## Chapter preset from undertow.json "presets" (M2-RND-05): storm property -> value, applied when set
## ("" = none). A cutscene tweens from one preset's values to the next.
@export var preset: String = "":
	set(value):
		preset = value
		if value != "":
			apply_preset(value)
## The Letting (Ch21, colour script rule 1; M2-RND-05): 0 = held (the wounds and their light sink),
## 1 = released (they rise in glimmer_lift). Tween it; see UndertowState.unbinding.
@export_range(0.0, 1.0, 0.01) var unbinding: float = 0.0:
	set(value):
		state.unbinding = value
		unbinding = state.unbinding

@export_group("Events")
## Near-field rain at the camera (M2-RND-05): -1 = from the camera's distance to the eye (undertow.json
## "rain"), else this amount (0..1).
@export_range(-1.0, 1.0, 0.01) var rain_amount: float = -1.0
## Dim the zone's key light and ambient when the storm shades the zone marker (this node).
@export var zone_shadow: bool = true
## The colour script's lightning frames: the zone Environment's exposure jumps at a strike
## (undertow.json "exposure_flash"; capped like battle flashes, gentler under reduced motion).
@export var exposure_flash: bool = true
## The zone's environment: its ambient for the zone shadow, its exposure for the lightning frames.
@export var world_environment: WorldEnvironment

@export_group("Sea level")
## World Y of the storm's sea surface when it is not taken from `water` (see sea_level()).
@export var sea_level_y: float = 0.0:
	set(value):
		sea_level_y = value
		_place()
## Take sea level from the zone `water` (its rest plane, WaterSurface's global Y) when it is set.
@export var sea_level_from_water: bool = true:
	set(value):
		sea_level_from_water = value
		_place()

@export_group("Clock")
## Advance the storm clock in _process. Off = the clock only moves through set_time().
@export var playing: bool = true
@export_range(0.0, 8.0, 0.01) var time_scale: float = 1.0:
	set(value):
		state.time_scale = value
		time_scale = state.time_scale
@export var start_time_s: float = 0.0

@export_group("Scene")
## The zone's ocean: its look is copied into the funnel, and the lid clears it over the funnel.
@export var water: WaterSurface
## Resolution fraction of the raymarched body (M2-RND-01, UndertowHalfRes): -1 = the quality tier's
## body_scale (undertow.json; 0.5 on Medium, 0.35 on High, 1 on Ultra), else this value (1 = full resolution).
@export_range(-1.0, 1.0) var half_res_body_scale: float = -1.0:
	set(value):
		half_res_body_scale = value
		if _built:
			_build()
## Whether the half-res body marches as a compute pass on the game view (M2-RND-01, UndertowBodyEffect:
## exact occlusion) where a RenderingDevice allows it. false = the SubViewport path (diagnosis and the
## A/B control; its occlusion is analytic and misses geometry inside the wall's foot).
@export var half_res_compute: bool = true:
	set(value):
		half_res_compute = value
		if half_res != null:
			half_res.teardown()
			half_res.queue_free()
			half_res = null
		if _built:
			_build()
## The zone's key light (sun or moon): its colour and energy light the storm.
@export var sun: DirectionalLight3D
@export var ambient_top: Color = Color("#6F7E8E")
@export var ambient_bottom: Color = Color("#0E4A55")
@export_range(0.0, 8.0, 0.01) var ambient_energy: float = 1.0
## Aerial-perspective colour: match the zone's fog/horizon colour.
@export var haze_color: Color = Color("#8A8790")
## Aerial-perspective visibility (m); 0 = undertow.json cloud.haze_visibility_m.
@export_range(0.0, 200000.0, 100.0, "suffix:m") var haze_visibility_m: float = 0.0
## Held motes torn off the wounds (GlimmerField); drawn after the storm.
@export var motes: GlimmerField

var state: UndertowState = UndertowState.new()
var visuals: Node3D
var sea: MeshInstance3D
var body: MeshInstance3D
var sea_material: ShaderMaterial
var body_material: ShaderMaterial
## The half-resolution body renderer while half_res_body_scale < 1 (else null).
var half_res: UndertowHalfRes
var shell_materials: Array[ShaderMaterial] = []
var spray_materials: Array[ShaderMaterial] = []
var lid: MeshInstance3D
var lid_material: ShaderMaterial
## Streamers, bolts, rain and the storm's hold on the zone (M2-RND-05; null in the editor).
var events: UndertowEvents

var _shells: Array[MeshInstance3D] = []
var _sprays: Array[MeshInstance3D] = []
var _built: bool = false
var _noise_tex: Texture3D


func _ready() -> void:
	state.time_s = start_time_s
	if Engine.is_editor_hint():
		# Preview only: never write the preview tier into the saved `quality`.
		if not _use_quality(editor_preview_quality):
			_use_quality(str(state.config.get("default_quality", "")))
		_build_gizmo()
		_place()
		return
	if not set_quality(quality if quality != "" else str(state.config.get("default_quality", ""))):
		push_warning("UndertowStorm: unknown quality '%s', using default" % quality)
		set_quality(str(state.config.get("default_quality", "")))
	_place()


func _update_half_res(body_priority: int) -> void:
	var scale := body_scale()
	var want := scale < 1.0 and body != null and body.visible and not Engine.is_editor_hint()
	if not want:
		if half_res != null:
			half_res.teardown()
			half_res.queue_free()
			half_res = null
		return
	if half_res == null:
		half_res = UndertowHalfRes.new()
		half_res.name = "HalfRes"
		add_child(half_res, false, Node.INTERNAL_MODE_FRONT)
		half_res.scale = scale
		half_res.allow_compute = half_res_compute
		half_res.setup(visuals, body, body_priority)
	half_res.scale = scale


## The body's resolution fraction in use: the export when set (>= 0), else the tier's body_scale.
func body_scale() -> float:
	if half_res_body_scale >= 0.0:
		return clampf(half_res_body_scale, UndertowState.MIN_BODY_SCALE, UndertowState.MAX_BODY_SCALE)
	return float(state.quality_plan()["body_scale"])


## Storm-local radius of the wall's foot (eye + wall + skirt): where the composite's occlusion starts.
func _wall_foot_radius() -> float:
	var sh := state.config.get("shape", {}) as Dictionary
	return (
		float(sh.get("eye_radius_m", 0.0))
		+ float(sh.get("wall_thickness_m", 0.0))
		+ float(sh.get("skirt_reach_m", 0.0))
	)


## A storm that leaves the tree takes its hold on the zone sea with it.
func _exit_tree() -> void:
	_clear_sea_response()


func _enter_tree() -> void:
	add_to_group(GraphicsSettings.VIEWPORT_STATE_GROUP)


## M1-RND-16: the viewport's AA or 3D scaling just changed (a scoped override was pushed or popped):
## re-gate the temporal jitter and push the dynamic uniforms now, not on the next _process.
func on_viewport_state_changed() -> void:
	_push_dynamic()


func _process(delta: float) -> void:
	if playing and not Engine.is_editor_hint():
		state.advance(delta)
	_place()
	_push_dynamic()
	if events != null:
		events.update()


# --- Clock -------------------------------------------------------------------------------------


func get_time() -> float:
	return state.time_s


func set_time(t: float) -> void:
	state.time_s = t
	_push_dynamic()


# --- Placement ---------------------------------------------------------------------------------


## Unit vector for an azimuth clockwise from north (-Z), with east = +X.
static func direction_from_azimuth(azimuth_deg: float) -> Vector3:
	var a := deg_to_rad(azimuth_deg)
	return Vector3(sin(a), 0.0, -cos(a))


## World position of the eye at sea level.
func storm_center() -> Vector3:
	var origin := global_position if is_inside_tree() else position
	var c := origin + direction_from_azimuth(approach_azimuth_deg) * approach_distance_m
	return Vector3(c.x, sea_level(), c.z)


## World Y of the storm's sea surface: the zone water's rest plane when `water` is set and
## sea_level_from_water is on, else sea_level_y. Independent of this node's Y.
func sea_level() -> float:
	if sea_level_from_water and water != null:
		return water.global_position.y if water.is_inside_tree() else water.position.y
	return sea_level_y


## World Y of the maelstrom's rest surface (no swell) at world point (xz.x, xz.y).
func sea_height_at(world_xz: Vector2) -> float:
	var c := storm_center()
	return c.y + state.sea_height(world_xz.distance_to(Vector2(c.x, c.z)))


# --- Quality -----------------------------------------------------------------------------------


func set_quality(id: String) -> bool:
	if not _use_quality(id):
		return false
	quality = id
	quality_changed.emit(id)
	return true


func _use_quality(id: String) -> bool:
	if not state.set_quality(id):
		return false
	_build()
	_push_static()
	_push_dynamic()
	return true


func get_quality() -> String:
	return state.get_quality()


func apply_graphics_settings(settings: GraphicsSettings) -> bool:
	return settings != null and set_quality(settings.preset_id)


## Every material the storm draws with on the current tier (prewarm and tests use it).
func materials() -> Array[ShaderMaterial]:
	var out: Array[ShaderMaterial] = []
	if sea_material != null:
		out.append(sea_material)
	if body_material != null:
		out.append(body_material)
	out.append_array(shell_materials)
	out.append_array(spray_materials)
	if events != null:
		out.append_array(events.all_materials())
	return out


# --- Cutscene helpers --------------------------------------------------------------------------


## The lightning site that faces `point` now (the smallest angle between the site and the direction
## from the eye toward point): a cutscene strikes it so its bolt lands in view (M2-RND-05; a bolt only
## draws on the camera's half of the storm).
func site_facing(point: Vector3) -> int:
	var c := storm_center()
	var to := Vector2(point.x - c.x, point.z - c.z).normalized()
	var sites := state.flash_sites(state.time_s)
	var best := 0
	var best_dot := -INF
	for i in state.flash_site_count():
		var d := Vector2(sites[i].x, sites[i].z).normalized().dot(to)
		if d > best_dot:
			best_dot = d
			best = i
	return best


func force_flash(site: int, start_s: float = -1.0) -> bool:
	var ok := state.force_flash(site, start_s)
	_push_dynamic()
	return ok


## Applies a chapter preset (undertow.json "presets"): each key is a storm property. False if unknown.
func apply_preset(id: String) -> bool:
	var values := state.preset(id)
	if values.is_empty():
		push_warning("UndertowStorm: unknown preset '%s'" % id)
		return false
	for key: String in values:
		set(key, values[key])
	return true


func refresh() -> void:
	_build()
	_push_static()
	_push_dynamic()


## The uniforms the scene pushes on top of the tunables: the key light and the zone's mood.
func mood_parameters() -> Dictionary:
	var cloud := state.config.get("cloud", {}) as Dictionary
	var sun_col := Color.BLACK
	var sun_e := 0.0
	if sun != null and sun.visible:
		sun_col = sun.light_color
		# The storm is lit by the zone's undimmed key: the zone shadow is the storm's own (M2-RND-05).
		sun_e = events.sun_energy() if events != null else sun.light_energy
	return {
		"col_sun": sun_col,
		"sun_energy": sun_e * float(cloud.get("sun_energy", 1.0)),
		"col_ambient_top": ambient_top,
		"col_ambient_bottom": ambient_bottom,
		"ambient_energy": ambient_energy * float(cloud.get("ambient_energy", 1.0)),
		"col_haze": haze_color,
		"haze_visibility_m":
		haze_visibility_m if haze_visibility_m > 0.0 else float(cloud.get("haze_visibility_m", 1.0)),
	}


## Height of the depth-only lid above the storm's sea level: the disc's lift plus the highest crest
## the zone's waves can reach (WaterSurface wave amplitudes), plus a margin.
func lid_height() -> float:
	var s := state.config.get("sea", {}) as Dictionary
	var ld := state.config.get("lid", {}) as Dictionary
	# In the editor `water` is a placeholder (WaterSurface is not @tool): no waves() to ask.
	var crest := water.waves().amplitude_sum if water != null and not Engine.is_editor_hint() else 0.0
	return float(s.get("lift_m", 0.0)) + crest + float(ld.get("margin_m", 0.0))


## Look parameters copied from the zone's WaterSurface material (empty without one).
func water_parameters() -> Dictionary:
	var out := {}
	if water == null:
		return out
	out[PARAM_SEA_GLOW] = water.sea_glow_energy
	if water.material != null:
		var deep: Variant = water.material.get_shader_parameter(PARAM_DEEP)
		if deep is Color:
			out[&"col_sea_deep"] = deep
			out[&"col_water_wall"] = deep
		var foam: Variant = water.material.get_shader_parameter(PARAM_FOAM)
		if foam is Color:
			out[PARAM_FOAM] = foam
	return out


# --- Internals ---------------------------------------------------------------------------------


func _place() -> void:
	if visuals != null:
		visuals.global_position = storm_center()


func _build() -> void:
	if not is_inside_tree():
		return
	var plan := state.quality_plan()
	var shaders := state.config.get("shaders", {}) as Dictionary
	var prio := state.config.get("render_priority", {}) as Dictionary
	if visuals == null:
		visuals = Node3D.new()
		visuals.name = VISUALS_NODE
		visuals.top_level = true
		add_child(visuals, false, Node.INTERNAL_MODE_FRONT)
	_place()
	var bound := state.bound_radius()
	var full_height := float((state.config.get("shape", {}) as Dictionary).get("height_m", 0.0))
	# Sea (every tier).
	if sea == null:
		var s := state.config.get("sea", {}) as Dictionary
		var sea_r := float(s.get("radius_m", 1.0))
		sea = MeshInstance3D.new()
		sea.name = SEA_NODE
		sea.mesh = UndertowMeshBuilder.sea_disc(
			sea_r, int(s.get("rings", 1)), int(s.get("segments", 3)), float(s.get("ring_power", 1.0))
		)
		var depth := float(s.get("funnel_depth_m", 0.0)) + SEA_AABB_TOP_M
		sea.custom_aabb = AABB(
			Vector3(-sea_r, -depth, -sea_r), Vector3(2.0 * sea_r, depth + SEA_AABB_TOP_M, 2.0 * sea_r)
		)
		sea.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		sea_material = _material(str(shaders.get("sea", "")), 0)
		sea.material_override = sea_material
		visuals.add_child(sea)
		var ld := state.config.get("lid", {}) as Dictionary
		var lid_r := float(s.get("fade_start_m", sea_r))
		lid = MeshInstance3D.new()
		lid.name = LID_NODE
		lid.mesh = UndertowMeshBuilder.sea_disc(lid_r, 1, int(ld.get("segments", 3)), 1.0)
		lid.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		lid_material = _material(str(shaders.get("lid", "")), int(prio.get("lid", 0)))
		lid.material_override = lid_material
		visuals.add_child(lid)
	# Body: raymarch or shells.
	var raymarch := str(plan["body"]) == UndertowState.BODY_RAYMARCH
	if raymarch:
		if body == null:
			body = MeshInstance3D.new()
			body.name = BODY_NODE
			body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			visuals.add_child(body)
		body.mesh = UndertowMeshBuilder.proxy(bound, full_height, PROXY_SEGMENTS)
		body.position = Vector3(0.0, full_height * 0.5, 0.0)
		var path := str(plan["body_shader"])
		if body_material == null or body_material.shader == null or body_material.shader.resource_path != path:
			body_material = _material(path, int(prio.get("body", 0)))
		body.material_override = body_material
		body.visible = true
		_update_half_res(int(prio.get("body", 0)))
	elif body != null:
		body.visible = false
		# Shells: no half-res body (the compute effect would otherwise keep marching the hidden body).
		_update_half_res(int(prio.get("body", 0)))
	_build_shells(plan, bound, full_height, str(shaders.get("shell", "")), int(prio.get("shells", 0)))
	_build_sprays(
		int(plan["spray_layers"]),
		str(shaders.get("spray", "")),
		int(prio.get("spray", 0)),
		int(prio.get("spray_outer", prio.get("spray", 0)))
	)
	# In the editor `motes` is a placeholder (GlimmerField is not @tool).
	if motes != null and not Engine.is_editor_hint() and motes.draw_material != null:
		motes.draw_material.render_priority = int(prio.get("motes", 0))
	if not Engine.is_editor_hint():
		if events == null:
			events = UndertowEvents.new()
			events.name = EVENTS_NODE
			add_child(events, false, Node.INTERNAL_MODE_FRONT)
		events.build(self)
	_built = true


func _build_shells(plan: Dictionary, bound: float, height: float, shader_path: String, prio: int) -> void:
	var fractions := plan["shell_fractions"] as Array
	var want := fractions.size() + (1 if bool(plan["shell_canopy"]) else 0)
	var sh := state.config.get("shells", {}) as Dictionary
	while _shells.size() < want:
		var mi := MeshInstance3D.new()
		mi.name = "%s%d" % [SHELL_NODE, _shells.size()]
		mi.mesh = UndertowMeshBuilder.unit_tube(int(sh.get("rings", 1)), int(sh.get("segments", 3)))
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var mat := _material(shader_path, prio)
		mi.material_override = mat
		visuals.add_child(mi)
		_shells.append(mi)
		shell_materials.append(mat)
	for i in _shells.size():
		var on := i < want
		_shells[i].visible = on
		_shells[i].custom_aabb = AABB(Vector3(-bound, 0.0, -bound), Vector3(2.0 * bound, height, 2.0 * bound))
		if on:
			var canopy := i >= fractions.size()
			shell_materials[i].set_shader_parameter(&"shell_kind", 1 if canopy else 0)
			shell_materials[i].set_shader_parameter(&"shell_fraction", 0.0 if canopy else float(fractions[i]))
			shell_materials[i].set_shader_parameter(&"alpha_cut", float(sh.get("alpha_cut", 0.5)))
	while shell_materials.size() > _shells.size():
		shell_materials.pop_back()


## Layer 0 is the outer curtain, in front of the wall's foot: it draws after the body (the body
## ignores depth, so it would cover it) and only its near half (the far half is behind the wall).
func _build_sprays(layers: int, shader_path: String, prio: int, outer_prio: int) -> void:
	var sp := state.config.get("spray", {}) as Dictionary
	var radii: Array[float] = [float(sp.get("outer_radius_m", 1.0)), float(sp.get("inner_radius_m", 1.0))]
	var sh := state.config.get("shells", {}) as Dictionary
	while _sprays.size() < radii.size():
		var mi := MeshInstance3D.new()
		mi.name = "%s%d" % [SPRAY_NODE, _sprays.size()]
		mi.mesh = UndertowMeshBuilder.unit_tube(1, int(sh.get("segments", 3)))
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var outer := _sprays.is_empty()
		var mat := _material(shader_path, outer_prio if outer else prio)
		mat.set_shader_parameter(&"spray_radius_m", radii[_sprays.size()])
		mat.set_shader_parameter(&"spray_front_only", outer)
		mi.material_override = mat
		var r := radii[_sprays.size()]
		var h := float(sp.get("height_m", 1.0))
		mi.custom_aabb = AABB(Vector3(-r, 0.0, -r), Vector3(2.0 * r, h, 2.0 * r))
		visuals.add_child(mi)
		_sprays.append(mi)
		spray_materials.append(mat)
	for i in _sprays.size():
		_sprays[i].visible = i < layers


func _material(shader_path: String, priority: int) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(shader_path) as Shader
	m.render_priority = priority
	return m


func _push_static() -> void:
	if not _built:
		return
	var params := state.static_parameters()
	params.merge(water_parameters(), true)
	for m in _active_materials():
		_set_all(m, params)
	if body_material != null:
		body_material.set_shader_parameter(PARAM_NOISE_TEX, _noise_texture())
	# The Low shells read the same lattice (M2-RND-08).
	for m in shell_materials:
		m.set_shader_parameter(PARAM_NOISE_TEX, _noise_texture())
	if lid_material != null:
		lid_material.set_shader_parameter(&"lid_height_m", lid_height())


func _push_dynamic() -> void:
	if not _built:
		return
	if half_res != null:
		var top := float((state.config.get("shape", {}) as Dictionary).get("height_m", 0.0))
		half_res.set_occluder(storm_center(), _wall_foot_radius(), top)
	state.temporal_aa = viewport_is_temporal(get_viewport() if is_inside_tree() else null)
	var params := state.dynamic_parameters()
	params["storm_center"] = storm_center()
	params.merge(mood_parameters(), true)
	if water != null:
		params[PARAM_SEA_GLOW] = water.sea_glow_energy
	for m in _active_materials():
		_set_all(m, params)
	_push_sea_response()


## The zone sea answers the storm (M2-RND-01): undertow.json "sea_response" onto the water's
## material, centred on the storm and scaled by its intensity. Cleared when the storm leaves.
func _push_sea_response() -> void:
	if water == null or water.material == null:
		return
	for key: String in state.sea_response_parameters():
		water.material.set_shader_parameter(key, state.sea_response_parameters()[key])
	var c := storm_center()
	water.material.set_shader_parameter(PARAM_STORM_CENTER_XZ, Vector2(c.x, c.z))


func _clear_sea_response() -> void:
	if water != null and water.material != null:
		water.material.set_shader_parameter(PARAM_STORM_REACH, 0.0)


## Editor-only footprint gizmo under the visuals (internal, so it is never saved with the scene).
func _build_gizmo() -> void:
	if visuals == null or visuals.has_node(GIZMO_NODE):
		return
	var sea_cfg := state.config.get("sea", {}) as Dictionary
	var radii := PackedFloat32Array(
		[
			state.eye_radius(0.0),
			state.wall_radius(0.0),
			float(sea_cfg.get("funnel_radius_m", 0.0)),
			float(sea_cfg.get("fade_start_m", 0.0)),
			state.bound_radius(),
		]
	)
	var gizmo := MeshInstance3D.new()
	gizmo.name = GIZMO_NODE
	gizmo.mesh = UndertowMeshBuilder.footprint(radii, state.height_now(), GIZMO_SEGMENTS)
	gizmo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = GIZMO_COLOR
	mat.no_depth_test = true
	gizmo.material_override = mat
	visuals.add_child(gizmo, false, Node.INTERNAL_MODE_FRONT)


## True when `vp` accumulates frames: TAA, or a temporal upscaler that replaces it (FSR2, or MetalFX
## temporal on macOS: not offered by the presets today, listed so the gate never drops jitter if it
## is). A null viewport counts as temporal (headless tests, before the node is in a tree).
static func viewport_is_temporal(vp: Viewport) -> bool:
	if vp == null:
		return true
	return vp.use_taa or TEMPORAL_SCALING_MODES.has(vp.scaling_3d_mode)


## The baked noise lattice (undertow.json "noise"), loaded once.
func _noise_texture() -> Texture3D:
	if _noise_tex == null and state.noise_texture_path() != "":
		_noise_tex = load(state.noise_texture_path()) as Texture3D
	return _noise_tex


func _active_materials() -> Array[ShaderMaterial]:
	var out: Array[ShaderMaterial] = []
	if sea_material != null:
		out.append(sea_material)
	if body_material != null and body != null and body.visible:
		out.append(body_material)
	for i in _shells.size():
		if _shells[i].visible:
			out.append(shell_materials[i])
	for i in _sprays.size():
		if _sprays[i].visible:
			out.append(spray_materials[i])
	if events != null:
		out.append_array(events.materials())
	return out


func _set_all(m: ShaderMaterial, params: Dictionary) -> void:
	for key: Variant in params:
		m.set_shader_parameter(StringName(str(key)), params[key])
