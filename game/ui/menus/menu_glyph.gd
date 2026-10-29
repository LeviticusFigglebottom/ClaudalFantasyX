class_name MenuGlyph
extends Control
## An item, equipment or ability icon drawn as vector strokes on a 48-unit grid, in StatusGlyph's
## style (docs/kb/art/ui.md §8: a flat tint backing behind a 2-unit stroke; original shapes). Each
## glyph is its own silhouette, so none depends on hue. Which glyph a thing shows, the backing's
## shape and the colour role of each family are data: game/data/ui/menu_glyphs.json (MenuGlyph.for_item,
## for_equipment, for_skill). Act I final pass (ADR 0041): the menus' rows had no icons.

const DATA_PATH := "res://game/data/ui/menu_glyphs.json"
const GRID := 48.0
const STROKE := 2.0
const ARC_STEPS := 16
## Every glyph with a drawing (tests check the data names none other).
const DRAWN: Array[StringName] = [
	&"bangle",
	&"blade",
	&"bolt",
	&"book",
	&"bottle",
	&"cleaver",
	&"cog",
	&"coral",
	&"crystals",
	&"cup",
	&"drop",
	&"feather",
	&"flame",
	&"flask",
	&"frost",
	&"gem",
	&"gem_key",
	&"guards",
	&"harness",
	&"hooks",
	&"jar",
	&"key",
	&"lantern",
	&"launcher",
	&"leaf",
	&"lume",
	&"mote",
	&"needle",
	&"net",
	&"pearl",
	&"pot",
	&"quick",
	&"scale",
	&"shard",
	&"shell",
	&"shield",
	&"sleeve",
	&"spark",
	&"spear",
	&"staff",
	&"ward",
	&"wave",
	&"wick",
	&"wraps",
]

static var _cache: Dictionary = {}
## Item id -> category and equipment id -> type (items.json, equipment.json), read once.
static var _goods: Dictionary = {}

var glyph: StringName = &""
## The palette role the strokes use (menu_glyphs.json families).
var role: StringName = &"text"


func _init(id: StringName = &"", color_role: StringName = &"text") -> void:
	glyph = id
	role = color_role
	mouse_filter = Control.MOUSE_FILTER_IGNORE


static func data() -> Dictionary:
	if _cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_cache = (parsed as Dictionary).get("menu_glyphs", {}) as Dictionary
	return _cache


## {glyph, role} for item `id` (its own glyph, else its category's); {} when it has neither.
static func for_item(id: StringName, category: String) -> Dictionary:
	var d := data()
	var g := str((d.get("items", {}) as Dictionary).get(String(id), ""))
	if g == "":
		g = str((d.get("item_categories", {}) as Dictionary).get(category, ""))
	return _entry(g, str((d.get("item_roles", {}) as Dictionary).get(category, "text")))


## {glyph, role} for equipment of type `type` (equipment.json "type").
static func for_equipment(type: String) -> Dictionary:
	var d := data()
	return _entry(str((d.get("equipment_types", {}) as Dictionary).get(type, "")), str(d.get("equipment_role", "text")))


## {glyph, role} for a skill: its element's glyph when it has one, else its kind's.
static func for_skill(kind: String, element: String) -> Dictionary:
	var d := data()
	var by_element: Dictionary = d.get("skill_elements", {})
	var key := element if by_element.has(element) else ""
	var g := str(by_element.get(key, "")) if key != "" else str((d.get("skill_kinds", {}) as Dictionary).get(kind, ""))
	var roles: Dictionary = d.get("skill_roles", {})
	return _entry(g, str(roles.get(kind, roles.get("", "text"))))


## {glyph, role} for an item or a piece of equipment by id (shops, the bag, the battle's Items, the loot).
static func for_goods(id: StringName) -> Dictionary:
	if _goods.is_empty():
		var db := ItemDB.load_default()
		for iid: Variant in db.items:
			_goods[StringName(str(iid))] = ["item", str((db.items[iid] as Dictionary).get("category", ""))]
		for eid: Variant in db.equipment:
			_goods[StringName(str(eid))] = ["equipment", str((db.equipment[eid] as Dictionary).get("type", ""))]
	var g: Array = _goods.get(id, [])
	if g.is_empty():
		return {}
	return for_equipment(str(g[1])) if g[0] == "equipment" else for_item(id, str(g[1]))


## {glyph, role} for the currency (the result panel's lume).
static func for_currency() -> Dictionary:
	return _entry(str(data().get("currency", "")), str(data().get("currency_role", "text")))


## {glyph, role} for skill row `skill` (a skills.json row).
static func for_skill_row(skill: Dictionary) -> Dictionary:
	return for_skill(str(skill.get("kind", "")), str(skill.get("element", "")))


static func _entry(g: String, r: String) -> Dictionary:
	return {} if g == "" else {"glyph": StringName(g), "role": StringName(r)}


## A glyph sized and placed for a menu row of height `row_h` at x `x` (MenuPage), or null for {}.
static func for_row(entry: Dictionary, x: float, row_h: float) -> MenuGlyph:
	if entry.is_empty():
		return null
	var px := float(data().get("row_px", 0.0))
	var g := MenuGlyph.new(StringName(str(entry["glyph"])), StringName(str(entry.get("role", "text"))))
	g.position = Vector2(x, (row_h - px) * 0.5)
	g.size = Vector2(px, px)
	return g


func _draw() -> void:
	if glyph == &"":
		return
	var col := get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
	var s := minf(size.x, size.y) / GRID
	var w := maxf(STROKE * s * 1.5, 1.0)
	var p := func(x: float, y: float) -> Vector2: return Vector2(x, y) * s
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.5
	draw_circle(c, r, Color(col, float(data().get("tint_alpha", 0.0))))
	if not _draw_item(p, col, w, s):
		if not _draw_gear(p, col, w, s):
			_draw_skill(p, col, w, s)


## The consumables, materials, facets and key items.
func _draw_item(p: Callable, col: Color, w: float, s: float) -> bool:
	match glyph:
		&"bottle":  # a tonic: a round-shouldered bottle, its neck and cork
			_poly(
				[
					p.call(17, 36),
					p.call(17, 24),
					p.call(21, 19),
					p.call(21, 13),
					p.call(27, 13),
					p.call(27, 19),
					p.call(31, 24),
					p.call(31, 36)
				],
				col,
				w,
				true
			)
			draw_line(p.call(20, 11), p.call(28, 11), col, w)
			draw_line(p.call(18, 28), p.call(30, 28), col, w)
		&"flask":  # a draught: a round flask whose shoulders meet its neck
			var neck := asin(3.0 / 9.0)
			draw_arc(p.call(24, 29), 9 * s, -PI * 0.5 + neck, PI * 1.5 - neck, ARC_STEPS * 2, col, w)
			_poly([p.call(21, 20.5), p.call(21, 12), p.call(27, 12), p.call(27, 20.5)], col, w)
			draw_line(p.call(19, 12), p.call(29, 12), col, w)
		&"leaf":
			draw_arc(p.call(30, 30), 14 * s, PI * 0.95, PI * 1.55, ARC_STEPS, col, w)
			draw_arc(p.call(18, 18), 14 * s, -PI * 0.05, PI * 0.55, ARC_STEPS, col, w)
			draw_line(p.call(14, 34), p.call(33, 15), col, w)
		&"drop":
			_drop(p, col, w, s, Vector2(24, 26), 1.0)
		&"quick":  # a drop that runs ahead of itself
			_drop(p, col, w, s, Vector2(20, 26), 0.85)
			_poly([p.call(30, 18), p.call(35, 24), p.call(30, 30)], col, w)
			_poly([p.call(34, 18), p.call(39, 24), p.call(34, 30)], col, w)
		&"crystals":  # smelling salts: three small crystals
			for at: Vector2 in [Vector2(17, 29), Vector2(24, 20), Vector2(31, 29)]:
				_diamond(p, col, w, at, 5.0)
		&"cup":
			_poly([p.call(14, 22), p.call(16, 34), p.call(30, 34), p.call(32, 22)], col, w, true)
			draw_arc(p.call(33, 27), 3.5 * s, -PI * 0.5, PI * 0.5, 8, col, w)
			draw_arc(p.call(20, 15), 3 * s, PI * 0.5, PI * 1.5, 8, col, w)
			draw_arc(p.call(26, 15), 3 * s, PI * 0.5, PI * 1.5, 8, col, w)
		&"jar":  # a salve
			draw_rect(Rect2(p.call(15, 20), p.call(18, 15)), col, false, w)
			draw_rect(Rect2(p.call(13, 15), p.call(22, 5)), col, false, w)
		&"wick":  # a candle stub and its flame
			draw_rect(Rect2(p.call(19, 26), p.call(10, 11)), col, false, w)
			_flame(p, col, w, Vector2(24, 18), 0.6)
		&"net":
			for i in 3:
				draw_line(p.call(13 + 7 * i, 13), p.call(27 + 7 * i, 35), col, w * 0.7)
				draw_line(p.call(35 - 7 * i, 13), p.call(21 - 7 * i, 35), col, w * 0.7)
		&"pot":  # an ember pot: a round pot with a flame at its mouth
			draw_arc(p.call(24, 29), 9 * s, -PI * 0.15, PI * 1.15, ARC_STEPS, col, w)
			draw_line(p.call(17, 22), p.call(31, 22), col, w)
			_flame(p, col, w, Vector2(24, 15), 0.5)
		&"shell":  # a fan shell, ribbed
			draw_arc(p.call(24, 34), 14 * s, PI, TAU, ARC_STEPS, col, w)
			draw_line(p.call(10, 34), p.call(38, 34), col, w)
			for a: float in [-0.6, -0.2, 0.2, 0.6]:
				draw_line(p.call(24, 34), p.call(24, 34) + Vector2(sin(a), -cos(a)) * 14.0 * s, col, w * 0.7)
		&"lantern":
			draw_rect(Rect2(p.call(17, 17), p.call(14, 16)), col, false, w)
			draw_arc(p.call(24, 17), 5 * s, PI, TAU, 8, col, w)
			draw_line(p.call(24, 21), p.call(24, 29), col, w)
			draw_line(p.call(15, 35), p.call(33, 35), col, w)
		&"feather":
			draw_line(p.call(14, 36), p.call(34, 12), col, w)
			draw_arc(p.call(30, 24), 9 * s, PI * 0.6, PI * 1.45, ARC_STEPS, col, w)
			draw_arc(p.call(18, 22), 9 * s, -PI * 0.4, PI * 0.45, ARC_STEPS, col, w)
		&"coral":
			_poly([p.call(24, 36), p.call(24, 22), p.call(17, 13)], col, w)
			_poly([p.call(24, 26), p.call(31, 17), p.call(33, 11)], col, w)
			_poly([p.call(20, 18), p.call(14, 18)], col, w)
		&"pearl":
			draw_arc(p.call(24, 24), 10 * s, 0.0, TAU, ARC_STEPS * 2, col, w)
			draw_arc(p.call(24, 24), 5 * s, PI * 1.05, PI * 1.45, 6, col, w)
		&"scale":  # overlapping scales, two rows
			for at: Vector2 in [Vector2(18, 21), Vector2(30, 21), Vector2(12, 31), Vector2(24, 31), Vector2(36, 31)]:
				draw_arc(p.call(at.x, at.y), 6 * s, PI, TAU, ARC_STEPS, col, w)
		&"shard":
			_poly([p.call(22, 11), p.call(32, 21), p.call(27, 37), p.call(16, 27)], col, w, true)
			draw_line(p.call(22, 11), p.call(24, 26), col, w * 0.7)
			draw_line(p.call(16, 27), p.call(24, 26), col, w * 0.7)
		&"cog":
			draw_arc(p.call(24, 24), 9 * s, 0.0, TAU, ARC_STEPS * 2, col, w)
			draw_arc(p.call(24, 24), 3.5 * s, 0.0, TAU, ARC_STEPS, col, w)
			for i in 8:
				var a := TAU * i / 8.0
				draw_line(
					p.call(24, 24) + Vector2(cos(a), sin(a)) * 9.0 * s,
					p.call(24, 24) + Vector2(cos(a), sin(a)) * 13.0 * s,
					col,
					w
				)
		&"needle":
			draw_line(p.call(13, 35), p.call(35, 13), col, w)
			draw_arc(p.call(32, 16), 3 * s, 0.0, TAU, 8, col, w * 0.8)
			draw_arc(p.call(22, 30), 7 * s, PI * 0.2, PI * 1.1, ARC_STEPS, col, w * 0.7)
		&"gem":
			_gem(p, col, w)
		&"gem_key":  # a key facet: the gem with a keyhole
			_gem(p, col, w)
			draw_circle(p.call(24, 25), 2.2 * s, col)
			draw_line(p.call(24, 26), p.call(24, 31), col, w)
		&"lume":  # the currency: a coin with a small flame inside
			draw_arc(p.call(24, 24), 12 * s, 0.0, TAU, ARC_STEPS * 2, col, w)
			_flame(p, col, w, Vector2(24, 25), 0.55)
		&"key":
			draw_arc(p.call(17, 19), 6 * s, 0.0, TAU, ARC_STEPS, col, w)
			draw_line(p.call(21, 23), p.call(35, 37), col, w)
			draw_line(p.call(29, 31), p.call(32, 28), col, w)
			draw_line(p.call(32, 34), p.call(35, 31), col, w)
		_:
			return false
	return true


## The heroes' weapons and gear, one glyph per equipment type.
func _draw_gear(p: Callable, col: Color, w: float, s: float) -> bool:
	match glyph:
		&"hooks":
			for x: float in [18.0, 30.0]:
				draw_line(p.call(x, 12), p.call(x, 28), col, w)
				draw_arc(p.call(x - 4, 28), 4 * s, 0.0, PI, 8, col, w)
		&"staff":  # a lantern staff
			draw_line(p.call(17, 37), p.call(29, 15), col, w)
			draw_rect(Rect2(p.call(27, 8), p.call(8, 9)), col, false, w)
		&"spear":
			draw_line(p.call(13, 35), p.call(31, 17), col, w)
			_poly([p.call(29, 15), p.call(37, 11), p.call(33, 19)], col, w, true)
		&"shield":
			_poly([p.call(14, 13), p.call(34, 13), p.call(34, 25), p.call(24, 36), p.call(14, 25)], col, w, true)
			draw_arc(p.call(24, 23), 4 * s, 0.0, TAU, 10, col, w * 0.8)
		&"harness":  # crossed straps and a ring
			draw_line(p.call(14, 13), p.call(34, 35), col, w)
			draw_line(p.call(34, 13), p.call(14, 35), col, w)
			draw_arc(p.call(24, 24), 4 * s, 0.0, TAU, 10, col, w)
		&"bangle":
			draw_arc(p.call(24, 25), 10 * s, 0.0, TAU, ARC_STEPS * 2, col, w)
			_diamond(p, col, w, Vector2(24, 15), 3.5)
		&"book":
			_poly(
				[p.call(12, 15), p.call(24, 18), p.call(36, 15), p.call(36, 33), p.call(24, 36), p.call(12, 33)],
				col,
				w,
				true
			)
			draw_line(p.call(24, 18), p.call(24, 36), col, w)
		&"guards":  # a bracer, laced
			_poly([p.call(17, 12), p.call(31, 12), p.call(33, 36), p.call(15, 36)], col, w, true)
			for y: float in [19.0, 26.0]:
				draw_line(p.call(19, y), p.call(29, y + 3), col, w * 0.7)
		&"cleaver":
			draw_line(p.call(14, 36), p.call(24, 26), col, w)
			_poly([p.call(22, 22), p.call(30, 12), p.call(37, 19), p.call(28, 28)], col, w, true)
		&"wraps":
			for i in 3:
				draw_line(p.call(14, 18 + 6 * i), p.call(34, 14 + 6 * i), col, w)
		&"launcher":  # a crank launcher: a bow across a stock
			draw_line(p.call(13, 30), p.call(35, 20), col, w)
			draw_arc(p.call(24, 34), 12 * s, PI * 1.15, PI * 1.85, ARC_STEPS, col, w)
			draw_arc(p.call(17, 33), 2.5 * s, 0.0, TAU, 8, col, w * 0.8)
		&"sleeve":  # a mesh sleeve
			draw_rect(Rect2(p.call(16, 12), p.call(16, 24)), col, false, w)
			for i in 3:
				draw_line(p.call(16, 18 + 6 * i), p.call(32, 12 + 6 * i), col, w * 0.6)
		_:
			return false
	return true


## The abilities: an element's glyph, else the kind's.
func _draw_skill(p: Callable, col: Color, w: float, s: float) -> void:
	match glyph:
		&"blade":  # a physical strike: a sword, its crossguard and pommel
			draw_line(p.call(17, 31), p.call(35, 13), col, w)
			draw_line(p.call(13, 27), p.call(21, 35), col, w)
			draw_line(p.call(17, 31), p.call(12, 36), col, w)
		&"flame":
			_flame(p, col, w, Vector2(24, 24), 1.0)
		&"wave":
			for y: float in [20.0, 29.0]:
				draw_arc(p.call(17, y), 5 * s, PI, TAU, 8, col, w)
				draw_arc(p.call(27, y), 5 * s, 0.0, PI, 8, col, w)
		&"bolt":
			_poly(
				[
					p.call(27, 11),
					p.call(17, 26),
					p.call(25, 26),
					p.call(21, 37),
					p.call(32, 21),
					p.call(24, 21),
					p.call(27, 11)
				],
				col,
				w
			)
		&"frost":  # a six-armed crystal
			for i in 3:
				var a := PI * i / 3.0
				var d := Vector2(cos(a), sin(a)) * 12.0 * s
				draw_line(p.call(24, 24) - d, p.call(24, 24) + d, col, w)
		&"mote":  # a healing mote rising
			draw_arc(p.call(24, 28), 6 * s, 0.0, TAU, ARC_STEPS, col, w)
			_poly([p.call(18, 17), p.call(24, 11), p.call(30, 17)], col, w)
		&"ward":
			draw_arc(p.call(24, 30), 13 * s, PI * 1.1, PI * 1.9, ARC_STEPS, col, w)
			draw_arc(p.call(24, 30), 7 * s, PI * 1.1, PI * 1.9, ARC_STEPS, col, w)
			draw_line(p.call(24, 30), p.call(24, 17), col, w * 0.7)
		&"spark":  # an unaspected working: a four-pointed star
			_poly(
				[
					p.call(24, 11),
					p.call(27, 21),
					p.call(37, 24),
					p.call(27, 27),
					p.call(24, 37),
					p.call(21, 27),
					p.call(11, 24),
					p.call(21, 21)
				],
				col,
				w,
				true
			)


func _gem(p: Callable, col: Color, w: float) -> void:
	_poly([p.call(16, 18), p.call(20, 13), p.call(28, 13), p.call(32, 18), p.call(24, 36)], col, w, true)
	draw_line(p.call(16, 18), p.call(32, 18), col, w * 0.7)
	draw_line(p.call(20, 13), p.call(24, 18), col, w * 0.7)
	draw_line(p.call(28, 13), p.call(24, 18), col, w * 0.7)


func _drop(p: Callable, col: Color, w: float, s: float, at: Vector2, k: float) -> void:
	var r := 7.0 * k
	draw_arc(p.call(at.x, at.y + 3 * k), r * s, -PI * 0.15, PI * 1.15, ARC_STEPS, col, w)
	_poly(
		[
			p.call(at.x - r * 0.97, at.y + 3 * k - r * 0.26),
			p.call(at.x, at.y - 11 * k),
			p.call(at.x + r * 0.97, at.y + 3 * k - r * 0.26)
		],
		col,
		w
	)


func _flame(p: Callable, col: Color, w: float, at: Vector2, k: float) -> void:
	_poly(
		[
			p.call(at.x, at.y - 12 * k),
			p.call(at.x + 7 * k, at.y + 2 * k),
			p.call(at.x + 4 * k, at.y + 10 * k),
			p.call(at.x - 4 * k, at.y + 10 * k),
			p.call(at.x - 7 * k, at.y + 2 * k)
		],
		col,
		w,
		true
	)
	draw_line(p.call(at.x, at.y - 2 * k), p.call(at.x, at.y + 8 * k), col, w * 0.7)


func _diamond(p: Callable, col: Color, w: float, at: Vector2, r: float) -> void:
	_poly(
		[p.call(at.x, at.y - r), p.call(at.x + r, at.y), p.call(at.x, at.y + r), p.call(at.x - r, at.y)], col, w, true
	)


func _poly(pts: Array, col: Color, w: float, closed: bool = false) -> void:
	var line := PackedVector2Array(pts)
	if closed:
		line.append(pts[0])
	draw_polyline(line, col, w, true)
