class_name TownServices
extends Node
## The zone-agnostic shop and inn hook (M2-UI-06). It listens to FieldEvents.INTERACTED on the
## EventBus and opens a menu for these payload keys, so a zone only authors an Interactable:
##   {"shop": "<shop id>"}  -> ShopMenu over that shops.json "shops" row,
##   {"inn": "<inn id>"}    -> InnMenu over that shops.json "inns" row,
##   {"reefball_outfitter": "<id>"} -> ReefballOutfitterMenu (Reefball-only gear, ADR 0040).
## Any other payload is ignored (story scripts such as HalunaStory read their own keys). Only one
## town menu is open at a time; a second interaction while one is open does nothing.
## FieldController adds one as a child in every zone, so the menu's layer hangs under the player.
## Tests build their own and call handle(), or give `model_factory` scratch models.

signal opened(menu: TownMenu)

const KEY_SHOP := "shop"
const KEY_INN := "inn"
const KEY_OUTFITTER := "reefball_outfitter"

## Optional func(key: String, id: StringName) -> RefCounted (a ShopMenuModel, InnMenuModel or
## ReefballOutfitterModel).
## Unset: the live game (ShopMenuModel.from_game / InnMenuModel.from_game).
var model_factory: Callable
## The menu on show (null when none).
var menu: TownMenu


func _enter_tree() -> void:
	FieldEvents.connect_interacted(_on_interacted)


func _exit_tree() -> void:
	if EventBus.is_connected(FieldEvents.INTERACTED, _on_interacted):
		EventBus.disconnect(FieldEvents.INTERACTED, _on_interacted)


func is_menu_open() -> bool:
	return menu != null and is_instance_valid(menu) and menu.is_open()


## Opens the shop or inn a payload names. Returns the menu, or null for any other payload (or
## while a town menu is already open).
func handle(payload: Dictionary) -> TownMenu:
	if is_menu_open():
		return null
	if payload.has(KEY_SHOP):
		var sm := _model(KEY_SHOP, StringName(str(payload[KEY_SHOP]))) as ShopMenuModel
		menu = ShopMenu.open_in(self, sm)
	elif payload.has(KEY_INN):
		var im := _model(KEY_INN, StringName(str(payload[KEY_INN]))) as InnMenuModel
		menu = InnMenu.open_in(self, im)
	elif payload.has(KEY_OUTFITTER):
		var om := _model(KEY_OUTFITTER, StringName(str(payload[KEY_OUTFITTER]))) as ReefballOutfitterModel
		menu = ReefballOutfitterMenu.open_in(self, om)
	else:
		return null
	menu.closed.connect(_on_closed)
	opened.emit(menu)
	return menu


func _model(key: String, id: StringName) -> RefCounted:
	if model_factory.is_valid():
		return model_factory.call(key, id)
	if key == KEY_OUTFITTER:
		return ReefballOutfitterModel.from_game()
	return ShopMenuModel.from_game(id) if key == KEY_SHOP else InnMenuModel.from_game(id)


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	handle(payload)


func _on_closed() -> void:
	menu = null
