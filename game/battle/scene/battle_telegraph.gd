class_name BattleTelegraph
extends RefCounted
## A telegraph that reads on stage (M3-BPR-413; Pillar 4: the player always sees what is coming). When a foe starts
## gathering a charged skill (a skill row's "charge": Hullgnaw's coil, the Matron's re-crust, the Spar-Wraith's lines,
## a Tide Crawler reaching for the stair, the Reach's hand and Breach), it plays choreo.json `telegraph.gather` (a
## root accent: it draws itself in and sways) on that action's contact, and again on each later turn of the charge.
## The timeline already names the intent; this makes the stage agree. A boss whose `bosses` row has its own gather for
## that charge (the Drownbell's toll) is left to BattleBossChoreo. Listen-only; nothing at instant pacing.

var choreo: BattleChoreo
var engine: BattleEngine
## Gathers played (tests): [[combatant id, skill id], ...].
var played: Array = []
var _on_contact: Array[StringName] = []


func _init(sequencer: BattleChoreo, battle: BattleEngine) -> void:
	choreo = sequencer
	engine = battle
	engine.charge_started.connect(_on_charge_started)
	engine.turn_started.connect(_on_turn_started)
	choreo.contact.connect(_on_contact_beat)


func _gather() -> Dictionary:
	return (choreo.data.get("telegraph", {}) as Dictionary).get("gather", {}) as Dictionary


## True when `c`'s own boss row gathers this charge (BattleBossChoreo plays it instead).
func _boss_owns(c: BattleCombatant, skill_id: StringName) -> bool:
	var row := (choreo.data.get("bosses", {}) as Dictionary).get(String(c.id).get_slice("#", 0), {}) as Dictionary
	var want := str(row.get("charge_skill", ""))
	return want != "" and (want == "*" or want == str(skill_id))


func _on_charge_started(actor: BattleCombatant, skill_id: StringName, _turns: int) -> void:
	if actor.team != BattleCombatant.TEAM_ENEMY or actor.is_entry() or _boss_owns(actor, skill_id):
		return
	_on_contact.append(actor.id)  # the gathering action's own contact
	played.append([actor.id, skill_id])


func _on_turn_started(actor: BattleCombatant) -> void:
	if actor.team != BattleCombatant.TEAM_ENEMY or actor.is_entry() or not actor.is_charging():
		return
	if actor.charge_left > 1 and not _boss_owns(actor, actor.charge_skill):
		choreo.accent(actor.id, _gather())
		played.append([actor.id, actor.charge_skill])


func _on_contact_beat(_result: ActionResult) -> void:
	var pending := _on_contact
	_on_contact = []
	for cid in pending:
		choreo.accent(cid, _gather())
