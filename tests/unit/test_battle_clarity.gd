extends TestCase
## M3-BPR-409, the Pillar 4 clarity pass: the player always knows who acts next and whom an action hits, even under
## a cinematic or heavy VFX. The order (timeline) and the party panel stay on screen through a boss intro, the toll, a
## Vowbound's first call (C10) and a hero's blow at its contact; the target
## ring draws after ground VFX (render_priority from battle_sandbox.json ring).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027

var ctl: BattleController


func _start(encounter: StringName, party: Array[StringName]) -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var none: Array[StringName] = []
	ctl.start_battle(party, none, encounter, SEED)


func test_the_order_stays_on_screen_through_a_boss_intro() -> void:
	var party: Array[StringName] = [&"rhen"]
	_start(&"ch01_hullgnaw", party)
	var intro := BattleBossIntro.of(ctl.stage)
	intro.live = false
	intro.force_play = true
	intro.play()
	intro.advance(float(intro.cfg["camera_in_sec"]) + float(intro.row["hold_sec"]) * 0.5)
	assert_true(intro.playing(), "mid-intro")
	assert_true(ctl.hud.timeline.is_visible_in_tree(), "who acts next stays on screen")
	assert_true(ctl.hud.party.is_visible_in_tree(), "and the party panel")
	_free()


func test_the_order_stays_on_screen_through_every_special() -> void:
	# The toll (a boss special), a Vowbound's first call (C10, the longest cinematic) and a hero's action mid-sequence.
	_start_fixture(&"choreo_toll")
	ctl.pacing_scale = 1.0
	var bell := ctl.engine.enemies[0].id
	var r := ActionResult.new()
	r.actor_id = bell
	r.skill_id = &"toll"
	for c in ctl.engine.party_active:
		r.hits.append({"target_id": c.id, "hit": true, "crit": false, "amount": 10, "statuses_added": []})
	ctl.engine.action_resolved.emit(r)
	var plan := ctl.stage.choreo.current()
	ctl.stage.choreo.seek(float(plan["contact"]))
	_assert_order_on_screen("the toll at its contact")
	_free()
	_start_fixture(&"choreo_vowbound_rise")
	var flag := &"ch03_ilun_first_call_seen"
	var was: Variant = Game.get_flag(flag)
	Game.set_flag(flag, false)
	var guard := 0
	while ctl.current_actor_id() != &"asha" and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	ctl.pacing_scale = 1.0
	ctl.persist_progress = true
	ctl.fixture = null
	ctl.stage.choreo.summon.live = false
	assert_true(ctl.vow.call_vowbound(&"ilun"), "Asha calls Ilun")
	assert_true(ctl.stage.choreo.summon.playing(), "the cinematic plays")
	ctl.stage.choreo.summon.advance(ctl.stage.choreo.summon.total_sec() * 0.5)
	_assert_order_on_screen("mid C10")
	ctl.persist_progress = false
	Game.set_flag(flag, was)
	_free()
	var party: Array[StringName] = [&"rhen", &"asha"]
	_start(&"sandbox_reef", party)
	ctl.pacing_scale = 1.0
	ctl.stage.choreo.live = false
	ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	if ctl.stage.choreo.playing():
		ctl.stage.choreo.seek(float(ctl.stage.choreo.current()["contact"]))
	_assert_order_on_screen("a hero's blow at its contact")
	_free()


func _assert_order_on_screen(when: String) -> void:
	assert_true(ctl.hud.timeline.is_visible_in_tree(), "%s: who acts next stays on screen" % when)
	assert_true(ctl.hud.party.is_visible_in_tree(), "%s: and the party panel" % when)


func _start_fixture(id: StringName) -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_fixture(BattleFixture.load_fixture(id))
	ctl.stage.choreo.live = false


func test_the_target_ring_draws_over_ground_vfx() -> void:
	var party: Array[StringName] = [&"rhen", &"asha"]
	_start(&"sandbox_reef", party)
	var want := int((BattleStage.config()["ring"] as Dictionary)["render_priority"])
	assert_true(want > 0, "above the default transparent order")
	for c in ctl.engine.enemies + ctl.engine.party_active:
		var f := ctl.stage.stand_in(c.id)
		assert_eq(f._ring_mat.render_priority, want, "%s's ring" % c.id)
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
