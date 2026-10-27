class_name PartySheet
extends RefCounted
## The party as the field menus see it (M2-MNU-01..04): each hero built exactly the way a live
## battle builds them (BattleVitals.setup), so the Status page, the Equip preview and a potion
## used from the Items page agree with the next fight:
##   characters.json base -> Lattice (LatticeProgress.apply_to) -> worn gear (EquipmentEffects)
##   -> the saved vitals (GameStateData.apply_vitals_to), LAST, so HP and MP clamp to the maxima.
## Gear's battle-only statuses (auto-Haste and the like) are left off: out of battle a hero carries
## only the statuses the save keeps. Node-free; it reads and writes `state` in place.
##
## Heroes: FieldMenuModel.field_heroes() (the joined party, or the first playable's stand-in).

## The save every page reads and writes (Game.state for the live menus).
var state: GameStateData
## Heroes in party order.
var heroes: Array[StringName] = []
var battle_db: BattleDB
var item_db: ItemDB
## The bag, the gear and the purse, wrapping `state` in place.
var goods: PartyGoods
## Lattice progress for `heroes` on the board the save names (BattleStage.lattice_for). Changes
## reach the save only through save_lattice().
var lattice: LatticeProgress
var effects: EquipmentEffects


func _init(
	with_state: GameStateData = null,
	hero_ids: Array[StringName] = [],
	with_battle_db: BattleDB = null,
	with_item_db: ItemDB = null
) -> void:
	state = with_state if with_state != null else GameStateData.new()
	heroes = hero_ids.duplicate()
	battle_db = with_battle_db if with_battle_db != null else BattleDB.load_default()
	item_db = with_item_db if with_item_db != null else ItemDB.load_default()
	goods = PartyGoods.from_state(item_db, state)
	lattice = BattleStage.lattice_for(heroes, state.lattice)
	effects = EquipmentEffects.new(item_db, goods.equipment)


## The live party: Game.state and the field menu's heroes.
static func from_game() -> PartySheet:
	return PartySheet.new(Game.state, FieldMenuModel.field_heroes())


## `cid` as characters.json alone builds them (no Lattice, gear or vitals); null if unknown.
func base_combatant(cid: StringName) -> BattleCombatant:
	if not battle_db.characters.has(cid):
		return null
	return BattleCombatant.from_dict(cid, BattleCombatant.TEAM_PARTY, battle_db.characters[cid])


## `cid` now: base, Lattice, worn gear, then the saved HP, MP and carried statuses. Null if unknown.
func combatant(cid: StringName) -> BattleCombatant:
	var c := base_combatant(cid)
	if c == null:
		return null
	lattice.apply_to(c)
	effects.apply_to(c)
	c.statuses.clear()  # gear's whole-battle statuses start with a fight, not in the field
	state.apply_vitals_to(c, Game.carried_duration())
	return c


func hero_name(cid: StringName) -> String:
	var row: Dictionary = battle_db.characters.get(cid, {})
	return CharacterNames.display(cid, str(row.get("name_key", "")))  # "The Kirru" until named (M3-C09-05)


## Writes the Lattice progress back into `state` (LatticeProgress.save_into: refused, keeping the
## save as it was, while the board or rules are broken). Returns true when it wrote.
func save_lattice() -> bool:
	return lattice.save_into(state)
