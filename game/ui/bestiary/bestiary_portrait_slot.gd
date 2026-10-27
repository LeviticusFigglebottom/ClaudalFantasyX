class_name BestiaryPortraitSlot
extends Control
## The portrait on the bestiary page (M2-UI-1000): the chosen foe's baked picture (CreaturePortraits, ADR 0120;
## tools/portraits/render.sh renders each creature from its own battle model, so the page loads a small
## texture instead of a model in a live viewport; ADR 0110). The slot takes the page's leftover height under the
## EnemyPageView and holds the picture square in its bottom-right corner, at most max_px and never past the
## slot, so it can never cover the text; below min_px (a long page at a large text size) it hides. A foe never
## Read shows as a flat silhouette in the theme's `silhouette_role` colour (its shape, which the party has seen in
## battle, but none of its colours); a foe with no picture shows nothing. clear() empties it: BestiaryMenu calls
## it on close. Metrics: game/data/ui/bestiary_menu.json "portrait".

const SILHOUETTE_SHADER := preload("res://game/ui/shaders/silhouette.gdshader")

## The foe on show (&"" when none).
var enemy_id: StringName = &""
## True while the foe on show is drawn as a silhouette (never Read).
var silhouette := false

var _m: Dictionary = {}
var _picture: TextureRect
var _silhouette_mat: ShaderMaterial


func _init(metrics: Dictionary = {}) -> void:
	_m = metrics
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	_picture = TextureRect.new()
	_picture.name = &"Portrait"
	_picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_picture.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_picture.visible = false
	add_child(_picture)
	resized.connect(_fit)


func _ready() -> void:
	_silhouette_mat = ShaderMaterial.new()
	_silhouette_mat.shader = SILHOUETTE_SHADER
	var tint := get_theme_color(StringName(str(_m.get("silhouette_role", ""))), HymnThemeBuilder.PALETTE_TYPE)
	tint.a = HudLayout.num(_m, "silhouette_alpha")
	_silhouette_mat.set_shader_parameter(&"tint", tint)
	_apply_silhouette()


## Shows foe `id`, as a silhouette unless `read`. False (and an empty slot) when it has no picture.
func show_enemy(id: StringName, read: bool) -> bool:
	silhouette = not read
	if id != enemy_id or _picture.texture == null:
		var tex := CreaturePortraits.texture(id)
		if tex == null:
			clear()
			return false
		_picture.texture = tex
		enemy_id = id
	_apply_silhouette()
	_fit()
	return true


## Empties the slot (the page closed, or the book is empty).
func clear() -> void:
	enemy_id = &""
	silhouette = false
	_picture.texture = null
	_picture.visible = false


func has_creature() -> bool:
	return _picture.texture != null


## True when the picture is drawn (a foe on show and room for it).
func is_showing() -> bool:
	return has_creature() and _picture.visible


## The picture (a TextureRect holding the baked PNG).
func portrait() -> TextureRect:
	return _picture


## The picture's side: the slot's smaller side, capped at max_px.
func _fit() -> void:
	var side := minf(minf(size.x, size.y), HudLayout.num(_m, "max_px"))
	_picture.visible = has_creature() and side >= HudLayout.num(_m, "min_px")
	_picture.size = Vector2(side, side)
	_picture.position = size - _picture.size


func _apply_silhouette() -> void:
	_picture.material = _silhouette_mat if silhouette else null
