extends TestCase
## M3-BPR-406: Ch8's set pieces (ADR 0100) play on the battle stage at full pacing: the three Fisher Stair waves and
## the Undertow's Reach run to an outcome through the controller and the choreography with no script error. Entries
## (the Climb, the Surge, the Kirru) have no fighter on stage and still take their turns; intercepts, counters and
## withdrawals sequence like any other action.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const ENCOUNTERS: Array[StringName] = [
	&"ch08_stair_hold_1", &"ch08_stair_hold_2", &"ch08_stair_hold_3", &"undertows_reach"
]
const SEED := 5
const MAX_STEPS := 3000
const STEP_SEC := 30.0

var ctl: BattleController


func test_every_ch8_set_piece_plays_to_an_outcome_on_stage() -> void:
	for enc in ENCOUNTERS:
		_make()
		var active: Array[StringName] = [&"rhen", &"asha", &"liss"]
		var reserve: Array[StringName] = [&"toma", &"ysolde", &"kerrid"]
		ctl.start_battle(active, reserve, enc, SEED)
		var choreo := ctl.stage.choreo
		choreo.live = false
		var policy := SimPolicyRoleAnswer.new()
		policy.config = {"guard_ward": true}
		var ward := ctl.engine.ward()
		assert_true(ward != null, "%s has its ward on the timeline" % enc)
		if ward != null:
			assert_eq(ctl.stage.stand_in(ward.id), null, "%s: an entry has no fighter on stage" % enc)
		var steps := 0
		while ctl.state != BattleController.STATE_RESULT and steps < MAX_STEPS:
			steps += 1
			if ctl.state == BattleController.STATE_COMMAND and ctl.engine.is_party_turn():
				var actor := ctl.engine.current.id
				policy.take_turn(ctl.engine)
				ctl.after_action(actor)
			if choreo.playing():
				choreo.finish()
			var intro := BattleBossIntro.of(ctl.stage)
			if intro != null and intro.playing():
				intro.skip()
			ctl.tick(STEP_SEC)
		assert_ne(ctl.engine.outcome, &"", "%s ends (%d steps)" % [enc, steps])
		assert_eq(ctl.state, BattleController.STATE_RESULT, "%s reaches its result panel" % enc)
		_free()


func _make() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 1.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func test_a_withdrawn_foe_leaves_the_stage_without_a_collapse() -> void:
	for mode: StringName in [&"instant", &"reduced", &"full"]:
		_make()
		var active: Array[StringName] = [&"rhen", &"asha"]
		var none: Array[StringName] = []
		ctl.start_battle(active, none, &"sandbox_reef", SEED)
		var choreo := ctl.stage.choreo
		choreo.live = false
		ctl.pacing_scale = 0.0 if mode == &"instant" else 1.0
		choreo.reduced_motion = mode == &"reduced"
		var foe := ctl.engine.enemies[0]
		var f := ctl.stage.stand_in(foe.id)
		var at := f.position
		foe.withdraw()
		ctl.stage.refresh_ko(ctl.engine)
		if mode == &"full":
			assert_true(f.visible, "full motion: it is still backing away")
			assert_eq(f.position, at, "from its mark")
		else:
			assert_false(f.visible, "%s: gone at once" % mode)
			assert_eq(f.position, at, "%s: no motion" % mode)
		ctl.stage.refresh_ko(ctl.engine)  # the stage re-applies after every action: once only
		assert_true(f.has_meta(BattleStage.WITHDRAWN_META))
		assert_true(foe.hp > 0, "not felled")
		_free()


func test_a_counter_is_answered_after_the_blow_by_the_hero_it_struck() -> void:
	_make()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var none: Array[StringName] = []
	ctl.start_battle(active, none, &"sandbox_reef", SEED)
	var foe := ctl.engine.enemies[0]
	var r := ActionResult.new()
	r.actor_id = foe.id
	r.skill_id = &"attack"
	r.hits = [
		{"target_id": &"rhen", "hit": true, "crit": false, "amount": 20, "statuses_added": []},
		{"target_id": foe.id, "hit": true, "crit": false, "amount": 15, "statuses_added": [], "counter_by": &"rhen"},
	]
	var data := ctl.stage.choreo.data
	var plan := BattleChoreoPlan.plan_for(data, ctl.engine, r)
	assert_eq(plan["targets"], [&"rhen"] as Array[StringName], "the riposte does not make the foe its own target")
	var answer: Dictionary = {}
	for re: Dictionary in plan["reactions"]:
		if re["target"] == foe.id:
			answer = re
	assert_false(answer.is_empty(), "the struck foe reacts to the riposte")
	assert_eq(answer["counter_by"], &"rhen")
	assert_true(float(answer["at"]) > float(plan["strike_end"]), "after its own blow")
	var answered := float(answer["at"]) + float((data["reaction"] as Dictionary)["damage"]["sec"])
	assert_true(float(plan["recover_end"]) >= answered - 0.001, "it stays where it struck until the answer lands")
	foe.hp = 0
	plan = BattleChoreoPlan.plan_for(data, ctl.engine, r)
	assert_true((plan["kos"] as Array).has(foe.id), "a riposte can fell it")
	assert_true(float(plan["ko_at"]) >= float(plan["return_end"]), "and it falls once it is home")
	_free()


func test_the_breach_closes_in_turn_by_turn() -> void:
	_make()
	var active: Array[StringName] = [&"rhen", &"asha", &"liss"]
	var reserve: Array[StringName] = [&"toma"]
	ctl.start_battle(active, reserve, &"undertows_reach", SEED)
	var cam := ctl.stage.choreo.camera
	var reach := ctl.engine.find(&"undertows_reach")
	if reach == null:
		reach = ctl.engine.enemies[0]
	assert_eq(cam.rest_fov(), cam.default_fov, "no telegraph: the default frame")
	reach.charge_skill = &"breach"
	var fovs: Array[float] = []
	for left in [4, 3, 2, 1]:
		reach.charge_left = left
		fovs.append(cam.rest_fov())
	for i in range(1, fovs.size()):
		assert_true(fovs[i] < fovs[i - 1], "it closes in a step each turn (%s)" % [fovs])
	var row := (cam.data["pressure"] as Dictionary)["breach"] as Dictionary
	assert_between(cam.default_fov - fovs[3], float(row["max_fov_deg"]) - 0.001, float(row["max_fov_deg"]) + 0.001)
	cam.rest()
	assert_true(cam.at_default(), "the resting frame is the narrowed one")
	ctl.stage.choreo.reduced_motion = true
	assert_eq(cam.rest_fov(), cam.default_fov, "reduced motion: no push-in")
	_free()


func test_the_stair_has_its_few_barks() -> void:
	# M3-C08-100: Toma's "Hold." on Hold the Stair; Asha says Virel's name as she calls her; most skills say nothing.
	_make()
	var active: Array[StringName] = [&"rhen", &"asha", &"liss"]
	var reserve: Array[StringName] = [&"toma"]
	ctl.start_battle(active, reserve, &"ch08_stair_hold_1", SEED)
	ctl.stage.choreo.live = false
	var barks := ctl.hud.get_node(NodePath(BattleBarks.NODE_NAME)) as BattleBarks
	assert_true(barks != null, "the barks listen")
	var heard: Array = []
	barks.barked.connect(func(who: StringName, key: String) -> void: heard.append([who, key]))
	var guard := 0
	while ctl.current_actor_id() != &"toma" and guard < 40:
		guard += 1
		if ctl.engine.is_party_turn():
			var a := ctl.engine.current.id
			ctl.engine.perform(&"stand_fast", [ctl.engine.current])
			ctl.after_action(a)
		ctl.tick(STEP_SEC)
	assert_eq(ctl.current_actor_id(), &"toma", "Toma's turn comes")
	var targets: Array[StringName] = []
	for t in ctl.default_targets(&"hold_the_stair"):
		targets.append(t.id)
	ctl.act(&"hold_the_stair", targets)
	assert_eq(heard.size(), 1, "one bark")
	if heard.size() == 1:
		assert_eq(heard[0][0], &"toma")
		assert_eq(heard[0][1], "BARK_SKILL_HOLD_THE_STAIR")
	# Asha's "Virel." on the call: test_battle_barks.gd (test_asha_names_virel_as_she_calls_him_and_ilun_comes_unnamed).
	_free()


func test_the_timeline_names_the_entries() -> void:
	# The Fisher Stair and the Surge read by name on the order, not as raw ids (the arena render showed "the_climb").
	_make()
	var active: Array[StringName] = [&"rhen", &"asha", &"liss"]
	var reserve: Array[StringName] = [&"toma"]
	ctl.start_battle(active, reserve, &"ch08_stair_hold_1", SEED)
	for c in ctl.engine.entries:
		var ident := ctl.hud.timeline._identity.get(c.id, {}) as Dictionary
		assert_eq(str(ident.get("label", "")), tr(c.name_key), "%s reads %s" % [c.id, tr(c.name_key)])
	assert_false(ctl.engine.entries.is_empty(), "the wave has its entries")
	_free()
