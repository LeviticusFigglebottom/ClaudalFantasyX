class_name BattleController
extends Node3D
## Glue for the battle sandbox (M1-CMB-01): drives a headless BattleEngine from player input,
## runs enemy turns with short readable pauses, and feeds the HUD and the 3D stage. It only
## calls the engine's public API (setup/begin/preview/perform/swap/escape/run_enemy_turn/
## xp_awards) and listens to its signals; it never writes combatant state itself.
##
## Player intent funnels into three public actions (act, swap_members, try_escape) that menus,
## tests and capture scripts all use. Time passes only through tick(), so tests can fast-forward.

signal state_changed(new_state: StringName)

const STATE_IDLE := &"idle"
const STATE_COMMAND := &"command"
const STATE_SKILLS := &"skills"
const STATE_TARGET := &"target"
const STATE_SWAP_IN := &"swap_in"
const STATE_SWAP_OUT := &"swap_out"
const STATE_BUSY := &"busy"
const STATE_RESULT := &"result"
const SCRIPT_PLAYER_PREVIEW := &"player_preview"
const SCRIPT_SWAP_MENU := &"swap_menu"
const SCRIPT_VICTORY := &"victory"
const CHOICE_RETRY := &"retry"
const CHOICE_RETURN := &"return"
const RETURN_SCENE := "res://game/core/boot.tscn"

## Capture entry point: on _ready, play deterministically to a fixed state (shots.json).
@export var scripted_state: StringName = &""
## Start the sandbox encounter on _ready (tests turn this off and call start_battle).
@export var auto_start := true
## 1.0 = readable pacing; 0.0 = instant (tests and captures).
@export var pacing_scale := 1.0
## Spawn damage numbers (off for captures so nothing is mid-flight in the frame).
@export var show_damage_numbers := true
## Write Lattice gains back to Game.state after a victory.
@export var persist_progress := true

var engine: BattleEngine
var progress: LatticeProgress
var menus: BattleMenus
var state: StringName = STATE_IDLE
## Last victory: id -> {xp, moves}; moves is -1 for a fighter with no Lattice start yet.
var last_awards: Dictionary = {}
var battles_started := 0

var _db: BattleDB
var _setup: Dictionary = {}
var _pacing: Dictionary = {}
var _damage_m: Dictionary = {}
var _marker_m: Dictionary = {}
var _wait_left := 0.0
var _after_wait := Callable()
var _draining := false
var _pending_skill: StringName = &""
var _group_target := false
var _candidates: Array[StringName] = []
var _target_index := 0
var _swap_in_id: StringName = &""
var _last_foe: StringName = &""

@onready var stage: BattleStage = %Stage
@onready var hud: BattleHud = %BattleHud


func _ready() -> void:
	_pacing = HudLayout.section(&"pacing")
	_damage_m = HudLayout.section(&"damage")
	_marker_m = HudLayout.section(&"actor_marker")
	menus = BattleMenus.new(int(HudLayout.section(&"commands").get("rank_swell_from", Formulas.DEFAULT_RANK)))
	_db = BattleDB.load_default()
	hud.commands.highlighted.connect(_on_menu_highlighted)
	hud.commands.chosen.connect(_on_menu_chosen)
	hud.commands.cancelled.connect(_on_menu_cancelled)
	hud.result.choice_made.connect(_on_result_choice)
	if scripted_state != &"":
		pacing_scale = 0.0
		show_damage_numbers = false
		persist_progress = false
		_run_script.call_deferred()
	elif auto_start:
		start_sandbox.call_deferred()


func _process(delta: float) -> void:
	tick(delta)


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Starts the configured sandbox fight (battle_sandbox.json) with the saved Lattice progress.
func start_sandbox(rng_seed: int = -1) -> void:
	var cfg := BattleStage.config()
	var active: Array[StringName] = _ids(cfg.get("active", []))
	var reserve: Array[StringName] = _ids(cfg.get("reserve", []))
	var s := int(cfg.get("seed", 0)) if rng_seed < 0 else rng_seed
	start_battle(active, reserve, StringName(str(cfg.get("encounter", ""))), s, _load_progress(active + reserve))


func start_battle(
	active: Array[StringName],
	reserve: Array[StringName],
	encounter: StringName,
	rng_seed: int,
	lattice: LatticeProgress = null
) -> void:
	_setup = {"active": active, "reserve": reserve, "encounter": encounter, "seed": rng_seed}
	battles_started += 1
	last_awards = {}
	_after_wait = Callable()
	progress = lattice
	engine = BattleEngine.new()
	if progress != null:
		engine.party_modifier = progress.apply_to
	engine.setup(_db, active, reserve, encounter, rng_seed)
	engine.action_resolved.connect(_on_action_resolved)
	stage.spawn(engine)
	for c in engine.party_active + engine.party_reserve + engine.enemies:
		var tint := Color.html(str(BattleStage.stand_in_spec(c.id).get("tint", "#A9B8CC")))
		hud.timeline.set_identity(c.id, menus.display_name(c), tint)
	hud.result.visible = false
	hud.set_combat_ui_visible(true)
	_rebuild_party_panel()
	engine.begin()
	_show_timeline(TurnTimeline.MODE_TURN)
	_next_turn()


## Advances paced waits by `delta` seconds (called from _process; tests call it directly).
func tick(delta: float) -> void:
	if not _after_wait.is_valid():
		return
	_wait_left -= delta
	if _wait_left <= 0.0:
		_drain()


## Routes one input event by state; returns true if consumed.
func handle_input(event: InputEvent) -> bool:
	match state:
		STATE_COMMAND, STATE_SKILLS, STATE_SWAP_IN:
			return hud.commands.handle_input(event)
		STATE_TARGET, STATE_SWAP_OUT:
			return _handle_pick_input(event)
		STATE_RESULT:
			return hud.result.handle_input(event)
	return false


# --- player actions (the only ways the player changes the battle) ------------------------


## Uses `skill_id` on `target_ids` for the current party member. Returns the engine's result.
func act(skill_id: StringName, target_ids: Array[StringName]) -> ActionResult:
	if not engine.is_party_turn():
		return ActionResult.failed(&"", skill_id, &"not_your_turn")
	var actor := engine.current
	var targets: Array[BattleCombatant] = []
	for tid in target_ids:
		var t := engine.find(tid)
		if t != null:
			targets.append(t)
	var result := engine.perform(skill_id, targets)
	_clear_targets()
	if not result.ok:
		hud.set_help(String(result.fail_reason))
		_open_command()
		return result
	if targets.size() == 1 and targets[0].team == BattleCombatant.TEAM_ENEMY:
		_last_foe = targets[0].id
	_after_action(actor.id)
	return result


## Swaps active `out_id` for reserve `in_id` at no time cost.
func swap_members(out_id: StringName, in_id: StringName) -> bool:
	if not engine.swap(out_id, in_id):
		return false
	_clear_targets()
	stage.sync_party(engine)
	_rebuild_party_panel()
	_show_timeline(TurnTimeline.MODE_PREVIEW)
	_open_command()
	return true


## Attempts to flee. A failure costs the actor a default-rank turn.
func try_escape() -> bool:
	if not engine.is_party_turn():
		return false
	var actor := engine.current.id
	if engine.escape():
		_set_state(STATE_BUSY)
		hud.commands.visible = false
		_wait(_pace(&"result_delay_sec"), _show_result)
		return true
	hud.set_help(tr("HUD_ESCAPE_FAILED"))
	_after_action(actor)
	return false


# --- queries for tests and captures ------------------------------------------------------


func current_actor_id() -> StringName:
	return engine.current.id if engine != null and engine.current != null else &""


func pending_skill() -> StringName:
	return _pending_skill


func picked_ids() -> Array[StringName]:
	if _candidates.is_empty():
		return []
	if _group_target:
		return _candidates.duplicate()
	return [_candidates[_target_index]]


func is_waiting() -> bool:
	return _after_wait.is_valid()


# --- turn flow ---------------------------------------------------------------------------


func _next_turn() -> void:
	if engine.outcome != &"":
		_set_state(STATE_BUSY)
		hud.commands.visible = false
		_wait(_pace(&"result_delay_sec"), _show_result)
		return
	hud.party.set_current(current_actor_id())
	_mark_actor()
	if engine.is_party_turn():
		_open_command()
		return
	_set_state(STATE_BUSY)
	hud.commands.visible = false
	hud.set_help("")
	_wait(_pace(&"enemy_think_sec"), _run_enemy)


func _run_enemy() -> void:
	var actor := engine.current
	var result := engine.run_enemy_turn()
	if result != null and result.ok:
		hud.set_help(
			tr("HUD_ENEMY_ACTS_FMT").format(
				{"name": menus.display_name(actor), "skill": menus.skill_name(engine, result.skill_id)}
			)
		)
	_after_action(actor.id)


func _after_action(actor_id: StringName) -> void:
	_set_state(STATE_BUSY)
	hud.commands.active = false
	hud.commands.visible = false
	hud.timeline.note_turn_taken(actor_id)
	_show_timeline(TurnTimeline.MODE_TURN)
	# The order already shows who is next; the party highlight and actor marker follow it.
	hud.party.set_current(current_actor_id())
	hud.target_cursor.show_actor(Vector2.ZERO, false)
	hud.party.refresh(pacing_scale > 0.0, _pace(&"action_hold_sec") * 0.5)
	stage.refresh_ko(engine)
	_wait(_pace(&"action_hold_sec"), _next_turn)


func _open_command() -> void:
	_set_state(STATE_COMMAND)
	_pending_skill = &""
	hud.commands.visible = true
	hud.commands.active = true
	hud.party.set_current(current_actor_id())
	hud.commands.open_root(BattleMenus.PAGE_ROOT, menus.display_name(engine.current), menus.root_rows(engine))


func _show_result() -> void:
	_set_state(STATE_RESULT)
	hud.set_combat_ui_visible(false)
	stage.clear_rings()
	var rows: Array[Dictionary] = []
	var title_key := "HUD_VICTORY"
	var sub_key := "HUD_VICTORY_SUB"
	if engine.outcome == BattleEngine.OUTCOME_VICTORY:
		rows = _award_victory()
	elif engine.outcome == BattleEngine.OUTCOME_DEFEAT:
		title_key = "HUD_DEFEAT"
		sub_key = "HUD_DEFEAT_SUB"
	else:
		title_key = "HUD_ESCAPED"
		sub_key = "HUD_ESCAPED_SUB"
	var choices: Array[Dictionary] = [
		{"id": CHOICE_RETRY, "label": tr("HUD_RESULT_RETRY"), "enabled": true},
		{"id": CHOICE_RETURN, "label": tr("HUD_RESULT_RETURN"), "enabled": true},
	]
	hud.result.show_result(engine.outcome, tr(title_key), tr(sub_key), rows, choices)


## XP from engine.xp_awards() becomes Lattice movement points (formulas.md, Progression).
func _award_victory() -> Array[Dictionary]:
	var awards := engine.xp_awards()
	var rows: Array[Dictionary] = []
	for c in engine.party_active + engine.party_reserve:
		if not c.participated:
			continue
		if not awards.has(c.id):
			rows.append(
				{"label": menus.display_name(c), "xp_text": "", "moves_text": tr("HUD_RESULT_FELL"), "fell": true}
			)
			continue
		var xp := int(awards[c.id])
		var moves := -1
		if progress != null and progress.traveler(c.id) != null:
			moves = progress.award_battle(c.id, xp)
		last_awards[c.id] = {"xp": xp, "moves": moves}
		var moves_text := tr("HUD_RESULT_MOVES_FMT").format({"n": moves}) if moves >= 0 else tr("HUD_RESULT_NO_LATTICE")
		rows.append(
			{
				"label": menus.display_name(c),
				"xp_text": tr("HUD_RESULT_XP_FMT").format({"xp": xp}),
				"moves_text": moves_text
			}
		)
	if persist_progress and progress != null:
		Game.state.lattice = progress.to_dict()
	return rows


# --- menus -------------------------------------------------------------------------------


func _on_menu_highlighted(_page: StringName, row: Dictionary) -> void:
	if engine == null or not engine.is_party_turn():
		return
	var rid := StringName(str(row.get("id", "")))
	match state:
		STATE_COMMAND:
			_highlight_root(rid)
		STATE_SKILLS:
			_preview_skill(rid, _default_targets(rid))
		STATE_SWAP_IN:
			var incoming := engine.find(rid)
			_show_timeline(TurnTimeline.MODE_PREVIEW)
			hud.set_help(menus.swap_in_help(engine, incoming) if incoming != null else "")


func _highlight_root(rid: StringName) -> void:
	match rid:
		BattleMenus.ROW_ATTACK:
			_preview_skill(BattleMenus.ATTACK_SKILL, _default_targets(BattleMenus.ATTACK_SKILL))
		BattleMenus.ROW_ESCAPE:
			# A failed attempt costs a default-rank turn: preview exactly that.
			var failed := engine.timeline.predict(CtbTimeline.PREVIEW_LENGTH - 1, engine.current, Formulas.DEFAULT_RANK)
			_show_timeline(TurnTimeline.MODE_PREVIEW, failed)
			hud.set_help(menus.escape_help(engine))
		BattleMenus.ROW_SWAP:
			_show_timeline(TurnTimeline.MODE_PREVIEW)
			hud.set_help(tr("HUD_HELP_SWAP"))
		_:
			_show_timeline(TurnTimeline.MODE_PREVIEW)
			hud.set_help(tr("HUD_HELP_SKILLS"))


func _on_menu_chosen(_page: StringName, row: Dictionary) -> void:
	var rid := StringName(str(row.get("id", "")))
	match state:
		STATE_COMMAND:
			match rid:
				BattleMenus.ROW_ATTACK:
					_begin_target(BattleMenus.ATTACK_SKILL)
				BattleMenus.ROW_SKILLS:
					_set_state(STATE_SKILLS)
					hud.commands.push(BattleMenus.PAGE_SKILLS, tr("HUD_CMD_SKILLS"), menus.skill_rows(engine))
				BattleMenus.ROW_ESCAPE:
					try_escape()
				BattleMenus.ROW_SWAP:
					_set_state(STATE_SWAP_IN)
					hud.commands.push(BattleMenus.PAGE_SWAP, tr("HUD_PAGE_RESERVE"), menus.reserve_rows(engine))
		STATE_SKILLS:
			_begin_target(StringName(str(row.get("skill", rid))))
		STATE_SWAP_IN:
			_swap_in_id = rid
			_begin_swap_out()


func _on_menu_cancelled(_page: StringName) -> void:
	if state in [STATE_SKILLS, STATE_SWAP_IN] and hud.commands.pop():
		_set_state(STATE_COMMAND)
		_highlight_root(StringName(str(hud.commands.current_row().get("id", ""))))


func _on_result_choice(choice: StringName) -> void:
	if choice == CHOICE_RETRY:
		var active: Array[StringName] = _setup.get("active", [])
		var reserve: Array[StringName] = _setup.get("reserve", [])
		var s := int(_setup.get("seed", 0)) + 1
		start_battle(active, reserve, _setup.get("encounter", &""), s, progress)
	elif choice == CHOICE_RETURN and is_inside_tree():
		SceneRouter.change_scene(RETURN_SCENE)


# --- targeting ---------------------------------------------------------------------------


func _begin_target(skill_id: StringName) -> void:
	var sk := engine.db.skill(skill_id)
	var kind := str(sk.get("target", "single_foe"))
	if kind == "self":
		act(skill_id, [engine.current.id])
		return
	_pending_skill = skill_id
	_group_target = kind.begins_with("all_")
	_candidates = _ids_of(_candidates_for(kind))
	if _candidates.is_empty():
		return
	var preferred := _default_targets(skill_id)
	_target_index = maxi(_candidates.find(preferred[0].id), 0) if not preferred.is_empty() else 0
	_set_state(STATE_TARGET)
	hud.commands.active = false
	_show_pick()


func _begin_swap_out() -> void:
	_pending_skill = &""
	_group_target = false
	_candidates = _ids_of(engine.party_active)
	_target_index = maxi(_candidates.find(engine.current.id), 0)
	_set_state(STATE_SWAP_OUT)
	hud.commands.active = false
	_show_pick()


func _handle_pick_input(event: InputEvent) -> bool:
	if event.is_action_pressed(&"ui_left", true) or event.is_action_pressed(&"ui_up", true):
		_cycle_target(-1)
	elif event.is_action_pressed(&"ui_right", true) or event.is_action_pressed(&"ui_down", true):
		_cycle_target(1)
	elif event.is_action_pressed(&"ui_accept"):
		_confirm_pick()
	elif event.is_action_pressed(&"ui_cancel"):
		_cancel_pick()
	else:
		return false
	return true


func _cycle_target(delta: int) -> void:
	if _group_target or _candidates.is_empty():
		return
	_target_index = posmod(_target_index + delta, _candidates.size())
	_show_pick()


func _confirm_pick() -> void:
	if state == STATE_SWAP_OUT:
		swap_members(_candidates[_target_index], _swap_in_id)
	else:
		act(_pending_skill, picked_ids())


func _cancel_pick() -> void:
	var was := state
	_clear_targets()
	hud.commands.active = true
	_set_state(
		STATE_SWAP_IN if was == STATE_SWAP_OUT else (STATE_SKILLS if hud.commands.depth() > 1 else STATE_COMMAND)
	)
	_on_menu_highlighted(hud.commands.page_id(), hud.commands.current_row())


func _show_pick() -> void:
	var ids := picked_ids()
	var hostile: Array[bool] = []
	var entries: Array[Dictionary] = []
	for cid in ids:
		var c := engine.find(cid)
		var foe := c.team == BattleCombatant.TEAM_ENEMY
		hostile.append(foe)
		(
			entries
			. append(
				{
					"id": cid,
					"label": menus.display_name(c),
					"group_label": menus.group_label(foe),
					"screen_pos": stage.screen_pos(cid, HudLayout.num(_marker_m, "head_offset_m")),
					"hostile": foe,
					"combatant": c,
					"revealed": false,
				}
			)
		)
	stage.set_rings(ids, hostile, _color(&"focus"), _color(&"danger"))
	hud.target_cursor.show_targets(entries)
	var ally_ids: Array[StringName] = []
	for i in ids.size():
		if not hostile[i]:
			ally_ids.append(ids[i])
	hud.party.set_targeted(ally_ids)
	if state == STATE_SWAP_OUT:
		_show_timeline(TurnTimeline.MODE_PREVIEW)
		hud.set_help(menus.swap_out_help(engine.find(_swap_in_id)))
		return
	var targets: Array[BattleCombatant] = []
	for cid in ids:
		targets.append(engine.find(cid))
	_preview_skill(_pending_skill, targets)


func _clear_targets() -> void:
	_candidates.clear()
	_target_index = 0
	stage.clear_rings()
	hud.target_cursor.clear()
	hud.party.set_targeted([])


func _candidates_for(kind: String) -> Array[BattleCombatant]:
	if kind.ends_with("foe") or kind.ends_with("foes"):
		return engine.living_foes_of(engine.current)
	return engine.living_allies_of(engine.current)


## The target a skill starts on: the last foe you hit, the most hurt ally for heals, yourself
## for other ally skills, or everyone for group skills.
func _default_targets(skill_id: StringName) -> Array[BattleCombatant]:
	var sk := engine.db.skill(skill_id)
	var kind := str(sk.get("target", "single_foe"))
	var pool := _candidates_for(kind)
	var out: Array[BattleCombatant] = []
	if kind == "self":
		out.append(engine.current)
	elif kind.begins_with("all_"):
		out = pool
	elif kind == "single_foe":
		var last := engine.find(_last_foe)
		out.append(last if last != null and last.is_alive() else pool[0])
	elif str(sk.get("kind", "")) == "heal":
		var best := pool[0]
		for c in pool:
			if c.hp * best.max_hp < best.hp * c.max_hp:
				best = c
		out.append(best)
	else:
		out.append(engine.current)
	return out


# --- presentation helpers ----------------------------------------------------------------


func _preview_skill(skill_id: StringName, targets: Array[BattleCombatant]) -> void:
	var single: BattleCombatant = targets[0] if targets.size() == 1 else null
	var preview := engine.preview(skill_id, single, CtbTimeline.PREVIEW_LENGTH - 1)
	_show_timeline(TurnTimeline.MODE_PREVIEW, preview, _ids_of(targets))
	hud.set_help(menus.skill_help(engine, skill_id, _ghost_slot() - 1))


func _show_timeline(mode: StringName, preview: Array[TurnEntry] = [], targets: Array[StringName] = []) -> void:
	if engine.outcome != &"":
		return
	var hostile := not targets.is_empty() and engine.find(targets[0]).team == BattleCombatant.TEAM_ENEMY
	var color := _color(&"danger") if hostile else _color(&"focus")
	hud.timeline.show_turns(current_actor_id(), engine.preview(), preview, targets, color, mode)


func _ghost_slot() -> int:
	for s in hud.timeline.slots:
		if bool(s["ghost"]):
			return int(s["slot"])
	return 0


func _mark_actor() -> void:
	var cid := current_actor_id()
	var shown := cid != &"" and stage.has_fighter(cid) and engine.is_party_turn()
	hud.target_cursor.show_actor(stage.screen_pos(cid, HudLayout.num(_marker_m, "head_offset_m")), shown)


func _rebuild_party_panel() -> void:
	var labels: Dictionary = {}
	for c in engine.party_active:
		labels[c.id] = menus.display_name(c)
	hud.party.show_members(engine.party_active, labels)
	hud.party.set_current(current_actor_id())


func _on_action_resolved(result: ActionResult) -> void:
	var stacks: Dictionary = {}
	for hit in result.hits:
		var tid: StringName = hit["target_id"]
		var target := engine.find(tid)
		var f := stage.stand_in(tid)
		# ActionResult.amount: positive = HP lost, negative = HP restored (BattleEngine._resolve_on).
		if f != null and int(hit["amount"]) > 0:
			f.flinch()
		if not show_damage_numbers or target == null:
			continue
		var n := int(stacks.get(tid, 0))
		stacks[tid] = n + 1
		var at := stage.screen_pos(tid, HudLayout.num(_damage_m, "head_offset_m"))
		var ally := target.team == BattleCombatant.TEAM_PARTY
		var amount := int(hit["amount"])
		if not bool(hit["hit"]):
			hud.pop_number(tr("HUD_MISS"), at, DamageNumber.KIND_MISS, ally, false, n)
		elif amount > 0:
			hud.pop_number(str(amount), at, DamageNumber.KIND_DAMAGE, ally, bool(hit["crit"]), n)
		elif amount < 0:
			hud.pop_number(str(-amount), at, DamageNumber.KIND_HEAL, ally, false, n)


func _wait(sec: float, then: Callable) -> void:
	_wait_left = sec
	_after_wait = then
	if _wait_left <= 0.0 and not _draining:
		_drain()


func _drain() -> void:
	_draining = true
	while _after_wait.is_valid() and _wait_left <= 0.0:
		var cb := _after_wait
		_after_wait = Callable()
		cb.call()
	_draining = false


func _pace(key: StringName) -> float:
	return HudLayout.num(_pacing, String(key)) * pacing_scale


func _set_state(s: StringName) -> void:
	if s == state:
		return
	state = s
	state_changed.emit(s)


func _color(role: StringName) -> Color:
	return hud.get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _load_progress(ids: Array[StringName]) -> LatticeProgress:
	var cfg := BattleStage.config()
	var board := LatticeBoard.load_board(StringName(str(cfg.get("board", LatticeBoard.DEFAULT_BOARD))))
	var rules := LatticeRules.load_file()
	var p: LatticeProgress
	if persist_progress and not Game.state.lattice.is_empty():
		p = LatticeProgress.from_dict(Game.state.lattice, board, rules)
	else:
		p = LatticeProgress.new(board, rules)
	for cid in ids:
		p.add_character(cid)
	return p


static func _ids(raw: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	for v: Variant in raw as Array:
		out.append(StringName(str(v)))
	return out


static func _ids_of(list: Array[BattleCombatant]) -> Array[StringName]:
	var out: Array[StringName] = []
	for c in list:
		out.append(c.id)
	return out


# --- capture scripts (deterministic; see tests/screenshots/shots.json) ---------------------


func _run_script() -> void:
	start_sandbox()
	match scripted_state:
		SCRIPT_PLAYER_PREVIEW:
			_script_to_turn_of(&"rhen")
			_press(&"ui_down")
			_press(&"ui_accept")
			hud.commands.select(&"undertow_cut")
			_press(&"ui_accept")
			_script_pick(&"gull_harrier")
		SCRIPT_SWAP_MENU:
			_script_to_turn_of(&"rhen")
			hud.commands.select(BattleMenus.ROW_SWAP)
			_press(&"ui_accept")
		SCRIPT_VICTORY:
			_script_play_to_victory()


## Plays (party: Attack the first living foe) until it is `cid`'s turn.
func _script_to_turn_of(cid: StringName) -> void:
	var guard := 0
	while engine.outcome == &"" and current_actor_id() != cid and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		if engine.is_party_turn():
			act(BattleMenus.ATTACK_SKILL, [engine.living_foes_of(engine.current)[0].id])


## The sandbox's "elegant answer" policy: bring Toma in for Asha, then hit the weakest foe.
func _script_play_to_victory() -> void:
	var guard := 0
	while engine.outcome == &"" and guard < CtbTimeline.PREVIEW_LENGTH * CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		if not engine.is_party_turn():
			break
		if engine.find(&"asha") in engine.party_active and engine.find(&"toma") in engine.party_reserve:
			swap_members(&"asha", &"toma")
			continue
		var weakest := engine.living_foes_of(engine.current)[0]
		for f in engine.living_foes_of(engine.current):
			if f.hp < weakest.hp:
				weakest = f
		act(BattleMenus.ATTACK_SKILL, [weakest.id])


func _script_pick(base_id: StringName) -> void:
	for i in _candidates.size():
		if String(_candidates[i]).get_slice("#", 0) == String(base_id):
			_target_index = i
			_show_pick()
			return


func _press(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	handle_input(ev)
