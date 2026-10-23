@tool
class_name UndertowState
extends RefCounted
## Pure, headless state of one Undertow storm (M1-RND-03, SPEC §8.2 item 9). No nodes, no rendering:
## UndertowStorm owns one and pushes what it computes into the storm's materials. Unit-tested.
##
## It holds the runtime API values (intensity, rotation speed, wound intensity, approach distance),
## the storm clock, the quality tier, the deterministic lightning schedule, and GDScript mirrors of
## the shader maths that gameplay needs (sea_height, omega, wall radii). Tunables come from
## game/data/vfx/undertow.json; docs/kb/tech/undertow.md.

const CONFIG_PATH := "res://game/data/vfx/undertow.json"
const QUALITY_IDS: Array[String] = ["low", "medium", "high", "ultra"]
const BODY_RAYMARCH := "raymarch"
const BODY_SHELLS := "shells"
## = UNDERTOW_MAX_FLASHES in undertow_common.gdshaderinc (tested).
const MAX_FLASHES := 4
## Mirrors UNDERTOW_AXIS_GUARD in undertow_common.gdshaderinc.
const AXIS_GUARD := 0.25
## PCG hash (O'Neill; the RXS-M-XS 32-bit output as in Jarzynski & Olano 2020), the same family
## common.gdshaderinc uses: stable on every platform, unlike hash().
const PCG_MUL := 747796405
const PCG_INC := 2891336453
const PCG_OUT := 277803737
const PCG_SELECT_SHIFT := 28
const PCG_BASE_SHIFT := 4
const PCG_OUT_SHIFT := 22
const U32_MASK := 0xFFFFFFFF
const U32_RANGE := 4294967296.0
## Per-site hash streams (arbitrary distinct salts).
const SALT_CHANCE := 1
const SALT_START := 2
const SALT_ANGLE := 3
const SALT_HEIGHT := 4
const SALT_SITE := 7919
## Golden-ratio step of the per-frame march jitter (R1 low-discrepancy sequence): TAA integrates it.
const JITTER_STEP := 0.6180339887
## Upper bounds of the tier parameters = the body shader's uniform hint ranges (undertow_body.gdshaderinc
## march_steps hint_range(4, 128), curl_reuse hint_range(1, 8); tested). The per-variant compiled cap
## UNDERTOW_MAX_STEPS still limits the loop inside the shader.
const MAX_MARCH_STEPS := 128
const MAX_CURL_REUSE := 8
## Range of a tier's body_scale (M2-RND-01): the raymarched body's resolution fraction (UndertowHalfRes).
const MIN_BODY_SCALE := 0.25
const MAX_BODY_SCALE := 1.0

## JSON section/key -> shader uniform. Colours are handled separately (colors section).
const UNIFORM_MAP := {
	"shape":
	{
		"eye_radius_m": "eye_radius_m",
		"eye_flare": "eye_flare",
		"eye_flare_power": "eye_flare_power",
		"wall_thickness_m": "wall_thickness_m",
		"wall_taper": "wall_taper",
		"wall_softness_m": "wall_softness_m",
		"height_m": "height_m",
		"top_softness": "top_softness",
		"canopy_height_m": "canopy_height_m",
		"canopy_thickness_m": "canopy_thickness_m",
		"canopy_radius_m": "canopy_radius_m",
		"canopy_softness_m": "canopy_softness_m",
		"band_radius_m": "band_radius_m",
		"band_height_m": "band_height_m",
		"band_arms": "band_arms",
		"band_twist": "band_twist",
		"band_sharpness": "band_sharpness",
		"band_density": "band_density",
		"calm_shrink": "calm_shrink",
		"skirt_height_m": "skirt_height_m",
		"skirt_reach_m": "skirt_reach_m",
		"skirt_density": "skirt_density",
		"band_join_m": "band_join_m",
		"striation_spacing_m": "striation_spacing_m",
		"striation_starts": "striation_starts",
		"striation_strength": "striation_strength",
		"striation_sharpness": "striation_sharpness",
		"bound_margin_m": "bound_margin_m",
	},
	"noise": {"texels": "noise_texels"},
	"flow":
	{
		"rotation_falloff": "rotation_falloff",
		"cycle_s": "flow_cycle_s",
		"inflow_m_s": "inflow_m_s",
		"updraft_m_s": "updraft_m_s",
		"curl_scale_m": "curl_scale_m",
		"curl_warp_m": "curl_warp_m",
	},
	"cloud":
	{
		"noise_scale_m": "noise_scale_m",
		"detail_scale_m": "detail_scale_m",
		"detail_weight": "detail_weight",
		"coverage_bias": "coverage_bias",
		"density_per_m": "density_per_m",
		"sun_extinction": "sun_extinction",
		"ambient_occlusion": "ambient_occlusion",
		"forward_scatter": "forward_scatter",
		"back_scatter": "back_scatter",
		"scatter_mix": "scatter_mix",
		"light_step_m": "light_step_m",
		"base_darkening": "base_darkening",
		"haze_visibility_m": "haze_visibility_m",
		"albedo_gain": "albedo_gain",
		"jitter": "jitter",
		"empty_step": "empty_step",
		"dense_step": "dense_step",
		"erosion_envelope": "erosion_envelope",
		"erosion_threshold": "erosion_threshold",
		"erosion_contrast": "erosion_contrast",
		"sun_clear_height": "sun_clear_height",
		"sun_low_floor": "sun_low_floor",
		"scud_height_m": "scud_height_m",
		"scud_stretch": "scud_stretch",
		"water_wall_height_m": "water_wall_height_m",
		"water_wall_mix": "water_wall_mix",
	},
	"wounds":
	{
		"scale_m": "wound_scale_m",
		"width": "wound_width",
		"coverage": "wound_coverage",
		"skin_m": "wound_skin_m",
		"height_min": "wound_height_min",
		"height_max": "wound_height_max",
		"presence_scale_m": "wound_presence_scale_m",
		"sink_m_s": "wound_sink_m_s",
		"energy": "wound_energy",
		"pocket_energy": "pocket_energy",
		"rent_depth": "rent_depth",
	},
	"lightning":
	{
		"radius_m": "lightning_radius_m",
		"energy": "lightning_energy",
	},
	"sea":
	{
		"funnel_depth_m": "funnel_depth_m",
		"throat_radius_m": "throat_radius_m",
		"funnel_radius_m": "funnel_radius_m",
		"lip_height_m": "lip_height_m",
		"lip_radius_m": "lip_radius_m",
		"lip_width_m": "lip_width_m",
		"swell_height_m": "swell_height_m",
		"swell_scale_m": "swell_scale_m",
		"radius_m": "sea_radius_m",
		"fade_start_m": "fade_start_m",
		"lift_m": "sea_lift_m",
		"foam_scale_m": "foam_scale_m",
		"foam_streak": "foam_streak",
		"foam_amount": "foam_amount",
		"foam_pitch": "foam_pitch",
		"foam_ring_spacing_m": "foam_ring_spacing_m",
		"foam_ring_radius_m": "foam_ring_radius_m",
		"darkening": "sea_darkening",
		"reflection_dim": "sea_reflection_dim",
		"roughness": "sea_roughness",
		"throat_glow_energy": "throat_glow_energy",
		"glow_sink_m_s": "glow_sink_m_s",
	},
	"spray":
	{
		"height_m": "spray_height_m",
		"scale_m": "spray_scale_m",
		"rise_m_s": "spray_rise_m_s",
		"density": "spray_density",
		"sun": "spray_sun",
	},
}
## sea_response keys that fade with the storm's intensity (a sleeping storm leaves the sea alone).
const SEA_RESPONSE_SCALED: Array[String] = ["darken", "chop", "roughness", "streak_amount"]
## colors key -> shader uniform(s).
const COLOR_MAP := {
	"albedo": ["col_albedo"],
	"wound": ["col_wound"],
	"held": ["col_held"],
	"lightning": ["col_lightning"],
	"foam": ["col_foam", "col_spray"],
	"sea_deep": ["col_sea_deep", "col_water_wall"],
}

var config: Dictionary = {}
var time_s: float = 0.0
var intensity: float = 1.0:
	set(value):
		intensity = clamp_value("intensity", value)
var rotation_rad_s: float = 0.0:
	set(value):
		rotation_rad_s = clamp_value("rotation_rad_s", value)
var wound_intensity: float = 1.0:
	set(value):
		wound_intensity = clamp_value("wound_intensity", value)
var approach_distance_m: float = 0.0:
	set(value):
		approach_distance_m = clamp_value("approach_distance_m", value)
var time_scale: float = 1.0:
	set(value):
		time_scale = clamp_value("time_scale", value)

## Frames the clock has advanced (drives the temporal march jitter; frozen while the storm is held).
var frame: int = 0
## Whether the viewport the storm draws in accumulates over frames (TAA, or a temporal upscaler such
## as FSR2). UndertowStorm sets it every frame; without it the rotating jitter is crawling grain.
var temporal_aa: bool = true
## Named look from undertow.json "looks" ("" = the tunables alone).
var look: String = ""
var _quality: String = ""
var _forced_start: Array[float] = []


func _init(cfg: Dictionary = {}) -> void:
	config = cfg if not cfg.is_empty() else load_config()
	intensity = default_of("intensity")
	rotation_rad_s = default_of("rotation_rad_s")
	wound_intensity = default_of("wound_intensity")
	approach_distance_m = default_of("approach_distance_m")
	time_scale = default_of("time_scale")
	_forced_start.resize(MAX_FLASHES)
	_forced_start.fill(-INF)
	set_quality(str(config.get("default_quality", "high")))


static func load_config(path: String = CONFIG_PATH) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("UndertowState: cannot parse %s" % path)
		return {}
	return parsed as Dictionary


# --- API values --------------------------------------------------------------------------------


## (min, max) of a runtime API value from undertow.json "state".
func range_of(key: String) -> Vector2:
	var s := _section("state").get(key, {}) as Dictionary
	return Vector2(float(s.get("min", 0.0)), float(s.get("max", 0.0)))


func default_of(key: String) -> float:
	return float((_section("state").get(key, {}) as Dictionary).get("default", 0.0))


func clamp_value(key: String, value: float) -> float:
	var r := range_of(key)
	return clampf(value, r.x, r.y)


## Advance the storm clock by delta seconds of game time (scaled by time_scale).
func advance(delta: float) -> void:
	time_s += delta * time_scale
	frame += 1


# --- Quality -----------------------------------------------------------------------------------


func set_quality(id: String) -> bool:
	if not QUALITY_IDS.has(id) or not (_section("quality") as Dictionary).has(id):
		return false
	_quality = id
	return true


func get_quality() -> String:
	return _quality


## What a tier draws: body kind ("raymarch" or "shells"), its shader, march steps, spray layers,
## sea foam octaves and the shell set (Low).
func quality_plan(id: String = "") -> Dictionary:
	var tier_id := id if id != "" else _quality
	var tier := _section("quality").get(tier_id, {}) as Dictionary
	var shaders := _section("shaders")
	var body := str(tier.get("body", BODY_SHELLS))
	var shells := _section("shells")
	return {
		"tier": tier_id,
		"body": body,
		"body_shader": str(shaders.get("body_" + tier_id, "")) if body == BODY_RAYMARCH else "",
		"march_steps": clampi(int(tier.get("march_steps", 0)), 0, MAX_MARCH_STEPS),
		"curl_reuse": clampi(int(tier.get("curl_reuse", 1)), 1, MAX_CURL_REUSE),
		"temporal_jitter": bool(tier.get("temporal_jitter", false)),
		"body_scale": clampf(float(tier.get("body_scale", MAX_BODY_SCALE)), MIN_BODY_SCALE, MAX_BODY_SCALE),
		"spray_layers": int(tier.get("spray_layers", 1)),
		"sea_foam_octaves": int(tier.get("sea_foam_octaves", 1)),
		"shell_fractions": (shells.get("fractions", []) as Array) if body == BODY_SHELLS else [],
		"shell_canopy": bool(shells.get("canopy", false)) and body == BODY_SHELLS,
	}


## Names of the looks in undertow.json "looks".
func look_ids() -> PackedStringArray:
	var out := PackedStringArray()
	for key: String in _section("looks"):
		if not key.begins_with("_"):
			out.append(key)
	return out


## Uniforms a named look overrides ({} for "" or an unknown look). "#hex" strings become Colors.
func look_parameters(id: String) -> Dictionary:
	var out := {}
	var src := _section("looks").get(id, {}) as Dictionary
	for key: String in src:
		if key.begins_with("_"):
			continue
		var v: Variant = src[key]
		out[key] = Color.from_string(str(v), Color.MAGENTA) if v is String else float(v)
	return out


## res:// path of the baked noise lattice the raymarched body samples ("" if none).
func noise_texture_path() -> String:
	return str(_section("noise").get("texture", ""))


# --- Shape mirrors (keep in step with undertow_common.gdshaderinc / undertow_sea.gdshader) -------


func height_now() -> float:
	var sh := _section("shape")
	return float(sh.get("height_m", 0.0)) * lerpf(float(sh.get("calm_shrink", 1.0)), 1.0, intensity)


func eye_radius(h: float) -> float:
	var sh := _section("shape")
	var hc := clampf(h, 0.0, 1.0)
	var flare := float(sh.get("eye_flare", 1.0))
	return float(sh.get("eye_radius_m", 0.0)) * (1.0 + (flare - 1.0) * pow(hc, float(sh.get("eye_flare_power", 1.0))))


func wall_radius(h: float) -> float:
	var sh := _section("shape")
	var hc := clampf(h, 0.0, 1.0)
	return eye_radius(h) + float(sh.get("wall_thickness_m", 0.0)) * (1.0 - float(sh.get("wall_taper", 0.0)) * hc)


## Radius of the cylinder every storm part fits in (the raymarch proxy), margin included.
func bound_radius() -> float:
	var sh := _section("shape")
	var r := maxf(float(sh.get("canopy_radius_m", 0.0)), float(sh.get("band_radius_m", 0.0)))
	r = maxf(r, wall_radius(1.0) + float(sh.get("wall_softness_m", 0.0)))
	return r + float(sh.get("bound_margin_m", 0.0))


## Angular speed (rad/s) of the vortex at radius r (m): fastest at the eyewall.
func omega(r: float) -> float:
	var eye := float(_section("shape").get("eye_radius_m", 1.0))
	var falloff := float(_section("flow").get("rotation_falloff", 0.0))
	return rotation_rad_s * pow(eye / maxf(r, eye * AXIS_GUARD), falloff)


## Rest height (m, relative to sea level) of the maelstrom at radius r, without swell or lift.
## Mirrors sea_profile() in undertow_sea.gdshader.
func sea_height(r: float) -> float:
	var s := _section("sea")
	var k := r / float(s.get("throat_radius_m", 1.0))
	var funnel_r := float(s.get("funnel_radius_m", 1.0))
	var funnel := -float(s.get("funnel_depth_m", 0.0)) / (1.0 + k * k)
	funnel *= 1.0 - smoothstep(0.35 * funnel_r, funnel_r, r)
	var x := (r - float(s.get("lip_radius_m", 0.0))) / float(s.get("lip_width_m", 1.0))
	var lip := float(s.get("lip_height_m", 0.0)) * exp(-x * x)
	return (funnel + lip) * intensity


# --- Lightning (deterministic) -----------------------------------------------------------------


func flash_site_count() -> int:
	return mini(int(_section("lightning").get("sites", 0)), MAX_FLASHES)


## Flash level of one site at storm time t (0 = dark). Scheduled flashes come from a stable hash of
## (site, period index); a forced flash (force_flash) is added on top.
func flash_level(site: int, t: float) -> float:
	if site < 0 or site >= flash_site_count():
		return 0.0
	var lt := _section("lightning")
	var period := _site_period(site)
	var duration := float(lt.get("duration_s", 0.0))
	var k := floori(t / period)
	var level := 0.0
	if hash01(site, k, SALT_CHANCE) < float(lt.get("chance", 0.0)) * intensity:
		var start := k * period + hash01(site, k, SALT_START) * maxf(period - duration, 0.0)
		level = _pulse(t - start)
	return maxf(level, _pulse(t - _forced_start[site]))


func flash_levels(t: float) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	out.resize(MAX_FLASHES)
	for i in flash_site_count():
		out[i] = flash_level(i, t)
	return out


## Storm-local positions of the lightning sites at time t (xyz) and their levels (w). Sites sit in
## the middle of the eyewall and ride its rotation.
func flash_sites(t: float) -> PackedVector4Array:
	var lt := _section("lightning")
	var out := PackedVector4Array()
	out.resize(MAX_FLASHES)
	var h_min := float(lt.get("height_min", 0.0))
	var h_max := float(lt.get("height_max", 1.0))
	var eye := float(_section("shape").get("eye_radius_m", 1.0))
	for i in flash_site_count():
		var k := floori(t / _site_period(i))
		var h := lerpf(h_min, h_max, hash01(i, k, SALT_HEIGHT))
		var r := 0.5 * (eye_radius(h) + wall_radius(h))
		var a := hash01(i, k, SALT_ANGLE) * TAU + omega(eye) * t
		out[i] = Vector4(r * cos(a), h * height_now(), r * sin(a), flash_level(i, t))
	return out


## Strike one site now (start_s < 0) or at storm time start_s. Cutscenes use it to time a flash.
func force_flash(site: int, start_s: float = -1.0) -> bool:
	if site < 0 or site >= flash_site_count():
		return false
	_forced_start[site] = start_s if start_s >= 0.0 else time_s
	return true


func clear_forced_flashes() -> void:
	_forced_start.fill(-INF)


## Stable hash of (a, b, salt) in [0, 1).
static func hash01(a: int, b: int, salt: int) -> float:
	var v := _pcg((a * SALT_SITE + salt) & U32_MASK)
	v = _pcg((v + b) & U32_MASK)
	return float(v) / U32_RANGE


# --- Shader parameters -------------------------------------------------------------------------


## Uniforms that only change with the tunables (shape, flow, look, colours) for every storm shader.
func static_parameters() -> Dictionary:
	var out := {}
	for section: String in UNIFORM_MAP:
		var src := _section(section)
		var keys := UNIFORM_MAP[section] as Dictionary
		for key: String in keys:
			if src.has(key):
				out[keys[key]] = float(src[key])
	var colors := _section("colors")
	for key: String in COLOR_MAP:
		for uniform_name: String in COLOR_MAP[key]:
			out[uniform_name] = Color.from_string(str(colors.get(key, "")), Color.MAGENTA)
	var plan := quality_plan()
	out["march_steps"] = int(plan["march_steps"])
	out["curl_reuse"] = int(plan["curl_reuse"])
	out.merge(look_parameters(look), true)
	out["foam_octaves"] = int(plan["sea_foam_octaves"])
	return out


## Water-material uniforms of the zone sea's storm response (undertow.json "sea_response"; the
## water shader's "storm" group). The darkening, chop and streaks scale with the storm's intensity.
func sea_response_parameters() -> Dictionary:
	var src := _section("sea_response")
	var out := {}
	for key: String in src:
		if key.begins_with("_"):
			continue
		var v := float(src[key])
		out["storm_" + key] = v * intensity if SEA_RESPONSE_SCALED.has(key) else v
	return out


## Uniforms that change every frame: the clock, the API values and the lightning sites.
func dynamic_parameters() -> Dictionary:
	return {
		"storm_time_s": time_s,
		"storm_intensity": intensity,
		"rotation_rad_s": rotation_rad_s,
		"wound_intensity": wound_intensity,
		"lightning_sites": flash_sites(time_s),
		"jitter_phase": jitter_phase(),
	}


## Per-frame rotation of the raymarch's start offset: an R1 sequence over frames, so TAA averages
## several step phases (M1-RND-10). 0 (a static pattern) when the tier has no temporal jitter or the
## viewport has no temporal AA (M1-RND-11). Frozen while held.
func jitter_phase() -> float:
	if not temporal_aa or not bool(quality_plan()["temporal_jitter"]):
		return 0.0
	return fposmod(frame * JITTER_STEP, 1.0)


# --- Internals ---------------------------------------------------------------------------------


func _section(key: String) -> Dictionary:
	return config.get(key, {}) as Dictionary


func _site_period(site: int) -> float:
	var lt := _section("lightning")
	return float(lt.get("period_s", 1.0)) * (1.0 + float(lt.get("period_spread", 0.0)) * site)


# A flash: a bright stroke decaying over decay_s, and a weaker re-strike restrike_s later.
func _pulse(tau: float) -> float:
	var lt := _section("lightning")
	if tau < 0.0 or tau >= float(lt.get("duration_s", 0.0)):
		return 0.0
	var decay := float(lt.get("decay_s", 1.0))
	var level := exp(-tau / decay)
	var restrike := float(lt.get("restrike_s", 0.0))
	if tau >= restrike:
		level += float(lt.get("restrike_gain", 0.0)) * exp(-(tau - restrike) / decay)
	return level


static func _pcg(v: int) -> int:
	var state := (v * PCG_MUL + PCG_INC) & U32_MASK
	var word := (((state >> ((state >> PCG_SELECT_SHIFT) + PCG_BASE_SHIFT)) ^ state) * PCG_OUT) & U32_MASK
	return ((word >> PCG_OUT_SHIFT) ^ word) & U32_MASK
