extends TestCase
## M3-C09-03: the Ebbing's motes. Every Ch9 `@vfx` cue's mark has a held field, the rig never releases, the staff's
## pull is low enough that a still at its highest point still reads as light going down (item 3), the mourners let
## go over their ramp (item 4), and the cutaway's field takes no attractor (item 8).

const CH09_DLG := "res://game/data/dialogue/ch09"
const RIG := "res://game/vfx/ebbing/ebbing_motes.gd"
const SHOTS := "res://game/levels/_tests/ebbing/ebbing_shots.tscn"
const GLIMMER := "res://game/data/vfx/glimmer.json"
const SAMPLES := 2000
const SEED := 905
## Item 3's bar: under the raised staff, at most this share of the held motes may head up (a still never reads as
## rising), while a full-strength pull lifts more than RISING_FULL_MIN_SHARE of them.
const RISING_MAX_SHARE := 0.05
const RISING_FULL_MIN_SHARE := 0.2


func test_every_ch09_cue_mark_has_a_held_field_and_nothing_is_released() -> void:
	var data := EbbingMotes.load_data()
	var fields := data["fields"] as Dictionary
	var cues := 0
	for f in DirAccess.get_files_at(CH09_DLG):
		if not f.ends_with(".dlg"):
			continue
		for raw in FileAccess.get_file_as_string(CH09_DLG.path_join(f)).split("\n"):
			var ln := raw.strip_edges()
			if not ln.begins_with("@vfx glimmer_held"):
				continue
			var at := ln.get_slice("at=", 1).get_slice(" ", 0)
			assert_true(fields.has(at), "%s: a field for %s" % [f, at])
			cues += 1
	assert_true(cues > 0, "the chapter cues its motes")
	var rig := EbbingMotes.new()
	rig.data = data
	for id: String in fields:
		var field := rig.build_field(fields[id] as Dictionary)
		assert_eq(field.mode, GlimmerState.Mode.HELD, "%s is held" % id)
		assert_true(field.sea_direction.z > 0.9, "%s drifts out of the harbour mouth" % id)
		field.free()
	rig.free()
	assert_false(FileAccess.get_file_as_string(RIG).contains(".release("), "the rig never lets the light go")


func test_the_cutaway_takes_no_attractor() -> void:
	var row := (EbbingMotes.load_data()["fields"] as Dictionary)["wallhead_motes"] as Dictionary
	assert_false(bool(row.get("staff", false)) or bool(row.get("mourners", false)), "nothing gathers on the wall-head")
	assert_false(bool(row.get("focus", true)), "and it is never the scene's focus")


## Item 3: with Asha's staff at its highest, the median heading of the motes it pulls up out of the stream below still
## goes down, and almost none of them rise (among the motes it has any hold on). A CPU replica of
## glimmer_motes_process.gdshader's held drift and orbit blend (target = mix(held, pull + held * keep, weight)),
## sampled through the stream under the raised head. A full-strength staff would lift a good share of the same motes
## (the test's own check that it can fail).
func test_a_still_at_the_staffs_highest_point_heads_down() -> void:
	var staff := EbbingMotes.load_data()["staff"] as Dictionary
	var tuned := _headings(float(staff["strength"]))
	assert_true(tuned[0] < 0.0, "the median mote under the raised staff still sinks (%f)" % tuned[0])
	assert_true(tuned[1] < RISING_MAX_SHARE, "almost none rise (%f)" % tuned[1])
	assert_true(_headings(1.0)[1] > RISING_FULL_MIN_SHARE, "a full-strength staff would lift them: the tuning holds")


## [median heading y (m/s), share heading up] of the motes under the raised head that the staff has any hold on.
func _headings(strength: float) -> Array[float]:
	var data := EbbingMotes.load_data()
	var g := JSON.parse_string(FileAccess.get_file_as_string(GLIMMER)) as Dictionary
	var held := (g["modes"] as Dictionary)["held"] as Dictionary
	var att := g["attractor"] as Dictionary
	var staff := data["staff"] as Dictionary
	var sea := EbbingMotes._vec(data["sea_direction"]).normalized()
	var head := EbbingMotes._vec(staff["head_offset_m"])
	var half := float(staff["half_height_m"])
	var radius := float(staff["radius_m"])
	var influence := maxf(radius * float(att["influence_scale"]), radius * 1.01)
	var rng := RandomNumberGenerator.new()
	rng.seed = SEED
	var ys: Array[float] = []
	for i in SAMPLES:
		# A mote in the stream under the raised head, within its reach.
		var p := (
			head
			+ Vector3(rng.randf_range(-1, 1) * influence, -rng.randf() * influence, rng.randf_range(-1, 1) * influence)
		)
		var heading := deg_to_rad((rng.randf() * 2.0 - 1.0) * float(held["heading_spread_deg"]))
		var lateral := sea.rotated(Vector3.UP, -heading)
		var bias := deg_to_rad(lerpf(float(held["down_bias_min_deg"]), float(held["down_bias_max_deg"]), rng.randf()))
		var speed := lerpf(float(held["drift_min_mps"]), float(held["drift_max_mps"]), rng.randf())
		var v_held := (lateral * cos(bias) - Vector3.UP * sin(bias)) * speed
		var axis := Vector3(head.x, clampf(p.y, head.y - half, head.y + half), head.z)
		var d := p - axis
		var dist := d.length()
		var w := (1.0 - smoothstep(radius, influence, dist)) * clampf(strength, 0.0, 1.0)
		var n := d / maxf(dist, 1e-5)
		var radial := -n * clampf((dist - radius) / radius, -1.0, 1.0) * float(att["pull_mps"]) * strength
		var flat := Vector3(n.x, 0.0, n.z)
		var tangent := Vector3.UP.cross(flat.normalized()) if flat.length() > 1e-5 else Vector3.ZERO
		var pull := radial + tangent * float(att["swirl_mps"]) * float(staff["swirl"]) * strength
		if w > 0.0:  # only the motes the staff has hold of
			ys.append(v_held.lerp(pull + v_held * float(att["keep_drift"]), w).y)
	ys.sort()
	var rising := ys.filter(func(y: float) -> bool: return y > 0.0).size()
	return [ys[ys.size() / 2], float(rising) / float(ys.size())] as Array[float]


func test_mourners_let_go_over_their_ramp() -> void:
	var ramp := float((EbbingMotes.load_data()["mourners"] as Dictionary)["ramp_s"])
	assert_eq(EbbingMotes.mourner_share(-1.0, ramp), 1.0, "held until the staff passes")
	assert_eq(EbbingMotes.mourner_share(0.0, ramp), 1.0, "it starts to let go as the staff passes")
	var mid := EbbingMotes.mourner_share(ramp * 0.5, ramp)
	assert_between(mid, 0.01, 0.99, "reluctantly, not at once")
	assert_eq(EbbingMotes.mourner_share(ramp + 0.1, ramp), 0.0, "gone after the ramp")


func test_the_zone_plays_every_field_with_its_anchors() -> void:
	var scene := (load(SHOTS) as PackedScene).instantiate() as EbbingShotRig
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(scene)
	var ebb := scene.ebbing
	assert_true(ebb != null, "the zone's dressing carries the Ebbing")
	assert_true(ebb.is_in_group(EbbingMotes.VFX_HOSTS_GROUP), "the sequencer can offer it the cues")
	var fields := ebb.data["fields"] as Dictionary
	assert_eq(ebb.fields.size(), fields.size(), "every field plays")
	assert_eq((ebb.fields[&"harbour_stream"] as GlimmerField).get_attractor_count(), 1, "the stream follows the staff")
	assert_eq((ebb.fields[&"mourners_motes"] as GlimmerField).get_attractor_count(), 5, "the staff and four mourners")
	assert_eq((ebb.fields[&"wallhead_motes"] as GlimmerField).get_attractor_count(), 0, "nothing on the wall-head")
	assert_true(ebb.staff_head != null and ebb.staff_head.get_parent().name == "asha", "the staff head rides on Asha")
	assert_false(ebb.play_vfx("glimmer_lift", &"harbour_stream"), "never released light")
	assert_false(ebb.play_vfx("glimmer_held", &"nowhere"), "other marks stay the placeholder's")
	scene.free()
