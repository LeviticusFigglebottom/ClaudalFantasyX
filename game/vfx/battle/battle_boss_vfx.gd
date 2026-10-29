class_name BattleBossVfx
extends Node3D
## A boss's set piece (M2-RND-04, the Drownbell). Docs: docs/kb/tech/battle_vfx.md "The Drownbell".
## - **Listens only**, like BattleBossHud: the engine's boss signals (battle_ctb.md "VFX hook points") drive
##   it, and it never writes combat state. BattleVfx attaches it when the encounter has a boss row in
##   game/data/vfx/battle/boss_vfx.json, so the controller needs no new line.
## - **Moments:**
##   - the toll's telegraph (a rim glow that builds per turn of the charge, gathering motes);
##   - the toll (a shockwave ring over the water and a capped flash);
##   - rim hits and the break (sparks, then a cyan burst);
##   - the Flood phase (the flood rig: the water rises, the key light falls, sea-glow rises);
##   - polyps (a cyan light each under the water, a mend stream to the bell);
##   - Call Ilun (Floodnet: a steady bound-light net, then the water falls back).
##   The bell's death plays effects.json's ko_overrides (motes slide seaward), through BattleVfx.
## - **The flood rig** is the battle scene's one hymn_water_level publisher (M1-RND-15): a WaterSurface that
##   publishes and moves. Leaving the tree resets the global (WaterSurface._exit_tree).

const DATA_PATH := "res://game/data/vfx/battle/boss_vfx.json"
const SHOCKWAVE_SHADER := "res://game/shaders/vfx/battle_shockwave.gdshader"
const FLOODNET_SHADER := "res://game/shaders/vfx/battle_floodnet.gdshader"
const GLOBAL_WIND := &"hymn_wind"

static var _data_cache: Dictionary = {}

## The boss's row of boss_vfx.json.
var cfg: Dictionary = {}
var vfx: BattleVfx
var bell_id: StringName = &""
## The flood water (null when the boss has no flood).
var water: WaterSurface
var glow: OmniLight3D
var ring: MeshInstance3D
var net: MeshInstance3D
var net_light: OmniLight3D
## Polyp id -> its OmniLight3D.
var polyp_lights: Dictionary = {}
## The water's target height now (from_m, or to_m while the flood is up).
var flood_target_m := 0.0
## Moments played, in order (tests and tools): &"telegraph", &"toll", &"rim_hit", &"rim_break", &"flood",
## &"polyp", &"mend", &"floodnet".
var moments: Array[StringName] = []
var _ctl: BattleController
var _engine: BattleEngine
var _glow_level := 0.0
var _charge_total := 0
var _glow_tween: Tween
var _water_tween: Tween
var _ring_tween: Tween
var _net_tween: Tween
var _sun_tween: Tween
var _sun: DirectionalLight3D
var _sun_energy := 0.0
var _hidden: Array[Node3D] = []
var _wind_before: Variant = null


static func load_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = parsed as Dictionary
		else:
			push_warning("BattleBossVfx: cannot read %s" % DATA_PATH)
	return _data_cache


## The first enemy of `engine` with a boss row, or null.
static func boss_of(engine: BattleEngine) -> BattleCombatant:
	var bosses := load_data().get("bosses", {}) as Dictionary
	for c: BattleCombatant in engine.enemies:
		var row: Variant = bosses.get(BattleVfx.base_id(c.id), null)
		if row != null and str((row as Dictionary).get("kind", "")) != BattleBossSetPiece.KIND:  # M3-BPR-420
			return c
	return null


## Builds the set piece under `player` when the encounter has a boss row (else null).
static func attached_if_boss(player: BattleVfx, controller: BattleController, engine: BattleEngine) -> BattleBossVfx:
	var bell := boss_of(engine)
	if bell == null:
		return null
	var view := BattleBossVfx.new()
	view.name = "BossVfx"
	player.add_child(view)
	view.attach(player, controller, engine, bell)
	return view


func attach(player: BattleVfx, controller: BattleController, engine: BattleEngine, bell: BattleCombatant) -> void:
	vfx = player
	_ctl = controller
	_engine = engine
	bell_id = bell.id
	cfg = (load_data().get("bosses", {}) as Dictionary).get(BattleVfx.base_id(bell.id), {}) as Dictionary
	engine.charge_started.connect(_on_charge_started)
	engine.charge_broken.connect(_on_charge_broken)
	engine.turn_started.connect(_on_turn_started)
	engine.phase_changed.connect(_on_phase_changed)
	engine.combatants_joined.connect(_on_joined)
	engine.field_cleared.connect(_on_field_cleared)
	# M2-BPR-04: with a choreography sequencer the toll (and rim hits, the mend) land on its contact beat.
	var choreo := controller.stage.choreo if controller != null else null
	if choreo != null:
		choreo.contact.connect(_on_action_resolved)
	else:
		engine.action_resolved.connect(_on_action_resolved)
	_build_glow()
	_build_ring()
	if cfg.has("flood"):
		_build_flood()
	if cfg.has("floodnet"):
		_build_net()


## The water's height now (world Y), or NAN without a flood.
func water_y() -> float:
	return water.global_position.y if water != null else NAN


## Jumps every running transition to its end: the water at its target, the light and sea-glow with it (screenshot
## fixtures and tools).
func settle() -> void:
	for tw: Tween in [_water_tween, _sun_tween, _glow_tween]:
		if tw != null and tw.is_valid():
			tw.custom_step(1e6)


## The rim glow's level now, 0..1 (before the pulse).
func glow_level() -> float:
	return _glow_level


func _process(_delta: float) -> void:
	if glow == null:
		return
	var t := _cfg("telegraph")
	var depth := _rm("pulse_depth", float(t.get("pulse_depth", 0.0)))
	var pulse := 1.0 - depth * 0.5 * (1.0 + sin(Time.get_ticks_msec() / 1000.0 * TAU * float(t.get("pulse_hz", 0.5))))
	glow.light_energy = float(t.get("glow_energy_max", 1.0)) * _glow_level * pulse
	glow.visible = _glow_level > 0.0
	if _ctl != null and _ctl.stage.has_fighter(bell_id):
		glow.global_position = vfx.anchor(bell_id, str(t.get("glow_at", "rim")))


# --- the toll ---


func _on_charge_started(actor: BattleCombatant, skill_id: StringName, turns: int) -> void:
	if actor.id != bell_id or str(skill_id) != str(_cfg("telegraph").get("charge_skill", "")):
		return
	_charge_total = maxi(turns, 1)
	_step_glow(actor)


func _on_turn_started(actor: BattleCombatant) -> void:
	if actor.id != bell_id or not actor.is_charging() or _charge_total <= 0:
		return
	_step_glow(actor)


## One step per turn of the charge: 1 / turns when it starts, full on the turn the toll fires.
func _step_glow(actor: BattleCombatant) -> void:
	_set_glow(clampf(float(_charge_total + 1 - actor.charge_left) / float(_charge_total), 0.0, 1.0))
	_gather()


func _gather() -> void:
	moments.append(&"telegraph")
	var id := str(_cfg("telegraph").get("gather", ""))
	if id != "":
		vfx.play(StringName(id), bell_id)


func _toll() -> void:
	moments.append(&"toll")
	_charge_total = 0
	var t := _cfg("toll")
	_set_glow(0.0, float(_cfg("telegraph").get("glow_out_s", 0.3)))
	var flash := str(t.get("flash", ""))
	if flash != "":
		vfx.play(StringName(flash), &"")
	var base := vfx.anchor(bell_id, "feet")
	var y := water_y() if water != null else base.y
	ring.global_position = Vector3(base.x, maxf(y, base.y) + float(t.get("ring_lift_m", 0.03)), base.z)
	ring.visible = true
	var sec := float(t.get("ring_s", 1.0)) * (_rm_scale("ring_s_scale"))
	var a0 := float(t.get("ring_alpha", 1.0)) * (_rm_scale("ring_alpha_scale"))
	var mat := ring.material_override as ShaderMaterial
	mat.set_shader_parameter(&"radius_m", 0.2)
	mat.set_shader_parameter(&"alpha", a0)
	if _ring_tween != null:
		_ring_tween.kill()
	_ring_tween = create_tween().set_parallel()
	var set_r := func(r: float) -> void: mat.set_shader_parameter(&"radius_m", r)
	var set_a := func(a: float) -> void: mat.set_shader_parameter(&"alpha", a)
	_ring_tween.tween_method(set_r, 0.2, float(t.get("ring_radius_m", 10.0)), sec).set_ease(Tween.EASE_OUT)
	_ring_tween.tween_method(set_a, a0, 0.0, sec).set_ease(Tween.EASE_IN)
	_ring_tween.chain().tween_callback(func() -> void: ring.visible = false)


func _on_charge_broken(enemy: BattleCombatant, _skill_id: StringName) -> void:
	if enemy.id != bell_id:
		return
	moments.append(&"rim_break")
	_charge_total = 0
	_set_glow(0.0, float(_cfg("telegraph").get("glow_out_s", 0.3)))
	var id := str(_cfg("weak_point").get("break", ""))
	if id != "":
		vfx.play(StringName(id), bell_id)


func _on_action_resolved(result: ActionResult) -> void:
	if result == null or not result.ok:
		return
	if str(result.skill_id) == str(_cfg("toll").get("skill", "")) and result.actor_id == bell_id:
		_toll()
	var crack := str(_cfg("weak_point").get("hit", ""))
	for hit: Dictionary in result.hits:
		if StringName(str(hit.get("target_id", ""))) == bell_id and hit.has("weak_point_hits"):
			if crack != "" and not hit.has("charge_broken"):
				moments.append(&"rim_hit")
				vfx.play(StringName(crack), bell_id)
	var p := _cfg("polyps")
	if str(result.skill_id) == str(p.get("mend_skill", "")) and _ctl != null:
		var from := vfx.anchor(result.actor_id, "chest")
		var to := vfx.anchor(bell_id, "chest")
		moments.append(&"mend")
		vfx.play_at(StringName(str(p.get("mend", ""))), from, to - from)
	_refresh_polyps()


# --- the flood ---


func _on_phase_changed(enemy: BattleCombatant, phase_id: StringName) -> void:
	var f := _cfg("flood")
	if enemy.id != bell_id or water == null or str(phase_id) != str(f.get("phase", "")):
		return
	moments.append(&"flood")
	_move_water(float(f.get("to_m", 0.0)), float(f.get("rise_s", 1.0)), true)
	if _sun != null:
		var to_e := _sun_energy * float(f.get("light_energy_scale", 1.0))
		_sun_tween = create_tween()
		_sun_tween.tween_property(_sun, "light_energy", to_e, float(f.get("rise_s", 1.0)))


func _on_field_cleared(field_id: StringName, fallen: Array[BattleCombatant]) -> void:
	var f := _cfg("flood")
	for c in fallen:
		_fade_polyp(c.id)
	if str(field_id) != str(f.get("field", "")):
		return
	_floodnet()
	if water != null:
		_move_water(float(f.get("from_m", 0.0)), float(f.get("fall_s", 1.0)), false)


func _move_water(to_m: float, sec: float, rising: bool) -> void:
	var f := _cfg("flood")
	flood_target_m = to_m
	if _water_tween != null:
		_water_tween.kill()
	_water_tween = create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_water_tween.tween_property(water, "global_position:y", to_m, sec)
	if rising:
		_water_tween.tween_property(water, "sea_glow_energy", float(f.get("sea_glow_to", 0.0)), sec)


func _build_flood() -> void:
	var f := _cfg("flood")
	for path: String in f.get("hide_nodes", []):
		var n := _ctl.get_node_or_null(NodePath(path)) as Node3D
		if n != null and n.visible:
			n.visible = false
			_hidden.append(n)
	water = WaterSurface.new()
	water.name = "FloodWater"
	water.publishes_water_level = true
	water.tide_line_y = float(f.get("datum_m", 0.0))
	water.core_half_extent_m = float(f.get("water_core_half_extent_m", 16.0))
	water.core_cell_m = float(f.get("water_core_cell_m", 0.25))
	water.outer_half_extent_m = float(f.get("water_outer_half_extent_m", 600.0))
	water.sea_glow_energy = float(f.get("sea_glow_from", 0.0))
	water.wave_set = _wave_set(f.get("waves", {}) as Dictionary)
	water.material = _look(f.get("look", {}) as Dictionary)
	if GraphicsRuntime.armed:
		water.quality = WaterSurface.quality_for_preset(GraphicsRuntime.settings().preset_id)
	add_child(water)
	flood_target_m = float(f.get("from_m", 0.0))
	water.global_position = Vector3(0.0, flood_target_m, 0.0)
	_start_weather(f.get("weather", {}) as Dictionary)
	_sun = _ctl.get_node_or_null(NodePath(str(f.get("sun_node", "")))) as DirectionalLight3D
	if _sun != null:
		_sun_energy = _sun.light_energy


## The flood's look: a water material with the data's look parameters (colours are swatches). WaterSurface picks
## the shader for its quality.
static func _look(look: Dictionary) -> ShaderMaterial:
	var mat := ShaderMaterial.new()
	mat.resource_name = "drownbell_flood"
	for key: String in look:
		if key.begins_with("_") or key == "swatches":
			continue
		var v: Variant = look[key]
		if v is String:
			mat.set_shader_parameter(StringName(key), Color(str(v)))
		elif v is Array:
			var a: Array = v
			mat.set_shader_parameter(StringName(key), Vector3(float(a[0]), float(a[1]), float(a[2])))
		else:
			mat.set_shader_parameter(StringName(key), float(v))
	return mat


static func _wave_set(waves: Dictionary) -> WaveSet:
	var ws := WaveSet.new()
	ws.amplitude_scale = float(waves.get("amplitude_scale", 1.0))
	for row: Array in waves.get("components", []):
		var c := WaveComponent.new()
		c.direction_deg = float(row[0])
		c.wavelength_m = float(row[1])
		c.amplitude_m = float(row[2])
		c.steepness = float(row[3])
		c.phase_rad = float(row[4])
		ws.components.append(c)
	return ws


## Sets a breeze when the wind is calm (see the data's note). The rig never writes the weather clock
## (hymn_wind_time): WeatherClock, SceneRouter's child, is its one writer (M2-ARC-02), and the flood water
## reads it from the global like any WaterSurface.
func _start_weather(w: Dictionary) -> void:
	if not bool(w.get("drive_clock", false)):
		return
	var wind := ShaderGlobals.get_value(GLOBAL_WIND, Vector4.ZERO) as Vector4
	if Vector2(wind.x, wind.z).length() < 0.01:
		_wind_before = wind
		var az := deg_to_rad(float(w.get("wind_azimuth_deg", 0.0)))
		var v := Vector2(sin(az), cos(az)) * float(w.get("wind_m_s", 0.0))
		ShaderGlobals.set_value(GLOBAL_WIND, Vector4(v.x, 0.0, v.y, float(w.get("gust", 0.0))))


func _exit_tree() -> void:
	if _wind_before != null:
		ShaderGlobals.set_value(GLOBAL_WIND, _wind_before)
		_wind_before = null
	for n in _hidden:
		if is_instance_valid(n):
			n.visible = true
	_hidden.clear()
	if _sun != null and is_instance_valid(_sun):
		_sun.light_energy = _sun_energy


# --- polyps ---


func _on_joined(added: Array[BattleCombatant]) -> void:
	var p := _cfg("polyps")
	for c in added:
		if BattleVfx.base_id(c.id) != str(p.get("enemy", "")):
			continue
		moments.append(&"polyp")
		vfx.play.call_deferred(StringName(str(p.get("rise", ""))), c.id)
		var l := OmniLight3D.new()
		l.name = "PolypLight_%s" % String(c.id).replace("#", "_")
		l.light_color = Color(str(p.get("light_color", "#FFFFFF")))
		l.light_energy = float(p.get("light_energy", 1.0))
		l.omni_range = float(p.get("light_range_m", 2.0))
		l.shadow_enabled = false
		add_child(l)
		polyp_lights[c.id] = l
		_place_polyp_light.call_deferred(c.id)


func _place_polyp_light(cid: StringName) -> void:
	var l := polyp_lights.get(cid) as OmniLight3D
	if l != null and l.is_inside_tree() and vfx.is_inside_tree():  # deferred: the fight may have left the tree since
		l.global_position = vfx.anchor(cid, str(_cfg("polyps").get("light_at", "chest")))


func _refresh_polyps() -> void:
	for cid: StringName in polyp_lights.keys():
		var c := _engine.find(cid) if _engine != null else null
		if c == null or c.hp <= 0:
			_fade_polyp(cid)


func _fade_polyp(cid: StringName) -> void:
	var l := polyp_lights.get(cid) as OmniLight3D
	if l == null:
		return
	polyp_lights.erase(cid)
	var tw := create_tween()
	tw.tween_property(l, "light_energy", 0.0, float(_cfg("polyps").get("light_fade_s", 0.5)))
	tw.tween_callback(l.queue_free)


# --- Ilun's Floodnet ---


func _floodnet() -> void:
	if net == null:
		return
	moments.append(&"floodnet")
	var n := _cfg("floodnet")
	var min_s := _rm("fade_min_s", 0.0)
	var y := water_y() if water != null else 0.0
	net.global_position = Vector3(0.0, y + 0.02, 0.0)
	net_light.global_position = Vector3(0.0, y + float(n.get("light_height_m", 2.0)), 0.0)
	net.visible = true
	net_light.visible = true
	var mat := net.material_override as ShaderMaterial
	var set_a := func(a: float) -> void:
		mat.set_shader_parameter(&"alpha", a)
		net_light.light_energy = float(n.get("light_energy", 1.0)) * a
	if _net_tween != null:
		_net_tween.kill()
	_net_tween = create_tween()
	_net_tween.tween_method(set_a, 0.0, 1.0, maxf(float(n.get("in_s", 0.5)), min_s))
	_net_tween.tween_interval(float(n.get("hold_s", 2.0)))
	_net_tween.tween_method(set_a, 1.0, 0.0, maxf(float(n.get("out_s", 1.0)), min_s))
	_net_tween.tween_callback(
		func() -> void:
			net.visible = false
			net_light.visible = false
	)


# --- builders and helpers ---


func _build_glow() -> void:
	var t := _cfg("telegraph")
	glow = OmniLight3D.new()
	glow.name = "RimGlow"
	glow.light_color = Color(str(t.get("glow_color", "#FFFFFF")))
	glow.omni_range = float(t.get("glow_range_m", 3.0))
	glow.light_energy = 0.0
	glow.shadow_enabled = false
	glow.visible = false
	add_child(glow)


func _build_ring() -> void:
	var t := _cfg("toll")
	var half := float(t.get("ring_radius_m", 10.0)) + 1.0
	var mesh := PlaneMesh.new()
	mesh.size = Vector2(half * 2.0, half * 2.0)
	var mat := ShaderMaterial.new()
	mat.shader = load(SHOCKWAVE_SHADER) as Shader
	mat.set_shader_parameter(&"color", Color(str(t.get("ring_color", "#FFFFFF"))))
	mat.set_shader_parameter(&"half_m", half)
	mat.set_shader_parameter(&"width_m", float(t.get("ring_width_m", 0.35)))
	mat.set_shader_parameter(&"wash_m", float(t.get("ring_wash_m", 1.5)))
	ring = MeshInstance3D.new()
	ring.name = "TollRing"
	ring.mesh = mesh
	ring.material_override = mat
	ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	ring.visible = false
	add_child(ring)


func _build_net() -> void:
	var n := _cfg("floodnet")
	var half := float(n.get("half_m", 10.0))
	var mesh := PlaneMesh.new()
	mesh.size = Vector2(half * 2.0, half * 2.0)
	var mat := ShaderMaterial.new()
	mat.shader = load(FLOODNET_SHADER) as Shader
	mat.set_shader_parameter(&"color", Color(str(n.get("color", "#FFFFFF"))))
	mat.set_shader_parameter(&"energy", float(n.get("energy", 1.0)))
	mat.set_shader_parameter(&"half_m", half)
	mat.set_shader_parameter(&"cell_m", float(n.get("cell_m", 1.0)))
	mat.set_shader_parameter(&"alpha", 0.0)
	net = MeshInstance3D.new()
	net.name = "Floodnet"
	net.mesh = mesh
	net.material_override = mat
	net.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	net.visible = false
	add_child(net)
	net_light = OmniLight3D.new()
	net_light.name = "FloodnetLight"
	net_light.light_color = Color(str(n.get("color", "#FFFFFF")))
	net_light.omni_range = float(n.get("light_range_m", 8.0))
	net_light.light_energy = 0.0
	net_light.shadow_enabled = false
	net_light.visible = false
	add_child(net_light)


func _set_glow(level: float, sec := -1.0) -> void:
	var t := _cfg("telegraph")
	var dur := sec if sec >= 0.0 else float(t.get("glow_in_s", 0.5))
	if _glow_tween != null:
		_glow_tween.kill()
	if not is_inside_tree() or dur <= 0.0:
		_glow_level = level
		return
	_glow_tween = create_tween()
	_glow_tween.tween_property(self, "_glow_level", level, dur)


func _cfg(key: String) -> Dictionary:
	return cfg.get(key, {}) as Dictionary


## A reduced-motion value from the data's reduced_motion block, or `normal` when motion is full.
func _rm(key: String, normal: float) -> float:
	if vfx == null or not vfx.reduced_motion:
		return normal
	return float((load_data().get("reduced_motion", {}) as Dictionary).get(key, normal))


func _rm_scale(key: String) -> float:
	return _rm(key, 1.0)
