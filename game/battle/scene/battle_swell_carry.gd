class_name BattleSwellCarry
extends RefCounted
## Swell across battles and in saves (M2-ARC-01, save v6; docs/kb/design/battle_ctb.md "Carried
## Swell"). Glue, not engine core: BattleSwell keeps its rules and plain-data record, and this
## class moves that record between it and Game.state.
##
## - Gauges and modes ride on the party combatants: Game.vitals_modifier() puts the saved `swell`
##   and `swell_mode` on them at setup, and BattleVitals.send_back hands them back to
##   Game.record_party after a victory or an escape. A defeat writes nothing.
## - The party's unlocked modes and unlock counts (GameStateData.swell) are loaded by attach()
##   before the battle and sent back by BattleVitals.send_back(engine, swell) with the party.
## - Outside battle (M2-UI-01's field menu): rules() is the BattleSwell for the saved record,
##   mode_rows() lists a hero's choosable modes, and set_mode() saves a choice.
## Capture fixtures and tests (`carry` off) never read or write any of it.


## Loads the saved record into `swell` when `carry` (a live battle), then attaches it to `engine`.
## `state` defaults to the live Game.state.
static func attach(swell: BattleSwell, engine: BattleEngine, carry: bool, state: GameStateData = null) -> void:
	if carry:
		swell.load_saved(_state(state).swell)
	swell.attach(engine)


## The Swell rules (swell.json) with the saved record loaded: which modes are choosable now.
static func rules(state: GameStateData = null) -> BattleSwell:
	var swell := BattleSwell.new(BattleSwell.load_config())
	swell.load_saved(_state(state).swell)
	return swell


## The modes hero `cid` may choose out of battle, in data order, with its saved mode `current`
## (BattleSwell.mode_rows_for). Empty for a character with no Swell.
static func mode_rows(cid: StringName, state: GameStateData = null) -> Array[Dictionary]:
	var swell := rules(state)
	return swell.mode_rows_for(cid, _state(state).swell_mode_of(cid, swell.default_mode))


## Saves `mode` as hero `cid`'s fill mode out of battle. Refused (false, nothing saved) for a
## character with no Swell or a mode that is not unlocked. The gauge keeps its points.
static func set_mode(cid: StringName, mode: StringName, state: GameStateData = null) -> bool:
	var swell := rules(state)
	if not swell.heroes.has(cid) or not swell.unlocked.has(mode):
		return false
	_state(state).set_swell_mode(cid, mode, swell.default_mode)
	return true


static func _state(state: GameStateData) -> GameStateData:
	return state if state != null else Game.state
