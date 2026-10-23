class_name Wallet
extends RefCounted
## The party's currency, lume (SPEC §6.5; the name is decided in docs/kb/design/economy.md).
## Wraps GameStateData.currency so shops, battle rewards and the UI all change the same number.
## The purse never goes below 0 or above its cap (ItemDB.currency_cap).

var state: GameStateData
var cap: int


func _init(game_state: GameStateData, currency_cap: int) -> void:
	state = game_state
	cap = currency_cap


func amount() -> int:
	return state.currency


func can_afford(price: int) -> bool:
	return price >= 0 and state.currency >= price


## Pays `price`; returns false (and changes nothing) if the party can't afford it.
func spend(price: int) -> bool:
	if not can_afford(price):
		return false
	state.currency -= price
	return true


## Adds lume up to the cap. Returns how much was actually added.
func earn(value: int) -> int:
	if value <= 0:
		return 0
	var added := mini(value, maxi(cap - state.currency, 0))
	state.currency += added
	return added
