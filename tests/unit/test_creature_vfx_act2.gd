extends TestCase
## M4-A2P-058: the four Act II bosses' own ambient VFX (CreatureAmbientVfx, game/data/creatures/creature_vfx.json).
## Each boss scene carries its effects, built from the data; the Ram's are soft puffs (no ice, frost or shards: ADR
## 0015, M4-A2P-059); every continuous effect stops on the KO, and the KO plays its lift (the Drowner's motes, the
## Engine's bound light) while the Engine's lamps go dark.

const BOSSES: Array[StringName] = [&"mangrove_drowner", &"lamp_engine", &"avalanche_ram", &"wakefin"]
const PALETTE_PATH := "res://docs/kb/art/palette.json"
## Words no effect of the Ram's may carry (in its id, swatches or materials).
const RAM_BANNED: Array[String] = ["ice", "frost", "shard", "rime", "icicle", "salt_glass", "crystal"]
## The soft round draws (radial gradient sprites): nothing angular.
const SOFT_DRAWS: Array[String] = ["puff", "glow", "flat_glow"]
const STEP_SEC := 0.05
## A material's float is single precision.
const EPS := 0.0001
const KO_ALPHA := 0.35
const LONG_SEC := 12.0
## The longest wait for a KO burst or a periodic one, in steps.
const MAX_STEPS := 240

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_every_act2_boss_scene_has_its_effects() -> void:
	for id in BOSSES:
		var a := _actor(id)
		var vfx := _vfx(a)
		assert_true(vfx != null, "%s has a CreatureAmbientVfx" % id)
		if vfx == null:
			continue
		vfx.build_late()
		var effects: Array = CreatureAmbientVfx.row_for(id).get("effects", [])
		assert_true(effects.size() >= 2, "%s has its effects in creature_vfx.json" % id)
		for e: Variant in effects:
			var eid := StringName(str((e as Dictionary)["id"]))
			assert_true(vfx.effect(eid) != null, "%s builds %s" % [id, eid])
	before_each()


func test_effects_are_driven_by_the_data() -> void:
	for id in BOSSES:
		var vfx := _vfx(_actor(id))
		for e: Variant in CreatureAmbientVfx.row_for(id).get("effects", []):
			var def := e as Dictionary
			if str(def.get("kind", "")) != CreatureAmbientVfx.KIND_PARTICLES:
				continue
			var p := vfx.effect(StringName(str(def["id"]))) as GPUParticles3D
			assert_eq(p.amount, int(def["amount"]), "%s %s amount" % [id, def["id"]])
			assert_eq(p.lifetime, float(def["lifetime_s"]), "%s %s lifetime" % [id, def["id"]])
			assert_eq(p.one_shot, not def.has("emit"), "%s %s: a burst is one-shot" % [id, def["id"]])
			var mat := p.process_material as ParticleProcessMaterial
			var size: Array = def["size_m"]
			assert_between(mat.scale_min, float(size[0]) - EPS, float(size[0]) + EPS, "%s %s size" % [id, def["id"]])
			assert_true(p.use_fixed_seed, "%s %s replays the same way" % [id, def["id"]])
	before_each()


func test_every_colour_is_its_palette_swatch() -> void:
	var swatches: Dictionary = (_json(PALETTE_PATH) as Dictionary).get("swatches", {})
	for id in BOSSES:
		for e: Variant in CreatureAmbientVfx.row_for(id).get("effects", []):
			var def := e as Dictionary
			var cols: Array = def.get("colors", [])
			if def.has("color"):
				cols = cols + [def["color"]]
			assert_false(cols.is_empty(), "%s %s has a colour" % [id, def["id"]])
			for c: Variant in cols:
				var sw := str((c as Dictionary).get("swatch", ""))
				assert_true(swatches.has(sw), "%s %s: %s is a palette swatch" % [id, def["id"], sw])
				if swatches.has(sw):
					var hex := str((swatches[sw] as Dictionary).get("hex", ""))
					assert_eq(
						str((c as Dictionary)["hex"]).to_upper(), hex.to_upper(), "%s %s %s hex" % [id, def["id"], sw]
					)


func test_the_ram_sheds_soft_puffs_never_ice() -> void:
	var draws: Dictionary = CreatureAmbientVfx.data().get("draws", {})
	for e: Variant in CreatureAmbientVfx.row_for(&"avalanche_ram").get("effects", []):
		var def := e as Dictionary
		var text := JSON.stringify(def).to_lower()
		for word in RAM_BANNED:
			assert_false(text.contains(word), "the Ram's %s has no %s" % [def["id"], word])
		if str(def.get("kind", "")) == CreatureAmbientVfx.KIND_PARTICLES:
			var draw := str(def.get("draw", ""))
			assert_true(SOFT_DRAWS.has(draw), "the Ram's %s is a soft round draw (%s)" % [def["id"], draw])
			var path := str((draws.get(draw, {}) as Dictionary).get("material", "")).to_lower()
			for word in RAM_BANNED:
				assert_false(path.contains(word), "the Ram's %s material %s is not %s" % [def["id"], path, word])
	var vfx := _vfx(_actor(&"avalanche_ram"))
	for n in vfx.actor.find_children("*", "GPUParticles3D", true, false):
		var p := n as GPUParticles3D
		var mesh := p.draw_pass_1 as QuadMesh
		assert_true(mesh != null, "%s draws a quad sprite" % p.get_parent().name)
		var mat := mesh.material as StandardMaterial3D
		assert_true(mat.albedo_texture is GradientTexture2D, "%s is a soft radial sprite" % p.get_parent().name)
		assert_eq((mat.albedo_texture as GradientTexture2D).fill, GradientTexture2D.FILL_RADIAL, "radial")
	before_each()


func test_continuous_effects_stop_on_the_ko() -> void:
	for id in BOSSES:
		var a := _actor(id)
		var vfx := _vfx(a)
		vfx.build_late()
		vfx._process(STEP_SEC)
		var always: Array[StringName] = []
		for e: Variant in CreatureAmbientVfx.row_for(id).get("effects", []):
			var def := e as Dictionary
			if str(def.get("emit", "")) == CreatureAmbientVfx.EMIT_ALWAYS:
				always.append(StringName(str(def["id"])))
		for eid in always:
			assert_true(vfx.is_emitting(eid), "%s %s emits alive" % [id, eid])
		a.set_ko(true, KO_ALPHA)
		vfx._process(STEP_SEC)
		for e: Variant in CreatureAmbientVfx.row_for(id).get("effects", []):
			var eid := StringName(str((e as Dictionary)["id"]))
			if (e as Dictionary).has("emit"):
				assert_false(vfx.is_emitting(eid), "%s %s stops on the KO" % [id, eid])
	before_each()


func test_the_engine_ko_lifts_its_light_and_darkens_its_lamps() -> void:
	var a := _actor(&"lamp_engine")
	var vfx := _vfx(a)
	vfx.build_late()
	vfx._process(STEP_SEC)
	var light := vfx.effect(&"core_light") as OmniLight3D
	assert_true(light != null and light.light_energy > 0.0, "the core light burns alive")
	a.set_ko(true, KO_ALPHA)
	_step(vfx, &"ko_lift")
	assert_true(vfx.played.has(&"ko_lift"), "the KO lifts the core's bound light")
	vfx._dark.custom_step(LONG_SEC)
	assert_eq(light.light_energy, 0.0, "the core light is out")
	var halo_mat := (vfx._halo_mats[&"lamp_halos"] as Array)[0] as StandardMaterial3D
	assert_eq(halo_mat.albedo_color.a, 0.0, "the lamps' halos are dark")
	assert_false(vfx._dark_mats.is_empty(), "the lamp glass and the core are this Engine's own copies")
	for pair: Array in vfx._dark_mats:
		var mat := pair[0] as ShaderMaterial
		assert_eq(float(mat.get_shader_parameter(&"emission_energy")), 0.0, "%s has gone dark" % mat.resource_name)
	var lift := vfx.effect(&"ko_lift") as GPUParticles3D
	var ramp := ((lift.process_material as ParticleProcessMaterial).color_ramp as GradientTexture1D).gradient
	assert_eq(ramp.interpolation_color_space, Gradient.GRADIENT_COLOR_SPACE_OKLAB, "the release blends in Oklab")
	before_each()


func test_the_drowner_motes_lift_on_a_break_and_on_the_ko() -> void:
	var a := _actor(&"mangrove_drowner")
	var vfx := _vfx(a)
	vfx._process(STEP_SEC)
	assert_true(vfx.is_emitting(&"snag_drift_a"), "the snagged motes drift in cradle A")
	var snag_a := a.find_child("SnagA", true, false) as Node3D
	snag_a.visible = false  # the break part's swap (CreatureActor.set_part_broken once combat keys it)
	vfx._process(STEP_SEC)
	assert_true(vfx.played.has(&"snag_lift_a"), "breaking cradle A lifts its motes")
	assert_false(vfx.is_emitting(&"snag_drift_a"), "cradle A's drift stops once its motes are freed")
	assert_true(vfx.is_emitting(&"snag_drift_b"), "cradle B still holds its motes")
	a.set_ko(true, KO_ALPHA)
	_step(vfx, &"snag_lift_b")
	assert_true(vfx.played.has(&"snag_lift_b"), "the KO lifts the motes still held")
	assert_eq(vfx.played.count(&"snag_lift_a"), 1, "freed motes do not lift twice")
	assert_false((a.find_child("SnagB", true, false) as Node3D).visible, "cradle B's beads are gone with the lift")
	before_each()


func test_the_drowner_drags_silt_while_it_hauls() -> void:
	var a := _actor(&"mangrove_drowner")
	var vfx := _vfx(a)
	vfx._process(STEP_SEC)
	assert_false(vfx.is_emitting(&"drag_silt_a"), "no silt at idle")
	a.play_clip(&"attack")
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.seek(a.contact_time(&"attack"), true)
	vfx._process(STEP_SEC)
	assert_true(vfx.is_emitting(&"drag_silt_a"), "silt trails the drag root at the haul")
	before_each()


func test_the_ram_breathes_and_sheds_on_hits_until_the_ko() -> void:
	var a := _actor(&"avalanche_ram")
	var vfx := _vfx(a)
	_step(vfx, &"breath")
	assert_true(vfx.played.has(&"breath"), "the Ram's breath steams")
	a.play_hit()
	vfx._process(STEP_SEC)
	assert_true(vfx.played.has(&"hit_snow_near"), "a hit shakes snow loose")
	a.play_clip(&"fleece_shake")
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	vfx._process(STEP_SEC)
	player.seek(a.contact_time(&"fleece_shake") + STEP_SEC, true)
	vfx._process(STEP_SEC)
	assert_true(vfx.played.has(&"shake_snow_near"), "the fleece shake flings snow at its contact")
	a.set_ko(true, KO_ALPHA)
	vfx._process(STEP_SEC)
	var breaths := vfx.played.count(&"breath")
	for i in MAX_STEPS:
		vfx._process(STEP_SEC)
	assert_eq(vfx.played.count(&"breath"), breaths, "a fallen Ram does not breathe")
	before_each()


func test_the_wake_stays_level_on_the_water_line() -> void:
	var a := _actor(&"wakefin")
	var vfx := _vfx(a)
	vfx._process(STEP_SEC)
	var p := vfx.effect(&"wake_wash") as GPUParticles3D
	var def: Dictionary = CreatureAmbientVfx.row_for(&"wakefin")["effects"][0]
	var local := a.global_transform.affine_inverse() * p.global_position
	assert_between(local.y, float(def["pin_y_m"]) - 0.001, float(def["pin_y_m"]) + 0.001, "the wake rides the water")
	assert_true(p.global_basis.y.is_equal_approx(a.global_basis.y), "the wake lies flat")
	before_each()


func _step(vfx: CreatureAmbientVfx, until: StringName) -> void:
	for i in MAX_STEPS:
		vfx._process(STEP_SEC)
		if vfx.played.has(until):
			return


func _vfx(a: CreatureActor) -> CreatureAmbientVfx:
	for c in a.get_children():
		if c is CreatureAmbientVfx:
			return c as CreatureAmbientVfx
	return null


func _actor(id: StringName) -> CreatureActor:
	var row := CreatureActor.row_for(id)
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


func _json(path: String) -> Variant:
	return JSON.parse_string(FileAccess.get_file_as_string(path))
