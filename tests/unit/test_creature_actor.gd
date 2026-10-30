extends TestCase
## M2-CRE-03: the battle creatures. CreatureActor plays the clip an action names and idles again, holds the KO,
## freezes under Petrify; an enemies.json `model` reaches the stand-in spec as its actor `scene`; every
## creatures.json row names a scene whose clips exist; and in a live sandbox battle the reef crab plays its
## action and hit clips from its choreography (BattleChoreo through BattleClips; phases and parts: BattleActorMotion).

const CRAB := "res://game/creatures/reef_crab/reef_crab_battle.tscn"
const SLUG := "res://game/creatures/oil_slug/oil_slug_battle.tscn"
const BELL := "res://game/creatures/drownbell/drownbell_battle.tscn"
const GNAW := "res://game/creatures/hullgnaw/hullgnaw_battle.tscn"
const MATRON := "res://game/creatures/cinder_matron/cinder_matron_battle.tscn"
const REACH := "res://game/creatures/undertows_reach/undertows_reach_battle.tscn"
const WRAITH := "res://game/creatures/spar_wraith/spar_wraith_battle.tscn"
const DROWNER := "res://game/creatures/mangrove_drowner/mangrove_drowner_battle.tscn"
const ENGINE := "res://game/creatures/lamp_engine/lamp_engine_battle.tscn"
const RAM := "res://game/creatures/avalanche_ram/avalanche_ram_battle.tscn"
## The Avalanche Ram's checks: how far before a clip's end its pose is read, how far a planted hoof may have moved,
## and how low its head lies at the end of the KO.
const RAM_END_SEC := 0.001
const RAM_FOOT_TOL_M := 0.01
const RAM_KO_HEAD_MAX_Y := 1.0
const WAKEFIN := "res://game/creatures/wakefin/wakefin_battle.tscn"
## The Wakefin's checks (y 0 is the water): the blade's upper bone stands above this in the idle, the dive takes it
## under at its deepest second, and at the end of the KO every bone lies within this band round the surface.
const FIN_IDLE_MIN_Y := 1.3
const FIN_DIVE_SEC := 1.13
const FIN_KO_BAND_M := 0.6
const FIN_BELLY_UP := -0.8
## M3-CRE-627, the Act II regulars. The tannin archer: its head rises this far over its idle for the long jet, and at
## the end of its KO it has rolled at least this far sideways off its root and lies with its head this low.
const ARCHER := "res://game/creatures/tannin_archer/tannin_archer_battle.tscn"
const ARCHER_AIM_RISE_M := 0.1
const ARCHER_KO_OFF_X := 0.2
const ARCHER_KO_MAX_Y := 0.25
## The gallery ray flies: its stand-in hover; the cast settles it at least this far down onto the pool, the KO lands its
## root on the floor (within this much of the hover), and in the idle its outer wing joints rise this far
## between strokes (over the body's bob).
const RAY := "res://game/creatures/gallery_ray/gallery_ray_battle.tscn"
const RAY_HOVER := 0.95
const RAY_POOL_DROP_M := 0.8
const RAY_FLOOR_TOL_M := 0.05
const RAY_STROKE_M := 0.03
## The rime urchin: on the hit every spine sector clenches at least this far (radians), on the cast every sector
## turns at least this far toward the target, and the KO settles the test at least this far onto its ice.
const URCHIN := "res://game/creatures/rime_urchin/rime_urchin_battle.tscn"
const URCHIN_CLENCH_RAD := 0.15
const URCHIN_AIM_RAD := 0.3
const URCHIN_SETTLE_M := 0.03
## The conduit crawler: its body sinks at least this far between its folded legs in the KO, and stays this high.
const CRAWLER := "res://game/creatures/conduit_crawler/conduit_crawler_battle.tscn"
const CRAWLER_KO_DROP_M := 0.12
const CRAWLER_KO_BODY_MIN_Y := 0.05
const LYNX := "res://game/creatures/ridge_lynx/ridge_lynx_battle.tscn"
## The ridge lynx's checks: its crouch (the telegraph, at CROUCH_SEC) lowers the body at least this far with the paws
## planted, the leap lifts the root above LEAP_MIN_M at its apex, and at the end of the KO it lies with its head low.
const LYNX_CROUCH_SEC := 0.38
const LYNX_CROUCH_MIN_M := 0.1
const LYNX_APEX_SEC := 0.6
const LYNX_LEAP_MIN_M := 0.5
const LYNX_KO_HEAD_MAX_Y := 0.4
const MOTH := "res://game/creatures/cord_moth/cord_moth_battle.tscn"
## The cord moth hovers this high (its stand-in lifts it; its model is at the 1.35x battle scale) and its KO comes down
## by exactly that, within the band.
const MOTH_HOVER_M := 1.12
const MOTH_BAND_M := 0.02
const SKATE := "res://game/creatures/glass_skate/glass_skate_battle.tscn"
## The glass skate lies flat (every bone under FLAT_MAX_M at rest and after the KO) and erupts above ERUPT_MIN_M.
const SKATE_FLAT_MAX_M := 0.2
const SKATE_ERUPT_SEC := 0.36
const SKATE_ERUPT_MIN_M := 0.4
## M3-CRE-637, the flat-engine (Ch14 boss part): its stilling lifts every paddle at least FLAT_LIFT_MIN_DEG at
## FLAT_LIFT_SEC and presses them flat (under FLAT_PRESSED_MAX_DEG) at its contact; a hit kicks one paddle up at
## least FLAT_KICK_MIN_DEG at its 0.1 s peak; its break (M4-CRB-009: the `broken` phase's clip, no longer the KO)
## tips each drum half apart by FLAT_SPLIT_DEG (min, max).
const FLAT := "res://game/creatures/flat_engine/flat_engine_battle.tscn"
const FLAT_CONTACT_SEC := 0.8
const FLAT_LIFT_SEC := 0.6
const FLAT_LIFT_MIN_DEG := 8.0
const FLAT_PRESSED_MAX_DEG := 1.0
const FLAT_HIT_PEAK_SEC := 0.1
const FLAT_KICK_MIN_DEG := 15.0
const FLAT_SPLIT_DEG := [12.0, 16.0]
## The Act II variants (M3-CRE-628) and their bases: the same rig and clips.
const VARIANTS := {
	"root_crab": "reef_crab",
	"fen_leech": "sail_leech",
	"scree_crawler": "slag_tortoise",
	"rim_crawler": "tide_crawler",
}
const RING := {"radius_factor": 1.4, "inner_soft_m": 0.25, "notches": 6}
const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261024
## Stepping a forced choreography (the sandbox test): seconds per step, and a cap on the steps.
const CHOREO_STEP_SEC := 0.05
const CHOREO_MAX_STEPS := 200

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
			for clip: Variant in ((phase as Dictionary).get("clips", {}) as Dictionary).values():
				needed.append(str(clip))
		for clip: Variant in row["hit_variants"]:
			needed.append(str(clip))
		needed.append(str((row["idle_variety"] as Dictionary).get("clip", "")))
		for clip in needed:
			if clip == "":
				continue  # a phase may keep the creature's idle (no `idle` of its own)
			assert_true(a.has_clip(StringName(clip)), "%s has the clip %s" % [id, clip])
		for clip: Variant in row["loop"]:
			var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert_eq(player.get_animation(StringName(str(clip))).loop_mode, Animation.LOOP_LINEAR, "%s loops" % clip)
	before_each()


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
	before_each()


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
	before_each()


func test_petrify_freezes_and_refuses_clips() -> void:
	var a := _actor(CRAB)
	a.set_frozen(true)
	assert_false(a.play_action(&"pinch", &"physical"))
	a.set_frozen(false)
	assert_true(a.play_action(&"pinch", &"physical"))
	before_each()


func test_a_creature_without_phases_or_parts_ignores_them() -> void:
	var a := _actor(CRAB)
	assert_false(a.enter_phase(&"flood"))
	assert_false(a.set_part_broken(&"toll", true))
	assert_false(a.is_part_broken(&"toll"))
	before_each()


func test_the_model_field_reaches_the_stand_in_spec() -> void:
	var spec := BattleStage.stand_in_spec(&"reef_crab#2")
	assert_eq(str(spec.get("scene", "")), str(CreatureModels.models()["reef_crab"]))
	assert_eq(str(spec["scene"]), CRAB)
	assert_true(is_equal_approx(float(spec["yaw_deg"]), 90.0), "turned to face the party")
	assert_true(
		is_equal_approx(float(spec["height"]), 0.62), "battle_sandbox.json's height still drives the VFX anchors"
	)
	var hero := str(BattleStage.stand_in_spec(&"rhen").get("scene", ""))  # a hero actor scene since M2-UI-07
	assert_false(CreatureModels.models().values().has(hero), "heroes are not creatures")
	assert_eq(CreatureModels.stand_in_overrides("no_such_enemy"), {})
	before_each()


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
	before_each()


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
	# The action and hit clips are BattleChoreo's (M2-BPR-01, through BattleClips; big7 merge): play every action's
	# choreography (forced on at pacing 0) and watch the crab's clip at each step.
	var choreo := ctl.stage.choreo
	choreo.force_play = true
	choreo.live = false
	var seen: Dictionary = {}
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
		var steps := 0
		while choreo.playing() and steps < CHOREO_MAX_STEPS:
			steps += 1
			choreo.advance(CHOREO_STEP_SEC)
			seen[crab.current_clip] = true
		ctl.tick(CHOREO_STEP_SEC * CHOREO_MAX_STEPS)
	assert_true(seen.has(&"hit"), "the crab flinched when struck")
	assert_true(seen.has(&"attack") or seen.has(&"cast"), "the crab played its own action")
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	ctl = null
	Game.state = _saved_state
	before_each()


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
	before_each()


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
	assert_true(a.play_action(&"flood_surge", &"magical"), "Floodtide has its own clip (clip_by_skill)")
	assert_eq(a.current_clip, &"flood_surge")
	player.advance(player.get_animation(&"flood_surge").length + 0.05)
	assert_eq(a.current_clip, &"idle_flood", "the flood idle after an action")
	# M3-CRB-013: the slam plays from the flood stance (the phase's clips map)
	assert_true(a.play_action(&"hood_slam", &"physical"))
	assert_eq(a.current_clip, &"attack_flood")
	assert_eq(a.contact_time(&"attack"), 0.8, "the flood slam lands when the slam does")
	assert_false(a.enter_phase(&"flood"), "already flooded")
	var b := _actor(BELL)
	b.enter_phase(&"flood")
	b.settle()
	assert_true(is_equal_approx((b.get_child(0) as Node3D).position.y, -0.35), "settle() ends the sink at once")
	assert_eq(b.current_clip, &"idle_flood")
	before_each()


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
	var w := _actor(WRAITH)
	var shroud := w.find_child("Shroud", true, false) as Node3D
	var sheath := w.find_child("Sheath", true, false) as Node3D
	assert_true(shroud.visible and not sheath.visible, "shrouded in the rigging; the sheath starts hidden")
	assert_true(w.enter_phase(&"hauled_down"))
	assert_true(shroud.visible, "M3-CRB-013: the shroud is seen hauled down with it in the drop")
	assert_false(sheath.visible, "the sea comes up its lines after the drop")
	w.settle()
	assert_false(shroud.visible, "hide_after: the shroud is gone once the drop has played")
	assert_true(sheath.visible, "show_after: sheathed once the drop has played")
	assert_eq(w.phase_clip(&"attack"), &"attack_deck", "it strikes from the deck")
	w.set_ko(true, 0.5)
	assert_eq(w.current_clip, &"ko_deck", "M3-CRB-013: the phase's clips map sends the KO too: it falls from the deck")
	before_each()


func test_a_phase_plays_its_own_strikes() -> void:
	var a := _actor(REACH)
	assert_true(a.play_clip(&"attack"))
	assert_eq(a.current_clip, &"attack", "the Grip strikes with the base clip")
	a.enter_phase(&"dark", true)
	assert_true(a.play_clip(&"attack"))
	assert_eq(a.current_clip, &"attack_dark", "the Dark strikes from the lifted hand")
	assert_eq(a.phase_clip(&"hit"), &"hit_dark")
	assert_eq(a.phase_clip(&"ko"), &"ko", "a clip the phase doesn't map plays as itself")
	assert_true(is_equal_approx(a.contact_time(&"attack"), 1.2), "contact follows the phase's clip")
	a.enter_phase(&"breach", true)
	assert_true(a.play_action(&"", &"magical"))
	assert_eq(a.current_clip, &"cast_breach")
	assert_eq(a.phase_clip(&"hit"), &"hit", "the Breach has no hit of its own")
	before_each()


func test_the_mangrove_drowner_uproots_and_strikes_risen() -> void:
	var d := _actor(DROWNER)
	var stump := d.find_child("Stump", true, false) as Node3D
	assert_true(stump != null and stump.visible, "it starts rooted under its trunk stump")
	assert_true(d.enter_phase(&"uprooted"))
	assert_eq(d.current_clip, &"phase_change")
	assert_true(stump.visible, "the stump is seen splintering first")
	d.settle()
	assert_false(stump.visible, "hide_after: the stump is gone once it has torn free")
	assert_eq(d.current_clip, &"idle_risen", "it idles risen on its legs")
	assert_true(d.play_clip(&"attack"))
	assert_eq(d.current_clip, &"attack_risen", "it drags from the risen pose")
	assert_true(is_equal_approx(d.contact_time(&"attack"), 0.7), "the drag lands at 0.7 s")
	assert_true(d.play_hit())
	assert_eq(d.current_clip, &"hit_risen", "the risen hit wins over the variants")
	before_each()


func test_the_lamp_engine_opens_its_rings_and_strikes_open() -> void:
	var e := _actor(ENGINE)
	var player := e.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var skel := e.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var petal := skel.find_bone("petal1_0")
	assert_true(petal >= 0, "the middle ring's petals are bones")
	assert_true(e.enter_phase(&"opened"))
	assert_eq(e.current_clip, &"phase_change", "the rings fold back first")
	e.settle()
	assert_eq(e.current_clip, &"idle_opened", "it idles open, the core showing")
	assert_eq(player.get_animation(&"idle_opened").loop_mode, Animation.LOOP_LINEAR, "the open idle loops")
	player.advance(0.5)  # past the cross-fade from the phase clip (this first step only starts the queued clip)
	player.advance(0.0)  # and this one applies its pose
	var rest := skel.get_bone_rest(petal).basis.get_rotation_quaternion()
	var fold := rad_to_deg(rest.angle_to(skel.get_bone_pose_rotation(petal)))
	assert_between(fold, 60.0, 76.0, "the middle ring stands folded back like a petal (%.1f deg)" % fold)
	assert_true(e.play_clip(&"attack"))
	assert_eq(e.current_clip, &"attack_opened", "it trims from the open pose")
	assert_true(is_equal_approx(e.contact_time(&"attack"), 0.6), "the trim lands at 0.6 s")
	assert_true(e.play_hit())
	assert_eq(e.current_clip, &"hit_opened", "the open hit wins over the variants")
	before_each()


func test_the_avalanche_ram_charges_bellows_and_lies_down() -> void:
	var r := _actor(RAM)
	assert_eq(r.current_clip, &"idle")
	assert_false(r.enter_phase(&"uprooted"), "not one of its phases (its own is torn_fleece)")
	assert_true(r.play_action(&"", &"physical"))
	assert_eq(r.current_clip, &"attack", "the charge")
	assert_true(is_equal_approx(r.contact_time(&"attack"), 0.75), "the charge lands at 0.75 s")
	assert_true(r.play_action(&"", &"magical"))
	assert_eq(r.current_clip, &"cast", "the bellow")
	var skel := r.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var bones: Array[String] = ["root", "body", "head", "jaw"]
	for k in 5:
		bones.append_array(["spine%d" % k, "neck%d" % k])
	for k in 6:
		bones.append_array(["lock%d_a" % k, "lock%d_b" % k])
	for leg in ["fl", "fr", "bl", "br"]:
		bones.append_array(["%s_upper" % leg, "%s_lower" % leg, "%s_foot" % leg])
	# M4-CRB-005: the herd-cord's swing, the shoulder plate that tears, and the boss anchors
	bones.append_array(["cord", "plate", "vfx_wound", "vfx_core", "vfx_phase"])
	for b in bones:
		assert_true(skel.find_bone(b) >= 0, "the rig has %s" % b)
	assert_eq(
		skel.get_bone_count(),
		bones.size(),
		"spine 5, neck 5, head, jaw, four legs of 3, six lock chains of 2, the cord, the plate and three anchors"
	)
	var player := r.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	for clip: StringName in [&"idle", &"attack", &"cast", &"hit", &"hit_b"]:
		player.play(clip)
		player.seek(player.get_animation(clip).length - RAM_END_SEC, true)
		for leg in ["fl", "fr", "bl", "br"]:
			var b := skel.find_bone("%s_foot" % leg)
			var moved := skel.get_bone_global_pose(b).origin.distance_to(skel.get_bone_global_rest(b).origin)
			assert_true(moved < RAM_FOOT_TOL_M, "%s ends with the %s hoof where it stood" % [clip, leg])
	player.play(&"ko")
	player.seek(player.get_animation(&"ko").length - RAM_END_SEC, true)
	var head := skel.global_transform * skel.get_bone_global_pose(skel.find_bone("head"))
	assert_true(head.origin.y < RAM_KO_HEAD_MAX_Y, "it lies down and lays its head on the ground")
	for b in skel.get_bone_count():
		var y := (skel.global_transform * skel.get_bone_global_pose(b)).origin.y
		assert_true(y > -RAM_FOOT_TOL_M, "%s stays above the ground in the KO" % skel.get_bone_name(b))
	before_each()


func test_the_wakefin_circles_cuts_dives_and_floats_belly_up() -> void:
	var w := _actor(WAKEFIN)
	assert_eq(w.current_clip, &"idle")
	assert_false(w.enter_phase(&"uprooted"), "not one of its phases (its own is close_circle)")
	assert_true(w.play_action(&"", &"physical"))
	assert_eq(w.current_clip, &"attack", "the cut")
	assert_true(is_equal_approx(w.contact_time(&"attack"), 0.8), "the blade sweeps the deck at 0.8 s")
	assert_true(w.play_action(&"", &"magical"))
	assert_eq(w.current_clip, &"cast", "the dive")
	var skel := w.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var bones: Array[String] = ["root", "head", "bill", "fin_0", "fin_1", "fin_2", "pec_l", "pec_r"]
	bones.append_array(["tail_upper", "tail_lower"])
	# M4-CRB-004: the breach root (its travel), the blade's torn tip, and the three VFX anchors
	bones.append_array(["breach", "blade_tip", "vfx_wound", "vfx_core", "vfx_phase"])
	for k in 10:
		bones.append("spine_%d" % k)
	for b in bones:
		assert_true(skel.find_bone(b) >= 0, "the rig has %s" % b)
	assert_eq(
		skel.get_bone_count(),
		bones.size(),
		"breach, spine 10, the bill, a blade of 3 and its tip, pectorals, tail lobes, three anchors"
	)
	var player := w.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var fin := skel.find_bone("fin_2")
	player.play(&"idle")
	player.seek(0.0, true)
	assert_true(_bone_y(skel, fin) > FIN_IDLE_MIN_Y, "the blade stands high out of the water as it circles")
	player.play(&"cast")
	player.seek(FIN_DIVE_SEC, true)
	assert_true(_bone_y(skel, fin) < 0.0, "the dive takes the blade under")
	player.play(&"ko")
	player.seek(player.get_animation(&"ko").length - RAM_END_SEC, true)
	var root := skel.global_transform.basis * skel.get_bone_global_pose(skel.find_bone("root")).basis
	assert_true(root.y.normalized().y < FIN_BELLY_UP, "it ends rolled belly-up")
	for b in skel.get_bone_count():
		var y := _bone_y(skel, b)
		assert_true(
			absf(y) < FIN_KO_BAND_M, "%s lies at the surface after the KO (y %.2f)" % [skel.get_bone_name(b), y]
		)
	before_each()


func _bone_y(skel: Skeleton3D, bone: int) -> float:
	return (skel.global_transform * skel.get_bone_global_pose(bone)).origin.y


func _skeleton(a: Node) -> Skeleton3D:
	return a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D


func _player(a: Node) -> AnimationPlayer:
	return a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer


func _seek(player: AnimationPlayer, clip: StringName, sec: float) -> void:
	player.play(clip)
	player.seek(sec, true)


func test_the_ridge_lynx_crouches_pounces_and_lies_down() -> void:
	var l := _actor(LYNX)
	assert_eq(l.current_clip, &"idle")
	assert_false(l.enter_phase(&"uprooted"), "no phases: its sheet asks for none")
	assert_true(l.play_action(&"", &"physical"))
	assert_eq(l.current_clip, &"attack", "the pounce")
	assert_true(is_equal_approx(l.contact_time(&"attack"), 0.7), "it comes down on the back row at 0.7 s")
	assert_true(l.play_action(&"", &"magical"))
	assert_eq(l.current_clip, &"cast", "the yowl")
	var skel := _skeleton(l)
	var bones: Array[String] = ["root", "body", "neck0", "neck1", "head", "jaw", "ear_l", "ear_r"]
	for k in 4:
		bones.append("spine%d" % k)
	for k in 3:
		bones.append("tail%d" % k)
	for leg in ["fl", "fr", "bl", "br"]:
		bones.append_array(["%s_upper" % leg, "%s_lower" % leg, "%s_paw" % leg])
	for b in bones:
		assert_true(skel.find_bone(b) >= 0, "the rig has %s" % b)
	assert_eq(skel.get_bone_count(), bones.size(), "spine 4, neck 2, head, jaw, ears, four legs of 3, tail 3")
	var player := _player(l)
	var paws: Array[int] = []
	for leg in ["fl", "fr", "bl", "br"]:
		paws.append(skel.find_bone("%s_paw" % leg))
	for clip: StringName in [&"idle", &"attack", &"cast", &"hit", &"hit_b"]:
		_seek(player, clip, player.get_animation(clip).length - RAM_END_SEC)
		for p in paws:
			var moved := skel.get_bone_global_pose(p).origin.distance_to(skel.get_bone_global_rest(p).origin)
			assert_true(moved < RAM_FOOT_TOL_M, "%s ends with %s where it stood" % [clip, skel.get_bone_name(p)])
	var body := skel.find_bone("body")
	_seek(player, &"attack", LYNX_CROUCH_SEC)
	assert_true(_bone_y(skel, body) < skel.get_bone_global_rest(body).origin.y - LYNX_CROUCH_MIN_M, "the crouch")
	for p in paws:
		var moved := skel.get_bone_global_pose(p).origin.distance_to(skel.get_bone_global_rest(p).origin)
		assert_true(moved < RAM_FOOT_TOL_M, "%s stays planted in the crouch" % skel.get_bone_name(p))
	_seek(player, &"attack", LYNX_APEX_SEC)
	assert_true(_bone_y(skel, skel.find_bone("root")) > LYNX_LEAP_MIN_M, "the leap clears the front row")
	_seek(player, &"ko", player.get_animation(&"ko").length - RAM_END_SEC)
	assert_true(_bone_y(skel, skel.find_bone("head")) < LYNX_KO_HEAD_MAX_Y, "it lies down with its head low")
	for b in skel.get_bone_count():
		assert_true(_bone_y(skel, b) > -RAM_FOOT_TOL_M, "%s stays above the snow in the KO" % skel.get_bone_name(b))
	before_each()


func test_the_cord_moth_hovers_opens_its_knots_and_drifts_down() -> void:
	var m := _actor(MOTH)
	assert_true(is_equal_approx(float(CreatureActor.row_for(&"cord_moth")["stand_in"]["hover"]), MOTH_HOVER_M))
	assert_true(m.play_action(&"", &"physical"))
	assert_true(is_equal_approx(m.contact_time(&"attack"), 0.5), "the wing-strike lands at 0.5 s")
	assert_true(m.play_action(&"", &"magical"))
	assert_eq(m.current_clip, &"cast", "the unravel")
	var skel := _skeleton(m)
	var bones: Array[String] = ["root", "body", "antenna_l", "antenna_r"]
	for tag in ["l", "r"]:
		for wing in ["fore", "hind"]:
			bones.append_array(["%s_%s0" % [wing, tag], "%s_%s1" % [wing, tag]])
	for b in bones:
		assert_true(skel.find_bone(b) >= 0, "the rig has %s" % b)
	assert_eq(skel.get_bone_count(), bones.size(), "body, four wing bones a side, antennae")
	var player := _player(m)
	_seek(player, &"ko", player.get_animation(&"ko").length - RAM_END_SEC)
	var root_y := _bone_y(skel, skel.find_bone("root"))
	assert_true(absf(root_y + MOTH_HOVER_M) < MOTH_BAND_M, "it comes down by its hover height (%.3f)" % root_y)
	for b in skel.get_bone_count():
		var y := _bone_y(skel, b) + MOTH_HOVER_M
		assert_true(
			y > -MOTH_BAND_M and y < MOTH_BAND_M * 10.0, "%s lies on the floor (y %.3f)" % [skel.get_bone_name(b), y]
		)
	before_each()


func test_the_glass_skate_lies_flat_erupts_and_flattens() -> void:
	var s := _actor(SKATE)
	assert_true(s.play_action(&"", &"physical"))
	assert_true(is_equal_approx(s.contact_time(&"attack"), 0.5), "the slap at 0.5 s")
	var skel := _skeleton(s)
	var bones: Array[String] = ["root", "body", "eye_l", "eye_r"]
	for k in 3:
		bones.append_array(["disc_l%d" % k, "disc_r%d" % k])
	for k in 4:
		bones.append("tail%d" % k)
	for b in bones:
		assert_true(skel.find_bone(b) >= 0, "the rig has %s" % b)
	assert_eq(skel.get_bone_count(), bones.size(), "disc chains of 3 a side, a tail of 4, the eyes")
	var player := _player(s)
	_seek(player, &"attack", SKATE_ERUPT_SEC)
	assert_true(_bone_y(skel, skel.find_bone("root")) > SKATE_ERUPT_MIN_M, "it erupts from the sand")
	_seek(player, &"ko", player.get_animation(&"ko").length - RAM_END_SEC)
	for b in skel.get_bone_count():
		var y := _bone_y(skel, b)
		assert_true(y > -RAM_FOOT_TOL_M and y < SKATE_FLAT_MAX_M, "%s lies flat (y %.3f)" % [skel.get_bone_name(b), y])
	before_each()


func test_the_act2_variants_keep_their_bases_rigs_and_clips() -> void:
	for id: String in VARIANTS:
		var v := _actor("res://game/creatures/%s/%s_battle.tscn" % [id, id])
		var b := _actor("res://game/creatures/%s/%s_battle.tscn" % [VARIANTS[id], VARIANTS[id]])
		var vs := _skeleton(v)
		var bs := _skeleton(b)
		assert_eq(vs.get_bone_count(), bs.get_bone_count(), "%s has its base's rig" % id)
		for k in bs.get_bone_count():
			assert_true(vs.find_bone(bs.get_bone_name(k)) >= 0, "%s has %s" % [id, bs.get_bone_name(k)])
		var vp := _player(v)
		var bp := _player(b)
		for clip in bp.get_animation_list():
			assert_true(vp.has_animation(clip), "%s has %s" % [id, clip])
			assert_true(
				is_equal_approx(vp.get_animation(clip).length, bp.get_animation(clip).length),
				"%s's %s is its base's" % [id, clip]
			)
	var crab := _skeleton(_actor("res://game/creatures/reef_crab/reef_crab_battle.tscn"))
	var root_crab := _skeleton(_actor("res://game/creatures/root_crab/root_crab_battle.tscn"))
	var knee := crab.find_bone("leg_l0_b")
	assert_true(
		root_crab.get_bone_global_rest(knee).origin.y > crab.get_bone_global_rest(knee).origin.y,
		"the root crab climbs on longer legs (a higher knee)"
	)
	var leech := _skeleton(_actor("res://game/creatures/sail_leech/sail_leech_battle.tscn"))
	var fen := _skeleton(_actor("res://game/creatures/fen_leech/fen_leech_battle.tscn"))
	var tail := leech.find_bone("tail2")
	assert_true(
		fen.get_bone_global_rest(tail).origin.z < leech.get_bone_global_rest(tail).origin.z, "the fen leech is longer"
	)
	before_each()


func test_hits_rotate_their_variants_and_a_phase_keeps_its_own() -> void:
	var a := _actor(CRAB)
	var played: Array[StringName] = []
	for i in 4:
		assert_true(a.play_hit())
		played.append(a.current_clip)
	assert_eq(played, [&"hit", &"hit_b", &"hit", &"hit_b"] as Array[StringName], "hits alternate their recoil")
	var r := _actor(REACH)
	r.enter_phase(&"dark", true)
	assert_true(r.play_hit())
	assert_eq(r.current_clip, &"hit_dark", "a phase's own hit wins over the variants")
	before_each()


func test_an_idling_creature_fidgets_now_and_then() -> void:
	var a := _actor(CRAB)
	var cfg: Dictionary = CreatureActor.row_for(&"reef_crab")["idle_variety"] as Dictionary
	var most := float((cfg["every_sec"] as Array)[1])
	var seen := false
	var t := 0.0
	while t < most + 0.5 and not seen:
		a._process(0.1)
		t += 0.1
		seen = a.current_clip == &"idle_b"
	assert_true(seen, "it fidgets within its longest interval")
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.advance(player.get_animation(&"idle_b").length + 0.05)
	assert_eq(a.current_clip, &"idle", "and idles again")
	var b := _actor(CRAB)
	b.set_ko(true, 0.0)
	for i in int((most + 0.5) / 0.1):
		b._process(0.1)
	assert_eq(b.current_clip, &"ko", "a fallen creature never fidgets")
	var c := _actor(CRAB)
	player = c.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.pause()
	for i in int((most + 0.5) / 0.1):
		c._process(0.1)
	assert_eq(c.current_clip, &"idle", "a held (paused) pose, as in a portrait, never fidgets")
	before_each()


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
	before_each()


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
	before_each()


func _actor(path: String) -> CreatureActor:
	var a := (load(path) as PackedScene).instantiate() as CreatureActor
	_add(a)
	return a


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


## M3-CRE-617: a hit cuts into its clip at hit_snap.preroll_sec with no blend, so a hit-stop that holds the player on
## the contact frame (M3-BPR-401) shows a struck pose, not the idle the hit came from.
func test_a_hit_snaps_onto_its_struck_pose() -> void:
	var a := _actor(CRAB)
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var skel := a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var snap := CreatureActor.data()["defaults"]["hit_snap"] as Dictionary
	var idle_pose: Array[Quaternion] = []
	for i in skel.get_bone_count():
		idle_pose.append(skel.get_bone_pose_rotation(i))
	assert_true(a.play_hit())
	player.speed_scale = 0.0  # the hit-stop's hold
	player.advance(0.0)
	assert_between(player.current_animation_position, float(snap["preroll_sec"]) - 0.001, 1.0, "pre-rolled")
	var moved := 0.0
	for i in skel.get_bone_count():
		moved += idle_pose[i].angle_to(skel.get_bone_pose_rotation(i))
	assert_true(moved > 0.05, "the held frame is a struck pose (%.3f rad off idle)" % moved)
	assert_true(a.is_hit_clip(&"hit_b") and not a.is_hit_clip(&"attack"), "hit variants snap, strikes do not")
	assert_true(a.play_action(&"pinch", &"physical"))
	assert_between(player.current_animation_position, 0.0, 0.001, "a strike still starts at its beginning")
	before_each()


## M3-CRE-627: an Act II regular strikes and casts on its clips, syncs both to its contact seconds and has its
## sheet's rig (exactly these bones).
func _act2_regular(path: String, contacts: Array[float], bones: Array[String]) -> CreatureActor:
	var a := _actor(path)
	assert_eq(a.current_clip, &"idle")
	assert_false(a.enter_phase(&"uprooted"), "%s: a regular has no phases" % path)
	for k in 2:
		var clip: StringName = [&"attack", &"cast"][k]
		assert_true(a.play_action(&"", [&"physical", &"magical"][k]))
		assert_eq(a.current_clip, clip)
		assert_true(
			is_equal_approx(a.contact_time(clip), contacts[k]), "%s: %s lands at %.2f s" % [path, clip, contacts[k]]
		)
	var skel := a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	for b in bones:
		assert_true(skel.find_bone(b) >= 0, "%s: the rig has %s" % [path, b])
	assert_eq(skel.get_bone_count(), bones.size(), "%s: the sheet's rig" % path)
	return a


## Poses the actor's model at `sec` into `clip` (clamped to just before its end) and returns its skeleton.
func _pose(a: CreatureActor, clip: StringName, sec: float) -> Skeleton3D:
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.play(clip)
	player.seek(minf(sec, player.get_animation(clip).length - RAM_END_SEC), true)
	return a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D


func _bone_at(skel: Skeleton3D, bone: String) -> Vector3:
	return (skel.global_transform * skel.get_bone_global_pose(skel.find_bone(bone))).origin


func test_the_tannin_archer_spits_from_its_root_and_rolls_off_it() -> void:
	var bones: Array[String] = ["root", "tail", "jaw", "pec_l", "pec_r"]
	for k in 5:
		bones.append("spine_%d" % k)
	var a := _act2_regular(ARCHER, [0.55, 0.9], bones)
	var skel := _pose(a, &"idle", 0.0)
	var jaw_rest := _bone_at(skel, "jaw")
	var root_rest := _bone_at(skel, "root")
	skel = _pose(a, &"cast", 0.9)
	assert_true(_bone_at(skel, "jaw").y > jaw_rest.y + ARCHER_AIM_RISE_M, "the long jet: it raises its head to aim")
	skel = _pose(a, &"ko", INF)
	assert_true(_bone_at(skel, "root").is_equal_approx(root_rest), "the mangrove root it lay on stays put")
	assert_true(_bone_at(skel, "spine_0").x > ARCHER_KO_OFF_X, "it rolls off the root to the side")
	assert_true(_bone_at(skel, "jaw").y < ARCHER_KO_MAX_Y, "and lies at the water")
	before_each()


func test_the_gallery_ray_glides_settles_into_its_pool_and_falls_flat() -> void:
	var bones: Array[String] = ["root", "body"]
	for side in ["l", "r"]:
		for k in 3:
			bones.append("wing_%s%d" % [side, k])
	for k in 4:
		bones.append("tail_%d" % k)
	var a := _act2_regular(RAY, [0.6, 0.9], bones)
	var spec := CreatureActor.row_for(&"gallery_ray")["stand_in"] as Dictionary
	assert_true(is_equal_approx(float(spec["hover"]), RAY_HOVER), "it flies below the battle camera")
	var skel := _pose(a, &"idle", 1.5)
	var up := _bone_at(skel, "wing_l2").y
	skel = _pose(a, &"idle", 0.0)
	assert_true(up - _bone_at(skel, "wing_l2").y > RAY_STROKE_M, "the wings undulate as it glides")
	skel = _pose(a, &"cast", 0.9)
	assert_true(_bone_at(skel, "root").y < -RAY_POOL_DROP_M, "the cast settles it into the pool")
	skel = _pose(a, &"ko", INF)
	assert_true(absf(_bone_at(skel, "root").y + RAY_HOVER) < RAY_FLOOR_TOL_M, "the KO lays it flat on the floor")
	before_each()


func test_the_rime_urchin_clenches_aims_its_spines_and_settles_on_its_mound() -> void:
	var bones: Array[String] = ["root", "body"]
	for k in 8:
		bones.append("sector_%d" % k)
	var a := _act2_regular(URCHIN, [0.5, 0.8], bones)
	var skel := _pose(a, &"idle", 0.0)
	var body_rest := _bone_at(skel, "body")
	var plinth := _bone_at(skel, "root")
	for clip_at: Array in [[&"hit", 0.1, URCHIN_CLENCH_RAD], [&"cast", 0.8, URCHIN_AIM_RAD]]:
		skel = _pose(a, clip_at[0], clip_at[1])
		for k in 8:
			var b := skel.find_bone("sector_%d" % k)
			var turned := skel.get_bone_rest(b).basis.get_rotation_quaternion().angle_to(skel.get_bone_pose_rotation(b))
			assert_true(turned > float(clip_at[2]), "%s: sector %d's spines move (%.2f rad)" % [clip_at[0], k, turned])
	skel = _pose(a, &"ko", INF)
	assert_true(_bone_at(skel, "body").y < body_rest.y - URCHIN_SETTLE_M, "the KO settles the test")
	assert_true(_bone_at(skel, "root").is_equal_approx(plinth), "on the ice plinth, which stays")
	before_each()


func test_the_conduit_crawler_scrubs_jabs_and_folds_its_legs() -> void:
	var bones: Array[String] = ["root", "body"]
	var legs: Array[String] = []
	for side in ["l", "r"]:
		for k in 3:
			legs.append_array(["leg_%s%d_a" % [side, k], "leg_%s%d_b" % [side, k]])
		bones.append_array(["arm_%s_a" % side, "arm_%s_b" % side])
	bones.append_array(legs)
	var a := _act2_regular(CRAWLER, [0.45, 1.0], bones)
	var skel := _pose(a, &"idle", 0.0)
	var body_rest := _bone_at(skel, "body").y
	for clip: StringName in [&"attack", &"cast", &"hit", &"hit_b"]:
		skel = _pose(a, clip, INF)
		for leg in legs:
			var b := skel.find_bone(leg)
			var moved := skel.get_bone_global_pose(b).origin.distance_to(skel.get_bone_global_rest(b).origin)
			assert_true(moved < RAM_FOOT_TOL_M, "%s ends with %s back where it stood" % [clip, leg])
	skel = _pose(a, &"ko", INF)
	var body := _bone_at(skel, "body").y
	assert_true(body < body_rest - CRAWLER_KO_DROP_M, "its legs fold and it sinks")
	assert_true(body > CRAWLER_KO_BODY_MIN_Y, "onto its belly plate, not through the floor")
	for leg in legs:
		assert_true(_bone_at(skel, leg).y > -RAM_FOOT_TOL_M, "%s stays above the floor" % leg)
	before_each()


func test_the_flat_engine_presses_the_water_flat_and_splits_on_its_break() -> void:
	var bones: Array[String] = ["root", "drum", "half_a", "half_b", "chimney"]
	for k in 8:
		bones.append("paddle%d" % k)
	bones.append_array(["vfx_wound", "vfx_core", "vfx_phase"])
	var e := _act2_regular(FLAT, [FLAT_CONTACT_SEC, FLAT_CONTACT_SEC], bones)
	var whole := e.find_child("Engine", true, false) as Node3D
	var broken := e.find_child("EngineBroken", true, false) as Node3D
	assert_true(whole != null and whole.visible, "it stands whole: the lit window, the fanned paddles")
	assert_true(broken != null and not broken.visible, "the broken variant waits for its break part")
	assert_false(e.set_part_broken(&"any_charge", true), "no charge skill names its part yet")
	var skel := _pose(e, &"cast", FLAT_LIFT_SEC)
	for k in 8:
		assert_true(_turn_deg(skel, "paddle%d" % k) > FLAT_LIFT_MIN_DEG, "the stilling lifts paddle %d" % k)
	skel = _pose(e, &"cast", FLAT_CONTACT_SEC)
	for k in 8:
		assert_true(_turn_deg(skel, "paddle%d" % k) < FLAT_PRESSED_MAX_DEG, "and presses paddle %d flat" % k)
	skel = _pose(e, &"hit", FLAT_HIT_PEAK_SEC)
	assert_true(_turn_deg(skel, "paddle3") > FLAT_KICK_MIN_DEG, "a hit kicks one paddle up at its peak")
	skel = _pose(e, &"break", INF)
	for h in ["half_a", "half_b"]:
		assert_between(_turn_deg(skel, h), FLAT_SPLIT_DEG[0], FLAT_SPLIT_DEG[1], "the break splits the drum: %s" % h)
	for b in bones:
		assert_true(_bone_at(skel, b).y > -RAM_FOOT_TOL_M, "%s stays on the water in the break" % b)
	before_each()


## How far a bone is turned from its rest (degrees).
func _turn_deg(skel: Skeleton3D, bone: String) -> float:
	var b := skel.find_bone(bone)
	return rad_to_deg(skel.get_bone_rest(b).basis.get_rotation_quaternion().angle_to(skel.get_bone_pose_rotation(b)))


## GPU QA row 40: the Oil Slug carries its eaten lamplight (an omni light); a KO fades it with the surfaces, and a
## revive lights it again.
func test_a_creatures_own_light_fades_with_its_ko() -> void:
	var a := _actor(SLUG)
	var lights := a.find_children("*", "Light3D", true, false)
	assert_eq(lights.size(), 1, "the slug's LampGlow")
	if lights.is_empty():
		before_each()
		return
	var glow := lights[0] as Light3D
	var full := glow.light_energy
	assert_true(full > 0.0, "lit while it stands")
	a.call(&"_set_transparency", 0.75)
	assert_true(is_equal_approx(glow.light_energy, full * 0.25), "fades with the surfaces")
	a.call(&"_set_transparency", 0.0)
	assert_true(is_equal_approx(glow.light_energy, full), "back at full")
	before_each()
