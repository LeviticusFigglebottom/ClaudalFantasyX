class_name BattleController
extends Node3D
## Glue for the battle sandbox (M1-CMB-01, M1-UI-02): drives a headless BattleEngine from player
## input, runs enemy and automatic (Berserk/Confuse) turns with short readable pauses, and feeds
## the HUD and the 3D stage. It only calls the engine's public API (setup/begin/preview/
## preview_swap/forced_target/reflect_recipient/perform/swap/escape/run_enemy_turn/xp_awards) and
## listens to its signals; it never writes combatant state itself.
##
## Player intent funnels into three public actions (act, swap_members, try_escape) that menus,
## tests and capture scripts all use. Time passes only through tick(), so tests can fast-forward.
## Capture states start from BattleFixture data (battle_fixtures.json), never from the live
## balance tables, so rebalancing never moves a screenshot baseline.

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
const SCRIPT_DEFEAT := &"defeat"
const SCRIPT_STATUSES := &"statuses"
const CHOICE_RETRY := &"retry"
const CHOICE_RETURN := &"return"
const RETURN_SCENE := "res://game/core/boot.tscn"

## Capture entry point: on _ready, play deterministically to a fixed state (shots.json).
@export var scripted_state: StringName = &""
## Start the sandbox encounter on _ready (tests turn this off and call start_battle).
@export var auto_start := true
## 1.0 = readable pacing; 0.0 = instant (tests and captures).
@export var pacing_scale := 1.0
## Spawn damage numbers, float text and camera shake (off for captures: nothing mid-flight).
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
## The fixture the current battle started from (null for live data).
var fixture: BattleFixture
## True while a staged build (start_battle_staged) is still spreading its steps over frames.
var building := false
## How a staged build waits between frames. Unset = the next process frame; tests set a callable
## that records the boundary and returns at once, so the whole build runs synchronously.
var frame_wait := Callable()

var _db: BattleDB
var _live_db: BattleDB
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
## The acting fighter as the action resolved: {id, hp, zombie, regen, doom} (end-of-turn feedback).
var _turn_snapshot: Dictionary = {}

@onready var stage: BattleStage = %Stage
@onready var hud: BattleHud = %BattleHud


func _ready() -> void:
	_pacing = HudLayout.section(&"pacing")
	_damage_m = HudLayout.section(&"damage")
	_marker_m = HudLayout.section(&"actor_marker")
	menus = BattleMenus.new(int(HudLayout.section(&"commands").get("rank_swell_from", Formulas.DEFAULT_RANK)))
	_live_db = BattleDB.load_default()
	_db = _live_db
	hud.commands.highlighted.connect(_on_menu_highlighted)
	hud.commands.chosen.connect(_on_menu_chosen)
	hud.commands.cancelled.connect(_on_menu_cancelled)
	hud.result.choice_made.connect(_on_result_choice)
	if scripted_state != &"":
		pacing_scale = 0.0
		show_damage_numbers = false
		persist_progress = false
		# Captures always render at the default accessibility settings, whatever the host saved.
		hud.apply_settings(UiSettings.new())
		run_script.call_deferred()
	elif auto_start:
		# Entered through SceneRouter: build over several frames behind its fade (M1-UI-03).
		start_sandbox.call_deferred(-1, true)


func _process(delta: float) -> void:
	tick(delta)


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Starts the configured sandbox fight (battle_sandbox.json) with the saved Lattice progress.
## `staged` spreads the build over frames (start_battle_staged); await it to know when it is done.
func start_sandbox(rng_seed: int = -1, staged: bool = false) -> void:
	fixture = null
	_db = _live_db
	var cfg := BattleStage.config()
	var active: Array[StringName] = _ids(cfg.get("active", []))
	var reserve: Array[StringName] = _ids(cfg.get("reserve", []))
	var s := int(cfg.get("seed", 0)) if rng_seed < 0 else rng_seed
	var encounter := StringName(str(cfg.get("encounter", "")))
	if not staged:
		start_battle(active, reserve, encounter, s, _load_progress(active + reserve))
		return
	building = true
	var lattice := _load_progress(active + reserve)
	await _wait_frame()
	await start_battle_staged(active, reserve, encounter, s, lattice)


## Starts a capture/test fixture (BattleFixture): frozen tables, opening statuses, a fresh
## (never persisted) Lattice progress.
func start_fixture(fx: BattleFixture) -> void:
	fixture = fx
	_db = fx.db
	start_battle(fx.active, fx.reserve, fx.encounter, fx.rng_seed, _fresh_progress(fx.active + fx.reserve))


## Builds and starts a battle in one call (tests, captures, retry).
func start_battle(
	active: Array[StringName],
	reserve: Array[StringName],
	encounter: StringName,
	rng_seed: int,
	lattice: LatticeProgress = null
) -> void:
	_build_engine(active, reserve, encounter, rng_seed, lattice)
	_build_hud()
	_begin_battle()
	_next_turn()


## The same build as start_battle, one step per frame, so no single frame carries all of it
## (SPEC §4.2 swap budget; the router keeps its fade up meanwhile). `building` is true until the
## first turn is open; input is ignored until then (state stays idle).
func start_battle_staged(
	active: Array[StringName],
	reserve: Array[StringName],
	encounter: StringName,
	rng_seed: int,
	lattice: LatticeProgress = null
) -> void:
	building = true
	# The 16 timeline chips are the heaviest part: build them hidden, half in each light frame.
	var half := CtbTimeline.PREVIEW_LENGTH / 2
	var frames: Array = [
		[_build_engine.bind(active, reserve, encounter, rng_seed, lattice), hud.timeline.prebuild.bind(half)],
		[_build_hud, hud.timeline.prebuild.bind(CtbTimeline.PREVIEW_LENGTH - half)],
		[_begin_battle],
		[_next_turn],
	]
	for i in frames.size():
		if i > 0:
			await _wait_frame()
		for step: Callable in frames[i]:
			step.call()
	building = false


## Step 1: the engine, fixture opening state and the 3D stand-ins.
func _build_engine(
	active: Array[StringName],
	reserve: Array[StringName],
	encounter: StringName,
	rng_seed: int,
	lattice: LatticeProgress
) -> void:
	_setup = {"active": active, "reserve": reserve, "encounter": encounter, "seed": rng_seed}
	battles_started += 1
	last_awards = {}
	_after_wait = Callable()
	_turn_snapshot = {}
	progress = lattice
	engine = BattleEngine.new()
	if progress != null:
		engine.party_modifier = progress.apply_to
	engine.setup(_db, active, reserve, encounter, rng_seed)
	if fixture != null:
		fixture.prepare(engine)
	engine.action_resolved.connect(_on_action_resolved)
	stage.spawn(engine)
	stage.refresh_ko(engine)


## Step 2: timeline identities and the party panel.
func _build_hud() -> void:
	for c in engine.party_active + engine.party_reserve + engine.enemies:
		hud.timeline.set_identity(c.id, menus.display_name(c), _tint(c.id))
	hud.result.visible = false
	hud.set_combat_ui_visible(true)
	_rebuild_party_panel()


## Step 3: the first turn order and its 16 timeline chips.
func _begin_battle() -> void:
	engine.begin()
	_show_timeline(TurnTimeline.MODE_TURN)


func _wait_frame() -> void:
	if frame_wait.is_valid():
		await frame_wait.call()
	elif is_inside_tree():
		await get_tree().process_frame


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
## A refused action costs nothing; the help line says why, in words (never the raw reason id).
func act(skill_id: StringName, target_ids: Array[StringName]) -> ActionResult:
	if not engine.is_party_turn():
		var refused := ActionResult.failed(current_actor_id(), skill_id, &"not_your_turn")
		if engine.is_auto_turn():
			refused.fail_reason = &"auto_turn"
		hud.set_help(menus.fail_text(refused.fail_reason, engine.current))
		return refused
	var actor := engine.current
	var targets: Array[BattleCombatant] = []
	for tid in target_ids:
		var t := engine.find(tid)
		if t != null:
			targets.append(t)
	var result := engine.perform(skill_id, targets)
	_clear_targets()
	if not result.ok:
		_open_command()
		hud.set_help(menus.fail_text(result.fail_reason, actor, engine.forced_target(actor, skill_id)))
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
	stage.refresh_ko(engine)
	hud.timeline.set_identity(in_id, menus.display_name(engine.find(in_id)), _tint(in_id))
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


## The ids the cursor may move between (one id when Provoke locks it).
func candidate_ids() -> Array[StringName]:
	return _candidates.duplicate()


func is_waiting() -> bool:
	return _after_wait.is_valid()


# --- turn flow ---------------------------------------------------------------------------


func _next_turn() -> void:
	if engine.outcome != &"":
		_set_state(STATE_BUSY)
		hud.commands.visible = false
		_wait(_pace(&"result_delay_sec"), _show_result)
		return
	var auto := _auto_reason()
	hud.party.set_current(current_actor_id(), auto)
	_mark_actor()
	if engine.is_party_turn():
		_open_command()
		return
	_set_state(STATE_BUSY)
	hud.commands.visible = false
	if auto != &"":
		# Pillar 4: say why the player has no menu, and give them time to read it.
		hud.set_help(menus.auto_announce(engine.current, auto))
		_wait(_pace(&"auto_announce_sec"), _run_enemy)
		return
	hud.set_help("")
	_wait(_pace(&"enemy_think_sec"), _run_enemy)


## Plays the current enemy turn, or the current automatic (Berserk/Confuse) turn on either side.
func _run_enemy() -> void:
	var actor := engine.current
	var auto := _auto_reason()
	var result := engine.run_enemy_turn()
	if auto != &"":
		hud.set_help(menus.auto_result(engine, actor, result, auto))
	elif result != null and result.ok:
		hud.set_help(
			tr("HUD_ENEMY_ACTS_FMT").format(
				{"name": menus.display_name(actor), "skill": menus.skill_name(engine, result.skill_id)}
			)
		)
	var hold := &"auto_hold_sec" if auto != &"" and actor.team == BattleCombatant.TEAM_PARTY else &"action_hold_sec"
	_after_action(actor.id, hold)


func _after_action(actor_id: StringName, hold: StringName = &"action_hold_sec") -> void:
	_set_state(STATE_BUSY)
	hud.commands.active = false
	hud.commands.visible = false
	_show_end_of_turn(actor_id)
	hud.timeline.note_turn_taken(actor_id)
	_show_timeline(TurnTimeline.MODE_TURN)
	# The order already shows who is next; the party highlight and actor marker follow it.
	hud.party.set_current(current_actor_id(), _auto_reason())
	hud.target_cursor.show_actor(Vector2.ZERO, false)
	hud.target_cursor.show_provoker(Vector2.ZERO, false)
	hud.party.refresh(pacing_scale > 0.0, _pace(&"action_hold_sec") * 0.5)
	stage.refresh_ko(engine)
	_wait(_pace(hold), _next_turn)


func _open_command() -> void:
	_set_state(STATE_COMMAND)
	_pending_skill = &""
	hud.commands.visible = true
	hud.commands.active = true
	hud.party.set_current(current_actor_id())
	_mark_provoker()
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
	if persist_progress and progress != null and fixture == null:
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
			# Hovering a reserve member previews them taking the acting fighter's place.
			var incoming := engine.find(rid)
			_show_swap_preview(current_actor_id(), rid)
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
	_candidates = _ids_of(_candidates_for(skill_id))
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
	_mark_provoker()
	_on_menu_highlighted(hud.commands.page_id(), hud.commands.current_row())


func _show_pick() -> void:
	var ids := picked_ids()
	var hostile: Array[bool] = []
	var entries: Array[Dictionary] = []
	var sk := engine.db.skill(_pending_skill) if state == STATE_TARGET else {}
	var forced := engine.forced_target(engine.current, _pending_skill) if state == STATE_TARGET else null
	var chosen: Array[BattleCombatant] = []
	for cid in ids:
		var c := engine.find(cid)
		var foe := c.team == BattleCombatant.TEAM_ENEMY
		hostile.append(foe)
		var entry := {
			"id": cid,
			"label": menus.display_name(c),
			"group_label": menus.group_label(foe),
			"screen_pos": _head(cid),
			"hostile": foe,
			"combatant": c,
			"revealed": false,
			"forced": forced != null and forced == c,
		}
		var land := engine.reflect_recipient(engine.current, c, sk) if ids.size() == 1 else c
		if land != c and land != null:
			entry["bounce_pos"] = _head(land.id)
			entry["bounce_id"] = land.id
		chosen.append(c)
		entries.append(entry)
	stage.set_rings(ids, hostile, _color(&"focus"), _color(&"danger"))
	hud.target_cursor.show_targets(entries)
	var ally_ids: Array[StringName] = []
	for i in ids.size():
		if not hostile[i]:
			ally_ids.append(ids[i])
	hud.party.set_targeted(ally_ids)
	if state == STATE_SWAP_OUT:
		_show_swap_preview(_candidates[_target_index], _swap_in_id)
		hud.set_help(menus.swap_out_help(engine.find(_swap_in_id)))
		return
	_preview_skill(_pending_skill, chosen)


func _clear_targets() -> void:
	_candidates.clear()
	_target_index = 0
	stage.clear_rings()
	hud.target_cursor.clear()
	hud.party.set_targeted([])


## Who the cursor may pick for `skill_id`: the provoker alone while Provoke forces it, otherwise
## every living foe or ally the skill's reach allows.
func _candidates_for(skill_id: StringName) -> Array[BattleCombatant]:
	var kind := str(engine.db.skill(skill_id).get("target", "single_foe"))
	var forced := engine.forced_target(engine.current, skill_id)
	if forced != null:
		var only: Array[BattleCombatant] = [forced]
		return only
	if kind.ends_with("foe") or kind.ends_with("foes"):
		return engine.living_foes_of(engine.current)
	return engine.living_allies_of(engine.current)


## The target a skill starts on: the provoker when Provoked, the last foe you hit, the most hurt
## ally for heals, yourself for other ally skills, or everyone for group skills.
func _default_targets(skill_id: StringName) -> Array[BattleCombatant]:
	var sk := engine.db.skill(skill_id)
	var kind := str(sk.get("target", "single_foe"))
	var pool := _candidates_for(skill_id)
	var out: Array[BattleCombatant] = []
	if pool.is_empty() and kind != "self":
		return out
	if kind == "self":
		out.append(engine.current)
	elif kind.begins_with("all_"):
		out = pool
	elif kind == "single_foe":
		var last := engine.find(_last_foe)
		out.append(last if last != null and last.is_alive() and pool.has(last) else pool[0])
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


## Previews `skill_id` on the chosen `targets`. A spell that Reflect would bounce is marked on
## the timeline where it really lands (engine.preview() already simulates the bounce).
func _preview_skill(skill_id: StringName, targets: Array[BattleCombatant]) -> void:
	var chosen: BattleCombatant = targets[0] if targets.size() == 1 else null
	var lands := engine.reflect_recipient(engine.current, chosen, engine.db.skill(skill_id))
	var preview := engine.preview(skill_id, chosen, CtbTimeline.PREVIEW_LENGTH - 1)
	var marked: Array[BattleCombatant] = targets
	if lands != chosen:
		marked = [lands]
	_show_timeline(TurnTimeline.MODE_PREVIEW, preview, _ids_of(marked))
	# What changes the outcome (Provoke, Reflect, Zombie) reads before the generic description.
	var parts := menus.target_notes(engine, skill_id, chosen, lands)
	parts.append(menus.skill_help(engine, skill_id, _ghost_slot() - 1))
	hud.set_help(" · ".join(parts))


## Shows the order exactly as it will stand after swapping `out_id` for `in_id`.
func _show_swap_preview(out_id: StringName, in_id: StringName) -> void:
	var after := engine.preview_swap(out_id, in_id)
	if after.is_empty():
		_show_timeline(TurnTimeline.MODE_PREVIEW)
		return
	var who: Array[StringName] = [out_id, in_id]
	_show_timeline(TurnTimeline.MODE_PREVIEW, after, who, true)


func _show_timeline(
	mode: StringName, preview: Array[TurnEntry] = [], targets: Array[StringName] = [], full: bool = false
) -> void:
	if engine.outcome != &"":
		return
	var marks := targets.duplicate() if not full else ([] as Array[StringName])
	var hostile := not marks.is_empty() and engine.find(marks[0]).team == BattleCombatant.TEAM_ENEMY
	var color := _color(&"danger") if hostile else _color(&"focus")
	hud.timeline.caption = menus.turn_caption(_auto_reason())
	hud.timeline.show_turns(current_actor_id(), engine.preview(), preview, marks, color, mode, full)


func _ghost_slot() -> int:
	for s in hud.timeline.slots:
		if bool(s["ghost"]):
			return int(s["slot"])
	return 0


func _mark_actor() -> void:
	var cid := current_actor_id()
	var shown := cid != &"" and stage.has_fighter(cid) and engine.is_player_side_turn()
	hud.target_cursor.show_actor(_head(cid), shown, _auto_reason())
	_mark_provoker()


## The Provoke hook hangs over the provoker while the acting party member is Provoked.
func _mark_provoker() -> void:
	var provoker: BattleCombatant = null
	if engine.is_party_turn():
		provoker = engine.forced_target(engine.current, BattleMenus.ATTACK_SKILL)
	var shown := provoker != null and stage.has_fighter(provoker.id)
	hud.target_cursor.show_provoker(_head(provoker.id) if shown else Vector2.ZERO, shown)


func _auto_reason() -> StringName:
	return BattleEngine.auto_reason(engine.current) if engine != null and engine.is_auto_turn() else &""


func _rebuild_party_panel() -> void:
	var labels: Dictionary = {}
	var tints: Dictionary = {}
	for c in engine.party_active:
		labels[c.id] = menus.display_name(c)
		tints[c.id] = _tint(c.id)
	hud.party.show_members(engine.party_active, labels, tints)
	hud.party.set_current(current_actor_id(), _auto_reason())


func _on_action_resolved(result: ActionResult) -> void:
	var actor := engine.find(result.actor_id)
	if actor != null:
		_turn_snapshot = {
			"id": actor.id,
			"hp": actor.hp,
			"zombie": actor.has_status(&"zombie"),
			"regen": actor.has_status(&"regen"),
			"doom": actor.doom_count(),
		}
	var kind := str(engine.db.skill(result.skill_id).get("kind", ""))
	var stacks: Dictionary = {}
	var heavy := false
	for hit in result.hits:
		var tid: StringName = hit["target_id"]
		var target := engine.find(tid)
		var f := stage.stand_in(tid)
		# ActionResult.amount: positive = HP lost, negative = HP restored (BattleEngine._resolve_on).
		var amount := int(hit["amount"])
		if f != null and amount > 0:
			f.flinch()
		heavy = heavy or bool(hit.get("crit", false))
		if not show_damage_numbers or target == null:
			continue
		var n := int(stacks.get(tid, 0))
		stacks[tid] = n + 1
		var at := _head(tid, &"damage")
		var ally := target.team == BattleCombatant.TEAM_PARTY
		if hit.has("reflected_from"):
			var from := StringName(str(hit["reflected_from"]))
			hud.pop_info(tr("HUD_FLOAT_REFLECTED"), _head(from, &"damage"), &"focus_gold")
		if not bool(hit["hit"]):
			hud.pop_number(tr("HUD_MISS"), at, DamageNumber.KIND_MISS, ally, false, n)
		elif amount > 0:
			hud.pop_number(str(amount), at, DamageNumber.KIND_DAMAGE, ally, bool(hit["crit"]), n)
			if kind == "heal":
				# Zombie: the heal landed as harm.
				hud.pop_info(tr("HUD_FLOAT_INVERTED"), at, &"danger")
		elif amount < 0:
			hud.pop_number(str(-amount), at, DamageNumber.KIND_HEAL, ally, false, n)
	if heavy and show_damage_numbers and hud.animations_enabled():
		stage.shake()


## End-of-turn HP changes the ActionResult cannot carry (Poison, Regen, Regen turned to harm by
## Zombie, and Doom running out), shown on the fighter who just acted.
func _show_end_of_turn(actor_id: StringName) -> void:
	var snap := _turn_snapshot
	_turn_snapshot = {}
	if not show_damage_numbers or snap.is_empty() or StringName(str(snap["id"])) != actor_id:
		return
	var c := engine.find(actor_id)
	if c == null or not stage.has_fighter(actor_id):
		return
	var at := _head(actor_id, &"damage")
	var ally := c.team == BattleCombatant.TEAM_PARTY
	if int(snap["doom"]) == 1 and c.hp <= 0:
		hud.pop_info(tr("HUD_FLOAT_DOOM"), at, &"danger")
		return
	var delta := c.hp - int(snap["hp"])
	if delta < 0:
		hud.pop_number(str(-delta), at, DamageNumber.KIND_DAMAGE, ally, false)
		if bool(snap["zombie"]) and bool(snap["regen"]):
			hud.pop_info(tr("HUD_FLOAT_REGEN_INVERTED"), at, &"danger")
	elif delta > 0:
		hud.pop_number(str(delta), at, DamageNumber.KIND_HEAL, ally, false)


func _head(cid: StringName, section: StringName = &"actor_marker") -> Vector2:
	var m := _damage_m if section == &"damage" else _marker_m
	return stage.screen_pos(cid, HudLayout.num(m, "head_offset_m"))


func _tint(cid: StringName) -> Color:
	return Color.html(str(BattleStage.stand_in_spec(cid).get("tint", "#A9B8CC")))


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
	if not persist_progress or Game.state.lattice.is_empty():
		return _fresh_progress(ids)
	var cfg := BattleStage.config()
	var board := LatticeBoard.load_board(StringName(str(cfg.get("board", LatticeBoard.DEFAULT_BOARD))))
	var p := LatticeProgress.from_dict(Game.state.lattice, board, LatticeRules.load_file())
	for cid in ids:
		p.add_character(cid)
	return p


func _fresh_progress(ids: Array[StringName]) -> LatticeProgress:
	var cfg := BattleStage.config()
	var board := LatticeBoard.load_board(StringName(str(cfg.get("board", LatticeBoard.DEFAULT_BOARD))))
	var p := LatticeProgress.new(board, LatticeRules.load_file())
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


## Plays the `scripted_state` fixture to its capture state. Public so tests can drive it.
func run_script(state_id: StringName = &"") -> void:
	var sid := state_id if state_id != &"" else scripted_state
	var fx := BattleFixture.load_fixture(sid)
	if fx == null:
		return
	start_fixture(fx)
	match sid:
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
		SCRIPT_DEFEAT:
			_script_play_naive()
		SCRIPT_STATUSES:
			# Ysolde is provoked by the reflecting Lantern Eel: Ember must go at it and bounces
			# onto Rhen (Doom, Zombie, Regen turned to harm); Asha stands as stone.
			_script_to_turn_of(&"ysolde")
			_press(&"ui_down")
			_press(&"ui_accept")
			hud.commands.select(&"ember")
			_press(&"ui_accept")


## Plays (party: Attack the first living foe) until it is `cid`'s turn.
func _script_to_turn_of(cid: StringName) -> void:
	var guard := 0
	while engine.outcome == &"" and current_actor_id() != cid and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		if engine.is_party_turn():
			act(BattleMenus.ATTACK_SKILL, [_default_targets(BattleMenus.ATTACK_SKILL)[0].id])


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


## Attack the first living foe until the fight ends.
func _script_play_naive() -> void:
	var guard := 0
	while engine.outcome == &"" and guard < CtbTimeline.PREVIEW_LENGTH * CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		if not engine.is_party_turn():
			break
		act(BattleMenus.ATTACK_SKILL, [engine.living_foes_of(engine.current)[0].id])


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
