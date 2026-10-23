extends TestCase
## M1-UI-04: the battle Items command and its warnings. The engine half (item_fells,
## item_defeats_party) runs headless on the live tables; the menu half drives the sandbox scene
## through BattleController with an injected bag, as the player would.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const WICK := &"relighting_wick"
const TONIC := &"salt_tonic"

var ctl: BattleController
var engine: BattleEngine
var item_db: ItemDB


func before_each() -> void:
	ctl = null
	engine = BattleEngine.new()
	item_db = ItemDB.load_default()


# --- engine: who a revive fells, and when that loses the fight --------------------------


func test_a_zombie_reviving_itself_as_the_last_one_standing_is_a_defeat() -> void:
	_engine_turn()
	var actor := engine.current
	_other(actor).fall()
	actor.add_status(&"zombie", -1)
	var bag := _bag({"relighting_wick": 1})
	assert_true(engine.item_defeats_party(WICK, _one(actor), bag), "predicted")
	var r := engine.use_item(WICK, _one(actor), bag)
	assert_true(r.ok, "the use is legal")
	assert_true(r.hits[0]["zombie_felled"])
	assert_eq(engine.outcome, BattleEngine.OUTCOME_DEFEAT, "the prediction is what play does")


func test_stone_does_not_count_as_standing() -> void:
	_engine_turn()
	var actor := engine.current
	assert_true(_other(actor).add_status(&"petrify", -1))
	actor.add_status(&"zombie", -1)
	var bag := _bag({"relighting_wick": 1})
	assert_true(engine.item_defeats_party(WICK, _one(actor), bag), "a petrified ally can't fight on")
	engine.use_item(WICK, _one(actor), bag)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_DEFEAT)


func test_no_defeat_while_someone_else_stands() -> void:
	_engine_turn()
	var actor := engine.current
	var ally := _other(actor)
	actor.add_status(&"zombie", -1)
	ally.add_status(&"zombie", -1)
	var bag := _bag({"relighting_wick": 1})
	assert_true(BattleEngine.item_fells(bag.action_for(WICK), actor), "the Wick still fells the user")
	assert_false(engine.item_defeats_party(WICK, _one(actor), bag), "the other Zombie fights on")
	assert_false(engine.item_defeats_party(WICK, _one(ally), bag), "felling an ally is not a defeat")
	engine.use_item(WICK, _one(actor), bag)
	assert_eq(engine.outcome, &"", "and play agrees")


func test_only_a_revive_on_the_living_fells() -> void:
	_engine_turn()
	var actor := engine.current
	var ally := _other(actor)
	var wick := ItemBattleAction.for_item(item_db, WICK)
	var tonic := ItemBattleAction.for_item(item_db, TONIC)
	ally.fall()
	assert_false(BattleEngine.item_fells(wick, ally), "a fallen ally is revived, not felled")
	actor.add_status(&"zombie", -1)
	assert_false(BattleEngine.item_fells(tonic, actor), "a heal harms a Zombie but is not a revive")
	assert_false(engine.item_defeats_party(WICK, _one(ally), _bag({"relighting_wick": 1})))


func test_a_refused_use_never_warns() -> void:
	_engine_turn()
	var actor := engine.current
	_other(actor).fall()
	actor.add_status(&"zombie", -1)
	assert_false(engine.item_defeats_party(WICK, _one(actor), _bag({})), "none in the bag")
	assert_false(engine.item_defeats_party(WICK, _one(actor), null), "no bag")
	assert_false(engine.item_defeats_party(&"crab_carapace", _one(actor), _bag({"crab_carapace": 1})))
	assert_false(engine.item_defeats_party(WICK, [] as Array[BattleCombatant], _bag({"relighting_wick": 1})))
	assert_false(engine.item_defeats_party(WICK, _one(engine.enemies[0]), _bag({"relighting_wick": 1})))


# --- the menu ----------------------------------------------------------------------------


func test_items_sits_between_skills_and_escape_only_when_there_is_a_bag() -> void:
	_start_menu({"salt_tonic": 2})
	# Rhen's Swell row sits under Attack (M2-UI-01).
	var bag: Array[StringName] = [&"attack", &"swell", &"skills", &"items", &"escape", &"swap"]
	assert_eq(_row_ids(), bag)
	_free()
	_start_menu({}, false)
	var no_bag: Array[StringName] = [&"attack", &"swell", &"skills", &"escape", &"swap"]
	assert_eq(_row_ids(), no_bag, "fixtures have no Items row")
	_free()


func test_the_items_page_lists_counts_and_greys_out_what_nobody_can_take() -> void:
	_start_menu({"salt_tonic": 2, "relighting_wick": 1, "crab_carapace": 3})
	_open_items()
	assert_eq(ctl.state, BattleController.STATE_ITEMS)
	var rows := ctl.hud.commands.top_page().rows
	assert_eq(rows.size(), 2, "materials have no battle use")
	var tonic := _row(TONIC)
	assert_eq(tonic["label"], tr("ITEM_SALT_TONIC"))
	assert_eq(tonic["mp"], tr("HUD_ITEM_COUNT_FMT").format({"n": 2}))
	assert_true(tonic["enabled"])
	assert_false(_row(WICK)["enabled"], "no one has fallen and no one is a Zombie")
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	_free()


func test_a_wick_on_the_fallen_revives_through_the_menu() -> void:
	_start_menu({"relighting_wick": 1})
	var ally := _other(ctl.engine.current)
	ally.fall()
	_open_items()
	ctl.hud.commands.select(WICK)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	assert_eq(ctl.pending_item(), WICK)
	assert_eq(ctl.picked_ids(), [ally.id] as Array[StringName], "a revive starts on the fallen")
	assert_eq(ctl.hud.help_role, &"", "nothing to warn about")
	var seen: Array[ActionResult] = []
	ctl.engine.action_resolved.connect(func(r: ActionResult) -> void: seen.append(r))
	_press(&"ui_accept")
	# Pacing is instant, so the foes have already acted: read the item's own result.
	assert_eq(seen[0].item_id, WICK)
	assert_true(bool(seen[0].hits[0]["revived"]), "revived")
	assert_eq(seen[0].hits[0]["target_id"], ally.id)
	assert_eq(ctl.items.count(WICK), 0, "one Wick spent")
	_free()


func test_a_zombie_last_standing_is_warned_before_reviving_itself() -> void:
	_start_menu({"relighting_wick": 1})
	var actor := ctl.engine.current
	_other(actor).fall()
	actor.add_status(&"zombie", -1)
	_open_items()
	ctl.hud.commands.select(WICK)
	_press(&"ui_accept")
	assert_eq(ctl.candidate_ids().size(), 2, "the fallen ally and the living Zombie")
	assert_eq(ctl.hud.help_role, &"", "reviving the ally is safe")
	_press(&"ui_right")
	assert_eq(ctl.picked_ids(), [actor.id] as Array[StringName])
	var warning := tr("HUD_HELP_ITEM_DEFEAT_FMT").format({"name": ctl.menus.display_name(actor)})
	assert_eq(ctl.hud.help_text(), warning, "the warning is the whole line")
	assert_eq(ctl.hud.help_role, &"danger", "in the danger color")
	for s in ctl.hud.timeline.slots.slice(1):
		assert_ne(s["id"], actor.id, "the preview shows the user falling out of the order")
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_ITEMS, "cancel goes back to the item list")
	assert_eq(ctl.pending_item(), &"")
	_press(&"ui_accept")
	_press(&"ui_right")
	_press(&"ui_accept")
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_DEFEAT, "warned, not forbidden: the choice is legal")
	_free()


func test_the_warning_shows_on_hover_when_the_user_is_the_only_target() -> void:
	_start_menu({"relighting_wick": 1, "salt_tonic": 1}, true, [&"rhen"] as Array[StringName])
	var actor := ctl.engine.current
	actor.add_status(&"zombie", -1)
	_open_items()
	ctl.hud.commands.select(WICK)
	assert_eq(ctl.hud.help_role, &"danger", "hovering the Wick already warns: %s" % ctl.hud.help_text())
	ctl.hud.commands.select(TONIC)
	assert_eq(ctl.hud.help_role, &"", "the tonic does not end the fight")
	var harm := tr("HUD_HELP_ZOMBIE_FMT").format({"name": ctl.menus.display_name(actor)})
	assert_true(ctl.hud.help_text().begins_with(harm), "but it is flagged as harm: %s" % ctl.hud.help_text())
	_free()


func test_felling_a_zombie_ally_is_noted_but_not_a_defeat() -> void:
	_start_menu({"relighting_wick": 1})
	var ally := _other(ctl.engine.current)
	ally.add_status(&"zombie", -1)
	_open_items()
	ctl.hud.commands.select(WICK)
	_press(&"ui_accept")
	assert_eq(ctl.picked_ids(), [ally.id] as Array[StringName])
	var note := tr("HUD_HELP_ITEM_FELLS_FMT").format({"name": ctl.menus.display_name(ally)})
	assert_true(ctl.hud.help_text().begins_with(note), ctl.hud.help_text())
	assert_eq(ctl.hud.help_role, &"")
	_free()


func test_items_ignore_provoke_in_the_cursor() -> void:
	_start_menu({"salt_tonic": 1})
	var actor := ctl.engine.current
	assert_true(actor.add_status(&"provoke", 3))
	actor.provoker_id = ctl.engine.enemies[0].id
	_open_items()
	ctl.hud.commands.select(TONIC)
	_press(&"ui_accept")
	assert_eq(ctl.candidate_ids().size(), ctl.engine.party_active.size(), "every ally, not the provoker")
	_free()


func test_a_refused_use_costs_nothing_and_says_why() -> void:
	_start_menu({"salt_tonic": 1})
	var actor := ctl.engine.current
	var r := ctl.use_item_on(WICK, [actor.id] as Array[StringName])
	assert_false(r.ok)
	assert_eq(r.fail_reason, &"no_item")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_eq(ctl.hud.help_text(), ctl.menus.fail_text(&"no_item", actor))
	assert_eq(ctl.current_actor_id(), actor.id, "still their turn")
	_free()


# --- helpers -----------------------------------------------------------------------------


func _engine_turn() -> void:
	var active: Array[StringName] = [&"rhen", &"asha"]
	engine.setup(BattleDB.load_default(), active, [] as Array[StringName], &"sandbox_reef", SEED)
	engine.begin()
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


func _bag(counts: Dictionary) -> InventoryItemSource:
	var inv := Inventory.new(item_db, {})
	for iid: Variant in counts:
		inv.add(StringName(str(iid)), int(counts[iid]))
	return InventoryItemSource.new(item_db, inv)


## The sandbox at Rhen's first turn, with `counts` in the bag (`with_bag` false: no bag at all).
func _start_menu(
	counts: Dictionary, with_bag: bool = true, active: Array[StringName] = [&"rhen", &"asha"] as Array[StringName]
) -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.items = _bag(counts) if with_bag else null
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid in active:
		p.add_character(cid)
	ctl.start_battle(active, [] as Array[StringName], &"sandbox_reef", SEED, p)
	var guard := 0
	while ctl.current_actor_id() != &"rhen" and ctl.engine.outcome == &"" and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.current_actor_id(), &"rhen")


## Rebuilds the turn's menu (the tests change combatants after it opened), then opens Items.
func _open_items() -> void:
	ctl._open_command()
	ctl.hud.commands.select(BattleMenus.ROW_ITEMS)
	_press(&"ui_accept")


func _row(iid: StringName) -> Dictionary:
	for r in ctl.hud.commands.top_page().rows:
		if StringName(str(r["id"])) == iid:
			return r
	return {}


func _row_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for r in ctl.hud.commands.top_page().rows:
		out.append(StringName(str(r["id"])))
	return out


func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out


func _other(c: BattleCombatant) -> BattleCombatant:
	var e := ctl.engine if ctl != null else engine
	return e.party_active[1] if e.party_active[0] == c else e.party_active[0]


func _press(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	ctl = null
