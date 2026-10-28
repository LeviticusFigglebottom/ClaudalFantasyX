class_name TownMenuShot
extends Control
## Capture driver for the shop and inn shots (M2-UI-06, tests/screenshots/shots.json). It opens
## the menu on a fixed scratch save and fixed flags, so the player's save never moves a baseline:
##   - "shop_buy": Haluna Market's stock with 100 lume and two Salt Tonics held; the cursor on
##     Salt Tonic asking for 3 (120 lume), so the status line shows a refusal in the danger color;
##   - "shop_sell": the sell page with tonics, a key item and Rhen's worn and spare hooks; the
##     cursor on the worn hooks ("Rhen is wearing it");
##   - "inn": Haluna's inn with 100 lume, the cursor on Rest (its price and what it restores);
##   - "reefball_outfitter": the Reefball outfitter (ADR 0040) with 600 lume, the Brass-Thread Band
##     owned and worn, the cursor on the Kelp-Dyed Band ("in place of" the worn band).

const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const PURSE := 100
const SHOP_ID := &"haluna_market"
const INN_ID := &"haluna_inn"
const OPEN_FLAG := "ch02_met_asha"
const OUTFITTER_PURSE := 600
const OUTFITTER_OWNED := {&"rbl_gear_brass_thread_band_owned": true, &"rbl_gear_kelp_dyed_band_owned": true}
const OUTFITTER_WORN := {&"rbl_worn_band": "brass_thread_band"}

## Which view to stage: &"shop_buy", &"shop_sell", &"inn" or &"reefball_outfitter".
@export var view: StringName = &"shop_buy"

var menu: TownMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var db := ItemDB.load_default()
	var state := GameStateData.new()
	state.currency = PURSE
	var goods := PartyGoods.from_state(db, state)
	var flags := FlagReader.new()
	flags.values[OPEN_FLAG] = true
	if view == &"reefball_outfitter":
		_outfitter(state)
		return
	if view == &"inn":
		var inn := InnMenuModel.new(Inn.new(db, INN_ID), goods, flags, Callable())
		menu = (load(InnMenu.SCENE_PATH) as PackedScene).instantiate() as InnMenu
		(menu as InnMenu).configure(inn)
		_add(menu)
		return
	goods.inventory.add(&"salt_tonic", 2)
	var shop := (load(ShopMenu.SCENE_PATH) as PackedScene).instantiate() as ShopMenu
	shop.configure(ShopMenuModel.new(db, Shop.new(db, SHOP_ID), goods, flags, NAMES))
	menu = shop
	if view == &"shop_sell":
		goods.inventory.add(&"bitterleaf", 5)
		goods.inventory.add(&"brass_lantern", 1)
		goods.equipment.grant_starting(&"rhen")
		goods.equipment.add_piece(&"rhen_coral_hooks")
	_add(shop)
	if view == &"shop_sell":
		shop.handle_input(_ev(&"ui_down"))  # Buy -> Sell
		shop.accept()
		for i in 3:  # tonic, bitterleaf, lantern -> Rhen's worn hooks
			shop.handle_input(_ev(&"ui_down"))
		return
	shop.accept()  # the stock, the cursor on Salt Tonic
	shop.handle_input(_ev(&"ui_right"))
	shop.handle_input(_ev(&"ui_right"))  # 3 for 120 lume: refused


func _outfitter(state: GameStateData) -> void:
	state.currency = OUTFITTER_PURSE
	var shown := OUTFITTER_OWNED.merged(OUTFITTER_WORN)
	var model := ReefballOutfitterModel.new(
		ReefballDB.load_default(),
		Wallet.new(state, OUTFITTER_PURSE),
		func(f: StringName) -> Variant: return shown.get(f, ""),
		func(_f: StringName, _v: Variant) -> void: pass
	)
	var outfitter := (load(ReefballOutfitterMenu.SCENE_PATH) as PackedScene).instantiate() as ReefballOutfitterMenu
	outfitter.configure(model)
	menu = outfitter
	_add(outfitter)
	outfitter.handle_input(_ev(&"ui_down"))  # the Kelp-Dyed Band, owned: "in place of" the worn band


func _add(m: TownMenu) -> void:
	m.pause_tree = false
	add_child(m)


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
