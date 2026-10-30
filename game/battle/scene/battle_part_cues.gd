class_name BattlePartCues
extends RefCounted
## Model parts that come and go with battle events, not with a phase (M3-C05-07): the Cinder Matron's Crust breaks
## off when she enters the Pour (creatures.json `phases`, CreatureActor), but the fight puts it back without a phase
## change, through her `recrust` skill or a water or ice hit that quenches her (BossMechanics: the hit records
## "reacted": true), and Kerrid's sundering blow takes it off again. battle_sandbox.json "part_cues", per creatures.json
## row id: `parts` (model node names), `show_on_skills` (a skill that lands on the creature), `show_on_reaction` (a
## hit on it that "reacted") and `hide_on_statuses` (a status a hit added to it).
## - On the action's contact beat (BattleChoreo.contact), so the crust closes or cracks as the blow lands; with the
##   choreography off, contact comes as the action resolves.
## - Within one hit, a hide comes before a show: the engine applies the hit's statuses first and the reaction's
##   cleanse after, so a hit that does both leaves her crusted, as the engine does.
## - BattleStage attaches one per sequencer (its `choreo` setter). Listens only: it never writes combat state.

## Combatant id -> its parts' last cue (true shown, false hidden), for tests and captures.
var shown: Dictionary = {}

var _stage: BattleStage
var _choreo: BattleChoreo
var _cues: Dictionary = {}


## Connects a helper to `sequencer`'s contact beat for the fighters on `stage`, dropping `previous` (a retry).
static func attach(stage: BattleStage, sequencer: BattleChoreo, previous: BattlePartCues = null) -> BattlePartCues:
	if previous != null:
		previous.detach()
	var cues := BattlePartCues.new()
	cues._stage = stage
	cues._cues = BattleStage.config().get("part_cues", {}) as Dictionary
	if sequencer != null:
		cues._choreo = sequencer
		sequencer.contact.connect(cues.on_contact)
	return cues


func detach() -> void:
	if _choreo != null and is_instance_valid(_choreo) and _choreo.contact.is_connected(on_contact):
		_choreo.contact.disconnect(on_contact)
	_choreo = null


## Applies `result`'s cues to every fighter a hit of it landed on.
func on_contact(result: ActionResult) -> void:
	if result == null or not result.ok:
		return
	for hit in result.hits:
		if not bool(hit.get("hit", false)):
			continue
		var cid := StringName(str(hit.get("target_id", "")))
		var actor := _actor(cid)
		if actor == null:
			continue
		var cue: Dictionary = _cues.get(String(actor.creature_id), {})
		if cue.is_empty():
			continue
		for sid: Variant in hit.get("statuses_added", []):
			if (cue.get("hide_on_statuses", []) as Array).has(str(sid)):
				_set_parts(cid, actor, cue, false)
		var by_skill := (cue.get("show_on_skills", []) as Array).has(String(result.skill_id))
		var by_reaction := bool(cue.get("show_on_reaction", false)) and bool(hit.get("reacted", false))
		if by_skill or by_reaction:
			_set_parts(cid, actor, cue, true)


func _set_parts(cid: StringName, actor: CreatureActor, cue: Dictionary, on: bool) -> void:
	for n: Variant in cue.get("parts", []):
		var node := actor.find_child(str(n), true, false) as Node3D
		if node != null:
			node.visible = on
	shown[cid] = on


func _actor(cid: StringName) -> CreatureActor:
	if _stage == null or not is_instance_valid(_stage):
		return null
	var f := _stage.stand_in(cid)
	return f.creature() if f != null else null
