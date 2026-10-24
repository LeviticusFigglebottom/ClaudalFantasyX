class_name Inn
extends RefCounted
## One inn from game/data/items/shops.json "inns" (M2-UI-06, SPEC §6.6 towns): a full rest for a
## price in lume. Resting heals the party exactly like a save shrine (the caller's `heal`, which
## in the game emits EventBus.party_full_heal_requested so Game.heal_party fills HP and MP and
## cures party_rest.json "shrine_cures"), but an inn never saves and never moves the respawn point.
##
## Rules: the inn is open once its requires_flag is set; a rest costs `price` and needs that much
## in the purse. Every action returns RESULT_OK or an ERR_* and rest_error() previews it, so the
## UI can say why a rest is refused (pillar 4). Headless and Node-free like Shop.

const RESULT_OK := &"ok"
const ERR_UNKNOWN_INN := &"unknown_inn"
const ERR_CLOSED := &"inn_closed"
const ERR_NO_FUNDS := Shop.ERR_NO_FUNDS

var db: ItemDB
var id: StringName
var row: Dictionary


func _init(item_db: ItemDB, inn_id: StringName) -> void:
	db = item_db
	id = inn_id
	row = db.inns.get(inn_id, {})


func exists() -> bool:
	return not row.is_empty()


func name_key() -> String:
	return str(row.get("name_key", ""))


func desc_key() -> String:
	return str(row.get("desc_key", ""))


## What one night costs, in lume (0 for an unknown inn).
func price() -> int:
	return maxi(int(row.get("price", 0)), 0)


func is_open(flags: FlagReader) -> bool:
	return exists() and flags.is_set(StringName(str(row.get("requires_flag", ""))))


func rest_error(party: PartyGoods, flags: FlagReader) -> StringName:
	if not exists():
		return ERR_UNKNOWN_INN
	if not is_open(flags):
		return ERR_CLOSED
	if not party.wallet.can_afford(price()):
		return ERR_NO_FUNDS
	return RESULT_OK


## Pays for a night, then calls `heal` with this inn's id (the full rest). Returns RESULT_OK or an
## ERR_*; a refused rest changes nothing and heals no one.
func rest(party: PartyGoods, flags: FlagReader, heal: Callable) -> StringName:
	var err := rest_error(party, flags)
	if err != RESULT_OK:
		return err
	party.wallet.spend(price())
	if heal.is_valid():
		heal.call(id)
	return RESULT_OK
