class_name BattleController
extends Node3D
## Glue for the battle sandbox (M1-CMB-01, M1-UI-02): drives a headless BattleEngine from player
## input, runs enemy and automatic (Berserk/Confuse) turns with short readable pauses, and feeds
## the HUD and the 3D stage. It only calls the engine's public API (setup/begin/preview/
## preview_swap/forced_target/reflect_recipient/perform/swap/escape/run_enemy_turn/xp_awards,
## use_item/preview_item/item_defeats_party) and listens to its signals; it never writes
## combatant state itself. Live battles carry party HP/MP in and out (BattleVitals, M1-CMB-08).
##
## Player intent funnels into four public actions (act, use_item_on, swap_members, try_escape) that menus,
## tests and capture scripts all use. Time passes only through tick(), so tests can fast-forward.
## Capture states start from BattleFixture data (battle_fixtures.json), never from the live
## balance tables, so rebalancing never moves a screenshot baseline.

signal state_changed(new_state: StringName)

const STATE_IDLE := &"idle"
const STATE_COMMAND := &"command"
const STATE_SKILLS := &"skills"
const STATE_ITEMS := &"items"
const STATE_TARGET := &"target"
const STATE_SWAP_IN := &"swap_in"
const STATE_SWAP_OUT := &"swap_out"
const STATE_SWELL := &"swell"
const STATE_SWELL_INPUT := &"swell_input"
const STATE_BUSY := &"busy"
const STATE_RESULT := &"result"
const SCRIPT_PLAYER_PREVIEW := &"player_preview"
const SCRIPT_SWAP_MENU := &"swap_menu"
const SCRIPT_VICTORY := &"victory"
const SCRIPT_DEFEAT := &"defeat"
const SCRIPT_STATUSES := &"statuses"
const SCRIPT_SWELL_RING := &"swell_ring"
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
## Last victory's lume and drops, paid into Game.state when live (BattleRewards.pay, M2-CMB-07).
var last_spoils: Dictionary = {}
var battles_started := 0
## The fixture the current battle started from (null for live data).
var fixture: BattleFixture
## True while a staged build (start_battle_staged) is still spreading its steps over frames.
var building := false
## The bag the Items command draws from. null = no Items command (capture fixtures, so their
## baselines keep the four-row root). start_sandbox() wraps the party's real inventory.
var items: BattleItemSource
## How a staged build waits between frames. Unset = the next process frame; tests set a callable
## that records the boundary and returns at once, so the whole build runs synchronously.
var frame_wait := Callable()
## Damage numbers and float words for resolved actions (BattleFloats).
var floats := BattleFloats.new(self)
## Read, the bestiary log and the opening (M1-CMB-03; BattleBestiary).
var bestiary := BattleBestiary.new(self)
## Swell gauges and techniques for the current battle (M1-CMB-04).
var swell: BattleSwell
## False freezes an open Swell input where it stands (capture scripts); tick() advances it.
var swell_input_live := true
## Boss mechanics on the stage and HUD (phases, spawns, the toll, the field; M2-FP-06).
var boss: BattleBossHud
## A set piece's entries, objective meter and withdrawals (M3-UI-100).
var set_piece: BattleSetPieceHud
## The Vowbound's call, menu, stage and panel (M2-UI-05; BattleVowboundHud).
var vow: BattleVowboundHud

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
var _pending_item: StringName = &""
var _group_target := false
var _candidates: Array[StringName] = []
var _target_index := 0
var _swap_in_id: StringName = &""
var _last_foe: StringName = &""
var _ring: SwellInput
var _ring_clock: SwellRingClock

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
		# Captures render at the default accessibility settings (or their fixture's), never the host's.
		hud.apply_settings(BattleFixture.capture_settings(scripted_state))
		run_script.call_deferred()
	elif auto_start:
		# Entered through SceneRouter: build over several frames behind its fade (M1-UI-03).
		start_sandbox.call_deferred(-1, true)


func _process(delta: float) -> void:
	tick(delta, true)


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Starts the configured sandbox fight (battle_sandbox.json) with the saved Lattice progress.
## `staged` spreads the build over frames (start_battle_staged); await it to know when it is done.
func start_sandbox(rng_seed: int = -1, staged: bool = false) -> void:
	fixture = null
	_db = _live_db
	var cfg := BattleStage.config()
	var active: Array[StringName] = BattleIds.from(cfg.get("active", []))
	var reserve: Array[StringName] = BattleIds.from(cfg.get("reserve", []))
	var s := int(cfg.get("seed", 0)) if rng_seed < 0 else rng_seed
	var encounter := StringName(str(cfg.get("encounter", "")))
	items = _live_items()
	if not staged:
		start_battle(
			active,
			reserve,
			encounter,
			s,
			BattleStage.lattice_for(active + reserve, Game.state.lattice if persist_progress else {})
		)
		return
	building = true
	var lattice := BattleStage.lattice_for(active + reserve, Game.state.lattice if persist_progress else {})
	await _wait_frame()
	await start_battle_staged(active, reserve, encounter, s, lattice)


## Starts a capture/test fixture (BattleFixture): frozen tables, opening statuses, a fresh
## (never persisted) Lattice progress.
func start_fixture(fx: BattleFixture) -> void:
	fixture = fx
	_db = fx.db
	start_battle(fx.active, fx.reserve, fx.encounter, fx.rng_seed, BattleStage.lattice_for(fx.active + fx.reserve))


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
	last_spoils = {}
	_after_wait = Callable()
	floats.reset()
	progress = lattice
	engine = BattleEngine.new()
	if persist_progress and fixture == null:  # flag-locked skills (requires_flag) follow the live story
		engine.story_flags = BattleBossHud.live_flags(_db)
	# Live battles start from the carried HP/MP and line up past the fallen (BattleVitals).
	BattleVitals.setup(engine, _db, _setup, progress, persist_progress and fixture == null)
	if fixture != null:
		fixture.prepare(engine)
	vow = BattleVowboundHud.attached(self, engine)  # engine.vowbound from the story or the fixture
	swell = BattleSwell.new(BattleSwell.load_config())
	BattleSwellCarry.attach(swell, engine, persist_progress and fixture == null)  # M2-ARC-01
	swell.mode_unlocked.connect(SwellModeRows.announce.bind(self))  # "Tether unlocked" (M2-UI-03)
	bestiary.attach(engine, persist_progress and fixture == null)
	BattleChoreo.attached(self, engine)  # M2-BPR-01: listen-only choreography; it lands the floats
	boss = BattleBossHud.attached(self, engine)
	set_piece = BattleSetPieceHud.attached(self, engine)
	BattleBarks.attached(self, engine)  # M3-C08-100: listen-only battle barks (skills/vowbound bark keys)
	BattleVfx.attached(self, engine)  # M2-RND-03: listen-only battle VFX (docs/kb/tech/battle_vfx.md)
	stage.spawn(engine)
	stage.refresh_ko(engine)


## Step 2: timeline identities and the party panel.
func _build_hud() -> void:
	for c in engine.party_active + engine.party_reserve + engine.enemies:  # entries: BattleSetPieceHud (M3-UI-100)
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


## Advances paced waits by `delta` seconds (called from _process; tests call it directly). A
## rendered `frame` moves an open Swell input by at most its max_step_sec (SwellRingClock).
func tick(delta: float, frame: bool = false) -> void:
	if state == STATE_SWELL_INPUT and swell_input_live:
		_ring_clock.step(delta, frame)  # input timing is real time: never scaled by pacing
		_after_ring()
	if not _after_wait.is_valid() or hud.holds_battle():  # the open Read panel holds every wait (M2-UI-02)
		return
	_wait_left -= delta
	if _wait_left <= 0.0:
		_drain()


## Routes one input event by state; returns true if consumed.
func handle_input(event: InputEvent) -> bool:
	match state:
		STATE_COMMAND, STATE_SKILLS, STATE_ITEMS, STATE_SWAP_IN, STATE_SWELL:
			return hud.commands.handle_input(event)
		STATE_TARGET, STATE_SWAP_OUT:
			return _handle_pick_input(event)
		STATE_SWELL_INPUT:
			return _handle_ring_input(event)
		STATE_RESULT:
			return hud.result.handle_input(event)
	return false


# --- player actions (the only ways the player changes the battle) ------------------------


## Uses `skill_id` on `target_ids` for the current party member. Returns the engine's result.
## A refused action costs nothing; the help line says why, in words (never the raw reason id).
func act(skill_id: StringName, target_ids: Array[StringName]) -> ActionResult:
	if not engine.is_party_turn():
		return _refuse_off_turn(skill_id)
	var actor := engine.current
	var targets := _found(target_ids)
	var result := vow.perform(skill_id, targets)  # engine.perform, or a Vowbound's finisher
	_clear_targets()
	if not result.ok:
		_open_command()
		hud.set_help(menus.fail_text(result.fail_reason, actor, engine.forced_target(actor, skill_id)))
		return result
	if targets.size() == 1 and targets[0].team == BattleCombatant.TEAM_ENEMY:
		_last_foe = targets[0].id
	after_action(actor.id)
	return result


## Uses one `item_id` from `items` on `target_ids` for the current party member (formulas.md
## § Items). A refused use costs nothing, as for act().
func use_item_on(item_id: StringName, target_ids: Array[StringName]) -> ActionResult:
	if not engine.is_party_turn():
		var off := _refuse_off_turn(&"")
		off.item_id = item_id
		return off
	var actor := engine.current
	var targets := _found(target_ids)
	var result := engine.use_item(item_id, targets, items)
	_clear_targets()
	if not result.ok:
		_open_command()
		hud.set_help(menus.fail_text(result.fail_reason, actor))
		return result
	if targets.size() == 1 and targets[0].team == BattleCombatant.TEAM_ENEMY:
		_last_foe = targets[0].id
	after_action(actor.id)
	return result


## Unleashes Swell technique `technique` for the current party member on `target_ids`, with its
## interactive input's `input` result ({cancelled, grades}; BattleSwell.perform). A refusal
## costs nothing, as for act(); on success the help line says what the input earned.
func unleash(technique: StringName, target_ids: Array[StringName], input: Dictionary) -> ActionResult:
	if not engine.is_party_turn():
		return _refuse_off_turn(technique)
	var actor := engine.current
	var result := swell.perform(technique, _found(target_ids), input)
	_clear_targets()
	if not result.ok:
		_open_command()
		hud.set_help(menus.fail_text(result.fail_reason, actor))
		return result
	hud.set_help(menus.swell_result_text(input.get(BattleSwell.RESULT_GRADES, []), result.swell_bonus_pct))
	after_action(actor.id)
	return result


func _refuse_off_turn(skill_id: StringName) -> ActionResult:
	var refused := ActionResult.failed(current_actor_id(), skill_id, &"not_your_turn")
	if engine.is_auto_turn():
		refused.fail_reason = &"auto_turn"
	hud.set_help(menus.fail_text(refused.fail_reason, engine.current))
	return refused


func _found(target_ids: Array[StringName]) -> Array[BattleCombatant]:
	var targets: Array[BattleCombatant] = []
	for tid in target_ids:
		var t := engine.find(tid)
		if t != null:
			targets.append(t)
	return targets


## Swaps active `out_id` for reserve `in_id` at no time cost.
func swap_members(out_id: StringName, in_id: StringName) -> bool:
	if not engine.swap(out_id, in_id):
		var locked := menus.swap_lock_text(engine, out_id)  # a set piece's lock says why (M3-UI-100)
		if locked != "":
			hud.set_help(locked)
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
		_wait(stage.outro_hold(_pace(&"result_delay_sec")), _show_result)  # M2-BPR-05 victory pose
		return true
	hud.set_help(tr("HUD_ESCAPE_FAILED"))
	after_action(actor)
	return false


# --- queries for tests and captures ------------------------------------------------------


func current_actor_id() -> StringName:
	return engine.current.id if engine != null and engine.current != null else &""


func pending_skill() -> StringName:
	return _pending_skill


func pending_item() -> StringName:
	return _pending_item


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


## The open Swell input (null when none is open).
func swell_input() -> SwellInput:
	return _ring if state == STATE_SWELL_INPUT else null


# --- turn flow ---------------------------------------------------------------------------


func _next_turn() -> void:
	if engine.outcome != &"":
		_set_state(STATE_BUSY)
		hud.commands.visible = false
		_wait(stage.outro_hold(_pace(&"result_delay_sec")), _show_result)  # M2-BPR-05 victory pose
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
	after_action(actor.id, hold)


## After `actor_id`'s action (or a Vowbound's call or dismissal): the order moves on, then the next turn.
func after_action(actor_id: StringName, hold: StringName = &"action_hold_sec") -> void:
	_set_state(STATE_BUSY)
	hud.commands.active = false
	hud.commands.visible = false
	floats.show_end_of_turn(actor_id)
	hud.timeline.note_turn_taken(actor_id)
	_show_timeline(TurnTimeline.MODE_TURN)
	# The order already shows who is next; the party highlight and actor marker follow it.
	hud.party.set_current(current_actor_id(), _auto_reason())
	hud.target_cursor.show_actor(Vector2.ZERO, false)
	hud.target_cursor.show_provoker(Vector2.ZERO, false)
	hud.party.refresh(pacing_scale > 0.0, _pace(&"action_hold_sec") * 0.5)
	stage.refresh_ko(engine)
	_wait(stage.hold_after(_pace(hold)), _next_turn)  # the choreography finishes first (M2-BPR-01)


func _open_command() -> void:
	_set_state(STATE_COMMAND)
	_pending_skill = &""
	_pending_item = &""
	hud.commands.visible = true
	hud.commands.active = true
	hud.party.set_current(current_actor_id())
	_mark_provoker()
	hud.commands.open_root(
		BattleMenus.PAGE_ROOT, menus.display_name(engine.current), menus.root_rows(engine, items, swell)
	)
	vow.show_note()  # a Vowbound's departure ("the party returns"), unless a boss prompt waits
	boss.show_prompt()  # a phase's one tutorial line, over the first highlight's help


func _show_result() -> void:
	_set_state(STATE_RESULT)
	hud.set_combat_ui_visible(false)
	stage.clear_rings()
	if persist_progress and fixture == null:
		BattleVitals.send_back(engine, swell)
	var rows: Array[Dictionary] = []
	var title_key := BattleMenus.victory_title_key(engine)
	var sub_key := "HUD_VICTORY_SUB"
	if engine.outcome in BattleSpoils.SPOILS_OUTCOMES:
		rows = BattleRewards.new().award_victory(self)
		sub_key = "HUD_SCRIPTED_ESCAPE_SUB" if engine.outcome == BattleEngine.OUTCOME_SCRIPTED_ESCAPE else sub_key
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


# --- menus -------------------------------------------------------------------------------


func _on_menu_highlighted(_page: StringName, row: Dictionary) -> void:
	if engine == null or not engine.is_party_turn() or SwellModeRows.highlight(self, row) or vow.highlight(row):
		return
	var rid := StringName(str(row.get("id", "")))
	match state:
		STATE_COMMAND:
			_highlight_root(rid)
		STATE_SKILLS, STATE_SWELL:
			_preview_skill(rid, default_targets(rid))
		STATE_ITEMS:
			_preview_item(rid, _default_item_targets(rid))
		STATE_SWAP_IN:
			# Hovering a reserve member previews them taking the acting fighter's place.
			var incoming := engine.find(rid)
			_show_swap_preview(current_actor_id(), rid)
			hud.set_help(menus.swap_in_help(engine, incoming) if incoming != null else "")


func _highlight_root(rid: StringName) -> void:
	match rid:
		BattleMenus.ROW_ATTACK, BattleMenus.ROW_UNLEASH:  # Attack, or a Vowbound's finisher (M2-UI-05)
			var sid := menus.root_skill(engine, rid)
			_preview_skill(sid, default_targets(sid))
		BattleMenus.ROW_ESCAPE:
			# A failed attempt costs a default-rank turn: preview exactly that.
			var failed := engine.timeline.predict(CtbTimeline.PREVIEW_LENGTH - 1, engine.current, Formulas.DEFAULT_RANK)
			_show_timeline(TurnTimeline.MODE_PREVIEW, failed)
			hud.set_help(menus.escape_help(engine))
		BattleMenus.ROW_SWAP:
			_show_timeline(TurnTimeline.MODE_PREVIEW)
			hud.set_help(tr("HUD_HELP_SWAP"))
		BattleMenus.ROW_ITEMS:
			_show_timeline(TurnTimeline.MODE_PREVIEW)
			hud.set_help(tr("HUD_HELP_ITEMS"))
		BattleMenus.ROW_SWELL:
			_show_timeline(TurnTimeline.MODE_PREVIEW)
			hud.set_help(menus.swell_root_help(engine, swell))  # gauge and mode until full (M2-UI-01)
		_:
			_show_timeline(TurnTimeline.MODE_PREVIEW)
			hud.set_help(tr("HUD_HELP_SKILLS"))


func _on_menu_chosen(_page: StringName, row: Dictionary) -> void:
	var rid := StringName(str(row.get("id", "")))
	match state:
		STATE_COMMAND:
			match rid:
				BattleMenus.ROW_ATTACK:
					_begin_target(menus.root_skill(engine, rid))  # Attack, or its override (M3-CMB-01)
				BattleMenus.ROW_SKILLS:
					_set_state(STATE_SKILLS)
					hud.commands.push(BattleMenus.PAGE_SKILLS, tr("HUD_CMD_SKILLS"), menus.skill_rows(engine))
				BattleMenus.ROW_SWELL:
					_set_state(STATE_SWELL)
					hud.commands.push(BattleMenus.PAGE_SWELL, tr("HUD_CMD_SWELL"), menus.swell_rows(engine, swell))
				BattleMenus.ROW_ITEMS:
					_set_state(STATE_ITEMS)
					hud.commands.push(BattleMenus.PAGE_ITEMS, tr("HUD_CMD_ITEMS"), menus.item_rows(engine, items))
				BattleMenus.ROW_ESCAPE:
					try_escape()
				BattleMenus.ROW_SWAP:
					_set_state(STATE_SWAP_IN)
					hud.commands.push(BattleMenus.PAGE_SWAP, tr("HUD_PAGE_RESERVE"), menus.reserve_rows(engine))
				_:  # Call, Dismiss and a Vowbound's finisher (M2-UI-05)
					vow.choose(row, _begin_target)
		STATE_SKILLS, STATE_SWELL:  # a Swell fill-mode row sets the mode instead (M2-UI-01)
			SwellModeRows.pick(self, row, _begin_target.bind(StringName(str(row.get("skill", rid)))))
		STATE_ITEMS:
			_begin_item_target(StringName(str(row.get("item", rid))))
		STATE_SWAP_IN:
			_swap_in_id = rid
			_begin_swap_out()


func _on_menu_cancelled(_page: StringName) -> void:
	if state in [STATE_SKILLS, STATE_ITEMS, STATE_SWAP_IN, STATE_SWELL] and hud.commands.pop():
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
		_commit_skill(skill_id, [engine.current.id])
		return
	_pending_skill = skill_id
	_group_target = kind.begins_with("all_")
	_candidates = BattleIds.of(menus.skill_candidates(engine, skill_id))
	if _candidates.is_empty():
		return
	var preferred := default_targets(skill_id)
	_target_index = maxi(_candidates.find(preferred[0].id), 0) if not preferred.is_empty() else 0
	_set_state(STATE_TARGET)
	hud.commands.active = false
	_show_pick()


## Like _begin_target, for an item: the cursor moves between whoever the item may take (the
## fallen and living Zombies for a revive). Self items still open the pick, so a warning about
## what the use costs is on screen before it is confirmed.
func _begin_item_target(item_id: StringName) -> void:
	var action := items.action_for(item_id) if items != null else null
	if action == null:
		return
	_candidates = BattleIds.of(menus.item_candidates(engine, action))
	if _candidates.is_empty():
		return
	_pending_skill = &""
	_pending_item = item_id
	_group_target = String(action.target).begins_with("all_")
	var preferred := _default_item_targets(item_id)
	_target_index = maxi(_candidates.find(preferred[0].id), 0) if not preferred.is_empty() else 0
	_set_state(STATE_TARGET)
	hud.commands.active = false
	_show_pick()


func _begin_swap_out() -> void:
	_pending_skill = &""
	_pending_item = &""
	_group_target = false
	_candidates = BattleIds.of(engine.party_active)
	_target_index = maxi(_candidates.find(engine.current.id), 0)
	_set_state(STATE_SWAP_OUT)
	hud.commands.active = false
	_show_pick()


func _handle_pick_input(event: InputEvent) -> bool:
	return BattlePointer.handle_pick(self, event, _target_index)  # keys, pad and mouse (M2-UI-26)


func _cycle_target(delta: int) -> void:
	if _group_target or _candidates.is_empty():
		return
	_target_index = posmod(_target_index + delta, _candidates.size())
	_show_pick()


func _confirm_pick() -> void:
	if state == STATE_SWAP_OUT:
		swap_members(_candidates[_target_index], _swap_in_id)
	elif _pending_item != &"":
		use_item_on(_pending_item, picked_ids())
	else:
		_commit_skill(_pending_skill, picked_ids())


## A skill acts at once; a Swell technique first opens its interactive input on the targets.
func _commit_skill(skill_id: StringName, target_ids: Array[StringName]) -> void:
	if not swell.is_technique(engine.current, skill_id):
		act(skill_id, target_ids)
		return
	_pending_skill = skill_id
	_ring = SwellInput.create(hud.settings.timing_input(swell.input_for(engine.current)))  # timing assist
	_ring_clock = SwellRingClock.new(_ring)
	_set_state(STATE_SWELL_INPUT)
	hud.commands.visible = false
	SwellInputKeys.carry_held(_ring_clock)  # an accept still held from the menu starts Toma's brace
	hud.swell_ring.open(_ring, menus.skill_name(engine, skill_id), tr(SwellRingView.hint_key(_ring.kind, false)))
	hud.set_help(menus.swell_help(engine, swell, skill_id, -1))


## The open input takes ui_accept and the directions (SwellInputKeys) and ui_cancel (back out,
## only before the first grade).
func _handle_ring_input(event: InputEvent) -> bool:
	if not SwellInputKeys.feed(hud.swell_ring.pointer_event(event), _ring_clock, swell_input_live):  # M2-UI-26
		return false
	_after_ring()
	return true


## Redraws the input; once it is done, unleashes the technique, or after a cancel goes back to
## the target pick with nothing spent.
func _after_ring() -> void:
	hud.swell_ring.refresh()
	if not _ring.grades.is_empty():
		hud.swell_ring.set_hint(tr(SwellRingView.hint_key(_ring.kind, true)))
	if not _ring.is_done():
		return
	hud.swell_ring.close()
	if not _ring.cancelled:
		unleash(_pending_skill, picked_ids(), _ring.result())
		return
	hud.commands.visible = true
	_set_state(STATE_TARGET)
	_show_pick()


func _cancel_pick() -> void:
	var back := STATE_SKILLS if hud.commands.depth() > 1 else STATE_COMMAND
	if hud.commands.page_id() == BattleMenus.PAGE_SWELL:
		back = STATE_SWELL
	if state == STATE_SWAP_OUT:
		back = STATE_SWAP_IN
	elif _pending_item != &"":
		back = STATE_ITEMS
	_pending_item = &""
	_clear_targets()
	hud.commands.active = true
	_set_state(back)
	_mark_provoker()
	_on_menu_highlighted(hud.commands.page_id(), hud.commands.current_row())


func _show_pick() -> void:
	var ids := picked_ids()
	var hostile: Array[bool] = []
	var entries: Array[Dictionary] = []
	var skill_pick := state == STATE_TARGET and _pending_item == &""
	var sk := engine.db.skill(_pending_skill) if skill_pick else {}
	# Items ignore Provoke and Reflect (formulas.md § Items).
	var forced := engine.forced_target(engine.current, _pending_skill) if skill_pick else null
	var chosen: Array[BattleCombatant] = []
	for cid in ids:
		var c := engine.find(cid)
		var foe := c.team == BattleCombatant.TEAM_ENEMY
		hostile.append(foe)
		var entry := {
			"id": cid,
			"label": menus.display_name(c),
			"group_label": menus.group_label(foe, str(sk.get("target", ""))),
			"screen_pos": head_pos(cid),
			"hostile": foe,
			"combatant": c,
			"revealed": bestiary.knows(c),
			"forced": forced != null and forced == c,
		}
		var land := engine.reflect_recipient(engine.current, c, sk) if ids.size() == 1 else c
		if land != c and land != null:
			entry["bounce_pos"] = head_pos(land.id)
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
		hud.set_help(menus.swap_out_help(engine.find(_swap_in_id), engine, _candidates[_target_index]))
		return
	if _pending_item != &"":
		_preview_item(_pending_item, chosen)
		return
	_preview_skill(_pending_skill, chosen)


func _clear_targets() -> void:
	_candidates.clear()
	_target_index = 0
	stage.clear_rings()
	hud.target_cursor.clear()
	hud.party.set_targeted([])


## The target a skill starts on (BattleMenus.default_targets). Public for the capture scripts.
func default_targets(skill_id: StringName) -> Array[BattleCombatant]:
	return menus.default_targets(engine, skill_id, _last_foe)


func _default_item_targets(item_id: StringName) -> Array[BattleCombatant]:
	return menus.default_item_targets(engine, items.action_for(item_id) if items != null else null, _last_foe)


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
	_show_timeline(TurnTimeline.MODE_PREVIEW, preview, BattleIds.of(marked))
	hud.set_help(menus.skill_preview_help(engine, swell, skill_id, chosen, lands, _ghost_slot() - 1))


## Previews item `item_id` on `targets`. What the use will really do leads the help line; a use
## that loses the fight on the spot (a Zombie reviving itself as the last one standing, M1-UI-04)
## is the whole line, in the danger color, while the timeline shows the user dropping out of it.
func _preview_item(item_id: StringName, targets: Array[BattleCombatant]) -> void:
	var chosen: BattleCombatant = targets[0] if targets.size() == 1 else null
	var preview := engine.preview_item(item_id, chosen, items, CtbTimeline.PREVIEW_LENGTH - 1)
	_show_timeline(TurnTimeline.MODE_PREVIEW, preview, BattleIds.of(targets))
	var parts := menus.item_notes(engine, items, item_id, chosen)
	if engine.item_defeats_party(item_id, targets, items):
		# The warning stands alone: nothing else about the item matters if it ends the fight.
		hud.set_help(" · ".join(parts), &"danger")
		return
	var help := menus.item_help(engine, items, item_id, _ghost_slot() - 1)
	if help != "":
		parts.append(help)
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
	hud.target_cursor.show_actor(head_pos(cid), shown, _auto_reason())
	_mark_provoker()


## The Provoke hook hangs over the provoker while the acting party member is Provoked.
func _mark_provoker() -> void:
	var provoker: BattleCombatant = null
	if engine.is_party_turn():
		provoker = engine.forced_target(engine.current, BattleMenus.ATTACK_SKILL)
	var shown := provoker != null and stage.has_fighter(provoker.id)
	hud.target_cursor.show_provoker(head_pos(provoker.id) if shown else Vector2.ZERO, shown)


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


## Screen position over `cid`'s head, offset by `section`'s head_offset_m (HUD coordinates).
func head_pos(cid: StringName, section: StringName = &"actor_marker") -> Vector2:
	var m := _damage_m if section == &"damage" else _marker_m
	var p := stage.screen_pos(cid, HudLayout.num(m, "head_offset_m"))
	var safe: Array = m.get("safe_px", [])
	if safe.size() == 4 and is_inside_tree():  # a float starts on screen, clear of the help line (damage)
		var size := get_viewport().get_visible_rect().size
		p.x = clampf(p.x, float(safe[0]), size.x - float(safe[2]))
		p.y = clampf(p.y, float(safe[1]), size.y - float(safe[3]))
	return p


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
	return HudLayout.num(_pacing, String(key)) * pacing_scale / stage.battle_speed(hud.battle_speed())  # M2-UI-23/BPR-03


func _set_state(s: StringName) -> void:
	if s == state:
		return
	state = s
	state_changed.emit(s)


func _color(role: StringName) -> Color:
	return hud.get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


## The party's bag for live play: the real inventory when the battle persists, otherwise a copy
## so a test or preview run never spends the player's items.
func _live_items() -> BattleItemSource:
	var item_db := ItemDB.load_default()
	var bag: Dictionary = Game.state.inventory if persist_progress else Game.state.inventory.duplicate(true)
	return InventoryItemSource.new(item_db, Inventory.new(item_db, bag))


# --- capture scripts (deterministic; see tests/screenshots/shots.json) ---------------------


## Plays the `scripted_state` fixture to its capture state (BattleCaptureScript); public for tests.
func run_script(state_id: StringName = &"") -> void:
	var sid := state_id if state_id != &"" else scripted_state
	var fx := BattleFixture.load_fixture(sid)
	if fx == null:
		return
	start_fixture(fx)
	BattleCaptureScript.play(self, sid)


## Moves the open target cursor onto the first candidate whose base id is `base_id` (captures).
func aim_at(base_id: StringName) -> void:
	for i in _candidates.size():
		if String(_candidates[i]).get_slice("#", 0) == String(base_id):
			_target_index = i
			_show_pick()
			return
