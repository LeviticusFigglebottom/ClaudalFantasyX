class_name BattleVfx
extends Node3D
## Battle VFX library player (M2-RND-03). Docs: docs/kb/tech/battle_vfx.md.
## - **Listens only.** It hooks the engine's `action_resolved` the way BattleBossHud does: one line in
##   BattleController._build_engine. It never writes combat state.
## - **Data-driven.** game/data/vfx/battle/effects.json maps skills, items, elements and events (heal, status,
##   KO, ambush, preemptive) to effects. effects_for() turns an ActionResult into [{effect, target}] with no
##   nodes, so it is tested headless.
## - **Effects:**
##   - particles: one-shot GPUParticles3D at a fighter, built from the definition (one shared billboard draw
##     material, battle_spark_draw.tres; a ParticleProcessMaterial per effect). Pooled per effect.
##   - flash: a full-screen tint on a CanvasLayer below the HUD (the timeline is never covered, pillar 4).
## - **Safety.** A flash is capped at safety.flash_max_alpha, and two are at least flash_min_interval_s apart
##   (photosensitivity). With UiSettings reduced motion, particles are fewer and slower and flashes are faint
##   and gentle.

signal effect_played(effect_id: StringName, position: Vector3)

## An entry's nominal height over its arena mark (a group of climbers on the stair head), for anchor_heights.
const ENTRY_HEIGHT_M := 1.6
const DATA_PATH := "res://game/data/vfx/battle/effects.json"
const DRAW_MATERIAL := "res://game/vfx/battle/materials/battle_spark_draw.tres"
const PROCESS_MATERIAL := "res://game/vfx/battle/materials/battle_spark_process.tres"
const KIND_PARTICLES := "particles"
const KIND_FLASH := "flash"
## Emitters kept per effect for reuse (a 3v3 all-foes skill needs three at once).
const POOL_PER_EFFECT := 6
## Visibility box of an emitter, in metres around it (effects stay within a fighter's reach).
const VISIBILITY_HALF_M := 3.0
const MSEC_PER_SEC := 1000.0
## Colour ramp: the alpha a particle still has at RAMP_HOLD of its life.
const RAMP_HOLD := 0.6
const RAMP_HOLD_ALPHA := 0.85

static var _data_cache: Dictionary = {}

var data: Dictionary = {}
var reduced_motion := false
## Every effect played, in order (tests and tools).
var played: Array[StringName] = []
## Flashes refused by the photosensitivity interval.
var flashes_suppressed := 0
## The boss's own VFX and set piece (M2-RND-04), when the encounter has one (else null).
var boss: BattleBossVfx
var _ctl: BattleController
var _engine: BattleEngine
var _flash_layer: CanvasLayer
var _flash_rect: ColorRect
var _flash_tween: Tween
var _last_flash_ms := -1000000
var _process_cache: Dictionary = {}
var _pool: Dictionary = {}
var _draw_mesh: QuadMesh
var _depth_cache: Dictionary = {}


static func load_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = parsed as Dictionary
		else:
			push_warning("BattleVfx: cannot read %s" % DATA_PATH)
	return _data_cache


## Builds the view under the controller's stage and connects it to `engine` (after setup).
static func attached(controller: BattleController, engine: BattleEngine) -> BattleVfx:
	# A retry builds a new engine: the previous view (its flood water publishes hymn_water_level) goes.
	var old := controller.stage.get_node_or_null(^"BattleVfx")
	if old != null:
		controller.stage.remove_child(old)
		old.queue_free()
	var view := BattleVfx.new()
	view.name = "BattleVfx"
	controller.stage.add_child(view)
	view.attach(controller, engine)
	return view


func _init() -> void:
	data = load_data()


func attach(controller: BattleController, engine: BattleEngine) -> void:
	_ctl = controller
	_engine = engine
	# M2-BPR-01: with a choreography sequencer the hit lands on its contact beat (instant when it isn't playing).
	var choreo := controller.stage.choreo
	if choreo != null:
		choreo.contact.connect(_on_action_resolved)
	else:
		engine.action_resolved.connect(_on_action_resolved)
	var settings := UiSettings.shared()
	if settings != null:
		reduced_motion = settings.reduced_motion()
		settings.changed.connect(func(_key: StringName) -> void: reduced_motion = settings.reduced_motion())
	_build_flash_layer(controller)
	boss = BattleBossVfx.attached_if_boss(self, controller, engine)
	BattleBossSetPiece.attach_all(self, controller, engine)  # M3-BPR-420: the other Act I bosses' set pieces
	if engine.vowbound != null:  # M3-BPR-420: a Vowbound's call, dismissal and fall play in bound light
		engine.vowbound.called.connect(
			func(vb: BattleCombatant) -> void: play_event.call_deferred(&"vowbound_call", vb.id)
		)
		engine.vowbound.departed.connect(_on_vowbound_departed)
	engine.turn_ended.connect(func(_a: BattleCombatant, changes: Array[Dictionary]) -> void: play_ticks(changes))
	engine.turn_lost.connect(_on_turn_lost)
	prebuild()
	var opening_event := _opening_event(engine.opening)
	if opening_event != &"":
		play_event.call_deferred(opening_event, &"")


## Builds one pooled emitter per layer of every particle effect, without emitting (M2-RND-07). The first
## emitter of a feature set (turbulence on) costs ~32 ms of main-thread work in the battle's tree; mid-fight,
## the Drownbell's polyp_rise put a 35-44 ms frame into the Flood (79 ms on a fresh install). attach() calls
## it in the frame the battle scene enters, under the router's opaque fade (about 45 ms in all on the RX
## 9070 XT). A staged prewarm didn't help: the cost is the emitter's, in this tree. Returns the emitters built.
## ADR 0041: with an engine, a skill's own effect is built only when someone in this battle can use that skill (Act I
## gave every ability its own); one that joins later (a summon's) is built on its first play.
func prebuild() -> int:
	var count := 0
	var unused := _unused_specials()
	for effect_id: String in data.get("effects", {}):
		var def := (data["effects"] as Dictionary)[effect_id] as Dictionary
		if str(def.get("kind", "")) != KIND_PARTICLES or unused.has(effect_id):
			continue
		var layers: Array = def.get("layers", [{}])
		for i in layers.size():
			_emitter(StringName("%s#%d" % [effect_id, i]), def.merged(layers[i] as Dictionary, true))
			count += 1
	return count


## M3-BPR-424: an end-of-turn effect shows on its fighter (BattleEngine.turn_ended's changes: poison, regen, a Doom
## count, Doom falling), each by map.ticks[cause]. Regen under Zombie (amount > 0) hurts: it plays the poison tick.
func play_ticks(changes: Array[Dictionary]) -> void:
	var ticks := (data.get("map", {}) as Dictionary).get("ticks", {}) as Dictionary
	for c in changes:
		var cause := str(c.get("cause", ""))
		if cause == "regen" and int(c.get("amount", 0)) > 0:
			cause = "poison"
		var eid := str(ticks.get(cause, ""))
		if eid != "":
			play(StringName(eid), StringName(str(c.get("target_id", ""))))


## A turn eaten by Sleep or Stop shows on the sleeper (map.ticks.sleep / stop), then its Doom ticks.
func _on_turn_lost(actor: BattleCombatant, reason: StringName, changes: Array[Dictionary]) -> void:
	var eid := str(((data.get("map", {}) as Dictionary).get("ticks", {}) as Dictionary).get(String(reason), ""))
	if eid != "":
		play(StringName(eid), actor.id)
	play_ticks(changes)


func _on_vowbound_departed(vb: BattleCombatant, fell: bool) -> void:
	play_event(&"vowbound_fell" if fell else &"vowbound_dismiss", vb.id)


## The effects nobody in this battle can use: every `map.skills` effect but those of the fighters' own skills, the
## Swell techniques and the Vowbound's, the Swell finishers (`map.swell_by_hero`) of heroes not in the party, and the
## set pieces of bosses not in this fight. {} without an engine.
func _unused_specials() -> Dictionary:
	if _engine == null:
		return {}
	var by_skill := (data.get("map", {}) as Dictionary).get("skills", {}) as Dictionary
	var wanted: Dictionary = {}
	for c in _engine.party_active + _engine.party_reserve + _engine.enemies + _engine.entries:
		for sid: StringName in c.skills:
			wanted[str(by_skill.get(String(sid), ""))] = true
	for sid: String in by_skill:
		if bool(_engine.db.skill(StringName(sid)).get("swell", false)):
			wanted[str(by_skill[sid])] = true
	for row: Dictionary in BattleVowbound.load_config():
		for sid: Variant in row.get("skills", []):
			wanted[str(by_skill.get(str(sid), ""))] = true
	var unused: Dictionary = {}
	for sid: String in by_skill:
		if not wanted.has(str(by_skill[sid])):
			unused[str(by_skill[sid])] = true
	var heroes: Dictionary = {}
	for c in _engine.party_active + _engine.party_reserve:
		heroes[base_id(c.id)] = true
	var swells := (data.get("map", {}) as Dictionary).get("swell_by_hero", {}) as Dictionary
	for hero: String in swells:  # a Swell finisher waits for its hero (M3-BPR-422)
		if not heroes.has(hero):
			unused[str(swells[hero])] = true
	var here: Dictionary = {}
	for c in _engine.enemies:
		here[base_id(c.id)] = true
	var rows := BattleBossVfx.load_data().get("bosses", {}) as Dictionary
	for bid: String in rows:  # a set-piece boss's effects wait for that boss
		var row := rows[bid] as Dictionary
		if str(row.get("kind", "")) != BattleBossSetPiece.KIND or here.has(bid):
			continue
		var ids: Array = [row.get("gather", ""), row.get("ko", "")] + (row.get("phases", {}) as Dictionary).values()
		for eid: Variant in ids:
			if str(eid) != "" and not wanted.has(str(eid)):
				unused[str(eid)] = true
	return unused


## What an action plays: [{"effect": id, "target": combatant id}], in order. No nodes: tests call it.
func effects_for(result: ActionResult) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if result == null or not result.ok:
		return out
	var map := data.get("map", {}) as Dictionary
	var events := map.get("events", {}) as Dictionary
	var special := ""
	var element := "none"
	if result.item_id != &"":
		special = str((map.get("items", {}) as Dictionary).get(String(result.item_id), ""))
	elif result.skill_id != &"":
		special = str((map.get("skills", {}) as Dictionary).get(String(result.skill_id), ""))
		if special == "" and _engine != null and bool(_engine.db.skill(result.skill_id).get("swell", false)):
			special = str((map.get("swell_by_hero", {}) as Dictionary).get(base_id(result.actor_id), ""))  # M3-BPR-422
		if _engine != null:
			element = str(_engine.db.skill(result.skill_id).get("element", "none"))
	var elements := map.get("elements", {}) as Dictionary
	for hit: Dictionary in result.hits:
		var target := StringName(str(hit.get("target_id", "")))
		if special != "":
			out.append({"effect": StringName(special), "target": target})
		if not bool(hit.get("hit", true)):
			continue
		var amount := int(hit.get("amount", 0))
		if amount > 0:
			out.append({"effect": StringName(str(elements.get(element, elements.get("none", "")))), "target": target})
		elif amount < 0:
			out.append({"effect": StringName(str(events.get("heal", ""))), "target": target})
		if not (hit.get("statuses_added", []) as Array).is_empty():
			out.append({"effect": StringName(str(events.get("status", ""))), "target": target})
		if amount > 0 and _is_down(target):
			var ko := str((map.get("ko_overrides", {}) as Dictionary).get(base_id(target), events.get("ko", "")))
			out.append({"effect": StringName(ko), "target": target})
	return out.filter(func(e: Dictionary) -> bool: return e["effect"] != &"")


## Plays an event's effect (events map: heal, status, ko, ambush, preemptive) at `target` ("" for a flash).
func play_event(event: StringName, target: StringName) -> void:
	var id := str(((data.get("map", {}) as Dictionary).get("events", {}) as Dictionary).get(String(event), ""))
	if id != "":
		play(StringName(id), target)


## Plays effect `effect_id` at fighter `target`. Returns the emitter (null for a flash, or when skipped).
func play(effect_id: StringName, target: StringName, aim := Vector3.ZERO) -> GPUParticles3D:
	var def := (data.get("effects", {}) as Dictionary).get(String(effect_id), {}) as Dictionary
	if def.is_empty():
		push_warning("BattleVfx: unknown effect %s" % effect_id)
		return null
	if str(def.get("kind", "")) == KIND_FLASH:
		_flash(effect_id, def)
		return null
	if not is_inside_tree():
		return null  # a hit resolved as the battle leaves the tree (ui-menus' error sweep, 10-29): nothing to place
	return play_at(effect_id, anchor(target, str(def.get("at", "chest"))), aim)


## Plays a particle effect at a world position (the probe tool and tests). An effect is one emitter, or
## one per entry of its "layers" (each a particle definition; the layer inherits the effect's keys it
## doesn't set). A non-zero `aim` replaces the layers' direction (a stream from one fighter to another).
## Returns the first layer's emitter.
func play_at(effect_id: StringName, at: Vector3, aim := Vector3.ZERO) -> GPUParticles3D:
	var def := (data.get("effects", {}) as Dictionary).get(String(effect_id), {}) as Dictionary
	if str(def.get("kind", "")) != KIND_PARTICLES or not is_inside_tree():
		return null
	var first: GPUParticles3D = null
	var layers: Array = def.get("layers", [{}])
	for i in layers.size():
		var layer := def.merged(layers[i] as Dictionary, true)
		var key := StringName("%s#%d" % [effect_id, i])
		var p := _emitter(key, layer)
		if aim != Vector3.ZERO:
			(p.process_material as ParticleProcessMaterial).direction = aim.normalized()
		p.global_position = at
		p.restart()
		p.emitting = true
		if first == null:
			first = p
	played.append(effect_id)
	effect_played.emit(effect_id, at)
	return first


## Flash opacity actually used for `def`: capped by safety, scaled by reduced motion.
func flash_alpha(def: Dictionary) -> float:
	var safety := data.get("safety", {}) as Dictionary
	var a := minf(float(def.get("alpha", 0.0)), float(safety.get("flash_max_alpha", 0.0)))
	if reduced_motion:
		a *= float((data.get("reduced_motion", {}) as Dictionary).get("flash_alpha_scale", 1.0))
	return a


func _on_action_resolved(result: ActionResult) -> void:
	for e in effects_for(result):
		play(e["effect"], e["target"])


## The table id of a combatant id ("drownbell#1" -> "drownbell").
static func base_id(cid: StringName) -> String:
	return String(cid).get_slice("#", 0)


static func _opening_event(opening: StringName) -> StringName:
	match opening:
		BattleOpening.AMBUSH:
			return &"ambush"
		BattleOpening.PREEMPTIVE:
			return &"preemptive"
	return &""


func _is_down(target: StringName) -> bool:
	if _engine == null:
		return false
	var c := _engine.find(target)
	return c != null and c.hp <= 0


## A fighter's point at `at` (an anchor_heights key: feet, rim, chest, hood, head). A set piece's entry with no
## fighter (the Climb) anchors on its arena mark (entry_mark); anything else not on the stage, this node's position.
func anchor(target: StringName, at: String) -> Vector3:
	if not is_inside_tree():
		return Vector3.ZERO  # off the tree there are no global positions to read (ui-menus' error sweep, 10-29)
	var frac := float((data.get("anchor_heights", {}) as Dictionary).get(at, 0.5))
	if _ctl == null or not _ctl.stage.has_fighter(target):
		var mark := entry_mark(target)
		return mark + Vector3.UP * ENTRY_HEIGHT_M * frac if mark != Vector3.INF else global_position
	var f := _ctl.stage.stand_in(target)
	if not f.is_inside_tree():
		return global_position
	var spec := BattleStage.stand_in_spec(target)
	var height := float(spec.get("height", 1.7))
	# M3-BPR-420: a flier stands at its hover (the gulls, the squall wings): its hit lands on it, not on the sand below.
	var p := f.global_position + Vector3.UP * (float(spec.get("hover", 0.0)) + height * frac)
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	if at == "feet" or cam == null:
		return p
	# M3-BPR-420: on the body's near face, not its middle: inside the Cinder Matron's 2.9 m bulk a hit was hidden.
	var to_cam := Vector3(cam.global_position.x - p.x, 0.0, cam.global_position.z - p.z)
	return p + to_cam.normalized() * _half_depth(target, f) if to_cam.length() > 0.01 else p


## Half the fighter's smaller horizontal extent (its actor's visible meshes, or its primitive's radius), measured once.
func _half_depth(target: StringName, f: FighterStandIn) -> float:
	if _depth_cache.has(target):
		return float(_depth_cache[target])
	var r := float(f.spec.get("radius", 0.0))
	if f.has_actor():
		var box := AABB()
		var first := true
		for n in f.actor().find_children("*", "MeshInstance3D", true, false):
			var mi := n as MeshInstance3D
			if mi.mesh != null and mi.is_inside_tree() and mi.is_visible_in_tree():
				var b := mi.global_transform * mi.get_aabb()
				box = b if first else box.merge(b)
				first = false
		r = 0.0 if first else minf(box.size.x, box.size.z) * 0.5
	_depth_cache[target] = r
	return r


## M3-BPR-1325: where a set piece's entry "is" in the arena: its role's StairHead_<role> mark (env-art-b's
## seawall arenas: the head of the Fisher Stair, where a group of climbers arrives), else EntryMarker_<role>;
## Vector3.INF for a fighter, or when the arena has no such mark.
func entry_mark(target: StringName) -> Vector3:
	var c := _engine.find(target) if _engine != null else null
	var arena := _ctl.get_node_or_null(NodePath(String(BattleArena.ARENA_NODE))) if _ctl != null else null
	if c == null or c.entry_role == &"" or arena == null:
		return Vector3.INF
	for mark: String in ["StairHead_%s", "EntryMarker_%s"]:
		var n := arena.get_node_or_null(NodePath(mark % c.entry_role)) as Node3D
		if n != null and n.is_inside_tree():
			return n.global_position
	return Vector3.INF


func _emitter(effect_id: StringName, def: Dictionary) -> GPUParticles3D:
	var list: Array = _pool.get(effect_id, [])
	for p: GPUParticles3D in list:
		if not p.emitting:
			_apply_motion(p, def)
			return p
	if list.size() >= POOL_PER_EFFECT:
		return list[0] as GPUParticles3D  # the oldest restarts: a burst beyond the pool replaces it
	var p := GPUParticles3D.new()
	p.name = "%s_%d" % [effect_id, list.size()]
	p.one_shot = true
	p.emitting = false
	p.local_coords = false
	p.lifetime = float(def.get("lifetime_s", 0.5))
	p.explosiveness = float(def.get("explosiveness", 0.9))
	p.process_material = _process_for(effect_id, def)
	if _draw_mesh == null:
		_draw_mesh = QuadMesh.new()
		_draw_mesh.material = load(DRAW_MATERIAL) as Material
	p.draw_pass_1 = _draw_mesh
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var h := VISIBILITY_HALF_M
	p.visibility_aabb = AABB(Vector3(-h, -h, -h), Vector3(2.0 * h, 2.0 * h, 2.0 * h))
	add_child(p)
	_apply_motion(p, def)
	list.append(p)
	_pool[effect_id] = list
	return p


## Amount (reduced motion: fewer), set on every reuse so a settings change applies at the next play.
func _apply_motion(p: GPUParticles3D, def: Dictionary) -> void:
	var rm := data.get("reduced_motion", {}) as Dictionary
	var scale := float(rm.get("particle_scale", 1.0)) if reduced_motion else 1.0
	p.amount = maxi(1, roundi(float(def.get("amount", 16)) * scale))
	var mat := p.process_material as ParticleProcessMaterial
	var vel: Array = def.get("velocity_m_s", [1.0, 2.0])
	var vscale := float(rm.get("velocity_scale", 1.0)) if reduced_motion else 1.0
	mat.initial_velocity_min = float(vel[0]) * vscale
	mat.initial_velocity_max = float(vel[1]) * vscale
	mat.turbulence_enabled = float(def.get("turbulence", 0.0)) > 0.0 and not reduced_motion


func _process_for(effect_id: StringName, def: Dictionary) -> ParticleProcessMaterial:
	if _process_cache.has(effect_id):
		return _process_cache[effect_id]
	var mat := (load(PROCESS_MATERIAL) as ParticleProcessMaterial).duplicate() as ParticleProcessMaterial
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	mat.emission_sphere_radius = float(def.get("emission_radius_m", 0.1))
	var d: Array = def.get("direction", [0, 1, 0])
	mat.direction = Vector3(float(d[0]), float(d[1]), float(d[2]))
	mat.spread = float(def.get("spread_deg", 180.0))
	var g: Array = def.get("gravity", [0, 0, 0])
	mat.gravity = Vector3(float(g[0]), float(g[1]), float(g[2]))
	var size: Array = def.get("size_m", [0.05, 0.1])
	mat.scale_min = float(size[0])
	mat.scale_max = float(size[1])
	mat.turbulence_noise_strength = float(def.get("turbulence", 0.0))
	var energy := float(def.get("energy", 1.0))
	var c0 := Color(str(def.get("color", "#FFFFFF")))
	var c1 := Color(str(def.get("color_end", def.get("color", "#FFFFFF"))))
	# Held near full until RAMP_HOLD of the life, then out: a linear fade emptied a burst before it read.
	var ramp := Gradient.new()
	ramp.set_color(0, Color(c0.r * energy, c0.g * energy, c0.b * energy, 1.0))
	ramp.set_color(1, Color(c1.r * energy, c1.g * energy, c1.b * energy, 0.0))
	var mid := c0.lerp(c1, RAMP_HOLD)
	ramp.add_point(RAMP_HOLD, Color(mid.r * energy, mid.g * energy, mid.b * energy, RAMP_HOLD_ALPHA))
	var tex := GradientTexture1D.new()
	tex.gradient = ramp
	mat.color_ramp = tex
	_process_cache[effect_id] = mat
	return mat


func _exit_tree() -> void:
	if _flash_layer != null and is_instance_valid(_flash_layer):
		_flash_layer.queue_free()
		_flash_layer = null


func _build_flash_layer(controller: Node) -> void:
	_flash_layer = CanvasLayer.new()
	_flash_layer.name = "BattleVfxFlash"
	_flash_layer.layer = int((data.get("safety", {}) as Dictionary).get("flash_layer", 0))
	_flash_rect = ColorRect.new()
	_flash_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_flash_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_flash_rect.color = Color(0, 0, 0, 0)
	_flash_layer.add_child(_flash_rect)
	controller.add_child(_flash_layer)


func _flash(effect_id: StringName, def: Dictionary) -> void:
	var safety := data.get("safety", {}) as Dictionary
	var now := Time.get_ticks_msec()
	if now - _last_flash_ms < int(float(safety.get("flash_min_interval_s", 0.0)) * MSEC_PER_SEC):
		flashes_suppressed += 1
		return
	_last_flash_ms = now
	played.append(effect_id)
	effect_played.emit(effect_id, Vector3.ZERO)
	if _flash_rect == null or not _flash_rect.is_inside_tree():
		return
	var rm := data.get("reduced_motion", {}) as Dictionary
	var min_ramp := float(rm.get("flash_min_ramp_s", 0.0)) if reduced_motion else 0.0
	var c := Color(str(def.get("color", "#FFFFFF")))
	_flash_rect.color = Color(c.r, c.g, c.b, 0.0)
	if _flash_tween != null:
		_flash_tween.kill()
	_flash_tween = create_tween()
	_flash_tween.tween_property(_flash_rect, "color:a", flash_alpha(def), maxf(float(def.get("in_s", 0.05)), min_ramp))
	_flash_tween.tween_property(_flash_rect, "color:a", 0.0, maxf(float(def.get("out_s", 0.3)), min_ramp))
