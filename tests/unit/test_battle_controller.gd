extends TestCase
## BattleController (M1-CMB-01) driven through its public API and simulated ui_* input, on the
## real sandbox scene and data. Pacing is instant unless a test turns it on.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022

var ctl: BattleController


func before_each() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_sandbox_reaches_a_player_turn_with_the_root_menu() -> void:
	_start()
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_true(ctl.engine.is_party_turn())
	var ids := _row_ids()
	# Rhen has a Swell: its row stays under Attack while the gauge fills (M2-UI-01).
	var want: Array[StringName] = [&"attack", &"swell", &"skills", &"escape", &"swap"]
	assert_eq(ids, want, "Swap is the last row")
	assert_eq(ctl.hud.commands.page_id(), BattleMenus.PAGE_ROOT)
	assert_eq(ctl.hud.timeline.slots.size(), CtbTimeline.PREVIEW_LENGTH, "16 turns are always visible")
	_free()


func test_rhen_and_asha_active_toma_and_ysolde_reserve() -> void:
	_start()
	assert_eq(_ids(ctl.engine.party_active), [&"rhen", &"asha"] as Array[StringName])
	assert_eq(_ids(ctl.engine.party_reserve), [&"toma", &"ysolde"] as Array[StringName])
	assert_eq(ctl.engine.encounter_id, &"sandbox_reef")
	assert_eq(ctl.hud.party.rows().size(), 2, "the HUD lists active fighters only")
	_free()


func test_hovering_skills_changes_the_preview_and_help() -> void:
	_start()
	_to_turn_of(&"rhen")
	ctl.hud.commands.select(BattleMenus.ROW_SKILLS)  # past Rhen's Swell row (M2-UI-01)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SKILLS)
	ctl.hud.commands.select(&"quick_hit")
	var fast := _ghost_slot()
	var help_fast := ctl.hud.help_text()
	ctl.hud.commands.select(&"undertow_cut")
	var slow := _ghost_slot()
	assert_true(fast < slow, "rank 2 previews an earlier next turn than rank 4 (%d vs %d)" % [fast, slow])
	assert_ne(ctl.hud.help_text(), help_fast)
	assert_true(ctl.hud.help_text().contains("2"), "the help line states the delay push")
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_eq(ctl.hud.commands.depth(), 1)
	_free()


func test_preview_follows_the_target() -> void:
	_start()
	_to_turn_of(&"rhen")
	ctl.hud.commands.select(BattleMenus.ROW_SKILLS)  # past Rhen's Swell row (M2-UI-01)
	_press(&"ui_accept")
	ctl.hud.commands.select(&"undertow_cut")
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	var first: Array[StringName] = ctl.picked_ids()
	var marked_first := _target_marked_ids()
	_press(&"ui_right")
	var second: Array[StringName] = ctl.picked_ids()
	assert_ne(first, second, "right moves the target")
	assert_ne(_target_marked_ids(), marked_first, "timeline target marks follow")
	assert_eq(ctl.stage.ringed_ids(), second, "the ground ring follows")
	assert_eq(ctl.hud.target_cursor.targeted_ids(), second)
	_free()


func test_confirming_an_attack_ends_the_turn_and_pops_numbers() -> void:
	_start()
	var actor := ctl.current_actor_id()
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	var target := ctl.engine.find(ctl.picked_ids()[0])
	var hp_before := target.hp
	var turns_before := ctl.engine.find(actor).turns_taken
	_press(&"ui_accept")
	assert_eq(ctl.engine.find(actor).turns_taken, turns_before + 1)
	assert_true(target.hp < hp_before or ctl.hud.damage_numbers_shown > 0, "a hit or a miss is shown")
	assert_true(ctl.hud.damage_numbers_shown > 0)
	assert_true(ctl.state in [BattleController.STATE_COMMAND, BattleController.STATE_RESULT])
	_free()


func test_numbers_use_damage_and_heal_kinds_by_sign() -> void:
	_start()
	_to_turn_of(&"rhen")
	ctl.hud.recent_numbers.clear()
	var foe := ctl.engine.living_foes_of(ctl.engine.current)[0]
	var hp := foe.hp
	var r := ctl.act(&"attack", [foe.id])
	var first: Dictionary = ctl.hud.recent_numbers[0]
	if bool(r.hits[0]["hit"]):
		assert_eq(first["kind"], DamageNumber.KIND_DAMAGE, "a hit on a foe pops a damage number")
		assert_eq(first["text"], str(hp - foe.hp), "showing the HP it lost")
		assert_false(first["on_ally"])
	else:
		assert_eq(first["kind"], DamageNumber.KIND_MISS)
	for n in ctl.hud.recent_numbers:
		if n["on_ally"] and n["kind"] != DamageNumber.KIND_MISS:
			assert_eq(n["kind"], DamageNumber.KIND_DAMAGE, "enemy hits on the party are damage (ui_danger)")
	_to_turn_of(&"asha")
	ctl.hud.recent_numbers.clear()
	ctl.act(&"mend", [&"asha"])
	var heal: Dictionary = ctl.hud.recent_numbers[0] if not ctl.hud.recent_numbers.is_empty() else {}
	if not heal.is_empty() and heal["text"] != "0":
		assert_eq(heal["kind"], DamageNumber.KIND_HEAL, "Mend pops a heal number")
	_free()


func test_swap_menu_swaps_at_no_time_cost() -> void:
	_start()
	var actor := ctl.current_actor_id()
	var now := ctl.engine.now
	var slot := ctl.engine.current.next_time
	ctl.hud.commands.select(BattleMenus.ROW_SWAP)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWAP_IN)
	assert_eq(_row_ids(), [&"toma", &"ysolde"] as Array[StringName])
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWAP_OUT)
	assert_eq(ctl.picked_ids(), [actor] as Array[StringName], "the acting fighter is the default to step back")
	_press(&"ui_accept")
	assert_eq(ctl.engine.now, now, "no time passed")
	assert_eq(ctl.current_actor_id(), &"toma", "Toma takes the turn")
	assert_eq(ctl.engine.current.next_time, slot, "and the slot")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_true(ctl.stage.has_fighter(&"toma"))
	assert_false(ctl.stage.has_fighter(actor))
	assert_true(ctl.hud.party.row_for(&"toma") != null)
	assert_eq(ctl.hud.timeline.slots[0]["id"], &"toma")
	_free()


func test_swap_can_be_cancelled_back_to_the_reserve_list() -> void:
	_start()
	ctl.hud.commands.select(BattleMenus.ROW_SWAP)
	_press(&"ui_accept")
	_press(&"ui_accept")
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_SWAP_IN)
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_eq(_ids(ctl.engine.party_active), [&"rhen", &"asha"] as Array[StringName], "nothing changed")
	_free()


func test_enemy_turns_wait_for_readable_pacing() -> void:
	ctl.pacing_scale = 1.0
	_start()
	var guard := 0
	while ctl.state != BattleController.STATE_BUSY and guard < 8:
		guard += 1
		_press(&"ui_accept")
		_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_BUSY)
	assert_true(ctl.is_waiting())
	var actor := ctl.current_actor_id()
	ctl.tick(0.01)
	assert_eq(ctl.current_actor_id(), actor, "nothing happens before the pause ends")
	var spins := 0
	while ctl.state == BattleController.STATE_BUSY and spins < 200:
		spins += 1
		ctl.tick(0.1)
	assert_true(ctl.state in [BattleController.STATE_COMMAND, BattleController.STATE_RESULT])
	_free()


func test_input_is_ignored_while_busy() -> void:
	ctl.pacing_scale = 1.0
	_start()
	while ctl.state == BattleController.STATE_COMMAND:
		_press(&"ui_accept")
		_press(&"ui_accept")
	if ctl.state == BattleController.STATE_BUSY:
		var actor := ctl.current_actor_id()
		assert_false(ctl.handle_input(_ev(&"ui_accept")))
		assert_eq(ctl.current_actor_id(), actor)
	_free()


func test_escape_ends_or_costs_a_turn() -> void:
	_start()
	var actor := ctl.current_actor_id()
	var turns := ctl.engine.find(actor).turns_taken
	ctl.hud.commands.select(BattleMenus.ROW_ESCAPE)
	_press(&"ui_accept")
	if ctl.engine.outcome == BattleEngine.OUTCOME_ESCAPED:
		assert_eq(ctl.state, BattleController.STATE_RESULT)
		assert_eq(ctl.hud.result.outcome, BattleEngine.OUTCOME_ESCAPED)
	else:
		assert_eq(ctl.engine.find(actor).turns_taken, turns + 1, "a failed escape costs the turn")
	_free()


func test_victory_feeds_xp_into_the_lattice() -> void:
	var p := _fresh_progress()
	_start(p)
	_play_elegant_answer()
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY, "this seed wins with the Toma swap")
	assert_eq(ctl.state, BattleController.STATE_RESULT)
	assert_true(ctl.hud.result.visible)
	var awards := ctl.engine.xp_awards()
	for cid: StringName in awards:
		var xp := int(awards[cid])
		assert_eq(int(ctl.last_awards[cid]["xp"]), xp)
		if p.traveler(cid) != null:
			var expected := ProgressionFormulas.convert_lp(xp, 0, ProgressionFormulas.MOVEMENT_POINT_CAP).x
			assert_eq(int(ctl.last_awards[cid]["moves"]), expected)
			assert_eq(p.traveler(cid).movement_points, expected, "%s banked movement points" % cid)
	var participants := (ctl.engine.party_active + ctl.engine.party_reserve).filter(
		func(c: BattleCombatant) -> bool: return c.participated
	)
	var fighters := ctl.hud.result.result_rows.filter(
		func(r: Dictionary) -> bool: return not r.has(BattleRewards.ROW_SPOILS)  # M2-CMB-07: lume, drops
	)
	assert_eq(fighters.size(), participants.size(), "fallen fighters are listed too")
	_free()


func test_defeat_shows_the_defeat_screen_and_retry_restarts() -> void:
	_start()
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 200:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_DEFEAT, "the naive policy loses (battle_ctb.md bands)")
	assert_eq(ctl.state, BattleController.STATE_RESULT)
	assert_eq(ctl.hud.result.outcome, BattleEngine.OUTCOME_DEFEAT)
	assert_true(ctl.last_awards.is_empty(), "no XP for a defeat")
	assert_eq(ctl.hud.result.current_choice(), BattleController.CHOICE_RETRY)
	_press(&"ui_accept")
	assert_eq(ctl.battles_started, 2)
	assert_eq(ctl.engine.outcome, &"")
	assert_false(ctl.hud.result.visible)
	_free()


func test_party_reflects_activated_lattice_nodes() -> void:
	var p := _fresh_progress()
	var inv := FacetInventory.new({"facet_speed": 1})
	var rhen := p.traveler(&"rhen")
	rhen.movement_points = 1
	var first := p.board.neighbors(rhen.position)[0]
	var node := p.board.lattice_node(first)
	assert_eq(p.move(&"rhen", first), LatticeProgress.RESULT_OK)
	var facet := p.rules.facet_for(node)
	inv.add(facet, 1)
	assert_eq(p.activate(&"rhen", inv), LatticeProgress.RESULT_OK)
	_start(p)
	var base: Dictionary = ctl.engine.db.characters[&"rhen"]["stats"]
	var c := ctl.engine.find(&"rhen")
	if node.kind == LatticeNode.KIND_STAT:
		var have: int = c.get(String(node.stat))
		assert_eq(have, int(base[String(node.stat)]) + node.value, "Lattice %s +%d" % [node.stat, node.value])
	_free()


func test_ui_strings_come_from_localization() -> void:
	_start()
	for row in ctl.hud.commands.top_page().rows:
		var label := str(row["label"])
		assert_false(label.begins_with("HUD_"), "row label '%s' is translated" % label)
	_free()


# --- helpers -----------------------------------------------------------------------------


func _start(p: LatticeProgress = null) -> void:
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED, p if p != null else _fresh_progress())


func _fresh_progress() -> LatticeProgress:
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	return p


func _play_elegant_answer() -> void:
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 300:
		guard += 1
		var e := ctl.engine
		if e.find(&"asha") in e.party_active and e.find(&"toma") in e.party_reserve:
			ctl.swap_members(&"asha", &"toma")
			continue
		var foes := e.living_foes_of(e.current)
		var weakest := foes[0]
		for f in foes:
			if f.hp < weakest.hp:
				weakest = f
		ctl.act(&"attack", [weakest.id])


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _ghost_slot() -> int:
	for s in ctl.hud.timeline.slots:
		if s["ghost"]:
			return int(s["slot"])
	return -1


func _target_marked_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for s in ctl.hud.timeline.slots:
		if s.get("targeted", false) and not out.has(s["id"]):
			out.append(s["id"])
	return out


func _row_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for r in ctl.hud.commands.top_page().rows:
		out.append(StringName(str(r["id"])))
	return out


func _ids(list: Array[BattleCombatant]) -> Array[StringName]:
	var out: Array[StringName] = []
	for c in list:
		out.append(c.id)
	return out


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _press(action: StringName) -> void:
	ctl.handle_input(_ev(action))


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


# --- M1-UI-02: swap preview, fail copy, Provoke, auto turns, statuses, fixtures ----------


func test_hovering_a_reserve_member_previews_the_swap() -> void:
	_start()
	var actor := ctl.current_actor_id()
	ctl.hud.commands.select(BattleMenus.ROW_SWAP)
	var before := _slot_ids()
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWAP_IN)
	assert_eq(ctl.hud.commands.current_row()["id"], &"toma")
	assert_eq(_slot_ids(), _entry_ids(ctl.engine.preview_swap(actor, &"toma")), "chips show the order after the swap")
	assert_ne(_slot_ids(), before, "hovering Toma moves the chips")
	assert_eq(ctl.hud.timeline.slots[0]["id"], &"toma", "Toma would take the acting turn")
	assert_eq(_ids(ctl.engine.party_active), [&"rhen", &"asha"] as Array[StringName], "a preview changes nothing")
	_free()


func test_swap_out_preview_follows_the_leaver_and_matches_the_real_swap() -> void:
	_start()
	var actor := ctl.current_actor_id()
	ctl.hud.commands.select(BattleMenus.ROW_SWAP)
	_press(&"ui_accept")
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWAP_OUT)
	assert_eq(_slot_ids(), _entry_ids(ctl.engine.preview_swap(actor, &"toma")))
	_press(&"ui_right")
	var leaver: StringName = ctl.picked_ids()[0]
	assert_ne(leaver, actor)
	var expected := _entry_ids(ctl.engine.preview_swap(leaver, &"toma"))
	assert_eq(_slot_ids(), expected, "the preview follows the highlighted leaver")
	assert_eq(ctl.hud.timeline.slots[0]["id"], actor, "the actor keeps the turn when someone else steps back")
	_press(&"ui_accept")
	assert_eq(_slot_ids(), expected, "the preview was exactly the order after the swap (pillar 4)")
	_free()


func test_every_engine_fail_reason_has_its_own_localized_text() -> void:
	_start()
	var src := FileAccess.get_file_as_string("res://game/battle/battle_engine.gd")
	var rx := RegEx.create_from_string('failed\\([^)]*&"([a-z_]+)"\\)')
	var engine_reasons: Array[StringName] = []
	for m in rx.search_all(src):
		engine_reasons.append(StringName(m.get_string(1)))
	assert_true(engine_reasons.size() >= 6, "found the engine's fail reasons")
	for r in engine_reasons:
		assert_true(BattleMenus.FAIL_REASONS.has(r), "BattleMenus.FAIL_REASONS lists '%s'" % r)
	var generic := tr("HUD_FAIL_GENERIC")
	var actor := ctl.engine.current
	for r in BattleMenus.FAIL_REASONS:
		var text := ctl.menus.fail_text(r, actor, ctl.engine.enemies[0])
		assert_ne(text, generic, "'%s' has its own sentence" % r)
		assert_ne(text, String(r), "'%s' is not shown as its raw id" % r)
		if String(r).contains("_"):
			assert_false(text.contains(String(r)), "'%s' never shows the raw id: %s" % [r, text])
		assert_false(text.contains("{"), "'%s' is fully formatted: %s" % [r, text])
		assert_false(text.begins_with("HUD_"), "'%s' is translated" % r)
	assert_eq(ctl.menus.fail_text(&"some_future_reason", actor), generic, "unknown reasons still read as words")
	_free()


func test_a_refused_action_explains_itself_in_words() -> void:
	_start()
	_to_turn_of(&"rhen")
	ctl.engine.current.mp = 0
	var r := ctl.act(&"quick_hit", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_false(r.ok)
	assert_eq(r.fail_reason, &"no_mp")
	assert_eq(ctl.state, BattleController.STATE_COMMAND, "nothing was spent; the menu is back")
	assert_eq(ctl.hud.help_text(), ctl.menus.fail_text(&"no_mp", ctl.engine.current))
	assert_false(ctl.hud.help_text().contains("no_mp"))
	_free()


func test_provoke_locks_the_cursor_on_the_provoker_and_marks_it() -> void:
	var harrier := &"gull_harrier#3"
	_start_fixture(
		&"player_preview", {"rhen": {"statuses": [{"id": "provoke", "duration": -1}], "provoked_by": harrier}}
	)
	_to_turn_of(&"rhen")
	assert_eq(ctl.current_actor_id(), &"rhen")
	assert_true(ctl.hud.target_cursor.provoker_marked(), "the hook hangs over the provoker on Rhen's turn")
	assert_true(ctl.hud.help_text().contains(ctl.menus.display_name(ctl.engine.find(harrier))), "help names it")
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	assert_eq(ctl.candidate_ids(), [harrier] as Array[StringName], "only the provoker can be picked")
	_press(&"ui_right")
	assert_eq(ctl.picked_ids(), [harrier] as Array[StringName], "the cursor cannot leave it")
	assert_true(bool(ctl.hud.target_cursor.targets[0]["forced"]), "the locked chevron is marked")
	_press(&"ui_cancel")
	var other := ctl.engine.find(&"reef_crab#1")
	var r := ctl.act(&"attack", [other.id])
	assert_eq(r.fail_reason, &"provoked")
	assert_eq(ctl.hud.help_text(), ctl.menus.fail_text(&"provoked", ctl.engine.current, ctl.engine.find(harrier)))
	_free()


func test_berserk_and_confused_party_turns_are_announced_and_play_themselves() -> void:
	for reason: StringName in [BattleMenus.AUTO_BERSERK, BattleMenus.AUTO_CONFUSE]:
		before_each()
		ctl.pacing_scale = 1.0
		_start_fixture(&"player_preview", {"asha": {"statuses": [{"id": String(reason), "duration": -1}]}})
		var asha := ctl.engine.find(&"asha")
		var announce := ctl.menus.auto_announce(asha, reason)
		var guard := 0
		while ctl.hud.help_text() != announce and guard < 400:
			guard += 1
			if ctl.state == BattleController.STATE_COMMAND:
				ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
			else:
				ctl.tick(0.05)
		assert_eq(ctl.hud.help_text(), announce, "%s: the turn is announced before it plays" % reason)
		assert_eq(ctl.current_actor_id(), &"asha")
		assert_eq(ctl.state, BattleController.STATE_BUSY, "no menu: the player does not choose")
		assert_false(ctl.hud.commands.visible)
		assert_eq(ctl.hud.party.row_for(&"asha").auto_reason, reason, "the party row marks an automatic turn")
		assert_eq(ctl.hud.timeline.caption, ctl.menus.turn_caption(reason), "slot 0 says why")
		assert_eq(ctl.hud.target_cursor.actor_auto, reason, "the actor marker is hollow")
		ctl.tick(HudLayout.num(HudLayout.section(&"pacing"), "enemy_think_sec") + 0.01)
		assert_eq(ctl.current_actor_id(), &"asha", "%s: held longer than an enemy's think time" % reason)
		var announced_at := ctl.hud.help_history.size()
		var spins := 0
		while ctl.current_actor_id() == &"asha" and spins < 100:
			spins += 1
			ctl.tick(0.05)
		var said := ctl.hud.help_history[mini(announced_at, ctl.hud.help_history.size() - 1)]
		var prefix := tr(
			"HUD_AUTO_CONFUSE_ACTS_FMT" if reason == BattleMenus.AUTO_CONFUSE else "HUD_AUTO_BERSERK_ACTS_FMT"
		)
		assert_true(said.begins_with(prefix.get_slice("{", 0)), "%s: the result says why ('%s')" % [reason, said])
		_free()


func test_doom_counts_down_on_the_chips_and_the_party_row() -> void:
	_start_fixture(&"player_preview", {"rhen": {"statuses": [{"id": "doom", "duration": 3}]}})
	var counts: Array[int] = []
	for s in ctl.hud.timeline.slots:
		if s["id"] == &"rhen":
			counts.append(int(s["doom"]))
	assert_eq(counts, [3, 2, 1] as Array[int], "three more turns, counting down, then none")
	var first := _first_slot_of(&"rhen")
	assert_eq(ctl.hud.timeline.chip_for_key(str(first["key"])).doom, 3, "the chip carries the count")
	assert_eq(ctl.hud.party.row_for(&"rhen").doom_text(), "3", "the party row shows it beside the hourglass")
	_free()


func test_statuses_capture_shows_provoke_reflect_petrify_and_doom() -> void:
	ctl.run_script(BattleController.SCRIPT_STATUSES)
	var eel := &"lantern_eel#2"
	assert_eq(ctl.current_actor_id(), &"ysolde")
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	assert_eq(ctl.pending_skill(), &"ember")
	assert_eq(ctl.candidate_ids(), [eel] as Array[StringName], "provoked by the eel")
	assert_eq(ctl.hud.target_cursor.bounce_ids(), [&"rhen"] as Array[StringName], "Reflect bounces Ember onto Rhen")
	assert_eq(_target_marked_ids(), [&"rhen"] as Array[StringName], "the timeline marks where it lands")
	var help := ctl.hud.help_text()
	assert_true(help.contains(ctl.menus.display_name(ctl.engine.find(&"rhen"))), "help: %s" % help)
	assert_true(ctl.hud.target_cursor.provoker_marked())
	assert_false(_slot_ids().has(&"asha"), "stone takes no turns")
	assert_true(ctl.hud.party.row_for(&"asha").is_stone(), "the party row turns to stone")
	assert_true(ctl.stage.stand_in(&"asha").is_stone(), "so does the stand-in")
	assert_true(int(_first_slot_of(&"rhen")["doom"]) > 0, "Rhen's chips count Doom down")
	var glyphs := ctl.hud.party.row_for(&"rhen").status_ids()
	assert_true(glyphs.has(&"zombie") and glyphs.has(&"regen"), "Zombie and (inverted) Regen are shown")
	assert_true(StatusGlyph.inverted_for(ctl.engine.find(&"rhen"), &"regen"))
	_free()


func test_a_reflected_spell_floats_reflected_over_the_reflector() -> void:
	ctl.run_script(BattleController.SCRIPT_STATUSES)
	ctl.show_damage_numbers = true
	ctl.hud.recent_numbers.clear()
	var r := ctl.act(&"ember", [&"lantern_eel#2"])
	assert_true(r.ok)
	assert_eq(StringName(str(r.hits[0].get("reflected_from", ""))), &"lantern_eel#2")
	var words := ctl.hud.recent_numbers.filter(func(n: Dictionary) -> bool: return n["kind"] == DamageNumber.KIND_INFO)
	assert_true(words.any(func(n: Dictionary) -> bool: return n["text"] == tr("HUD_FLOAT_REFLECTED")))
	_free()


func test_a_drain_heals_its_user_and_a_mended_part_is_named() -> void:
	# Act II hud.md sections 2 and 3: the fen leech's drain (M4-CMB-1001) and a conduit crawler's repair (M4-A2P-022).
	ctl.run_script(BattleController.SCRIPT_STATUSES)
	ctl.show_damage_numbers = true
	ctl.hud.recent_numbers.clear()
	var r := ActionResult.new()
	r.actor_id = &"lantern_eel#2"
	r.skill_id = &"ember"
	r.hits = (
		[
			{"target_id": &"rhen", "hit": true, "amount": 12, "crit": false, "drained": 6},
			{"target_id": &"lantern_eel#2", "hit": true, "amount": 0, "crit": false, "part_restored": &"toll_gather"},
		]
		as Array[Dictionary]
	)
	ctl.floats.show_hits(r, false)
	var nums := ctl.hud.recent_numbers
	assert_true(nums.any(func(n: Dictionary) -> bool: return n["kind"] == DamageNumber.KIND_HEAL and n["text"] == "6"))
	assert_true(nums.any(func(n: Dictionary) -> bool: return n["text"] == tr("HUD_FLOAT_DRAINED")))
	var part := tr(str(ctl.engine.db.skill(&"toll_gather").get("name_key", "")))
	var mended := tr("HUD_FLOAT_REPAIRED_FMT").format({"part": part})
	assert_true(nums.any(func(n: Dictionary) -> bool: return n["text"] == mended), "the mended part is named")
	_free()


func test_a_heal_on_a_zombie_is_flagged_before_and_after() -> void:
	_start_fixture(&"player_preview", {"rhen": {"statuses": [{"id": "zombie", "duration": -1}]}})
	ctl.show_damage_numbers = true
	_to_turn_of(&"asha")
	ctl.hud.commands.select(BattleMenus.ROW_SKILLS)  # past her Swell row (M2-UI-03)
	_press(&"ui_accept")
	ctl.hud.commands.select(&"mend")
	_press(&"ui_accept")
	var guard := 0
	while ctl.picked_ids()[0] != &"rhen" and guard < 4:
		guard += 1
		_press(&"ui_right")
	var note := tr("HUD_HELP_ZOMBIE_FMT").format({"name": ctl.menus.display_name(ctl.engine.find(&"rhen"))})
	assert_true(ctl.hud.help_text().contains(note), "the preview warns: %s" % ctl.hud.help_text())
	ctl.hud.recent_numbers.clear()
	var hp := ctl.engine.find(&"rhen").hp
	_press(&"ui_accept")
	assert_true(ctl.engine.find(&"rhen").hp < hp, "the heal harmed")
	var first: Dictionary = ctl.hud.recent_numbers[0]
	assert_eq(first["kind"], DamageNumber.KIND_DAMAGE, "shown as damage")
	assert_true(ctl.hud.recent_numbers.any(func(n: Dictionary) -> bool: return n["text"] == tr("HUD_FLOAT_INVERTED")))
	_free()


func test_regen_on_a_zombie_shows_its_end_of_turn_harm() -> void:
	var o := {"rhen": {"statuses": [{"id": "zombie", "duration": -1}, {"id": "regen", "duration": -1}]}}
	_start_fixture(&"player_preview", o)
	ctl.show_damage_numbers = true
	_to_turn_of(&"rhen")
	ctl.hud.recent_numbers.clear()
	var hp := ctl.engine.find(&"rhen").hp
	ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_true(ctl.engine.find(&"rhen").hp < hp or ctl.engine.outcome != &"", "Regen harmed Rhen")
	var regen_word := tr("HUD_FLOAT_REGEN_INVERTED")
	assert_true(ctl.hud.recent_numbers.any(func(n: Dictionary) -> bool: return n["text"] == regen_word))
	_free()


func test_the_current_actor_is_marked_everywhere() -> void:
	_start()
	var actor := ctl.current_actor_id()
	assert_true(ctl.hud.target_cursor.actor_visible(), "a marker over the acting fighter")
	assert_eq(ctl.hud.target_cursor.actor_auto, &"", "solid: the player chooses")
	assert_true(ctl.hud.party.row_for(actor).is_current)
	var head: Dictionary = ctl.hud.timeline.slots[0]
	assert_true(bool(head["is_current"]))
	assert_eq(ctl.hud.timeline.chip_for_key(str(head["key"])).caption, tr("HUD_TL_NOW"), "slot 0 says Acting now")
	_free()


func test_capture_states_run_on_fixture_data_not_live_balance() -> void:
	var live := BattleDB.load_default()
	for sid: StringName in BattleFixture.fixture_ids():
		before_each()
		ctl.run_script(sid)
		assert_true(ctl.fixture != null, "%s starts from a fixture" % sid)
		assert_eq(ctl.engine.db, ctl.fixture.db, "%s uses the frozen tables" % sid)
		assert_ne(ctl.engine.db, live)
		match sid:
			BattleController.SCRIPT_PLAYER_PREVIEW:
				assert_eq(ctl.state, BattleController.STATE_TARGET)
				assert_eq(ctl.pending_skill(), &"undertow_cut")
			BattleController.SCRIPT_SWAP_MENU:
				assert_eq(ctl.state, BattleController.STATE_SWAP_IN)
			BattleController.SCRIPT_VICTORY:
				assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
				# M2-CMB-07: the fixture's foes carry lume and certain drops: Lume, Crab Carapace,
				# Salt Tonic and Eel Lantern rows follow the fighters, listed but never paid.
				assert_eq(ctl.hud.result.result_rows.size(), 7, "Rhen, Toma and Asha all stood; four spoils")
				for row in ctl.hud.result.result_rows.slice(0, 3):
					assert_false(bool(row.get("fell", false)))
					assert_false(row.has(BattleRewards.ROW_SPOILS))
				assert_eq(int(ctl.last_spoils[BattleRewards.KEY_LUME]), 62)
				assert_false(bool(ctl.last_spoils[BattleRewards.KEY_PAID]), "a capture never pays")
			BattleController.SCRIPT_DEFEAT:
				assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_DEFEAT)
				assert_eq(ctl.state, BattleController.STATE_RESULT)
			BattleController.SCRIPT_STATUSES:
				assert_eq(ctl.state, BattleController.STATE_TARGET)
		_free()


func test_fixture_overrides_never_touch_the_shared_tables() -> void:
	var tables := {"enemies": [{"id": "a", "stats": {"hp": 10, "agility": 5}}]}
	var out := BattleFixture.merged_tables(tables, {"enemies": {"a": {"stats": {"hp": 1}}}})
	assert_eq(int(out["enemies"][0]["stats"]["hp"]), 1)
	assert_eq(int(out["enemies"][0]["stats"]["agility"]), 5, "deep merge keeps the other stats")
	assert_eq(int(tables["enemies"][0]["stats"]["hp"]), 10, "the source is untouched")
	var fx := BattleFixture.load_fixture(&"victory")
	assert_eq(int(fx.db.enemies[&"reef_crab"]["stats"]["hp"]), 1)
	assert_eq(fx.encounter, &"fixture_reef", "its own encounter, not sandbox_reef")


# --- M1-UI-02 helpers --------------------------------------------------------------------


func _start_fixture(fid: StringName, opening: Dictionary = {}) -> void:
	var fx := BattleFixture.load_fixture(fid)
	if not opening.is_empty():
		fx.opening = opening
	ctl.start_fixture(fx)


func _slot_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for s in ctl.hud.timeline.slots:
		out.append(s["id"])
	return out


func _entry_ids(entries: Array[TurnEntry]) -> Array[StringName]:
	var out: Array[StringName] = []
	for e in entries:
		out.append(e.combatant_id)
	return out


func _first_slot_of(cid: StringName) -> Dictionary:
	for s in ctl.hud.timeline.slots:
		if s["id"] == cid:
			return s
	return {}


func test_the_help_line_wraps_only_when_one_line_cannot_hold_it() -> void:
	ctl.run_script(BattleController.SCRIPT_PLAYER_PREVIEW)
	assert_false(ctl.hud.help_wraps(), "a one-line help keeps the panel one line tall")
	_free()
	before_each()
	ctl.run_script(BattleController.SCRIPT_STATUSES)
	assert_true(ctl.hud.help_wraps(), "Reflect + Provoke notes take a second line instead of being cut")
	_free()


# --- M1-UI-03: staged build (scene-swap frame budget) ----------------------------------


func test_staged_build_spreads_over_frames_and_ends_like_the_one_shot_build() -> void:
	var seen: Array[Dictionary] = []
	ctl.frame_wait = func() -> void:
		(
			seen
			. append(
				{
					"engine": ctl.engine != null,
					"pooled": ctl.hud.timeline.pooled_count(),
					"rows": ctl.hud.party.rows().size(),
					"slots": ctl.hud.timeline.slots.size(),
					"state": ctl.state,
				}
			)
		)
	ctl.start_sandbox(-1, true)
	assert_eq(seen.size(), 4, "lattice | engine + 8 chips | party + 8 chips | first order | first turn")
	assert_false(seen[0]["engine"], "frame 0 only loads the Lattice progress")
	assert_eq(seen[1]["pooled"], CtbTimeline.PREVIEW_LENGTH / 2, "half the chips are built hidden in frame 1")
	assert_eq(seen[1]["rows"], 0, "the party panel waits for frame 2")
	assert_eq(seen[2]["pooled"], CtbTimeline.PREVIEW_LENGTH, "the rest in frame 2")
	assert_eq(seen[3]["slots"], CtbTimeline.PREVIEW_LENGTH, "frame 3 shows the order from the pool")
	assert_eq(seen[3]["pooled"], 0, "every pooled chip was used, none built then")
	for snap in seen:
		assert_eq(snap["state"], BattleController.STATE_IDLE, "no input until the first turn is open")
	assert_false(ctl.building)
	assert_true(ctl.state in [BattleController.STATE_COMMAND, BattleController.STATE_RESULT])
	var staged_ids := _slot_ids()
	var staged_actor := ctl.current_actor_id()
	_free()
	before_each()
	ctl.start_sandbox()
	assert_eq(_slot_ids(), staged_ids, "same order as the one-shot build")
	assert_eq(ctl.current_actor_id(), staged_actor)
	_free()


func test_prebuilt_chips_are_reused_not_duplicated() -> void:
	var tl := ctl.hud.timeline
	var before := tl.get_child_count()
	tl.prebuild(CtbTimeline.PREVIEW_LENGTH)
	assert_eq(tl.get_child_count(), before + CtbTimeline.PREVIEW_LENGTH)
	_start()
	assert_eq(tl.pooled_count(), 0)
	assert_eq(tl.get_child_count(), before + CtbTimeline.PREVIEW_LENGTH, "the first order made no new chips")
	for s in tl.slots:
		assert_true(tl.chip_for_key(str(s["key"])).visible, "pooled chips are shown when used")
	_free()
