class_name PartyJoins
extends RefCounted
## Who joins the party, and when (M2-CMB-07 follow-up; data: first_playable.json "party").
## Joining writes `party_ids` and grants the hero's starting gear (PartyGoods.join), so a fresh
## New Game has a geared party before its first fight, not only after a load.
##   new_game          Game.new_game() joins these heroes (Rhen).
##   joins[flag]       the first time `flag` is set truthy, these heroes join (Cutscene A sets
##                     ch02_met_asha: Asha and Toma). Game wires EventBus.flag_changed here.
## Idempotent: a hero who has joined is never added twice, and gear they already wear is never
## replaced (EquipmentBag.grant_starting). A load runs SaveSystem's ensure_starting_gear for the
## joined members, which grants nothing more.

const KEY_NEW_GAME := "new_game"
const KEY_JOINS := "joins"


## The heroes a new game starts with join `state`. Returns who was new.
static func on_new_game(state: GameStateData, cfg: Dictionary = {}) -> Array[StringName]:
	var block := cfg if not cfg.is_empty() else _config()
	return _join(state, FirstPlayableConfig.ids(block.get(KEY_NEW_GAME, [])))


## `flag` changed to `value`: when it is set truthy and names a join, those heroes join `state`.
## Returns who was new.
static func on_flag(state: GameStateData, flag: StringName, value: Variant, cfg: Dictionary = {}) -> Array[StringName]:
	var none: Array[StringName] = []
	if not value:
		return none
	var block := cfg if not cfg.is_empty() else _config()
	var joins: Dictionary = block.get(KEY_JOINS, {})
	if not joins.has(String(flag)):
		return none
	return _join(state, FirstPlayableConfig.ids(joins[String(flag)]))


static func _join(state: GameStateData, ids: Array[StringName]) -> Array[StringName]:
	var added: Array[StringName] = []
	if ids.is_empty():
		return added
	var goods := PartyGoods.from_state(ItemDB.load_default(), state)
	for cid in ids:
		if goods.join(state, cid):
			added.append(cid)
	return added


static func _config() -> Dictionary:
	return FirstPlayableConfig.section(FirstPlayableConfig.SECTION_PARTY)
