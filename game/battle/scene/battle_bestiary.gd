class_name BattleBestiary
extends RefCounted
## Read, the bestiary log and the battle opening for one BattleController (M1-CMB-03). Glue, not
## engine core: it sets the engine's opening and listens to its signals.
##
## attach(engine, live) runs after setup() and before begin():
##   - a live battle (persist_progress on, no capture fixture) rolls its opening
##     (BattleOpening.choose) and logs into Game.state.bestiary; tests and capture fixtures open
##     normally and log into a scratch dictionary, so no baseline or save moves;
##   - every Read hit is logged (Bestiary.record_read) and kept in `last_reveal` for the HUD,
##     floats the target's weaknesses over it, and opens the Read panel on it (M2-UI-02:
##     BattleHud.read_panel(), which holds the battle until it is closed);
##   - a victory logs one defeat per enemy in the encounter (Bestiary.record_defeated). Read and
##     victory credit key the log by the same id, BattleEngine.enemy_id (Read's reveal carries the
##     row that rule finds). A KO'd foe stays in engine.enemies, so it is credited; the engine has
##     no rule that removes a foe mid-battle today, and a foe such a rule removed would not be;
##   - an opening other than normal shows the opening banner at the first turn (M2-UI-02:
##     BattleHud.opening_banner(); it replaced the caption float).
## Hold the instance for the whole battle: a signal connection does not keep it alive.

const KEY_WEAK := "weak"
const ELEMENT_KEY_PREFIX := "ELEMENT_"
const READ_WEAK_KEY := "HUD_READ_WEAK"
const READ_NO_WEAKNESS_KEY := "HUD_READ_NO_WEAKNESS"
const FLOAT_ROLE := &"focus_gold"

var ctl: BattleController
var engine: BattleEngine
## The log this battle writes into (Game.state.bestiary when live).
var book: Bestiary = Bestiary.new()
## The latest Read's reveal (BattleRead.reveal), {} before any Read this battle.
var last_reveal: Dictionary = {}
## Live battles roll their opening while this is on. Tests about other rules turn it off so the
## party always opens as the seed alone decides (a rolled ambush plays enemy turns at once).
var roll_openings := true

var _opening_shown := false


func _init(controller: BattleController = null) -> void:
	ctl = controller


func attach(battle: BattleEngine, live: bool) -> void:
	engine = battle
	book = Bestiary.new(Game.state.bestiary if live else {})
	last_reveal = {}
	_opening_shown = false
	if ctl != null and ctl.hud != null:
		ctl.hud.close_overlays()
	if live and roll_openings:
		engine.opening = BattleOpening.choose(engine)
	engine.action_resolved.connect(_on_action_resolved)
	engine.battle_finished.connect(_on_battle_finished)
	engine.turn_started.connect(_on_turn_started)


## "Weak to Fire, Ice", or "No weakness found", for a reveal.
static func weakness_text(reveal: Dictionary) -> String:
	var weak: Array = (reveal.get("affinities", {}) as Dictionary).get(KEY_WEAK, [])
	if weak.is_empty():
		return TranslationServer.translate(READ_NO_WEAKNESS_KEY)
	var names: Array[String] = []
	for el: Variant in weak:
		names.append(TranslationServer.translate(ELEMENT_KEY_PREFIX + str(el).to_upper()))
	return TranslationServer.translate(READ_WEAK_KEY).format({"list": ", ".join(names)})


## True when the log holds a Read of foe `c`'s kind, in this battle or before it (M2-UI-04): the
## target info panel then shows its HP instead of "HP unknown until Read". False for the party.
func knows(c: BattleCombatant) -> bool:
	return c != null and c.team == BattleCombatant.TEAM_ENEMY and book.is_read(BattleEngine.enemy_id(c))


func _on_action_resolved(result: ActionResult) -> void:
	for hit in result.hits:
		if not hit.has("read"):
			continue
		last_reveal = hit["read"]
		book.record_read(StringName(str(last_reveal.get("enemy_id", ""))))
		var shown := _show_read.bind(StringName(str(hit["target_id"])), last_reveal)
		var choreo := ctl.stage.choreo if ctl != null and ctl.stage != null else null
		if choreo != null:  # M2-BPR-01: on the Read's contact beat (at once when nothing plays)
			choreo.contact.connect(func(_r: ActionResult) -> void: shown.call(), CONNECT_ONE_SHOT)
		else:
			shown.call()


func _show_read(cid: StringName, reveal: Dictionary) -> void:
	_float(cid, weakness_text(reveal))
	_open_panel(reveal)


func _on_battle_finished(outcome: StringName) -> void:
	if outcome != BattleEngine.OUTCOME_VICTORY:
		return
	for e in engine.enemies:
		book.record_defeated(BattleEngine.enemy_id(e))


func _on_turn_started(_actor: BattleCombatant) -> void:
	if _opening_shown:
		return
	_opening_shown = true
	if ctl != null and ctl.hud != null and BattleOpening.CAPTION_KEYS.has(engine.opening):
		ctl.hud.opening_banner().show_opening(engine.opening, ctl.pacing_scale > 0.0)


## The Read panel, for a foe (a Confused reader's Read on an ally has no enemies.json page).
func _open_panel(reveal: Dictionary) -> void:
	if ctl == null or ctl.hud == null or str(reveal.get("enemy_id", "")) == "":
		return
	var page := reveal.duplicate()
	page["broken_parts"] = broken_part_keys(engine, StringName(str(reveal.get("target_id", ""))))
	ctl.hud.read_panel().open(EnemyPage.new().from_reveal(page, engine.db.statuses), ctl.pacing_scale > 0.0)


## The name keys of the parts the foe `cid` has broken and not yet mended (M4-A2P-083): each part is named by its
## charge skill, as the "repaired" float names it.
static func broken_part_keys(battle: BattleEngine, cid: StringName) -> Array[String]:
	var out: Array[String] = []
	var c := battle.find(cid)
	if c == null:
		return out
	for part in c.broken_parts:
		out.append(str(battle.db.skill(part).get("name_key", String(part))))
	return out


func _float(cid: StringName, text: String) -> void:
	if ctl == null or not ctl.show_damage_numbers or not ctl.stage.has_fighter(cid):
		return
	ctl.hud.pop_info(text, ctl.head_pos(cid, &"damage"), FLOAT_ROLE)
