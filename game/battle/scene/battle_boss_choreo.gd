class_name BattleBossChoreo
extends RefCounted
## A boss's set piece on the stage (M2-BPR-04, the Drownbell; docs/kb/tech/battle_presentation.md "Specials").
## - **Listens only**, like BattleBossVfx: the engine's boss signals (battle_ctb.md "VFX hook points") drive it, and
##   it never writes combat state. BattleChoreo.attached builds it when an enemy has a row in choreo.json "bosses".
## - **The toll** itself is an ordinary action: choreo.json style_by_skill gives it the "toll" style (the bell rears
##   and lurches; every party member recoils hard as the shockwave reaches it, wave_m_s, which matches
##   BattleBossVfx's ring; BattleBossVfx plays the ring on BattleChoreo.contact).
## - **Moments** (accents on fighters' roots, BattleChoreo.accent): the gather (charge_started, then each turn of the
##   charge: the bell sways), the rim break (charge_broken: the bell staggers, on the breaking blow's contact), the
##   flood (phase_changed to the flood phase: the party braces in turn, once the action playing is done).
## - Root motion only: a creature actor (claude/creatures CreatureActor) plays the bell's own phase clips under it.

var choreo: BattleChoreo
var engine: BattleEngine
## The boss's row of choreo.json "bosses".
var cfg: Dictionary = {}
var boss_id: StringName = &""
## Moments played, in order (tests and tools): &"gather", &"rim_break", &"flood".
var moments: Array[StringName] = []
## Accents that wait for the next contact beat (the action whose resolution raised them): [[cid, spec]].
var _on_contact: Array[Array] = []


## Builds the helper when one of `engine`'s enemies has a row in choreo.json "bosses" (else null).
static func attached_if_boss(sequencer: BattleChoreo, battle: BattleEngine) -> BattleBossChoreo:
	var bosses := sequencer.data.get("bosses", {}) as Dictionary
	for c: BattleCombatant in battle.enemies:
		var base := String(c.id).get_slice("#", 0)
		if bosses.has(base):
			var b := BattleBossChoreo.new()
			b.attach(sequencer, battle, c.id, bosses[base] as Dictionary)
			return b
	return null


func attach(sequencer: BattleChoreo, battle: BattleEngine, bell: StringName, row: Dictionary) -> void:
	choreo = sequencer
	engine = battle
	boss_id = bell
	cfg = row
	engine.charge_started.connect(_on_charge_started)
	engine.turn_started.connect(_on_turn_started)
	engine.charge_broken.connect(_on_charge_broken)
	engine.phase_changed.connect(_on_phase_changed)
	choreo.contact.connect(_on_contact_beat)


func _on_charge_started(actor: BattleCombatant, skill_id: StringName, _turns: int) -> void:
	if actor.id == boss_id and str(skill_id) == str(cfg.get("charge_skill", "")):
		_queue(boss_id, _row("gather"))  # the gathering action's own contact
		moments.append(&"gather")


## Each later turn of the charge sways again; the turn it fires plays the toll instead.
func _on_turn_started(actor: BattleCombatant) -> void:
	if actor.id == boss_id and actor.is_charging() and actor.charge_left > 1:
		if str(actor.charge_skill) == str(cfg.get("charge_skill", "")):
			choreo.accent(boss_id, _row("gather"))
			moments.append(&"gather")


func _on_charge_broken(enemy: BattleCombatant, _skill_id: StringName) -> void:
	if enemy.id == boss_id:
		_queue(boss_id, _row("break"))  # the breaking blow's contact
		moments.append(&"rim_break")


func _on_phase_changed(enemy: BattleCombatant, phase_id: StringName) -> void:
	var flood := _row("flood")
	if enemy.id != boss_id or str(phase_id) != str(flood.get("phase", "")):
		return
	moments.append(&"flood")
	choreo.after_sequence(_brace)


## The party braces against the rising water, one after another in slot order.
func _brace() -> void:
	var flood := _row("flood")
	var spec := flood.get("accent", {}) as Dictionary
	for i in engine.party_active.size():
		choreo.accent(engine.party_active[i].id, spec, float(flood.get("stagger_sec", 0.0)) * i)


func _queue(cid: StringName, spec: Dictionary) -> void:
	_on_contact.append([cid, spec])


func _on_contact_beat(_result: ActionResult) -> void:
	var pending := _on_contact
	_on_contact = []
	for q: Array in pending:
		choreo.accent(StringName(q[0]), q[1] as Dictionary)


func _row(key: String) -> Dictionary:
	return cfg.get(key, {}) as Dictionary
