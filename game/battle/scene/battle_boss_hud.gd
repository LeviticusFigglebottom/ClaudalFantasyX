class_name BattleBossHud
extends RefCounted
## Presentation of boss mechanics (M2-FP-06, the Drownbell; battle_ctb.md "The Drownbell"): it
## listens to the engine's boss signals and shows them. A view: it never writes combat state.
##   phase_changed      queues the phase's tutorial prompt (prompt_key; one per phase, SPEC tone)
##   combatants_joined  seats the new fighters on the stage and gives them timeline identities
##   charge_started     floats the telegraphed skill's name over the user (the timeline already
##                      marks the turn it fires on: TurnEntry.intent, TurnTimeline.intent_labels)
##   charge_broken      floats "<part> breaks" over the user; weak-point hits float a count
##   field_cleared      floats the field clearing over each fighter that leaves with it
## After each of those (and every action) the standing read-out, BattleBossStatus, refreshes
## (M2-FP-12): floats are transient and off with damage numbers; the read-out is neither.
## The encounter's own prompt_key is the opening prompt. show_prompt() puts a queued prompt on the
## help line once, when the next command menu opens.

var ctl: BattleController
## The tutorial line waiting for the next command menu ("" when none).
var pending_prompt := ""
## The standing read-out under the target info (one per HUD, reused by a retry).
var status: BattleBossStatus
var _engine: BattleEngine


func _init(controller: BattleController) -> void:
	ctl = controller


## Story flags the battle tables gate skills on (skills.json "requires_flag") that are set, as
## the engine wants them before setup(). `is_set`: (flag: StringName) -> bool.
static func story_flags(db: BattleDB, is_set: Callable) -> Array[StringName]:
	var out: Array[StringName] = []
	for sid: StringName in db.skills:
		var flag := StringName(str(db.skill(sid).get("requires_flag", "")))
		if flag != &"" and not out.has(flag) and bool(is_set.call(flag)):
			out.append(flag)
	return out


## story_flags() read from the live game (Game.get_flag, so the flag registry checks them).
static func live_flags(db: BattleDB) -> Array[StringName]:
	return story_flags(db, func(f: StringName) -> bool: return Game.get_flag(f) == true)


## A view of `engine` for `controller`, already attached.
static func attached(controller: BattleController, engine: BattleEngine) -> BattleBossHud:
	var view := BattleBossHud.new(controller)
	view.attach(engine)
	return view


## Connects to `engine` (after setup) and queues the encounter's opening prompt.
func attach(engine: BattleEngine) -> void:
	pending_prompt = _text(str(engine.db.encounters.get(engine.encounter_id, {}).get("prompt_key", "")))
	engine.phase_changed.connect(_on_phase_changed)
	engine.combatants_joined.connect(_on_joined)
	engine.charge_started.connect(_on_charge_started)
	engine.charge_broken.connect(_on_charge_broken)
	engine.field_cleared.connect(_on_field_cleared)
	engine.action_resolved.connect(_on_action_resolved)
	engine.battle_finished.connect(_on_finished)
	_engine = engine
	status = ctl.hud.get_node_or_null(^"BossStatus") as BattleBossStatus
	if status == null and BattleBossStatus.boss_of(engine) != null:
		status = BattleBossStatus.new()
		ctl.hud.add_child(status)
	refresh()
	var labels: Dictionary = {}
	for sid: StringName in engine.db.skills:
		var charge: Dictionary = engine.db.skill(sid).get("charge", {})
		if not charge.is_empty():
			var charged := StringName(str(charge.get("skill", "")))
			labels[charged] = ctl.menus.skill_name(engine, charged)
	ctl.hud.timeline.intent_labels = labels


## Re-reads the boss's state into the read-out (hidden when there is no boss).
func refresh() -> void:
	if status != null and _engine != null:
		status.refresh(_engine, ctl.menus)


## Shows the queued prompt on the help line (once). True if it did.
func show_prompt() -> bool:
	if pending_prompt == "":
		return false
	ctl.hud.set_help(pending_prompt, &"focus_gold")
	pending_prompt = ""
	return true


func _on_phase_changed(enemy: BattleCombatant, phase_id: StringName) -> void:
	for row: Variant in enemy.phases:
		var p: Dictionary = row
		if StringName(str(p.get("id", ""))) == phase_id:
			pending_prompt = _text(str(p.get("prompt_key", "")))
	refresh()


func _on_joined(added: Array[BattleCombatant]) -> void:
	for c in added:
		ctl.stage.add_enemy(c, ctl.engine)
		var tint := Color.html(str(BattleStage.stand_in_spec(c.id).get("tint", "#A9B8CC")))
		ctl.hud.timeline.set_identity(c.id, ctl.menus.display_name(c), tint)
	refresh()


func _on_charge_started(actor: BattleCombatant, skill_id: StringName, _turns: int) -> void:
	_float(actor, ctl.menus.skill_name(ctl.engine, skill_id), &"danger")
	refresh()


func _on_charge_broken(enemy: BattleCombatant, skill_id: StringName) -> void:
	var text := (
		tr("HUD_CHARGE_BROKEN_FMT")
		. format(
			{
				"name": ctl.menus.display_name(enemy),
				"part": tr(str(enemy.weak_point.get("name_key", ""))),
				"skill": ctl.menus.skill_name(ctl.engine, skill_id),
			}
		)
	)
	_float(enemy, text, &"focus_gold")
	refresh()


func _on_field_cleared(_field_id: StringName, fallen: Array[BattleCombatant]) -> void:
	for c in fallen:
		_float(c, tr("HUD_FIELD_CLEARED"), &"focus")
	refresh()


func _on_finished(_outcome: StringName) -> void:
	if status != null:
		status.hide_status()


## A weak-point hit that did not break the charge yet shows its count ("Rim 2/3").
func _on_action_resolved(result: ActionResult) -> void:
	refresh()
	for hit in result.hits:
		if not hit.has("weak_point_hits") or hit.has("charge_broken"):
			continue
		var t := ctl.engine.find(StringName(str(hit["target_id"])))
		if t == null:
			continue
		var text := (
			tr("HUD_WEAK_POINT_FMT")
			. format(
				{
					"part": tr(str(t.weak_point.get("name_key", ""))),
					"hits": int(hit["weak_point_hits"]),
					"need": int(t.weak_point.get("hits", 1)),
				}
			)
		)
		_float(t, text, &"focus_gold")


func _float(c: BattleCombatant, text: String, role: StringName) -> void:
	if ctl.show_damage_numbers and ctl.stage.has_fighter(c.id):
		ctl.hud.pop_info(text, ctl.head_pos(c.id, &"damage"), role)


static func _text(key: String) -> String:
	return str(TranslationServer.translate(key)) if key != "" else ""
