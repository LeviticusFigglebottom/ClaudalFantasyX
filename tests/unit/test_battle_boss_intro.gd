extends TestCase
## M3-BPR-02: boss intros. Every Act I boss encounter and the Drownbell has a row whose loc keys exist and whose
## shot frames its boss; the first turn waits for the intro (no enemy acts, the command menu stays hidden); it waits
## for the router's fade and the opening banner; confirm skips it; at instant pacing or with skip animations it never
## plays; reduced motion keeps the camera on the default and the card only fades; the camera is home at the end; a
## retry skips it unless the row says on_retry; the card stays clear of the timeline and the HUD panels.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const EPS := 0.001
const BOSSES := {
	&"ch01_hullgnaw": [&"rhen"],
	&"ch04_bottle_hermit": [&"rhen", &"asha", &"toma"],
	&"ch04_spar_wraith": [&"rhen", &"asha", &"toma"],
	&"ch05_cinder_matron": [&"rhen", &"asha", &"toma"],
	&"ch06_inquisitor": [&"rhen", &"asha", &"toma"],
	&"drownbell": [&"rhen", &"asha", &"toma"],
	&"undertows_reach": [&"rhen", &"asha", &"liss"],  # M3-BPR-406: Ch8's W18, low and looking up
}
const SEED := 20261024

var ctl: BattleController
var cfg: Dictionary


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	cfg = BattleChoreo.load_data()["boss_intro"] as Dictionary


func _start(encounter: StringName, pacing: float) -> BattleBossIntro:
	ctl.pacing_scale = pacing
	var party: Array[StringName] = []
	party.assign(BOSSES[encounter] as Array)
	var none: Array[StringName] = []
	ctl.start_battle(party, none, encounter, SEED)
	var intro := BattleBossIntro.of(ctl.stage)
	intro.live = false
	ctl.stage.choreo.live = false
	return intro


func _total(intro: BattleBossIntro) -> float:
	return intro.total_sec() / ctl.stage.choreo.speed


# --- data -----------------------------------------------------------------------------------


func test_every_boss_encounter_has_a_row_with_real_keys() -> void:
	var rows := cfg["rows"] as Dictionary
	var db := BattleDB.load_default()
	for enc: StringName in BOSSES:
		assert_true(rows.has(String(enc)), "%s has an intro row" % enc)
		var row := rows[String(enc)] as Dictionary
		assert_true(db.enemies.has(StringName(str(row["enemy"]))), "%s names an enemy" % enc)
		for key: String in ["title_key", "epithet_key"]:
			var k := str(row[key])
			assert_ne(TranslationServer.translate(k), k, "%s %s is translated" % [enc, key])
		assert_false(bool(row.get("on_retry", false)), "Fight again skips it by default")
	_free()


func test_each_row_frames_its_boss() -> void:
	for enc: StringName in BOSSES:
		var intro := _start(enc, 0.0)
		assert_false(intro.holding(), "%s: instant pacing plays nothing" % enc)
		intro.force_play = true
		intro.play()
		assert_true(intro.playing(), "%s plays when forced" % enc)
		# M3-BPR-423: the boss's hero shot, unless its row keeps the fitted shot (hero false)
		var want := str(intro.row["shot"]) if intro.row.get("hero", true) == false else BattleBossIntro.HERO_SHOT
		assert_eq(intro.shot_id, want, "%s: the shot frames the boss" % enc)
		assert_eq(String(intro.boss_id).get_slice("#", 0), str(intro.row["enemy"]))
		intro.skip()
	_free()


func test_the_card_stays_clear_of_the_timeline_and_the_panels() -> void:
	var card := HudLayout.rect_of(cfg["card"] as Dictionary)
	for sec: StringName in [&"timeline", &"party", &"help_line", &"target_info", &"opening_banner"]:
		assert_false(card.intersects(HudLayout.rect_of(HudLayout.section(sec))), "the card is clear of %s" % sec)
	_free()


# --- the first turn waits -----------------------------------------------------------------


func test_the_first_turn_waits_for_it() -> void:
	var intro := _start(&"ch01_hullgnaw", 1.0)
	assert_true(intro.playing(), "it plays at the first turn")
	assert_true(ctl.hud.holds_battle(), "it holds the battle")
	assert_eq(ctl.hud.commands.modulate.a, 0.0, "a party turn's menu stays hidden")
	var acted: Array[int] = [0]
	ctl.engine.action_resolved.connect(func(_r: ActionResult) -> void: acted[0] += 1)
	var first := ctl.engine.current
	ctl.tick(30.0)
	assert_eq(acted[0], 0, "nobody acts while it plays")
	assert_eq(ctl.engine.current, first, "the first turn is still the first")
	intro.advance(_total(intro) + EPS)
	assert_true(intro.done(), "it ends on its own")
	assert_false(ctl.hud.holds_battle(), "the battle goes on")
	assert_eq(ctl.hud.commands.modulate.a, 1.0, "the menu is back")
	assert_true(ctl.stage.choreo.camera.at_default(), "the camera is home")
	_free()


func test_it_tells_audio_when_it_starts() -> void:
	var heard: Array = []
	var on_event := func(ev: StringName, args: Array) -> void: heard.append([ev, args])
	EventBus.dialogue_event.connect(on_event)
	var intro := _start(&"ch01_hullgnaw", 1.0)
	EventBus.dialogue_event.disconnect(on_event)
	assert_true(intro.playing())
	var mine := heard.filter(func(h: Array) -> bool: return h[0] == BattleBossIntro.AUDIO_EVENT)
	assert_eq(mine.size(), 1, "announced once")
	assert_eq(StringName(str(mine[0][1][0])), &"ch01_hullgnaw")
	_free()


func test_it_waits_for_the_fade_and_the_banner() -> void:
	var intro := _start(&"ch01_hullgnaw", 0.0)
	ctl.pacing_scale = 1.0
	var covered: Array[bool] = [true]
	intro.screen_covered = func() -> bool: return covered[0]
	intro._on_first_turn(ctl.engine.current)
	assert_true(intro.holding() and not intro.playing(), "it waits while the screen is covered")
	assert_true(ctl.hud.holds_battle())
	intro.advance(0.5)
	assert_false(intro.playing())
	covered[0] = false
	intro.advance(0.0)
	assert_true(intro.playing(), "it plays once the screen is uncovered")
	intro.skip()
	var banner := ctl.hud.opening_banner()
	banner.show_opening(OpeningBanner.KIND_AMBUSH, false)
	ctl.remove_meta(BattleBossIntro.META_PLAYED)
	intro._on_first_turn(ctl.engine.current)
	assert_false(intro.playing(), "it waits for the opening banner")
	banner.hide_banner()
	intro.advance(0.0)
	assert_true(intro.playing(), "then plays")
	intro.skip()
	covered[0] = true
	ctl.remove_meta(BattleBossIntro.META_PLAYED)
	intro._on_first_turn(ctl.engine.current)
	intro.advance(float(cfg["reveal_wait_max_sec"]) + EPS)
	assert_true(intro.playing(), "it gives up waiting at its cap")
	_free()


func test_confirm_skips_it() -> void:
	var intro := _start(&"ch01_hullgnaw", 1.0)
	intro.advance(float(cfg["camera_in_sec"]))
	assert_true(intro.card() != null, "the card shows")
	var ev := InputEventAction.new()
	ev.action = &"ui_accept"
	ev.pressed = true
	intro._input(ev)
	assert_true(intro.done(), "confirm skips it")
	assert_true(intro.card() == null, "the card is gone")
	assert_true(ctl.stage.choreo.camera.at_default(), "the camera is home")
	assert_false(ctl.hud.holds_battle())
	_free()


# --- instant, reduced motion, retry ---------------------------------------------------------


func test_instant_pacing_and_skip_animations_play_none() -> void:
	var intro := _start(&"ch01_hullgnaw", 0.0)
	assert_false(intro.holding(), "instant pacing")
	assert_false(ctl.hud.holds_battle())
	assert_true(ctl.stage.choreo.camera.at_default())
	ctl.pacing_scale = 1.0
	ctl.remove_meta(BattleBossIntro.META_PLAYED)
	assert_true(intro.wants_play())
	ctl.stage.choreo.skip = true
	assert_false(intro.wants_play(), "skip animations")
	intro.force_play = true
	assert_true(intro.wants_play(), "a capture forces it")
	_free()


func test_reduced_motion_keeps_the_camera_and_the_card_only_fades() -> void:
	var intro := _start(&"ch01_hullgnaw", 0.0)
	ctl.stage.choreo.reduced_motion = true
	intro.force_play = true
	intro.play()
	var at := float(cfg["card_at_sec"]) + float(cfg["card_in_sec"]) * 0.5
	intro.advance(at)
	assert_true(ctl.stage.choreo.camera.at_default(), "reduced motion keeps the default")
	var a := intro.card().modulate.a
	assert_true(a > 0.0 and a < 1.0, "the card fades in")
	var rest := HudLayout.rect_of(cfg["card"] as Dictionary).position.y
	assert_between(intro.card().position.y, rest - EPS, rest + EPS, "no rise")
	_free()


func test_the_camera_frames_the_boss_and_comes_home() -> void:
	var intro := _start(&"ch01_hullgnaw", 0.0)
	intro.force_play = true
	intro.play()
	intro.advance(float(cfg["camera_in_sec"]) + float(intro.row["hold_sec"]) * 0.5)
	assert_false(ctl.stage.choreo.camera.at_default(), "the camera is on the boss")
	assert_between(intro.card().modulate.a, 1.0 - EPS, 1.0 + EPS, "the card is fully shown mid-hold")
	assert_eq(intro.title_text(), str(TranslationServer.translate(str(intro.row["title_key"]))))
	assert_eq(intro.epithet_text(), str(TranslationServer.translate(str(intro.row["epithet_key"]))))
	intro.advance(_total(intro))
	assert_true(intro.done())
	assert_true(ctl.stage.choreo.camera.at_default(), "home at the end")
	_free()


func test_the_shot_fits_the_boss_model_size() -> void:
	# M3-BPR-404: the distance follows the model's bounds, so a big boss is never framed too close.
	var intro := _start(&"ch01_hullgnaw", 0.0)
	intro.force_play = true
	intro.play()
	var pose := intro._pose
	assert_false(pose.is_empty(), "Hullgnaw has a fitted shot")
	var small := intro._fit(pose, AABB(Vector3(-0.5, 0.0, -0.5), Vector3.ONE), 1.0)
	var big := intro._fit(pose, AABB(Vector3(-1.5, 0.0, -1.5), Vector3.ONE * 3.0), 1.0)
	var d_small := (small["pos"] as Vector3).distance_to(small["look"] as Vector3)
	var d_big := (big["pos"] as Vector3).distance_to(big["look"] as Vector3)
	assert_true(d_big > d_small, "a bigger model is framed from farther away")
	var dir := ((pose["pos"] as Vector3) - (pose["look"] as Vector3)).normalized()
	var dir_big := ((big["pos"] as Vector3) - (big["look"] as Vector3)).normalized()
	assert_between(dir.dot(dir_big), 1.0 - EPS, 1.0 + EPS, "the fit keeps the shot's angle")
	assert_eq(big["fov"], pose["fov"], "and its field of view")
	var fc := cfg["fit"] as Dictionary
	var r := Vector3.ONE.length() * 1.5
	var half := deg_to_rad(float(pose["fov"])) * 0.5
	var need := r * float(fc["margin"]) / sin(half)
	assert_true(d_big >= minf(need, float(fc["max_m"])) - EPS, "the whole bounding sphere fits the frame")
	intro.skip()
	_free()


func test_a_row_can_widen_the_fit() -> void:
	var intro := _start(&"ch06_inquisitor", 0.0)
	intro.force_play = true
	intro.play()
	var box := AABB(Vector3(-2.0, 0.0, -2.0), Vector3.ONE * 4.0)
	var plain := intro._fit(intro._pose, box, 1.0)
	intro.row = intro.row.duplicate()
	intro.row["fit_margin"] = float((cfg["fit"] as Dictionary)["margin"]) * 1.5
	var wide := intro._fit(intro._pose, box, 1.0)
	var d_wide := (wide["pos"] as Vector3).distance_to(wide["look"] as Vector3)
	var d_plain := (plain["pos"] as Vector3).distance_to(plain["look"] as Vector3)
	assert_true(d_wide > d_plain, "fit_margin overrides the default margin")
	intro.skip()
	_free()


func test_every_boss_stands_clear_of_the_title_card() -> void:
	# M3-BPR-404: a small boss framed close sank behind the card (the Inquisitor's capsule).
	for enc: StringName in BOSSES:
		var intro := _start(enc, 0.0)
		intro.force_play = true
		intro.play()
		var f := ctl.stage.stand_in(intro.boss_id)
		var b := intro._bounds(f)
		# M3-BPR-423: a hero shot keeps the upper body clear (its feet may pass behind the card, as on a poster)
		var hero := intro.shot_id == BattleBossIntro.HERO_SHOT
		var frac := float((cfg["hero"] as Dictionary)["head_frac"]) if hero else 0.0
		var at := Vector3(b.get_center().x, b.position.y + b.size.y * frac, b.get_center().z)
		assert_true(intro._clears_card(intro._pose, at), "%s: it stands clear of the card" % enc)
		intro.skip()
	_free()


func test_a_hero_shot_has_nobody_in_front_of_the_boss() -> void:
	# M3-BPR-423 (the Lead, 03:41): the Hullgnaw raft's rail cut its intro in half; a hero stood in the lens. big14's
	# merged raft and deck meshes slipped a bounds-only test: the surfaces decide.
	for enc: StringName in BOSSES:
		var intro := _start(enc, 0.0)
		intro.force_play = true
		intro.play()
		if intro.shot_id != BattleBossIntro.HERO_SHOT:
			intro.skip()
			continue
		var b := intro._bounds(ctl.stage.stand_in(intro.boss_id))
		var pos: Vector3 = intro._pose["pos"]
		var occluders := BattleBossHeroShot._occluders(intro, b)
		assert_false(
			BattleBossHeroShot.sight_blocked(occluders, pos, pos + Vector3.UP * BattleBossHeroShot.HEADROOM_M),
			"%s: the lens is under nothing" % enc
		)
		assert_true(
			BattleBossHeroShot.foreground_share(occluders, intro._pose, b) <= BattleBossHeroShot.FOREGROUND_MAX,
			"%s: no near wall fills the frame's foot" % enc
		)
		var lens := Transform3D(Basis.looking_at((intro._pose["look"] as Vector3) - pos, Vector3.UP), pos)
		for p in BattleBossHeroShot.sight_points(b, lens):  # the arena's and the party's own surfaces, not bounds
			assert_false(
				BattleBossHeroShot.sight_blocked(occluders, pos, p),
				"%s: nothing stands between the lens and the boss" % enc
			)
		assert_true(BattleBossHeroShot._party_small(intro, intro._pose), "%s: no hero crowds the frame" % enc)
		intro.skip()
	_free()


func test_a_retry_skips_it_unless_the_row_says_so() -> void:
	var intro := _start(&"ch01_hullgnaw", 1.0)
	assert_true(intro.playing())
	intro.skip()
	var again := _start(&"ch01_hullgnaw", 1.0)
	assert_ne(again, intro, "a retry builds a new intro")
	assert_false(again.holding(), "Fight again skips it")
	assert_false(ctl.hud.holds_battle())
	again.row = again.row.duplicate()
	again.row["on_retry"] = true
	assert_true(again.wants_play(), "unless the row says on_retry")
	_free()


func test_an_encounter_without_a_row_has_no_intro() -> void:
	ctl.pacing_scale = 1.0
	var party: Array[StringName] = [&"rhen", &"asha"]
	var none: Array[StringName] = []
	ctl.start_battle(party, none, &"ch02_tideline", SEED)
	var intro := BattleBossIntro.of(ctl.stage)
	assert_true(intro.row.is_empty())
	assert_false(intro.holding())
	assert_false(ctl.hud.holds_battle())
	_free()


# --- M3-BPR-03: the Inquisitor (Ch6 B04) ---------------------------------------------------


## His card names a man, not a monster: his name and rank from the beats, and a sober epithet.
func test_ch06_the_inquisitor_has_a_sincere_card() -> void:
	var row := (cfg["rows"] as Dictionary)["ch06_inquisitor"] as Dictionary
	assert_eq(str(row["enemy"]), "stillguard_inquisitor")
	assert_eq(str(row["shot"]), "boss")
	assert_eq(str(TranslationServer.translate(str(row["title_key"]))), "Inquisitor Hadric Moll")
	var epithet := str(TranslationServer.translate(str(row["epithet_key"])))
	assert_ne(epithet, str(row["epithet_key"]), "the epithet is translated")
	_free()


## The intro hides the encounter's opening prompt while it plays and gives it back after; Toma's first-turn bark
## (turn_prompt_key) still shows on his first turn.
func test_ch06_the_intro_and_the_first_turn_prompts_do_not_collide() -> void:
	var intro := _start(&"ch06_inquisitor", 1.0)
	assert_true(intro.playing(), "it plays at the first turn")
	var help := ctl.hud.get_node(BattleBossIntro.HELP_LINE) as CanvasItem
	assert_eq(help.modulate.a, 0.0, "the help line is hidden while it plays")
	intro.advance(_total(intro) + EPS)
	assert_true(intro.done())
	assert_eq(help.modulate.a, 1.0, "the help line is back after it")
	ctl.pacing_scale = 0.0
	var bark := tr("BARK_CH06_TOMA_NOT_THEM")
	var guard := 0
	while guard < 200 and not (ctl.state == BattleController.STATE_COMMAND and ctl.engine.current.id == &"toma"):
		guard += 1
		if ctl.state == BattleController.STATE_COMMAND:
			ctl.act(&"attack", [ctl.engine.enemies[0].id] as Array[StringName])
		else:
			ctl.tick(10.0)
	assert_eq(ctl.engine.current.id, &"toma", "Toma's first turn comes")
	assert_eq(ctl.hud.help_text(), bark, "his bark shows on it")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func test_an_act_two_boss_gets_its_intro_wherever_it_appears() -> void:
	# M3-BPR-408: the Lamp Engine and the Avalanche Ram have no encounters yet; their rows are by enemy id.
	var by := cfg["by_enemy"] as Dictionary
	for boss: String in ["lamp_engine", "avalanche_ram", "mangrove_drowner", "wakefin"]:  # M3-BPR-418: two more
		assert_true(by.has(boss), "%s has an intro row" % boss)
		var ids: Array[StringName] = [StringName("%s#1" % boss)]
		var r := BattleBossIntro.row_for(cfg, &"some_future_encounter", ids)
		assert_eq(str(r.get("enemy", "")), boss, "%s: framed on itself" % boss)
		for key: String in ["title_key", "epithet_key"]:
			assert_ne(TranslationServer.translate(str(r[key])), str(r[key]), "%s %s is translated" % [boss, key])
		assert_true((BattleChoreo.load_data()["camera"]["shots"] as Dictionary).has(str(r["shot"])), "a real shot")
	var none: Array[StringName] = [&"reef_crab#1"]
	assert_true(BattleBossIntro.row_for(cfg, &"sandbox_reef", none).is_empty(), "a regular fight has none")
	var own: Array[StringName] = [&"hullgnaw#1"]
	assert_eq(BattleBossIntro.row_for(cfg, &"ch01_hullgnaw", own), cfg["rows"]["ch01_hullgnaw"], "its own row wins")
	_free()


func test_no_party_member_crowds_a_boss_intro() -> void:
	# M3-BPR-404 (big11 playtest): the real Toma stood huge over the timeline in the Drownbell's intro.
	for enc: StringName in BOSSES:
		var intro := _start(enc, 0.0)
		intro.force_play = true
		intro.play()
		assert_false(intro._pose.is_empty(), "%s has a fitted shot" % enc)
		var clear := (
			BattleBossHeroShot._party_small(intro, intro._pose)
			if intro.shot_id == BattleBossIntro.HERO_SHOT
			else intro._party_clear(intro._pose)
		)
		assert_true(clear, "%s: the party is off screen or small and clear of the HUD" % enc)
		intro.skip()
	_free()


func test_the_party_rule_widens_a_shot_only_when_the_party_crowds_it() -> void:
	# PC render c1d1e3e: at party_max_h 0.3 Rhen (0.35 of the screen, inside the safe frame at Hullgnaw's side) pushed
	# the camera out past the raft's rope rail, which then cut across the serpent. Hullgnaw keeps the frame it has
	# with no party rule at all; the Drownbell (Toma over the timeline) still orbits.
	var intro := _start(&"ch01_hullgnaw", 0.0)
	intro.row = intro.row.duplicate()
	intro.row["hero"] = false  # the fitted shot's own rule (M3-BPR-423's hero shot is tried first otherwise)
	intro.force_play = true
	intro.play()
	var ruled := intro._pose.duplicate()
	intro.skip()
	intro.cfg = intro.cfg.duplicate(true)
	(intro.cfg["fit"] as Dictionary)["party_max_h"] = 100.0
	intro.play()
	assert_true(
		(ruled["pos"] as Vector3).is_equal_approx(intro._pose["pos"] as Vector3), "Hullgnaw: the same frame as unruled"
	)
	intro.skip()
	_free()


func test_a_boss_model_plays_its_intro_clip() -> void:
	# M3-CRB-009: a boss model with an `intro` clip plays it while the camera holds on it; one without just idles.
	var with_clip := 0
	for enc: StringName in BOSSES:
		var intro := _start(enc, 0.0)
		intro.force_play = true
		intro.play()
		var f := ctl.stage.stand_in(intro.boss_id)
		var actor := f.creature() if f != null else null
		if actor != null and actor.has_clip(BattleBossIntro.INTRO_CLIP):
			assert_eq(actor.current_clip, BattleBossIntro.INTRO_CLIP, "%s plays its intro clip" % enc)
			with_clip += 1
		intro.skip()
	print("bosses with an intro clip: %d" % with_clip)
	_free()
