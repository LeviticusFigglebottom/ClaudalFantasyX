class_name InnMenuModel
extends RefCounted
## The words and choices of the inn menu (M2-UI-06), Node-free, over one Inn and a PartyGoods.
## The view is InnMenu. Rest pays the inn's price and calls `heal` with the inn id: in the game
## that is EventBus.party_full_heal_requested, the same request a save shrine makes, so the rest
## fills HP and MP and cures party_rest.json "shrine_cures" (Game.heal_party). The inn never
## saves: the line under the page says so, and nothing here touches SaveSystem.

const ROW_REST := &"rest"
const ROW_LEAVE := &"leave"
const ROOT_IDS: Array[StringName] = [ROW_REST, ROW_LEAVE]
const LEAVE_KEY := "INN_MENU_LEAVE"
const LEAVE_DESC_KEY := "INN_MENU_LEAVE_DESC"
const REST_KEY := "INN_MENU_REST"
const REST_DESC_KEY := "INN_MENU_REST_DESC"
const NO_SAVE_KEY := "INN_MENU_NO_SAVE"
const RESTED_KEY := "INN_MENU_RESTED"
const PREVIEW_KEY := "INN_MENU_PREVIEW_FMT"
const UNKNOWN_TITLE_KEY := "INN_MENU_UNKNOWN_TITLE"
## A night that costs nothing (price 0: Sefir's guest rooms in Ansedra, Act II screens.md section 5).
const FREE_KEY := "INN_MENU_FREE"
const PREVIEW_FREE_KEY := "INN_MENU_PREVIEW_FREE"
## An inn marked `order` in shops.json turns the party away once they are outside the Level (heresy.md section 2).
const ERR_HERETIC := ShopMenuModel.ERR_HERETIC
const REFUSAL_KEYS := {
	ERR_HERETIC: "INN_ERR_HERETIC",
	Inn.ERR_UNKNOWN_INN: "INN_ERR_UNKNOWN",
	Inn.ERR_CLOSED: "INN_ERR_CLOSED",
	Inn.ERR_NO_FUNDS: "INN_ERR_NO_FUNDS_FMT",
}

var inn: Inn
var party: PartyGoods
var flags: FlagReader
## func(source_id: StringName): the full rest. Tests pass their own; from_game() asks Game.
var heal: Callable
## Rests taken through this model (tests and the view read it).
var rests := 0


func _init(with_inn: Inn, goods: PartyGoods, flag_reader: FlagReader, heal_party: Callable) -> void:
	inn = with_inn
	party = goods
	flags = flag_reader
	heal = heal_party


## The live menu: inn `inn_id` over Game.state; a rest requests EventBus.party_full_heal_requested.
static func from_game(inn_id: StringName) -> InnMenuModel:
	var item_db := ItemDB.load_default()
	return InnMenuModel.new(
		Inn.new(item_db, inn_id),
		PartyGoods.from_state(item_db, Game.state),
		FlagReader.from_access(GameFlagAccess.new()),
		func(source: StringName) -> void: EventBus.party_full_heal_requested.emit(source)
	)


func title() -> String:
	return _tr(inn.name_key()) if inn.exists() else _tr(UNKNOWN_TITLE_KEY)


func lume(amount: int) -> String:
	return _tr(ShopMenuModel.AMOUNT_KEY) % amount


func purse_text() -> String:
	return _tr(ShopMenuModel.PURSE_KEY).format({"amount": lume(party.wallet.amount())})


## Rest (with its price on the right, disabled-colored when refused) and Leave.
func root_rows() -> Array[Dictionary]:
	var ok := rest_error() == Inn.RESULT_OK
	return [
		{
			"id": ROW_REST,
			"label": _tr(REST_KEY),
			"right": price_text(),
			"right_role": &"text" if ok else &"text_disabled",
			"enabled": inn.exists() and inn.is_open(flags) and not _heretic(),
		},
		{"id": ROW_LEAVE, "label": _tr(LEAVE_KEY), "right": "", "enabled": true},
	]


## What the highlighted row does. Rest: the inn's own words, what a rest restores, and that it
## does not save.
func row_desc(id: StringName) -> String:
	if id == ROW_LEAVE:
		return _tr(LEAVE_DESC_KEY)
	var lines: Array[String] = []
	var own := _tr(inn.desc_key())
	if own != "":
		lines.append(own)
	lines.append(_tr(REST_DESC_KEY))
	lines.append(_tr(NO_SAVE_KEY))
	return "\n".join(lines)


## A night's price as the Rest row shows it ("No charge" when it is free).
func price_text() -> String:
	return _tr(FREE_KEY) if inn.price() == 0 else lume(inn.price())


## Why the party can't rest here now (Inn.rest_error, then the heresy for an Order house), or RESULT_OK.
func rest_error() -> StringName:
	return ERR_HERETIC if _heretic() else inn.rest_error(party, flags)


## {text, ok}: the cost of a night, or why the inn turns the party away.
func rest_line() -> Dictionary:
	var err := rest_error()
	if err != Inn.RESULT_OK:
		return {"text": refusal_text(err), "ok": false}
	if inn.price() == 0:
		return {"text": _tr(PREVIEW_FREE_KEY), "ok": true}
	return {"text": _tr(PREVIEW_KEY).format({"price": lume(inn.price())}), "ok": true}


## Pays and rests. Returns {ok, text}: "The party wakes restored." or the refusal.
func rest() -> Dictionary:
	var err := ERR_HERETIC if _heretic() else inn.rest(party, flags, heal)
	if err != Inn.RESULT_OK:
		return {"text": refusal_text(err), "ok": false}
	rests += 1
	return {"text": _tr(RESTED_KEY), "ok": true}


func refusal_text(err: StringName) -> String:
	var key := str(REFUSAL_KEYS.get(err, ""))
	if key == "":
		return ""
	return _tr(key).format({"price": lume(inn.price()), "purse": lume(party.wallet.amount())})


func _heretic() -> bool:
	return bool(inn.row.get(ShopMenuModel.KEY_ORDER, false)) and flags.is_set(ShopMenuModel.HERETIC_FLAG)


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""
