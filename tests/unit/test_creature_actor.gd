extends TestCase
## M2-CRE-03: the battle creatures. CreatureActor plays the clip an action names and idles again, holds the KO,
## freezes under Petrify; an enemies.json `model` reaches the stand-in spec as its actor `scene`; every
## creatures.json row names a scene whose clips exist; and in a live sandbox battle the reef crab plays its
## clips from the engine's signals (BattleActorMotion).

const CRAB := "res://game/creatures/reef_crab/reef_crab_battle.tscn"
const BELL := "res://game/creatures/drownbell/drownbell_battle.tscn"
const GNAW := "res://game/creatures/hullgnaw/hullgnaw_battle.tscn"
const MATRON := "res://game/creatures/cinder_matron/cinder_matron_battle.tscn"
const RING := {"radius_factor": 1.4, "inner_soft_m": 0.25, "notches": 6}
const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261024

var made: Array[Node] = []
var ctl: BattleController
var _saved_state: GameStateData


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_every_creature_row_names_a_scene_with_its_clips() -> void:
	var rows: Dictionary = CreatureActor.data().get("creatures", {})
	assert_false(rows.is_empty())
	for id: Variant in rows:
		var row := CreatureActor.row_for(StringName(str(id)))
		var a := _actor(str(row["scene"]))
		assert_eq(a.creature_id, StringName(str(id)), "%s: the scene names its row" % id)
		var needed: Array[String] = [str(row["idle"]), str(row["hit"]), str(row["ko"])]
		for clip: Variant in (
			(row["clip_by_kind"] as Dictionary).values() + (row["clip_by_skill"] as Dictionary).values()
		):
			needed.append(str(clip))
		for phase: Variant in (row["phases"] as Dictionary).values():
			needed.append(str((phase as Dictionary).get("clip", "")))
			needed.append(str((phase as Dictionary).get("idle", "")))
		for clip in needed:
			if clip == "":
				continue  # a phase may keep the creature's idle (no `idle` of its own)
			assert_true(a.has_clip(StringName(clip)), "%s has the clip %s" % [id, clip])
		for clip: Variant in row["loop"]:
			var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert_eq(player.get_animation(StringName(str(clip))).loop_mode, Animation.LOOP_LINEAR, "%s loops" % clip)


func test_an_action_plays_its_clip_and_the_actor_idles_again() -> void:
	var a := _actor(CRAB)
	assert_eq(a.current_clip, &"idle", "idles from the start")
	assert_eq(a.clip_for(&"pinch", &"physical"), &"attack", "by kind")
	assert_eq(a.clip_for(&"brine_spit", &"physical"), &"cast", "clip_by_skill wins")
	assert_eq(a.clip_for(&"anything", &"heal"), &"cast")
	assert_eq(a.clip_for(&"anything", &"no_such_kind"), &"")
	assert_false(a.play_action(&"anything", &"no_such_kind"), "no clip, nothing plays")
	assert_true(a.play_action(&"pinch", &"physical"))
	assert_eq(a.current_clip, &"attack")
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.advance(player.get_animation(&"attack").length + 0.05)
	assert_eq(a.current_clip, &"idle", "back to idle when the clip ends")
	assert_true(a.play_hit())
	assert_eq(a.current_clip, &"hit")
	assert_true(is_equal_approx(a.contact_time(&"attack"), 0.5), "the pinch lands at 0.5 s")
	assert_eq(a.contact_time(&"hit"), -1.0)
	assert_true(a.clip_length(&"attack") > a.contact_time(&"attack"))
	assert_eq(a.clip_length(&"no_such_clip"), 0.0)


func test_ko_holds_its_pose_and_a_revive_returns_to_idle() -> void:
	var a := _actor(CRAB)
	a.set_ko(true, 0.35)
	assert_true(a.is_ko())
	assert_eq(a.current_clip, &"ko")
	assert_false(a.play_hit(), "a fallen creature does not flinch")
	a.set_ko(true, 0.35)
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.advance(player.get_animation(&"ko").length + 0.5)
	assert_eq(a.current_clip, &"ko", "holds the KO; never idles again on its own")
	a.set_ko(false, 0.35)
	assert_eq(a.current_clip, &"idle")
	for g in a.find_children("*", "GeometryInstance3D", true, false):
		assert_eq((g as GeometryInstance3D).transparency, 0.0, "opaque again")


func test_petrify_freezes_and_refuses_clips() -> void:
	var a := _actor(CRAB)
	a.set_frozen(true)
	assert_false(a.play_action(&"pinch", &"physical"))
	a.set_frozen(false)
	assert_true(a.play_action(&"pinch", &"physical"))


func test_a_creature_without_phases_or_parts_ignores_them() -> void:
	var a := _actor(CRAB)
	assert_false(a.enter_phase(&"flood"))
	assert_false(a.set_part_broken(&"toll", true))
	assert_false(a.is_part_broken(&"toll"))


func test_the_model_field_reaches_the_stand_in_spec() -> void:
	var spec := BattleStage.stand_in_spec(&"reef_crab#2")
	assert_eq(str(spec.get("scene", "")), str(CreatureModels.models()["reef_crab"]))
	assert_eq(str(spec["scene"]), CRAB)
	assert_true(is_equal_approx(float(spec["yaw_deg"]), 90.0), "turned to face the party")
	assert_true(
		is_equal_approx(float(spec["height"]), 0.62), "battle_sandbox.json's height still drives the VFX anchors"
	)
	assert_false(BattleStage.stand_in_spec(&"rhen").has("scene"), "heroes are not creatures")
	assert_eq(CreatureModels.stand_in_overrides("no_such_enemy"), {})


func test_the_stand_in_hands_ko_and_stone_to_the_creature() -> void:
	var f := FighterStandIn.new()
	f.setup(&"reef_crab#1", BattleStage.stand_in_spec(&"reef_crab#1"), RING)
	_add(f)
	assert_true(f.creature() != null, "the model, not the box")
	assert_true(f.play_action(&"pinch", &"physical"))
	f.set_ko(true, 0.25, 0.35)
	assert_true(f.creature().is_ko())
	assert_true(is_equal_approx(f.actor().position.y, 0.0), "it does not sink: the KO clip settles it")
	f.set_ko(false, 0.25, 0.35)
	f.set_stone(true, Color.GRAY, 1.0)
	assert_false(f.play_hit(), "frozen")
	f.set_stone(false, Color.GRAY, 1.0)
	assert_true(f.play_hit())
	var plain := FighterStandIn.new()
	plain.setup(&"lantern_eel#1", {"height": 2.1, "radius": 0.24}, RING)
	_add(plain)
	assert_false(plain.play_action(&"lure_glow", &"magical"), "a primitive plays nothing")
	assert_false(plain.enter_phase(&"flood"))
	assert_false(plain.set_part_broken(&"toll", true))


func test_a_sandbox_battle_drives_the_crabs_clips() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	_add(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED, null)
	var e := ctl.engine
	var crab_id := &""
	for c in e.enemies:
		if String(c.id).begins_with("reef_crab"):
			crab_id = c.id
	assert_ne(crab_id, &"", "the sandbox encounter has a crab")
	var crab := ctl.stage.stand_in(crab_id).creature()
	assert_true(crab != null, "the crab is its model on the stage")
	var seen: Dictionary = {}
	e.action_resolved.connect(func(_r: ActionResult) -> void: seen[crab.current_clip] = true)
	var n := 0
	while e.outcome == &"" and n < 60 and not (seen.has(&"hit") and (seen.has(&"attack") or seen.has(&"cast"))):
		n += 1
		if e.is_party_turn():
			var target: Array[StringName] = [
				crab_id if e.find(crab_id).is_alive() else e.living_foes_of(e.current)[0].id
			]
			ctl.act(&"attack", target)
		else:
			e.run_enemy_turn()
	assert_true(seen.has(&"hit"), "the crab flinched when struck")
	assert_true(seen.has(&"attack") or seen.has(&"cast"), "the crab played its own action")
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	ctl = null
	Game.state = _saved_state


func test_the_drownbells_rim_breaks_and_mends() -> void:
	var a := _actor(BELL)
	var rim := a.find_child("Rim", true, false) as Node3D
	var broken := a.find_child("RimBroken", true, false) as Node3D
	assert_true(rim != null and broken != null, "the GLB carries both rims")
	assert_true(rim.visible and not broken.visible, "whole at the start")
	assert_true(a.set_part_broken(&"toll", true))
	assert_true(a.is_part_broken(&"toll"))
	assert_true(broken.visible and not rim.visible, "charge_broken shows the broken lip")
	a.set_part_broken(&"toll", false)
	assert_true(rim.visible and not broken.visible, "a new toll mends it")
	assert_false(a.set_part_broken(&"hood_slam", true), "no part for that skill")


func test_the_flood_phase_sinks_the_bell_and_idles_on_its_flood_clip() -> void:
	var a := _actor(BELL)
	assert_true(a.enter_phase(&"flood", true))
	assert_eq(a.phase(), &"flood")
	assert_eq(a.current_clip, &"phase_change")
	var model := a.get_child(0) as Node3D
	assert_true(is_equal_approx(model.position.y, -0.35), "it settles into the water")
	assert_true(is_equal_approx(model.rotation_degrees.z, -6.0), "tilted seaward")
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.advance(player.get_animation(&"phase_change").length + 0.05)
	assert_eq(a.current_clip, &"idle_flood")
	assert_true(a.play_action(&"toll", &"physical"), "toll swings (clip_by_skill)")
	assert_eq(a.current_clip, &"cast")
	player.advance(player.get_animation(&"cast").length + 0.05)
	assert_eq(a.current_clip, &"idle_flood", "the flood idle after an action")
	assert_false(a.enter_phase(&"flood"), "already flooded")
	var b := _actor(BELL)
	b.enter_phase(&"flood")
	b.settle()
	assert_true(is_equal_approx((b.get_child(0) as Node3D).position.y, -0.35), "settle() ends the sink at once")
	assert_eq(b.current_clip, &"idle_flood")


func test_phase_nodes_hide_at_once_or_after_the_clip() -> void:
	var m := _actor(MATRON)
	var crust := m.find_child("Crust", true, false) as Node3D
	assert_true(crust != null and crust.visible, "the Matron starts crusted")
	assert_true(m.enter_phase(&"pour"))
	assert_false(crust.visible, "the pour hides the crust at once")
	var g := _actor(GNAW)
	var ribs := g.find_child("Ribs", true, false) as Node3D
	assert_true(ribs != null and ribs.visible, "the hullgnaw starts in its frames")
	assert_true(g.enter_phase(&"breaking"))
	assert_eq(g.current_clip, &"phase_break")
	assert_true(ribs.visible, "the frames are seen falling first")
	g.settle()
	assert_false(ribs.visible, "hide_after: gone once the clip has played (settle() jumps there)")
	var h := _actor(GNAW)
	h.enter_phase(&"breaking", true)
	assert_false((h.find_child("Ribs", true, false) as Node3D).visible, "an instant phase change hides them at once")


func test_a_drownbell_fight_breaks_the_rim_and_floods_the_bell() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	_add(ctl)
	var active: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var reserve: Array[StringName] = []
	ctl.start_battle(active, reserve, &"drownbell", SEED, null)
	var e := ctl.engine
	var bell := ctl.stage.stand_in(e.enemies[0].id).creature()
	assert_true(bell != null and bell.creature_id == &"drownbell", "the bell is its model")
	var log: Array[String] = []
	e.charge_broken.connect(
		func(_c: BattleCombatant, _s: StringName) -> void: log.append("broken:%s" % bell.is_part_broken(&"toll"))
	)
	e.phase_changed.connect(func(_c: BattleCombatant, p: StringName) -> void: log.append("phase:%s" % bell.phase()))
	var sim := BattleSim.new()
	var policy := sim.make_policy(&"smart")
	policy.reset()
	var n := 0
	while e.outcome == &"" and n < 400 and not log.has("phase:flood"):
		n += 1
		if e.is_party_turn():
			policy.take_turn(e)
		else:
			e.run_enemy_turn()
	assert_true(log.has("phase:flood"), "the bell flooded (%s)" % [log])
	assert_true(log.has("broken:true"), "the smart party broke the toll, and the rim with it (%s)" % [log])
	assert_false(log.has("broken:false"))
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	ctl = null
	Game.state = _saved_state


func test_a_portrait_shows_an_enemy_with_a_model_and_nothing_otherwise() -> void:
	var p := (load("res://game/creatures/creature_portrait.tscn") as PackedScene).instantiate() as CreaturePortrait
	_add(p)
	assert_true(p.show_enemy(&"reef_crab"))
	assert_true(p.has_creature() and p.actor.creature_id == &"reef_crab")
	assert_eq(p.enemy_id, &"reef_crab")
	var cam := p.get_node(^"Viewport/Camera") as Camera3D
	var box := CreatureFraming.bounds([p.actor])
	assert_true(cam.position.distance_to(box.get_center()) > box.size.length() * 0.5, "framed from outside")
	assert_true(p.show_enemy(&"drownbell"), "a second call replaces the first")
	assert_eq(p.actor.creature_id, &"drownbell")
	assert_eq(p.get_node(^"Viewport/Holder").get_child_count(), 1)
	assert_false(p.show_enemy(&"no_such_enemy"))
	assert_false(p.has_creature())


func _actor(path: String) -> CreatureActor:
	var a := (load(path) as PackedScene).instantiate() as CreatureActor
	_add(a)
	return a


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)
