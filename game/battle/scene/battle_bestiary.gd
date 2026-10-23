class_name BattleBestiary
extends RefCounted
## Read, the bestiary log and the battle opening for one BattleController (M1-CMB-03). Glue, not
## engine core: it sets the engine's opening and listens to its signals.
##
## attach(engine, live) runs after setup() and before begin():
##   - a live battle (persist_progress on, no capture fixture) rolls its opening
##     (BattleOpening.choose) and logs into Game.state.bestiary; tests and capture fixtures open
##     normally and log into a scratch dictionary, so no baseline or save moves;
##   - every Read hit is logged (Bestiary.record_read) and kept in `last_reveal` for the HUD, and
##     floats the target's weaknesses over it;
##   - a victory logs one defeat per enemy in the encounter (Bestiary.record_defeated);
##   - an opening other than normal floats its caption over the first combatant to act.
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


func _on_action_resolved(result: ActionResult) -> void:
	for hit in result.hits:
		if not hit.has("read"):
			continue
		last_reveal = hit["read"]
		book.record_read(StringName(str(last_reveal.get("enemy_id", ""))))
		_float(StringName(str(hit["target_id"])), weakness_text(last_reveal))


func _on_battle_finished(outcome: StringName) -> void:
	if outcome != BattleEngine.OUTCOME_VICTORY:
		return
	for e in engine.enemies:
		book.record_defeated(StringName(String(e.id).get_slice("#", 0)))


func _on_turn_started(actor: BattleCombatant) -> void:
	if _opening_shown:
		return
	_opening_shown = true
	var key := str(BattleOpening.CAPTION_KEYS.get(engine.opening, ""))
	if key != "":
		_float(actor.id, TranslationServer.translate(key))


func _float(cid: StringName, text: String) -> void:
	if ctl == null or not ctl.show_damage_numbers or not ctl.stage.has_fighter(cid):
		return
	ctl.hud.pop_info(text, ctl.head_pos(cid, &"damage"), FLOAT_ROLE)
