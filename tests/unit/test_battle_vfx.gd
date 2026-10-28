extends TestCase
## M2-RND-03: the battle VFX library. Its data names real skills, elements and palette swatches; an action
## result maps to the right effects (element hit, heal, status, KO, special skill, nothing for a miss or a
## failure); flashes respect the photosensitivity caps; and reduced motion thins and slows the particles.

const PALETTE := "res://docs/kb/art/palette.json"
## The photosensitivity contract (effects.json safety.doc, docs/kb/tech/battle_vfx.md): the data may be stricter,
## never looser (M2-RND-06).
const CONTRACT_FLASH_MAX_ALPHA := 0.3
const CONTRACT_FLASH_MIN_INTERVAL_S := 0.5
const BATTLE_SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const HUD_LAYER_NODE := &"HudLayer"
const ENCOUNTER := &"sandbox_reef"

var engine: BattleEngine
var vfx: BattleVfx


func before_each() -> void:
	engine = BattleEngine.new()
	var party: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = []
	engine.setup(BattleDB.load_default(), party, reserve, ENCOUNTER, 7)
	vfx = BattleVfx.new()
	vfx._engine = engine


func test_data_names_real_skills_elements_and_swatches() -> void:
	var data := BattleVfx.load_data()
	var effects := data["effects"] as Dictionary
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	for id: String in effects:
		var def := effects[id] as Dictionary
		assert_true(def["kind"] in [BattleVfx.KIND_PARTICLES, BattleVfx.KIND_FLASH], "%s kind" % id)
		var parts: Array = def.get("layers", [def])
		for part: Dictionary in parts:
			var colors: Array = [part.get("color", "")]
			if part.has("color_end"):
				colors.append(part["color_end"])
			var names: Array = part.get("swatches", [])
			assert_eq(names.size(), colors.size(), "%s names a swatch per colour" % id)
			for i in colors.size():
				assert_true(swatches.has(names[i]), "%s: no swatch %s" % [id, names[i]])
				assert_eq(str(colors[i]).to_upper(), str((swatches[names[i]] as Dictionary)["hex"]).to_upper(), id)
	var map := data["map"] as Dictionary
	for section in ["elements", "skills", "items", "events"]:
		for key: String in map[section]:
			assert_true(effects.has(map[section][key]), "%s.%s -> missing effect" % [section, key])
	for sid: String in map["skills"]:
		assert_false(engine.db.skill(StringName(sid)).is_empty(), "map.skills names a real skill: %s" % sid)
	for row: Dictionary in engine.db.skills.values():
		assert_true((map["elements"] as Dictionary).has(str(row.get("element", "none"))), "element of %s" % row["id"])
	for ev in ["heal", "status", "ko", "ambush", "preemptive"]:
		assert_true((map["events"] as Dictionary).has(ev), "event %s" % ev)
	vfx.free()


func test_damage_plays_the_skill_elements_hit() -> void:
	var r := _result(&"ember", [{"target_id": _foe(), "hit": true, "amount": 12, "statuses_added": []}])
	# ADR 0041: every Act I skill plays its own effect first (tools/vfx/gen_act1_ability_vfx.py), then its element's.
	assert_eq(_ids(vfx.effects_for(r)), [&"ember", &"hit_fire"])
	r = _result(&"attack", [{"target_id": _foe(), "hit": true, "amount": 5, "statuses_added": []}])
	assert_eq(_ids(vfx.effects_for(r)), [&"hit_none"])
	vfx.free()


func test_heal_status_and_ko() -> void:
	var ally := engine.party_active[1].id
	var r := _result(&"mend", [{"target_id": ally, "hit": true, "amount": -9, "statuses_added": []}])
	assert_eq(_ids(vfx.effects_for(r)), [&"mend", &"heal"])
	r = _result(&"frost", [{"target_id": _foe(), "hit": true, "amount": 3, "statuses_added": [&"slow"]}])
	assert_eq(_ids(vfx.effects_for(r)), [&"frost", &"hit_ice", &"status_apply"])
	engine.find(_foe()).hp = 0
	r = _result(&"attack", [{"target_id": _foe(), "hit": true, "amount": 30, "statuses_added": []}])
	assert_eq(_ids(vfx.effects_for(r)), [&"hit_none", &"ko_release"], "a KO dissolves into released glimmer")
	vfx.free()


func test_signature_skills_play_their_own_effect_per_target() -> void:
	var r := _result(&"lamp_dive", [{"target_id": _foe(), "hit": true, "amount": 20, "statuses_added": []}])
	assert_eq(_ids(vfx.effects_for(r)), [&"lamp_dive", &"hit_none"])
	var hits: Array[Dictionary] = []
	for c in engine.party_active:
		hits.append({"target_id": c.id, "hit": true, "amount": -4, "statuses_added": []})
	r = _result(&"shallows_verse", hits)
	assert_eq(_ids(vfx.effects_for(r)).count(&"shallows_verse"), hits.size(), "once per ally")
	r = _result(&"read", [{"target_id": _foe(), "hit": true, "amount": 0, "statuses_added": []}])
	assert_eq(_ids(vfx.effects_for(r)), [&"read"])
	vfx.free()


func test_misses_and_failures_play_nothing_extra() -> void:
	var r := _result(&"attack", [{"target_id": _foe(), "hit": false, "amount": 0, "statuses_added": []}])
	assert_eq(vfx.effects_for(r).size(), 0, "a miss")
	assert_eq(vfx.effects_for(ActionResult.failed(&"rhen", &"ember", &"no_mp")).size(), 0, "a failed action")
	vfx.free()


func test_flashes_are_capped_and_spaced() -> void:
	var data := BattleVfx.load_data()
	var safety := data["safety"] as Dictionary
	var cap := float(safety["flash_max_alpha"])
	assert_true(cap <= CONTRACT_FLASH_MAX_ALPHA, "a flash never washes the frame out (cap %.2f)" % cap)
	var interval := float(safety["flash_min_interval_s"])
	assert_true(interval >= CONTRACT_FLASH_MIN_INTERVAL_S, "at most 2 flashes a second (%.2f s apart)" % interval)
	var effects := data["effects"] as Dictionary
	var flashes := 0
	for id: String in effects:
		var def := effects[id] as Dictionary
		if def["kind"] == BattleVfx.KIND_FLASH:
			flashes += 1
			assert_true(float(def.get("alpha", INF)) <= cap, "%s's own alpha is within the cap" % id)
	assert_true(flashes > 0, "the library has flashes to check")
	var bright := {"kind": "flash", "alpha": 0.9}
	assert_eq(vfx.flash_alpha(bright), cap, "capped")
	vfx.reduced_motion = true
	assert_true(vfx.flash_alpha(bright) < cap, "fainter with reduced motion")
	vfx.reduced_motion = false
	var host := Node.new()
	_host().add_child(host)
	vfx._build_flash_layer(host)
	var hud_layer := _hud_layer()
	assert_true(
		vfx._flash_layer.layer < hud_layer, "below the HUD's CanvasLayer (%d): the timeline stays readable" % hud_layer
	)
	vfx.play(&"flash_ambush", &"")
	vfx.play(&"flash_preemptive", &"")
	assert_eq(vfx.played.count(&"flash_ambush") + vfx.played.count(&"flash_preemptive"), 1, "the second is too soon")
	assert_eq(vfx.flashes_suppressed, 1)
	host.free()
	vfx.free()


func test_reduced_motion_thins_and_slows_particles() -> void:
	_host().add_child(vfx)
	var full := vfx.play_at(&"heal", Vector3.ZERO)
	var full_amount := full.amount
	var full_vel := (full.process_material as ParticleProcessMaterial).initial_velocity_max
	vfx.reduced_motion = true
	# A fresh emitter (the first is still emitting) takes the reduced settings.
	var reduced := vfx.play_at(&"heal", Vector3.ZERO)
	assert_true(reduced != full)
	assert_true(reduced.amount < full_amount, "fewer particles")
	assert_true((reduced.process_material as ParticleProcessMaterial).initial_velocity_max < full_vel + 1e-6)
	assert_eq(vfx.played, [&"heal", &"heal"])
	vfx.play_at(&"ko_release", Vector3.ZERO)
	var motes := vfx.get_node(NodePath("ko_release#1_0")) as GPUParticles3D
	assert_true(motes != null, "the KO's second layer: its rising motes")
	assert_false((motes.process_material as ParticleProcessMaterial).turbulence_enabled, "no turbulence")
	_host().remove_child(vfx)
	vfx.free()


## M2-RND-07: attach pre-builds one emitter per layer of every particle effect (none emitting), so no
## effect's first emitter is built mid-fight (the Drownbell's polyp_rise cost 35-79 ms); nothing is played.
func test_prebuild_makes_every_particle_emitter_without_playing() -> void:
	_host().add_child(vfx)
	var layers := 0
	var unused := vfx._unused_specials()  # ADR 0041: skills' own effects nobody in this battle can use wait
	assert_false(unused.is_empty(), "an Act I fight leaves other fights' abilities unbuilt")
	for id: String in vfx.data["effects"]:
		var def := (vfx.data["effects"] as Dictionary)[id] as Dictionary
		if str(def.get("kind", "")) == BattleVfx.KIND_PARTICLES and not unused.has(id):
			layers += (def.get("layers", [{}]) as Array).size()
	assert_eq(vfx.prebuild(), layers, "one emitter per particle layer")
	assert_true(vfx.played.is_empty(), "prebuilding plays nothing")
	var p := vfx.get_node(NodePath("polyp_rise#0_0")) as GPUParticles3D
	assert_true(p != null and not p.emitting, "the Drownbell's polyp rise is built, not emitting")
	assert_eq(vfx.play_at(&"polyp_rise", Vector3.ZERO), p, "the first play takes the prebuilt emitter")
	_host().remove_child(vfx)
	vfx.free()


func _result(skill: StringName, hits: Array) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = engine.party_active[0].id
	r.skill_id = skill
	for h: Dictionary in hits:
		r.hits.append(h)
	return r


## The HudLayer's `layer` as battle_sandbox.tscn sets it (CanvasLayer's default when the scene doesn't).
func _hud_layer() -> int:
	var state := (load(BATTLE_SCENE) as PackedScene).get_state()
	for i in state.get_node_count():
		if state.get_node_name(i) != HUD_LAYER_NODE:
			continue
		for p in state.get_node_property_count(i):
			if state.get_node_property_name(i, p) == &"layer":
				return int(state.get_node_property_value(i, p))
		var probe := CanvasLayer.new()
		var layer := probe.layer
		probe.free()
		return layer
	fail("%s has no %s" % [BATTLE_SCENE, HUD_LAYER_NODE])
	return 0


func _foe() -> StringName:
	return engine.enemies[0].id


func _host() -> Node:
	# The tree root is busy while the runner scene is readying, so attach under the running scene.
	return (Engine.get_main_loop() as SceneTree).current_scene


func _ids(list: Array[Dictionary]) -> Array[StringName]:
	var out: Array[StringName] = []
	for e in list:
		out.append(e["effect"])
	return out
