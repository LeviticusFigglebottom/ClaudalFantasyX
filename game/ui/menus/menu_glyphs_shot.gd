class_name MenuGlyphsShot
extends Control
## Capture driver for the menu_glyphs review sheet (Act I final pass, ADR 0041): every glyph menu_glyphs.json
## names, in its family's role, at row size and enlarged, with its name under it, on the menus' panel.

const COLUMNS := 9
const CELL := Vector2(204.0, 172.0)
const BIG := 96.0
const ORIGIN := Vector2(48.0, 36.0)


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_deep", HymnThemeBuilder.PALETTE_TYPE)
	add_child(back)
	var i := 0
	for e in glyphs():
		var at := ORIGIN + Vector2(i % COLUMNS, i / COLUMNS) * CELL
		var big := MenuGlyph.new(e["glyph"], e["role"])
		big.position = at
		big.size = Vector2(BIG, BIG)
		add_child(big)
		var small := MenuGlyph.for_row(e, at.x + BIG + 12.0, BIG)
		small.position.y += at.y
		add_child(small)
		var name := Label.new()
		name.theme_type_variation = &"SmallLabel"
		name.text = String(e["glyph"])
		name.position = at + Vector2(0.0, BIG + 6.0)
		add_child(name)
		i += 1


## Every distinct glyph the data names, each once, with the role it is first used in.
static func glyphs() -> Array[Dictionary]:
	var d := MenuGlyph.data()
	var out: Array[Dictionary] = []
	var seen: Dictionary = {}
	var add := func(g: String, r: String) -> void:
		if g != "" and not seen.has(g):
			seen[g] = true
			out.append({"glyph": StringName(g), "role": StringName(r)})
	var items: Dictionary = d.get("items", {})
	var roles: Dictionary = d.get("item_roles", {})
	for cat: Variant in d.get("item_categories", {}):
		add.call(str(d["item_categories"][cat]), str(roles.get(cat, "text")))
		for id: Variant in ItemDB.load_default().items:
			if str((ItemDB.load_default().items[id] as Dictionary).get("category", "")) == str(cat):
				add.call(str(items.get(str(id), "")), str(roles.get(cat, "text")))
	for t: Variant in d.get("equipment_types", {}):
		add.call(str(d["equipment_types"][t]), str(d.get("equipment_role", "text")))
	for k: Variant in d.get("skill_kinds", {}):
		add.call(str(d["skill_kinds"][k]), str((d.get("skill_roles", {}) as Dictionary).get(k, "text")))
	add.call(str(d.get("currency", "")), str(d.get("currency_role", "text")))
	for el: Variant in d.get("skill_elements", {}):
		add.call(str(d["skill_elements"][el]), "focus")
	return out
