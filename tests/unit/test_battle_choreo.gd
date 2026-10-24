extends TestCase
## M2-BPR-01/02: the battle choreography sequencer and the clip contract. Its data names real styles, skills and
## contract clips; an action becomes the right plan (style, beats, reactions, KOs); with pacing on, the actor
## travels and comes back, the floats and hit VFX land on the contact beat, a KO waits for its collapse and the
## controller's hand-off waits for the sequence; with pacing off or "skip animations" everything lands at once.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const EPS := 0.001

var ctl: BattleController
var choreo: BattleChoreo
var contacts := 0


func before_each() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED, p)
	choreo = ctl.stage.choreo
	choreo.live = false
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0
	contacts = 0
	choreo.contact.connect(func(r: ActionResult) -> void: contacts += 1 if r.actor_id == &"rhen" else 0)


# --- data -----------------------------------------------------------------------------------


func test_data_names_real_styles_skills_and_contract_clips() -> void:
	var data := BattleChoreo.load_data()
	var styles := data["styles"] as Dictionary
	assert_true(styles.has(BattleChoreo.FALLBACK_STYLE), "the fallback style exists")
	for id: String in styles:
		var st := styles[id] as Dictionary
		assert_true(float(st["strike_sec"]) > 0.0, "%s strikes for a while" % id)
		assert_between(float(st["contact_at"]), EPS, 1.0, "%s contact inside the strike" % id)
		assert_true(BattleClips.ALL.has(StringName(str(st["clip"]))), "%s clip is in the contract" % id)
		assert_true(str(st["travel"]) in ["target", "step", "none"], "%s travel" % id)
	for section in ["style_by_kind", "style_by_target", "style_by_skill"]:
		for key: String in data[section]:
			assert_true(styles.has(str(data[section][key])), "%s.%s names a style" % [section, key])
	assert_true(styles.has(str(data["item_style"])), "item style")
	for sid: String in data["style_by_skill"]:
		assert_false(ctl.engine.db.skill(StringName(sid)).is_empty(), "style_by_skill names a real skill: %s" % sid)
	for row: Dictionary in ctl.engine.db.skills.values():
		assert_true((data["style_by_kind"] as Dictionary).has(str(row["kind"])), "kind %s has a style" % row["kind"])
	for kind in ["damage", "heal", "miss"]:
		var clip := StringName(str(((data["reaction"] as Dictionary)[kind] as Dictionary)["clip"]))
		assert_true(BattleClips.ALL.has(clip), "reaction %s clip" % kind)
	_free()


# --- plans ----------------------------------------------------------------------------------


func test_attack_plans_a_melee_run_with_contact_inside_the_strike() -> void:
	var foe := _foe()
	var plan := choreo.plan_for(_result(&"attack", [_hit(foe, 10)]))
	assert_eq(plan["style"], "melee")
	assert_eq(plan["actor"], &"rhen")
	assert_true(float(plan["contact"]) > float(plan["approach_end"]), "contact after the approach")
	assert_true(float(plan["contact"]) <= float(plan["strike_end"]), "contact inside the strike")
	assert_true(float(plan["total"]) >= float(plan["return_end"]), "the total covers the return")
	assert_eq((plan["reactions"] as Array).size(), 1)
	assert_eq((plan["reactions"] as Array)[0]["kind"], BattleChoreo.REACT_DAMAGE)
	assert_eq((plan["kos"] as Array).size(), 0, "a foe left standing does not collapse")
	_free()


func test_styles_follow_skill_kind_target_and_item() -> void:
	var foe := _foe()
	assert_eq(choreo.plan_for(_result(&"ember", [_hit(foe, 8)]))["style"], "cast", "magical")
	assert_eq(choreo.plan_for(_result(&"mend", [_hit(&"asha", -12)]))["style"], "support", "heal")
	assert_eq(choreo.plan_for(_result(&"brace", [_hit(&"rhen", 0)]))["style"], "guard", "self target")
	assert_eq(choreo.plan_for(_result(&"read", [_hit(foe, 0)]))["style"], "read", "by skill")
	assert_eq(choreo.plan_for(_result(&"lamp_dive", [_hit(foe, 30)]))["style"], "dive", "a Swell finisher (M2-BPR-04)")
	var item := _result(&"", [_hit(&"asha", -20)])
	item.item_id = &"tonic"
	assert_eq(choreo.plan_for(item)["style"], "item", "an item")
	_free()


func test_reactions_by_hit_and_none_for_the_actor_itself() -> void:
	var foe := _foe()
	var miss := _hit(foe, 0)
	miss["hit"] = false
	var plan := choreo.plan_for(_result(&"attack", [miss]))
	assert_eq((plan["reactions"] as Array)[0]["kind"], BattleChoreo.REACT_MISS)
	plan = choreo.plan_for(_result(&"mend", [_hit(&"asha", -10), _hit(&"rhen", -10)]))
	assert_eq((plan["reactions"] as Array).size(), 1, "the actor never reacts to its own action")
	assert_eq((plan["reactions"] as Array)[0]["kind"], BattleChoreo.REACT_HEAL)
	assert_eq(choreo.plan_for(_result(&"brace", [_hit(&"rhen", 0)]))["reactions"], [])
	_free()


func test_a_felled_target_collapses_after_contact() -> void:
	var foe := ctl.engine.find(_foe())
	foe.hp = 0
	var plan := choreo.plan_for(_result(&"attack", [_hit(foe.id, 10)]))
	assert_eq(plan["kos"], [foe.id] as Array[StringName])
	assert_true(float(plan["ko_at"]) > float(plan["contact"]), "the KO waits for the blow")
	var collapse := float((BattleChoreo.load_data()["ko"] as Dictionary)["collapse_sec"])
	assert_true(float(plan["total"]) >= float(plan["ko_at"]) + collapse - EPS, "the total covers the collapse")
	_free()


func test_a_failed_action_has_no_plan() -> void:
	assert_eq(choreo.plan_for(ActionResult.failed(&"rhen", &"attack", &"no_mp")), {})
	assert_eq(choreo.plan_for(null), {})
	_free()


# --- playback -------------------------------------------------------------------------------


func test_instant_pacing_lands_everything_at_once() -> void:
	_to_turn_of(&"rhen")
	contacts = 0
	var r := ctl.act(&"attack", [_foe()])
	assert_true(r.ok)
	assert_false(choreo.playing(), "pacing 0 plays no sequence")
	assert_eq(contacts, 1, "the contact landed with the action")
	_assert_home(&"rhen")
	_free()


func test_skip_animations_lands_everything_at_once() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	choreo.skip = true
	ctl.act(&"attack", [_foe()])
	assert_false(choreo.playing())
	assert_eq(contacts, 1)
	assert_eq(ctl.stage.hold_after(0.8), 0.8, "the hand-off keeps its own hold")
	_free()


func test_attack_runs_to_the_target_lands_on_contact_and_comes_back() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var foe := _foe()
	var start := _pos(&"rhen")
	var gap := start.distance_to(_pos(foe))
	var finished: Array[StringName] = []
	choreo.sequence_finished.connect(func(cid: StringName) -> void: finished.append(cid))
	ctl.act(&"attack", [foe])
	assert_true(choreo.playing(), "the attack plays")
	assert_eq(contacts, 0, "nothing lands before the blow")
	var plan := choreo.current()
	assert_true(ctl.is_waiting(), "the controller holds the next turn")
	assert_true(choreo.remaining_sec() > 0.0)
	choreo.advance(float(plan["approach_end"]))
	assert_true(_pos(&"rhen").distance_to(_pos(foe)) < gap - 0.5, "Rhen ran at the foe")
	choreo.advance(float(plan["contact"]) - float(plan["approach_end"]) + EPS)
	assert_eq(contacts, 1, "the blow lands on the contact beat")
	# The clip contract: a model with a hit clip plays it (the sandbox foes are creature models since M2-CRE-03);
	# a primitive stand-in recoils procedurally.
	var model := ctl.stage.stand_in(foe)
	if BattleClips.has_clip(model, BattleClips.HIT):
		assert_eq(
			StringName(str(BattleClips.creature_of(model).get("current_clip"))), BattleClips.HIT, "the foe flinches"
		)
	else:
		assert_true(_pos(foe).distance_to(_home_pos(foe)) > EPS, "the foe recoils")
	choreo.advance(float(plan["total"]))
	assert_false(choreo.playing())
	assert_eq(finished, [&"rhen"] as Array[StringName])
	assert_eq(contacts, 1, "the blow lands once")
	_assert_home(&"rhen")
	_assert_home(foe)
	_assert_eq_v(start, _pos(&"rhen"), "back on the mark")
	_free()


func test_hand_off_waits_for_the_choreography() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	var rest := choreo.remaining_sec()
	var settle := float(BattleChoreo.load_data()["settle_sec"])
	assert_between(ctl.stage.hold_after(0.0), rest + settle - EPS, rest + settle + EPS)
	assert_eq(ctl.stage.hold_after(100.0), 100.0, "never shorter than the base hold")
	ctl.tick(rest * 0.5)
	assert_true(ctl.is_waiting(), "the next turn waits while the choreography plays")
	_free()


func test_the_hud_names_the_playing_action_and_the_next_actor() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	var head: Dictionary = ctl.hud.timeline.slots[0]
	assert_eq(str(head["caption"]), tr("HUD_TL_NEXT"), "the head is who acts next while Rhen's attack plays")
	assert_true(ctl.hud.help_text().contains(ctl.menus.display_name(ctl.engine.find(&"rhen"))), "help names Rhen")
	choreo.finish()
	head = ctl.hud.timeline.slots[0]
	assert_eq(str(head["caption"]), ctl.hud.timeline.caption, "the turn caption is back")
	_free()


func test_frozen_holds_the_hand_off_and_ignores_finish() -> void:
	_to_turn_of(&"rhen")
	choreo.force_play = true
	choreo.frozen = true
	ctl.act(&"attack", [_foe()])
	assert_true(choreo.playing(), "force_play plays at pacing 0")
	assert_eq(ctl.stage.hold_after(0.0), INF)
	choreo.finish()
	assert_true(choreo.playing(), "a freeze-frame never ends")
	_free()


func test_a_ko_waits_for_its_collapse_beat() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var foe := ctl.engine.find(_foe())
	foe.hp = 1
	ctl.act(&"attack", [foe.id])
	assert_eq(foe.hp, 0, "the engine already felled it")
	var plan := choreo.current()
	assert_eq(plan["kos"], [foe.id] as Array[StringName])
	assert_true(choreo.holds_ko(foe.id), "the stage holds the KO look back")
	choreo.advance(float(plan["ko_at"]) + EPS)
	var f := ctl.stage.stand_in(foe.id)
	if BattleClips.has_clip(f, BattleClips.KO):
		# A model with a KO clip (a creature, M2-CRE-03) plays its own KO at the collapse beat, on its mark.
		assert_false(choreo.holds_ko(foe.id), "released on the collapse beat")
		assert_eq(StringName(str(BattleClips.creature_of(f).get("current_clip"))), BattleClips.KO, "it plays its KO")
		choreo.advance(float(plan["total"]))
		_assert_home(foe.id)
		_free()
		return
	var mid := f.transform
	assert_true(mid.origin.y < _home_pos(foe.id).y, "it starts to drop")
	choreo.advance(float(plan["total"]))
	assert_false(choreo.holds_ko(foe.id), "released")
	var fallen := ctl.stage.stand_in(foe.id).transform
	assert_true(fallen.basis.y.dot(Vector3.UP) < 0.9, "a stand-in with no KO clip lies tipped over")
	choreo.on_ko_state(foe.id, false)
	_assert_home(foe.id)
	_free()


func test_finish_lands_what_is_left() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	var ran := [false]
	choreo.after_sequence(func() -> void: ran[0] = true)
	assert_false(ran[0], "waits for the sequence")
	choreo.finish()
	assert_true(ran[0], "after_sequence runs at the end")
	assert_eq(contacts, 1, "the contact landed on finish")
	_assert_home(&"rhen")
	var now := [false]
	choreo.after_sequence(func() -> void: now[0] = true)
	assert_true(now[0], "runs at once when nothing plays")
	_free()


func test_seek_holds_a_freeze_frame() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	var plan := choreo.current()
	choreo.seek(float(plan["contact"]))
	assert_eq(contacts, 1, "the contact beat fired")
	var at := _pos(&"rhen")
	choreo.seek(float(plan["contact"]))
	_assert_eq_v(at, _pos(&"rhen"), "the same time gives the same pose")
	_free()


func test_speed_scales_the_remaining_time_and_clamps() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	var at1 := choreo.remaining_sec()
	choreo.set_speed(2.0)
	assert_between(choreo.remaining_sec(), at1 * 0.5 - EPS, at1 * 0.5 + EPS)
	var speeds := BattleChoreo.load_data()["speeds"] as Dictionary
	choreo.set_speed(100.0)
	assert_eq(choreo.speed, float(speeds["max"]))
	choreo.set_speed(0.0)
	assert_eq(choreo.speed, float(speeds["min"]))
	_free()


func test_reduced_motion_shortens_the_run() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var foe := _foe()
	choreo.reduced_motion = true
	ctl.act(&"attack", [foe])
	var plan := choreo.current()
	var full := (plan["from"] as Vector3).distance_to(_home_pos(foe)) - float(choreo.style("melee")["stop_short_m"])
	var ran := (plan["from"] as Vector3).distance_to(plan["to"] as Vector3)
	var k := float((BattleChoreo.load_data()["reduced_motion"] as Dictionary)["travel_scale"])
	assert_between(ran, full * k - 0.01, full * k + 0.01)
	_free()


func test_hit_vfx_land_on_the_contact_beat() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	var before := vfx.played.size()
	ctl.act(&"attack", [_foe()])
	assert_eq(vfx.played.size(), before, "no spark before the blow")
	choreo.finish()
	assert_true(vfx.played.size() > before, "the spark lands with the blow")
	_free()


func test_a_swapped_in_fighter_walks_onto_its_mark() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	assert_true(ctl.swap_members(&"asha", &"toma"))
	assert_true(choreo.is_entering(&"toma"), "Toma walks in")
	var home := _home_pos(&"toma")
	assert_true(_pos(&"toma").distance_to(home) > EPS, "from behind the mark")
	choreo.advance(float((BattleChoreo.load_data()["enter"] as Dictionary)["sec"]) + EPS)
	assert_false(choreo.is_entering(&"toma"))
	_assert_home(&"toma")
	_free()


func test_a_new_action_finishes_the_last_sequence() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [_foe()])
	ctl.tick(ctl.stage.hold_after(0.0) + 1.0)  # the controller moves on without the frames
	var r := ctl.engine.run_enemy_turn() if not ctl.engine.is_party_turn() else null
	if r != null:
		assert_eq(choreo.played.size(), 2, "the next action started its own sequence")
	_assert_home(&"rhen")
	_free()


# --- outro (M2-BPR-05) ------------------------------------------------------------------


func test_the_party_holds_a_victory_pose_before_the_result() -> void:
	_to_turn_of(&"rhen")
	for e in ctl.engine.enemies:
		e.hp = 1 if e.id == _foe() else 0
	ctl.pacing_scale = 1.0
	var outro := choreo.outro
	outro.live = false
	ctl.act(&"attack", [_foe()])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(outro.playing, &"", "the pose waits for the last blow")
	assert_true(ctl.stage.outro_hold(0.0) > choreo.remaining_sec(), "the result waits for the blow and the pose")
	choreo.finish()
	assert_eq(outro.playing, BattleOutro.VICTORY)
	var cfg := outro.cfg(BattleOutro.VICTORY)
	outro.advance(float(cfg["delay_sec"]) + float(cfg["sec"]) * 0.25)
	assert_true(_pos(&"rhen").y > _home_pos(&"rhen").y + EPS, "Rhen hops")
	var hold := ctl.stage.outro_hold(0.0)
	assert_between(hold, outro.remaining_sec(), outro.remaining_sec() + 1.0)
	outro.advance(outro.duration(BattleOutro.VICTORY))
	assert_eq(outro.playing, &"")
	_assert_home(&"rhen")
	assert_eq(ctl.stage.outro_hold(0.6), 0.6, "nothing left to wait for")
	_free()


func test_an_escape_walks_the_party_off() -> void:
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	choreo.outro.live = false
	ctl.engine.rng.seed = 1
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 40:
		guard += 1
		if ctl.engine.is_party_turn():
			ctl.try_escape()
		choreo.finish()
		ctl.tick(100.0)
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_ESCAPED, "the party got away")
	assert_eq(choreo.outro.playing, BattleOutro.ESCAPE)
	choreo.outro.advance(choreo.outro.duration(BattleOutro.ESCAPE))
	var f := ctl.stage.stand_in(&"rhen")
	assert_true(f.transform.origin.distance_to(choreo._home_of(&"rhen").origin) > 1.0, "Rhen walked off")
	_free()


func test_no_outro_when_instant() -> void:
	_to_turn_of(&"rhen")
	for e in ctl.engine.enemies:
		e.hp = 1 if e.id == _foe() else 0
	ctl.act(&"attack", [_foe()])
	assert_eq(choreo.outro.playing, &"")
	assert_eq(ctl.stage.outro_hold(0.0), 0.0)
	_free()


# --- clip contract --------------------------------------------------------------------------


func test_a_model_with_the_clip_plays_it_and_idles_after() -> void:
	var f := Node3D.new()
	var player := AnimationPlayer.new()
	var lib := AnimationLibrary.new()
	for clip in [BattleClips.IDLE, BattleClips.ATTACK]:
		var a := Animation.new()
		a.length = 0.5
		lib.add_animation(clip, a)
	player.add_animation_library(&"", lib)
	f.add_child(player)
	ctl.add_child(f)
	assert_true(BattleClips.has_clip(f, BattleClips.ATTACK))
	assert_false(BattleClips.has_clip(f, BattleClips.CAST))
	assert_true(BattleClips.play(f, BattleClips.ATTACK, 1.5))
	assert_eq(str(player.current_animation), str(BattleClips.ATTACK))
	assert_eq(player.speed_scale, 1.5)
	assert_eq(str(player.get_queue()), str([BattleClips.IDLE]), "idle after the one-shot")
	assert_false(BattleClips.play(f, BattleClips.CAST), "no such clip: the caller moves it procedurally")
	assert_false(BattleClips.play(null, BattleClips.ATTACK))
	f.queue_free()
	_free()


func test_a_creature_actor_strikes_with_its_own_clip_on_its_own_contact_frame() -> void:
	var f := _FakeStandIn.new()
	var cr := _FakeCreature.new()
	var player := AnimationPlayer.new()
	var lib := AnimationLibrary.new()
	for clip in [BattleClips.IDLE, BattleClips.ATTACK, BattleClips.HIT, BattleClips.KO]:
		var a := Animation.new()
		a.length = 1.5
		lib.add_animation(clip, a)
	player.add_animation_library(&"", lib)
	cr.add_child(player)
	f.add_child(cr)
	f.fake = cr
	ctl.add_child(f)
	assert_eq(BattleClips.creature_of(f), cr)
	assert_eq(BattleClips.action_clip(f, &"pinch", &"physical"), BattleClips.ATTACK)
	assert_eq(BattleClips.action_clip(f, &"brine_spit", &"magical"), &"", "no cast clip: the style's fallback")
	assert_eq(BattleClips.contact_sec(f, BattleClips.ATTACK), _FakeCreature.CONTACT)
	assert_true(BattleClips.play_action(f, &"pinch", &"physical", BattleClips.ATTACK))
	assert_eq(cr.actions, [&"pinch"] as Array[StringName], "the creature plays its own action clip")
	assert_eq(BattleClips.contact_sec(ctl.stage.stand_in(&"rhen"), BattleClips.ATTACK), -1.0, "a primitive can't say")
	var plan := choreo.plan_for(_result(&"attack", [_hit(_foe(), 10)]))
	var strike_end := float(plan["strike_end"])
	var late := float(plan["approach_end"]) + 1.2
	choreo._move_contact(plan, late)
	assert_eq(float(plan["contact"]), late, "the blow lands on the clip's frame")
	assert_between(float(plan["strike_end"]), late - EPS, late + EPS, "later beats move with it")
	assert_true(float(plan["total"]) > float(plan["return_end"]) - EPS and float(plan["strike_end"]) > strike_end)
	f.queue_free()
	_free()


func test_a_hero_strike_lands_on_its_clips_contact_marker() -> void:
	var f := Node3D.new()
	var player := AnimationPlayer.new()
	var lib := AnimationLibrary.new()
	for clip in [BattleClips.IDLE, BattleClips.ATTACK]:
		var a := Animation.new()
		a.length = 0.6
		lib.add_animation(clip, a)
	lib.get_animation(BattleClips.ATTACK).add_marker(BattleClips.CONTACT_MARKER, 0.33)
	player.add_animation_library(&"", lib)
	f.add_child(player)
	ctl.add_child(f)
	assert_between(BattleClips.contact_sec(f, BattleClips.ATTACK), 0.33 - EPS, 0.33 + EPS, "the clip's own marker")
	assert_eq(BattleClips.contact_sec(f, BattleClips.IDLE), -1.0, "no marker, no say")
	f.queue_free()
	_free()


func test_a_primitive_stand_in_has_no_clips() -> void:
	var f := ctl.stage.stand_in(&"rhen")
	assert_eq(BattleClips.player_of(f), null)
	for clip in BattleClips.ALL:
		assert_false(BattleClips.play(f, clip))
	_free()


# --- helpers --------------------------------------------------------------------------------


func _foe() -> StringName:
	for e in ctl.engine.enemies:
		if e.is_alive():
			return e.id
	return &""


func _hit(tid: StringName, amount: int) -> Dictionary:
	return {"target_id": tid, "hit": true, "crit": false, "amount": amount, "statuses_added": []}


func _result(skill: StringName, hits: Array[Dictionary]) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = &"rhen"
	r.skill_id = skill
	r.hits = hits
	return r


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	contacts = 0


func _pos(cid: StringName) -> Vector3:
	return ctl.stage.stand_in(cid).global_position


func _home_pos(cid: StringName) -> Vector3:
	return ctl.stage.get_global_transform() * choreo._home_of(cid).origin


func _assert_home(cid: StringName) -> void:
	var f := ctl.stage.stand_in(cid)
	var home := choreo._home_of(cid)
	assert_true(f.transform.is_equal_approx(home), "%s stands on its mark" % cid)


func _assert_eq_v(a: Vector3, b: Vector3, msg: String) -> void:
	assert_true(a.distance_to(b) < EPS, "%s (%s vs %s)" % [msg, a, b])


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


class _FakeCreature:
	extends Node3D
	const CONTACT := 0.9
	var actions: Array[StringName] = []

	func clip_for(_skill: StringName, kind: StringName) -> StringName:
		return BattleClips.ATTACK if kind == &"physical" else BattleClips.CAST

	func play_action(skill: StringName, _kind: StringName) -> bool:
		actions.append(skill)
		return true

	func play_clip(_clip: StringName) -> bool:
		return true

	func contact_time(_clip: StringName) -> float:
		return CONTACT


class _FakeStandIn:
	extends Node3D
	var fake: Node

	func creature() -> Node:
		return fake
