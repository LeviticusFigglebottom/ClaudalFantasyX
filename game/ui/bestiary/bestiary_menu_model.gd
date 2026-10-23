class_name BestiaryMenuModel
extends RefCounted
## What the bestiary menu shows (M2-UI-02, SPEC §6.11), from the saved log (Bestiary, over
## GameStateData.bestiary) and the enemy table (enemies.json). Node-free: BestiaryMenu is its view.
##
## - entries(): every logged foe enemies.json still lists, in enemies.json order (the book's own
##   order, the same in every language). An id the table no longer lists is skipped on screen but
##   never removed from the save (Bestiary keeps it; skipped_ids() names them).
## - page(id): a Read foe's full page (EnemyPage.from_row: stats, weaknesses, lore, defeat count);
##   a foe defeated but never Read shows its name and count only (EnemyPage.name_only).
## Only the facts are saved, so the page always reflects today's enemies.json.

var book: Bestiary
## enemies.json rows by id (BattleDB.enemies).
var enemies: Dictionary

var _pages := EnemyPage.new()


func _init(log_book: Bestiary = null, enemy_rows: Dictionary = {}) -> void:
	book = log_book if log_book != null else Bestiary.new()
	enemies = enemy_rows


## The live log and enemy table the game uses.
static func from_game() -> BestiaryMenuModel:
	return BestiaryMenuModel.new(Bestiary.new(Game.state.bestiary), BattleDB.load_default().enemies)


## [{id, name, read, defeated}] for every logged foe in the table, in table order.
func entries() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var known := book.known_ids()
	for eid: Variant in enemies:
		var id := StringName(str(eid))
		if not known.has(id):
			continue
		var row: Dictionary = enemies[eid]
		var key := str(row.get("name_key", ""))
		var shown_name := tr(key) if key != "" else String(id)
		out.append({"id": id, "name": shown_name, "read": book.is_read(id), "defeated": book.defeated(id)})
	return out


## Logged ids enemies.json no longer lists (kept in the save, not shown).
func skipped_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for id in book.known_ids():
		if not enemies.has(id) and not enemies.has(String(id)):
			out.append(id)
	return out


## The EnemyPage for `id` ({} when it is not a shown entry).
func page(id: StringName) -> Dictionary:
	if not book.known_ids().has(id) or not enemies.has(id):
		return {}
	var row: Dictionary = enemies[id]
	if book.is_read(id):
		return _pages.from_row(id, row, book.defeated(id))
	return _pages.name_only(row, book.defeated(id))


## "Read 1 of 3 known" (header), or the empty-book line.
func summary() -> String:
	var shown := entries()
	if shown.is_empty():
		return tr("BESTIARY_EMPTY")
	var read := 0
	for e in shown:
		if bool(e["read"]):
			read += 1
	return tr("BESTIARY_COUNT_FMT").format({"read": read, "known": shown.size()})


## The list's right column for an entry: its defeat count.
func count_text(entry: Dictionary) -> String:
	return tr("BESTIARY_ROW_COUNT_FMT").format({"n": int(entry.get("defeated", 0))})
