extends TestCase
## M2-HER-1104: HeroIdleMicro, the idle micro-motion layered on a hero's clip or pose: breathing and a
## weight shift from data, deterministic per actor, nothing at amount 0, a soft no-op without bones,
## and a head lead (capped) that follows the body's turn rate.

const ASHA := "res://assets/characters/asha/asha.glb"
const DT := 1.0 / 60.0
const EPS := 0.00001
const SECONDS := 6.0


func _sample(m: HeroIdleMicro) -> Array:
	var out: Array = []
	for c: Dictionary in m.contributions():
		out.append(snappedf(float(c["angle"]), EPS))
	return out


func _run(m: HeroIdleMicro, sec: float) -> void:
	for i in roundi(sec / DT):
		m.advance(DT)


func _all_zero(angles: Array) -> bool:
	for a: Variant in angles:
		if absf(float(a)) > EPS:
			return false
	return true


func test_tuning_comes_from_data() -> void:
	var m := HeroIdleMicro.new(&"asha")
	var d := HeroIdleMicro.load_data()
	assert_eq(m.data, d, "the modifier reads idle_micro.json")
	var b := d["breath"] as Dictionary
	var base := float(b["period_sec"])
	var spread := float(b["period_spread"])
	assert_between(m.breath_period(), base * (1.0 - spread), base * (1.0 + spread), "the breath period")
	assert_true(m.sway_period() > m.breath_period(), "the weight shifts slower than she breathes")
	m.free()


func test_the_same_actor_moves_the_same_way() -> void:
	var a := HeroIdleMicro.new(&"asha")
	var b := HeroIdleMicro.new(&"asha")
	_run(a, SECONDS)
	_run(b, SECONDS)
	assert_eq(_sample(a), _sample(b), "same id, same clock: the same pose")
	var r := HeroIdleMicro.new(&"rhen")
	_run(r, SECONDS)
	assert_ne(_sample(a), _sample(r), "another hero breathes out of step")
	assert_ne(a.breath_period(), r.breath_period(), "and at its own rate")
	for m: HeroIdleMicro in [a, b, r]:
		m.free()


func test_it_breathes_and_shifts_over_time() -> void:
	var m := HeroIdleMicro.new(&"toma")
	var lo := 1.0
	var hi := 0.0
	var sway_lo := 1.0
	var sway_hi := -1.0
	for i in roundi(m.sway_period() / DT):
		m.advance(DT)
		lo = minf(lo, m.breath())
		hi = maxf(hi, m.breath())
		sway_lo = minf(sway_lo, m.sway())
		sway_hi = maxf(sway_hi, m.sway())
	assert_true(lo < 0.05 and hi > 0.95, "a full breath in and out")
	assert_true(sway_lo < -0.95 and sway_hi > 0.95, "the weight goes to each foot")
	m.free()


func test_amount_zero_is_no_motion() -> void:
	var m := HeroIdleMicro.new(&"asha")
	m.amount = 0.0
	m.amount_now = 0.0
	for i in 5:
		_run(m, 0.7)
		assert_true(_all_zero(_sample(m)), "no breathing or sway at amount 0 (t=%.2f)" % m.clock)
	m.amount = 1.0
	_run(m, 1.0)
	assert_false(_all_zero(_sample(m)), "back to breathing once standing")
	m.free()


func test_amount_eases_rather_than_pops() -> void:
	var m := HeroIdleMicro.new(&"asha")
	m.amount = 0.0
	m.advance(DT)
	var fade := float(m.data["amount_fade_sec"])
	assert_between(m.amount_now, 1.0 - DT / fade - EPS, 1.0 - DT / fade + EPS, "one frame of the fade")
	_run(m, fade)
	assert_eq(m.amount_now, 0.0, "out after amount_fade_sec")
	m.free()


func test_the_head_leads_a_turn_and_is_capped() -> void:
	var m := HeroIdleMicro.new(&"asha")
	m.use_measured_rate = false
	var lead := m.data["head_lead"] as Dictionary
	var cap := deg_to_rad(float(lead["max_deg"]))
	m.turn_rate = deg_to_rad(90.0)
	assert_between(m.head_lead(), deg_to_rad(90.0) * float(lead["lead_sec"]) - EPS, cap, "ahead, by lead_sec")
	m.turn_rate = -deg_to_rad(3000.0)
	assert_between(m.head_lead(), -cap - EPS, -cap + EPS, "never further than max_deg")
	m.turn_rate = 0.0
	assert_eq(m.head_lead(), 0.0, "still: the head over the body")
	m.free()


func test_the_turn_rate_is_measured_from_the_body() -> void:
	var m := HeroIdleMicro.new(&"asha")
	var yaw := 0.0
	var rate := deg_to_rad(120.0)
	for i in 60:
		m.advance(DT, wrapf(yaw, -PI, PI))
		yaw += rate * DT
	assert_between(m.turn_rate, rate * 0.98, rate * 1.02, "the smoothed rate reaches the body's")
	for i in 30:
		m.advance(DT, wrapf(yaw, -PI, PI))
	assert_between(m.turn_rate, -0.01, 0.01, "and falls back once it stops")
	m.free()


func test_it_turns_the_real_bones_and_none_on_a_bare_skeleton() -> void:
	var a := (load(ASHA) as PackedScene).instantiate() as Node3D
	_host().add_child(a)
	var skel := HeroMotion.skeleton_of(a)
	var m := HeroIdleMicro.new(&"asha")
	_run(m, 1.3)
	var chest := skel.find_bone("DEF-spine.003")
	var before := skel.get_bone_pose_rotation(chest)
	assert_true(m.apply(skel) > 0, "breathing turns Asha's bones")
	var after := skel.get_bone_pose_rotation(chest)
	assert_true(before.angle_to(after) > 0.0001, "the chest moved")
	assert_true(before.angle_to(after) < deg_to_rad(5.0), "a little")
	var fwd := HeroIdleMicro.forward_of(skel)
	assert_true(fwd.z > 0.9, "the hero glTFs face +Z, read from the feet")
	var bare := Skeleton3D.new()
	bare.add_bone("root")
	_host().add_child(bare)
	assert_eq(m.apply(bare), 0, "no listed bones: nothing turned")
	assert_eq(m.apply(null), 0, "no skeleton: nothing")
	assert_eq(HeroIdleMicro.forward_of(bare), HeroIdleMicro.DEFAULT_FORWARD, "and the default facing")
	m.free()
	a.free()
	bare.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
