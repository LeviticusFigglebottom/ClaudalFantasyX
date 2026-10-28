class_name BattleRewards
extends RefCounted
## The result panel's victory rows and the Lattice award behind them. Moved out of
## BattleController (M1-CMB-04) unchanged, to keep the controller under the file-length cap.
## M2-CMB-07: a live victory also pays the engine's lume and drops into the party's goods (pay()),
## and the panel lists them under the fighters (spoil_rows()). Fixtures and tests only list them.

## pay()'s record (ctl.last_spoils): the engine's lume, what reached the purse (the cap may hold
## some back), the purse after it (-1 unpaid), the drops (item id -> count) and how many of each
## fitted in the bag.
const KEY_LUME := "lume"
const KEY_LUME_ADDED := "lume_added"
const KEY_PURSE := "purse"
const KEY_DROPS := "drops"
const KEY_KEPT := "kept"
const KEY_PAID := "paid"
## Marks the panel rows that are spoils, not fighters.
const ROW_SPOILS := "spoils"


## XP from engine.xp_awards() becomes Lattice movement points (formulas.md, Progression). Fills
## `ctl.last_awards` and, for a live battle, writes the Lattice back to Game.state. Then the spoils:
## paid into Game.state for a live battle, listed either way (ctl.last_spoils).
func award_victory(ctl: BattleController) -> Array[Dictionary]:
	var engine := ctl.engine
	var progress := ctl.progress
	var awards := engine.xp_awards()
	var rows: Array[Dictionary] = []
	for c in engine.party_active + engine.party_reserve:
		if not c.participated:
			continue
		var label := ctl.menus.display_name(c)
		if not awards.has(c.id):
			rows.append(
				{"label": label, "xp_text": "", "moves_text": tr("HUD_RESULT_FELL"), "fell": true, "fighter": c.id}
			)
			continue
		var xp := int(awards[c.id])
		var moves := -1
		if progress != null and progress.traveler(c.id) != null:
			moves = progress.award_battle(c.id, xp)
		ctl.last_awards[c.id] = {"xp": xp, "moves": moves}
		var moves_text := tr("HUD_RESULT_MOVES_FMT").format({"n": moves}) if moves >= 0 else tr("HUD_RESULT_NO_LATTICE")
		var count: Array[Dictionary] = [{"cell": "xp", "key": "HUD_RESULT_XP_FMT", "arg": "xp", "n": xp}]
		if moves >= 0:
			count.append({"cell": "moves", "key": "HUD_RESULT_MOVES_FMT", "arg": "n", "n": moves})
		(
			rows
			. append(
				{
					"label": label,
					"fighter": c.id,
					"xp_text": tr("HUD_RESULT_XP_FMT").format({"xp": xp}),
					"moves_text": moves_text,
					"count": count,
				}
			)
		)
	var live := ctl.persist_progress and ctl.fixture == null
	if live and progress != null:
		# M1-ARC-13: refused (the save keeps its progress) while the Lattice tables are broken.
		progress.save_into(Game.state)
	var item_db := ItemDB.load_default()
	var wallet := Wallet.new(Game.state, item_db.currency_cap) if live else null
	ctl.last_spoils = pay(engine, wallet, Inventory.new(item_db, Game.state.inventory) if live else null)
	rows.append_array(spoil_rows(ctl.last_spoils, item_db))
	return rows


## Pays `engine`'s victory spoils (formulas.md § Rewards: currency_award(), drop_awards()) into
## the party's purse and bag (both wrap GameStateData in place, so it is what gets saved): the lume
## through Wallet.earn, each drop through Inventory.add (a full stack keeps what fits). With
## `wallet` null it only reports them (KEY_PAID false). Any outcome but victory pays nothing.
static func pay(engine: BattleEngine, wallet: Wallet, bag: Inventory) -> Dictionary:
	var lume := engine.currency_award()
	var drops := engine.drop_awards()
	var kept: Dictionary = {}
	var added := 0
	if wallet != null:
		added = wallet.earn(lume)
		for iid: StringName in drops:
			kept[iid] = bag.add(iid, int(drops[iid]))
	return {
		KEY_LUME: lume,
		KEY_LUME_ADDED: added,
		KEY_PURSE: wallet.amount() if wallet != null else -1,
		KEY_DROPS: drops,
		KEY_KEPT: kept,
		KEY_PAID: wallet != null,
	}


## The panel rows for pay()'s record: the lume (and the purse, once paid), then one row per drop
## in roll order, marked when a full stack left some behind. No rows when nothing was won.
func spoil_rows(spoils: Dictionary, item_db: ItemDB) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var paid := bool(spoils.get(KEY_PAID, false))
	var lume := int(spoils.get(KEY_LUME, 0))
	if lume > 0:
		var purse := tr("HUD_RESULT_PURSE_FMT").format({"n": int(spoils[KEY_PURSE])}) if paid else ""
		(
			rows
			. append(
				{
					"label": tr("HUD_RESULT_LUME"),
					"glyph": MenuGlyph.for_currency(),
					"xp_text": tr("HUD_RESULT_LUME_FMT").format({"n": lume}),
					"moves_text": purse,
					"count": [{"cell": "xp", "key": "HUD_RESULT_LUME_FMT", "arg": "n", "n": lume}],
					ROW_SPOILS: true,
				}
			)
		)
	var drops: Dictionary = spoils.get(KEY_DROPS, {})
	var kept: Dictionary = spoils.get(KEY_KEPT, {})
	for iid: StringName in drops:
		var n := int(drops[iid])
		var full := paid and int(kept.get(iid, 0)) < n
		(
			rows
			. append(
				{
					"label": tr(str(item_db.item(iid).get("name_key", iid))),
					"glyph": MenuGlyph.for_goods(iid),
					"xp_text": tr("HUD_RESULT_DROP_FMT").format({"n": n}),
					"count": [{"cell": "xp", "key": "HUD_RESULT_DROP_FMT", "arg": "n", "n": n}],
					"moves_text": tr("HUD_RESULT_BAG_FULL") if full else "",
					ROW_SPOILS: true,
				}
			)
		)
	return rows
