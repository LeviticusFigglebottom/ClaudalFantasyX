extends TestCase
## M2-BPR-04: the specials' presentation. Each Swell technique plays its own row (Lamp Dive leaps and plunges,
## the Verse lifts each ally in turn, Return Tide braces then counters, Written Light writes its glyph); the
## Drownbell's toll lands on the contact beat (BattleBossVfx's ring with it) and the shockwave reaches each party
## member in turn; BattleBossChoreo only listens; the Vowbound's call steps the party off and Ilun rises, a
## dismissal sinks him and walks the party back, a fall takes the blow and draws him under; at pacing 0 it all
## lands at once; the capture states reach their frames.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const EPS := 0.001
const ILUN := &"ilun"

var ctl: BattleController
var choreo: BattleChoreo
var data: Dictionary


func before_each() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	data = BattleChoreo.load_data()


func _start(fixture_id: StringName) -> void:
	ctl.start_fixture(BattleFixture.load_fixture(fixture_id))
	choreo = ctl.stage.choreo
	choreo.live = false
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0


# --- data -----------------------------------------------------------------------------------


func test_every_swell_technique_and_the_toll_has_its_own_row() -> void:
	var by_skill := data["style_by_skill"] as Dictionary
	var swell := BattleSwell.load_config()
	var seen: Dictionary = {}
	for hero: Dictionary in swell["heroes"]:
		for tech: String in hero["techniques"]:
			var sid := str(by_skill.get(tech, ""))
			assert_true((data["styles"] as Dictionary).has(sid), "%s has a style" % tech)
			assert_false(seen.has(sid), "%s does not share its row" % tech)
			seen[sid] = true
			var st := (data["styles"] as Dictionary)[sid] as Dictionary
			assert_true(BattleClips.ALL.has(StringName(str(st["clip"]))), "%s clip is in the contract" % tech)
			assert_eq(str(st.get("shot", "")), "finisher", "%s asks the camera for its finisher framing" % tech)
	assert_eq(str(by_skill["toll"]), "toll")
	var db := BattleDB.load_default()
	for boss: String in data["bosses"]:
		if boss == "doc":
			continue
		assert_true(db.enemies.has(StringName(boss)), "%s is an enemy" % boss)
		assert_false(db.skill(StringName(str(data["bosses"][boss]["charge_skill"]))).is_empty(), "charge skill")
	var vb := data["vowbound"] as Dictionary
	assert_true(float(vb["entry"]["sec"]) > float(data["enter"]["sec"]), "Ilun's entry is longer than a walk-in")
	_free()


# --- Swell finishers ------------------------------------------------------------------------


func test_lamp_dive_leaps_then_plunges_onto_the_contact() -> void:
	_start(&"choreo_lamp_dive")
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var foe := _foe(&"gull_harrier")
	var r := ctl.unleash(&"lamp_dive", [foe], {})
	assert_true(r.ok, "Lamp Dive unleashed")
	var plan := choreo.current()
	assert_eq(plan["style"], "dive")
	assert_eq(plan["shot"], "finisher", "the camera director reads the framing from the plan")
	var arc := float(choreo.style("dive")["arc_m"])
	var home_y := choreo._home_of(&"rhen").origin.y
	choreo.advance(float(plan["approach_end"]))
	assert_between(_at(&"rhen").y - home_y, arc * 0.95, arc + EPS, "the leap's top at the end of the approach")
	var mid := (float(plan["approach_end"]) + float(plan["contact"])) * 0.5
	choreo.advance(mid - float(plan["approach_end"]))
	var mid_y := _at(&"rhen").y - home_y
	assert_true(mid_y > 0.1 and mid_y < arc * 0.9, "mid-plunge: falling (%s)" % mid_y)
	choreo.advance(float(plan["contact"]) - mid + EPS)
	assert_true(_at(&"rhen").y - home_y < 0.05, "down on the contact")
	choreo.finish()
	_assert_home(&"rhen")
	_free()


func test_the_verse_lifts_each_healed_ally_in_turn() -> void:
	_start(&"choreo_lamp_dive")
	var r := _result(&"asha", &"shallows_verse", [_hit(&"rhen", -20), _hit(&"toma", -20), _hit(&"ysolde", -20)])
	var plan := choreo.plan_for(r)
	assert_eq(plan["style"], "verse")
	var stagger := float(choreo.style("verse")["stagger_sec"])
	var ats: Array[float] = []
	for x: Dictionary in plan["reactions"]:
		assert_eq(x["kind"], BattleChoreo.REACT_HEAL)
		ats.append(float(x["at"]))
	assert_eq(ats.size(), 3)
	for i in ats.size():
		assert_between(ats[i], float(plan["contact"]) + stagger * i - EPS, float(plan["contact"]) + stagger * i + EPS)
	var heal_sec := float(data["reaction"]["heal"]["sec"])
	assert_true(float(plan["total"]) >= ats[2] + heal_sec - EPS, "the total covers the last lift")
	_free()


func test_written_light_writes_its_glyph_and_reaches_each_foe_in_turn() -> void:
	_start(&"choreo_lamp_dive")
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var foes: Array[StringName] = []
	var hits: Array[Dictionary] = []
	for e in ctl.engine.enemies:
		foes.append(e.id)
		hits.append(_hit(e.id, 5))
	ctl.engine.action_resolved.emit(_result(&"rhen", &"written_light", hits))
	var plan := choreo.current()
	assert_eq(plan["style"], "glyph")
	var st := choreo.style("glyph")
	var a := float(plan["approach_end"])
	var c := float(plan["contact"])
	choreo.seek(a + (c - a) * 0.5 / float(st["trace_strokes"]))  # the first stroke at its widest
	var from: Vector3 = plan["to"]
	var dir: Vector3 = plan["dir"]
	var side := Vector3.UP.cross(dir).normalized()
	if not bool(plan["actor_clip"]):  # a hero model's finisher clip writes it in place of the traced strokes
		assert_between((_at(&"rhen") - from).dot(side), float(st["trace_m"]) - 0.01, float(st["trace_m"]) + 0.01)
	var stagger := float(st["stagger_sec"])
	choreo.seek(c + stagger * 0.5)
	assert_true(_struck(foes[0]), "the first foe is struck")
	assert_false(_struck(foes[2]), "the light has not reached the last yet")
	choreo.seek(c + stagger * 2.5)
	assert_true(_struck(foes[2]), "then it does")
	_free()


func test_return_tide_braces_back_then_counters() -> void:
	_start(&"choreo_lamp_dive")
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var foe := _foe(&"gull_harrier")
	ctl.engine.action_resolved.emit(_result(&"rhen", &"return_tide", [_hit(foe, 10)]))
	var plan := choreo.current()
	assert_eq(plan["style"], "brace")
	var st := choreo.style("brace")
	var a := float(plan["approach_end"])
	var c := float(plan["contact"])
	var to: Vector3 = plan["to"]
	var dir: Vector3 = plan["dir"]
	if bool(plan["actor_clip"]):  # a hero model's finisher clip braces and counters in place of the procedural shape
		choreo.seek(c)
		var p := BattleClips.player_of(ctl.stage.stand_in(&"rhen"))
		assert_eq(StringName(p.current_animation), BattleClips.FINISHER, "the finisher clip plays to its contact")
		_free()
		return
	choreo.seek(a + (c - a) * float(st["windup_at"]))
	var braced := _at(&"rhen")
	assert_true((braced - to).dot(dir) < -0.1, "planted and pushed back by the tide")
	assert_true(braced.y < to.y - 0.05, "crouched")
	choreo.seek(c)
	assert_true((_at(&"rhen") - to).dot(dir) > 0.3, "the counter thrust lands on the contact")
	_free()


# --- the Drownbell --------------------------------------------------------------------------


func test_the_toll_lands_on_contact_and_the_wave_reaches_each_member_in_turn() -> void:
	_start(&"choreo_toll")
	ctl.pacing_scale = 1.0
	var bell := ctl.engine.enemies[0].id
	var boss_vfx := (ctl.stage.get_node(^"BattleVfx") as BattleVfx).boss
	var hits: Array[Dictionary] = []
	for c in ctl.engine.party_active:
		hits.append(_hit(c.id, 10))
	ctl.engine.action_resolved.emit(_result(bell, &"toll", hits))
	var plan := choreo.current()
	assert_eq(plan["style"], "toll")
	assert_eq(plan["shot"], "toll")
	assert_false(boss_vfx.moments.has(&"toll"), "no shockwave before the toll lands")
	choreo.seek(float(plan["contact"]))
	assert_true(boss_vfx.moments.has(&"toll"), "BattleBossVfx's shockwave starts on the contact beat")
	var st := choreo.style("toll")
	var wave := float(st["wave_m_s"])
	var nearest := plan["reactions"][0] as Dictionary
	for x: Dictionary in plan["reactions"]:
		var tid := StringName(str(x["target"]))
		var dist := Vector2(_home(tid).x - _home(bell).x, _home(tid).z - _home(bell).z).length()
		assert_between(float(x["at"]) - float(plan["contact"]), dist / wave - 0.01, dist / wave + 0.01, "%s" % tid)
		if float(x["at"]) < float(nearest["at"]):
			nearest = x
	var near_id := StringName(str(nearest["target"]))
	var react_sec := float(data["reaction"]["damage"]["sec"])
	choreo.seek(float(nearest["at"]) + react_sec * 0.5)
	var recoil := float(data["reaction"]["damage"]["recoil_m"]) * float(st["react_scale"]) * float(nearest["weight"])
	assert_between(_at(near_id).distance_to(_home(near_id)), recoil * 0.9, recoil * 1.1, "a hard recoil")
	for x: Dictionary in plan["reactions"]:
		if float(x["at"]) > float(nearest["at"]) + react_sec * 0.5 + EPS:
			var far := StringName(str(x["target"]))
			assert_true(_at(far).distance_to(_home(far)) < EPS, "%s waits for the wave" % far)
	choreo.finish()
	for c in ctl.engine.party_active:
		_assert_home(c.id)
	_free()


func test_the_boss_helper_only_listens() -> void:
	_start(&"choreo_toll")
	ctl.pacing_scale = 1.0
	var boss := choreo.boss
	assert_true(boss != null, "the Drownbell has a set piece")
	var bell := ctl.engine.find(boss.boss_id)
	var before := _state()
	ctl.engine.charge_started.emit(bell, &"toll", 2)
	assert_false(choreo.has_accent(bell.id), "the gather waits for its action's contact")
	choreo.contact.emit(_result(bell.id, &"toll_gather", []))
	assert_true(choreo.has_accent(bell.id), "the bell sways as it gathers")
	choreo.advance(10.0)
	ctl.engine.charge_broken.emit(bell, &"toll")
	choreo.contact.emit(_result(&"toma", &"attack", [_hit(bell.id, 5)]))
	assert_true(choreo.has_accent(bell.id), "the rim break staggers the bell on the blow's contact")
	choreo.advance(10.0)
	ctl.engine.phase_changed.emit(bell, &"flood")
	for c in ctl.engine.party_active:
		assert_true(choreo.has_accent(c.id), "%s braces against the flood" % c.id)
	choreo.advance(0.05)
	var first := ctl.engine.party_active[0].id
	assert_true(_at(first).distance_to(_home(first)) > EPS, "the brace moves the root, the first in slot order first")
	var last := ctl.engine.party_active[ctl.engine.party_active.size() - 1].id
	assert_true(_at(last).distance_to(_home(last)) < EPS, "the last braces after")
	choreo.advance(10.0)
	assert_eq(boss.moments, [&"gather", &"rim_break", &"flood"] as Array[StringName])
	assert_eq(_state(), before, "no combat state changed")
	for c in ctl.engine.party_active:
		_assert_home(c.id)
	_free()


func test_no_boss_no_helper_and_nothing_moves_at_pacing_0() -> void:
	_start(&"choreo_lamp_dive")
	assert_eq(choreo.boss, null, "a reef battle has no set piece")
	_free()
	before_each()
	_start(&"choreo_toll")
	var bell := ctl.engine.find(choreo.boss.boss_id)
	ctl.engine.charge_started.emit(bell, &"toll", 2)
	choreo.contact.emit(_result(bell.id, &"toll_gather", []))
	assert_false(choreo.has_accent(bell.id), "instant pacing: no accent")
	_free()


# --- the Vowbound ---------------------------------------------------------------------------


func test_the_call_steps_the_party_off_and_ilun_rises_at_his_slot() -> void:
	_start(&"choreo_vowbound_rise")
	_to_turn_of(&"asha")
	ctl.pacing_scale = 1.0
	var rhen := ctl.stage.stand_in(&"rhen")
	assert_true(ctl.vow.call_vowbound(ILUN))
	assert_false(choreo.leaving(&"rhen").is_empty(), "Rhen steps off")
	assert_false(choreo.leaving(&"asha").is_empty(), "Asha steps off")
	assert_true(choreo.has_accent(&"asha"), "the caller makes her call first")
	assert_false(choreo.has_accent(&"rhen"), "only the caller calls")
	assert_true(choreo.is_entering(ILUN), "Ilun enters")
	var ilun := ctl.stage.stand_in(ILUN)
	assert_false(ilun.visible, "unseen until the party has stepped off")
	var rise := choreo.entering(ILUN)
	var spec := rise["spec"] as Dictionary
	assert_eq(spec, data["vowbound"]["entry"] as Dictionary, "the Vowbound's own entrance")
	assert_true(ctl.stage.hold_after(0.0) >= -float(rise["t"]) + float(spec["sec"]) - EPS, "the hand-off waits")
	choreo.advance(-float(rise["t"]) + float(spec["sec"]) * 0.5)
	assert_true(ilun.visible, "rising")
	var below := choreo._home_of(ILUN).origin.y - ilun.transform.origin.y
	assert_true(below > 0.3 and below < float(spec["depth_m"]), "half way up out of the water (%s)" % below)
	assert_true(rhen.is_queued_for_deletion(), "the party has stepped off and gone")
	choreo.advance(float(spec["sec"]))
	assert_false(choreo.is_entering(ILUN))
	_assert_home(ILUN)
	_free()


func test_a_dismissal_sinks_ilun_and_walks_the_party_back() -> void:
	_start(&"choreo_vowbound_rise")
	_to_turn_of(&"asha")
	ctl.pacing_scale = 1.0
	ctl.vow.call_vowbound(ILUN)
	choreo.advance(10.0)
	var ilun := ctl.stage.stand_in(ILUN)
	assert_true(ctl.vow.dismiss(), "dismissed on his own turn")
	var gone := choreo.leaving(ILUN)
	assert_eq(gone["spec"], data["vowbound"]["dismiss"], "he sinks back")
	var walk := choreo.entering(&"rhen")
	assert_false(walk.is_empty(), "the party walks back in")
	assert_true(float(walk["t"]) < 0.0 and not ctl.stage.stand_in(&"rhen").visible, "after Ilun has begun to go")
	assert_true(float(choreo.entering(&"asha")["t"]) < float(walk["t"]), "in slot order")
	choreo.advance(float(data["vowbound"]["dismiss"]["sec"]) * 0.5)
	assert_true(ilun.transform.origin.y < choreo._home_of(&"rhen").origin.y, "Ilun goes down into the water")
	choreo.advance(10.0)
	assert_true(ilun.is_queued_for_deletion(), "and is gone")
	for cid: StringName in [&"rhen", &"asha"]:
		assert_true(ctl.stage.stand_in(cid).visible)
		_assert_home(cid)
	_free()


func test_a_fallen_ilun_takes_the_blow_then_is_drawn_under() -> void:
	_start(&"choreo_vowbound_rise")
	_to_turn_of(&"asha")
	ctl.pacing_scale = 1.0
	ctl.vow.call_vowbound(ILUN)
	choreo.advance(10.0)
	var ilun := ctl.stage.stand_in(ILUN)
	var foe := ctl.engine.enemies[0].id
	ctl.engine.find(ILUN).hp = 0  # the blow below felled him (the test stands in for the engine)
	ctl.engine.action_resolved.emit(_result(foe, &"attack", [_hit(ILUN, 50)]))
	var plan := choreo.current()
	assert_eq(plan["kos"], [ILUN] as Array[StringName])
	ctl.engine.vowbound.recall(ctl.engine, false)
	var gone := choreo.leaving(ILUN)
	assert_eq(float((gone["spec"] as Dictionary)["tilt_deg"]), float(data["vowbound"]["fall"]["tilt_deg"]), "a fall")
	assert_between(-float(gone["t"]), float(plan["ko_at"]) - EPS, float(plan["ko_at"]) + EPS, "after the blow")
	var react_sec := float(data["reaction"]["damage"]["sec"])
	choreo.advance(float(plan["contact"]) + react_sec * 0.5)
	assert_true(ilun.transform.origin.distance_to(choreo._home(ilun).origin) > EPS, "he takes the blow first")
	choreo.advance(float(plan["ko_at"]) - float(plan["contact"]) - react_sec * 0.5)
	var fall_sec := float(data["vowbound"]["fall"]["sec"])
	choreo.advance(fall_sec * 0.5)
	assert_true(ilun.transform.basis.y.dot(Vector3.UP) < 0.95, "tipped back")
	assert_true(ilun.transform.origin.y < choreo._home(ilun).origin.y - 0.3, "drawn under")
	choreo.advance(fall_sec)
	assert_true(ilun.is_queued_for_deletion(), "gone")
	_free()


func test_instant_pacing_seats_the_call_and_the_dismissal_at_once() -> void:
	_start(&"choreo_vowbound_rise")
	_to_turn_of(&"asha")
	var rhen := ctl.stage.stand_in(&"rhen")
	ctl.vow.call_vowbound(ILUN)
	assert_true(choreo.leaving(&"rhen").is_empty() and rhen.is_queued_for_deletion(), "Rhen goes at once")
	assert_false(choreo.is_entering(ILUN))
	assert_true(ctl.stage.stand_in(ILUN).visible)
	_assert_home(ILUN)
	var ilun := ctl.stage.stand_in(ILUN)
	ctl.vow.dismiss()
	assert_true(choreo.leaving(ILUN).is_empty() and ilun.is_queued_for_deletion(), "Ilun goes at once")
	assert_false(choreo.is_entering(&"rhen"))
	assert_eq(ctl.stage.hold_after(0.4), 0.4, "nothing to wait for")
	_free()


# --- capture states -------------------------------------------------------------------------


func test_the_capture_states_reach_their_frames() -> void:
	ctl.run_script(&"choreo_lamp_dive")
	var plan := ctl.stage.choreo.current()
	assert_eq(plan.get("style"), "dive", "Lamp Dive plays")
	assert_true(ctl.stage.choreo.frozen)
	assert_true(ctl.stage.choreo.plan_time() < float(plan["contact"]), "mid-plunge, before the contact")
	_free()
	before_each()
	ctl.run_script(&"choreo_toll")
	plan = ctl.stage.choreo.current()
	assert_eq(plan.get("style"), "toll", "the Toll plays")
	assert_true((ctl.stage.get_node(^"BattleVfx") as BattleVfx).boss.moments.has(&"toll"), "its ring has started")
	_free()
	before_each()
	ctl.run_script(&"choreo_vowbound_rise")
	var rise := ctl.stage.choreo.entering(ILUN)
	assert_false(rise.is_empty(), "Ilun is rising")
	assert_between(float(rise["t"]), 0.0, float((rise["spec"] as Dictionary)["sec"]), "mid-rise")
	_free()


# --- helpers --------------------------------------------------------------------------------


func _foe(base: StringName) -> StringName:
	for e in ctl.engine.enemies:
		if String(e.id).get_slice("#", 0) == String(base) and e.is_alive():
			return e.id
	return ctl.engine.enemies[0].id


func _hit(tid: StringName, amount: int) -> Dictionary:
	return {"target_id": tid, "hit": true, "crit": false, "amount": amount, "statuses_added": []}


func _result(actor: StringName, skill: StringName, hits: Array[Dictionary]) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = actor
	r.skill_id = skill
	r.hits = hits
	return r


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


## Every combatant's combat state, for the listen-only check.
func _state() -> Array:
	var out: Array = [ctl.engine.now, ctl.engine.current.id if ctl.engine.current != null else &""]
	for c in ctl.engine.party_active + ctl.engine.party_reserve + ctl.engine.enemies:
		out.append([c.id, c.hp, c.mp, c.next_time, c.charge_left, c.charge_skill, c.swell])
	return out


## A fighter's stage-local position now / at home.
func _at(cid: StringName) -> Vector3:
	return ctl.stage.stand_in(cid).transform.origin


func _home(cid: StringName) -> Vector3:
	return choreo._home_of(cid).origin


func _assert_home(cid: StringName) -> void:
	var f := ctl.stage.stand_in(cid)
	assert_true(f.transform.is_equal_approx(choreo._home_of(cid)), "%s stands on its mark" % cid)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


## A foe reacting to a hit: a model with a hit clip plays it (creature models, M2-CRE-03; the clip contract), a
## primitive stand-in is knocked off its mark.
func _struck(id: StringName) -> bool:
	var f := ctl.stage.stand_in(id)
	if BattleClips.has_clip(f, BattleClips.HIT):
		return StringName(str(BattleClips.creature_of(f).get("current_clip"))) == BattleClips.HIT
	return _at(id).distance_to(_home(id)) > EPS
