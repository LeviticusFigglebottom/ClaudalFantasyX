class_name ReefballOutfitterModel
extends RefCounted
## The words and choices of the Reefball outfitter (ADR 0040, M3-C07-05), Node-free: Reefball-only
## gear (game/data/reefball/gear.json) bought with lume and worn by the side in its matches. It never
## touches battle equipment. Owning a piece is the flag rbl_gear_<id>_owned; the worn piece of each
## kind is the flag rbl_worn_<kind> (a gear id, or ""). One piece of each kind is worn at a time:
## buying a piece wears it when nothing of its kind is worn, and choosing an owned piece puts it on
## (taking off the other of its kind) or takes it off. The view is ReefballOutfitterMenu; the match
## flow passes worn_ids() to ReefballMatch.setup.

const ROW_LEAVE := &"leave"
const OWNED_FLAG_FMT := "rbl_gear_%s_owned"
const WORN_FLAG_FMT := "rbl_worn_%s"
const TITLE_KEY := "RBL_OUTFIT_TITLE"
const OWNED_KEY := "RBL_OUTFIT_OWNED"
const WORN_KEY := "RBL_OUTFIT_WORN"
const LEAVE_KEY := "RBL_OUTFIT_LEAVE"
const LEAVE_DESC_KEY := "RBL_OUTFIT_LEAVE_DESC"
const BONUS_FMT_KEY := "RBL_OUTFIT_BONUS_FMT"
const BONUS_JOIN_KEY := "RBL_OUTFIT_BONUS_JOIN"
const STAT_KEY_FMT := "RBL_STAT_%s"
const BUY_FMT_KEY := "RBL_OUTFIT_BUY_FMT"
const NO_FUNDS_FMT_KEY := "RBL_OUTFIT_NO_FUNDS_FMT"
const WEAR_FMT_KEY := "RBL_OUTFIT_WEAR_FMT"
const SWAP_FMT_KEY := "RBL_OUTFIT_SWAP_FMT"
const TAKE_OFF_FMT_KEY := "RBL_OUTFIT_TAKE_OFF_FMT"
const BOUGHT_FMT_KEY := "RBL_OUTFIT_BOUGHT_FMT"
const NOW_WORN_FMT_KEY := "RBL_OUTFIT_NOW_WORN_FMT"
const TAKEN_OFF_FMT_KEY := "RBL_OUTFIT_TAKEN_OFF_FMT"
const PURSE_KEY := "SHOP_MENU_PURSE_FMT"
const AMOUNT_KEY := "CURRENCY_AMOUNT"

var db: ReefballDB
var wallet: Wallet
## (flag: StringName) -> Variant, and (flag: StringName, value: Variant) -> void.
var get_flag: Callable
var set_flag: Callable


func _init(reefball: ReefballDB, purse: Wallet, read_flag: Callable, write_flag: Callable) -> void:
	db = reefball
	wallet = purse
	get_flag = read_flag
	set_flag = write_flag


static func from_game() -> ReefballOutfitterModel:
	var goods := PartyGoods.from_state(ItemDB.load_default(), Game.state)
	return ReefballOutfitterModel.new(
		ReefballDB.load_default(),
		goods.wallet,
		func(f: StringName) -> Variant: return Game.get_flag(f, ""),
		func(f: StringName, v: Variant) -> void: Game.set_flag(f, v)
	)


## The gear the side wears, one per kind, in gear.json order (for ReefballMatch.setup).
static func worn_ids(reefball: ReefballDB, read_flag: Callable) -> Array[StringName]:
	var out: Array[StringName] = []
	for gid: StringName in reefball.gear:
		var kind := str((reefball.gear[gid] as Dictionary).get("kind", ""))
		if StringName(str(read_flag.call(StringName(WORN_FLAG_FMT % kind)))) == gid:
			out.append(gid)
	return out


func title() -> String:
	return _tr(TITLE_KEY)


func purse_text() -> String:
	return _tr(PURSE_KEY).format({"amount": lume(wallet.amount())})


func lume(amount: int) -> String:
	return _tr(AMOUNT_KEY) % amount


func ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for gid: StringName in db.gear:
		out.append(gid)
	out.append(ROW_LEAVE)
	return out


## Menu rows: each piece with its price, Owned or Worn on the right; Leave last.
func rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for gid: StringName in db.gear:
		var right := lume(price(gid))
		if is_worn(gid):
			right = _tr(WORN_KEY)
		elif is_owned(gid):
			right = _tr(OWNED_KEY)
		out.append({"id": gid, "label": name_of(gid), "right": right, "enabled": true})
	out.append({"id": ROW_LEAVE, "label": _tr(LEAVE_KEY), "right": "", "enabled": true})
	return out


func name_of(gid: StringName) -> String:
	return _tr(str(_row(gid).get("name_key", "")))


func price(gid: StringName) -> int:
	return int(_row(gid).get("price", 0))


func kind_of(gid: StringName) -> String:
	return str(_row(gid).get("kind", ""))


func is_owned(gid: StringName) -> bool:
	var v: Variant = get_flag.call(StringName(OWNED_FLAG_FMT % gid))
	return typeof(v) == TYPE_BOOL and bool(v)


func is_worn(gid: StringName) -> bool:
	return worn_of(kind_of(gid)) == gid


## The piece of `kind` the side wears (&"" for none).
func worn_of(kind: String) -> StringName:
	return StringName(str(get_flag.call(StringName(WORN_FLAG_FMT % kind))))


## The line about a row: the piece's words and what it adds ("Grip +1 · Strip +1").
func row_desc(gid: StringName) -> String:
	if gid == ROW_LEAVE:
		return _tr(LEAVE_DESC_KEY)
	return "%s\n%s" % [_tr(str(_row(gid).get("desc_key", ""))), bonus_text(gid)]


func bonus_text(gid: StringName) -> String:
	var parts: Array[String] = []
	var bonus: Dictionary = _row(gid).get("bonus", {})
	for stat: Variant in bonus:
		var stat_name := _tr(STAT_KEY_FMT % str(stat).to_upper())
		parts.append(_tr(BONUS_FMT_KEY).format({"stat": stat_name, "amount": int(bonus[stat])}))
	return _tr(BONUS_JOIN_KEY).join(parts)


## What choosing the row would do: {"ok", "text"} (a refusal has ok false).
func row_line(gid: StringName) -> Dictionary:
	if gid == ROW_LEAVE:
		return {}
	var piece := {"name": name_of(gid), "price": lume(price(gid))}
	if not is_owned(gid):
		if not wallet.can_afford(price(gid)):
			return {"ok": false, "text": _tr(NO_FUNDS_FMT_KEY).format(piece)}
		return {"ok": true, "text": _tr(BUY_FMT_KEY).format(piece)}
	if is_worn(gid):
		return {"ok": true, "text": _tr(TAKE_OFF_FMT_KEY).format(piece)}
	var other := worn_of(kind_of(gid))
	if other != &"":
		return {"ok": true, "text": _tr(SWAP_FMT_KEY).format({"name": name_of(gid), "other": name_of(other)})}
	return {"ok": true, "text": _tr(WEAR_FMT_KEY).format(piece)}


## Chooses the row: buys (and wears, if nothing of its kind is worn), puts on, or takes off. Returns
## the status line {"ok", "text"}; a refusal changes nothing.
func choose(gid: StringName) -> Dictionary:
	if not db.gear.has(gid):
		return {}
	var piece := {"name": name_of(gid)}
	if not is_owned(gid):
		if not wallet.spend(price(gid)):
			return row_line(gid)
		set_flag.call(StringName(OWNED_FLAG_FMT % gid), true)
		if worn_of(kind_of(gid)) == &"":
			_wear(gid)
		return {"ok": true, "text": _tr(BOUGHT_FMT_KEY).format(piece)}
	if is_worn(gid):
		set_flag.call(StringName(WORN_FLAG_FMT % kind_of(gid)), "")
		return {"ok": true, "text": _tr(TAKEN_OFF_FMT_KEY).format(piece)}
	_wear(gid)
	return {"ok": true, "text": _tr(NOW_WORN_FMT_KEY).format(piece)}


func _wear(gid: StringName) -> void:
	set_flag.call(StringName(WORN_FLAG_FMT % kind_of(gid)), String(gid))


func _row(gid: StringName) -> Dictionary:
	return db.gear.get(gid, {}) as Dictionary


static func _tr(key: String) -> String:
	return str(TranslationServer.translate(key)) if key != "" else ""
