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
	assert_eq(ids, [&"attack", &"skills", &"escape", &"swap"] as Array[StringName], "Swap is the last row")
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
	_press(&"ui_down")
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
	_press(&"ui_down")
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
	assert_eq(ctl.hud.result.result_rows.size(), participants.size(), "fallen fighters are listed too")
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
