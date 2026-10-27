class_name BestiaryPortraitSlot
extends Control
## The live portrait on the bestiary page (M2-UI-26): the chosen foe's battle model, rendered by the creatures
## track's CreaturePortrait (its clip, time and framing come from creatures.json `portrait`, so the picture never
## moves between frames). The slot takes the page's leftover height under the EnemyPageView and holds the portrait
## square in its bottom-right corner, at most max_px and never past the slot, so it can never cover the text; below
## min_px (a long page at a large text size) it hides. A foe never Read shows as a flat silhouette in the theme's
## `silhouette_role` colour (its shape, which the party has seen in battle, but none of its colours); a foe with no
## model shows nothing. clear() frees the model and stops the portrait's viewport: BestiaryMenu calls it on close.
## Metrics: game/data/ui/bestiary_menu.json "portrait".

const PORTRAIT_SCENE := "res://game/creatures/creature_portrait.tscn"
const SILHOUETTE_SHADER := preload("res://game/ui/shaders/silhouette.gdshader")

## The foe on show (&"" when none).
var enemy_id: StringName = &""
## True while the foe on show is drawn as a silhouette (never Read).
var silhouette := false

var _m: Dictionary = {}
var _portrait: CreaturePortrait
var _silhouette_mat: ShaderMaterial


func _init(metrics: Dictionary = {}) -> void:
	_m = metrics
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	_portrait = (load(PORTRAIT_SCENE) as PackedScene).instantiate() as CreaturePortrait
	_portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_portrait.custom_minimum_size = Vector2.ZERO
	_portrait.visible = false
	add_child(_portrait)
	resized.connect(_fit)


func _ready() -> void:
	_silhouette_mat = ShaderMaterial.new()
	_silhouette_mat.shader = SILHOUETTE_SHADER
	var tint := get_theme_color(StringName(str(_m.get("silhouette_role", ""))), HymnThemeBuilder.PALETTE_TYPE)
	tint.a = HudLayout.num(_m, "silhouette_alpha")
	_silhouette_mat.set_shader_parameter(&"tint", tint)
	_apply_silhouette()


## Shows foe `id`, as a silhouette unless `read`. False (and an empty slot) when it has no model.
func show_enemy(id: StringName, read: bool) -> bool:
	silhouette = not read
	if id != enemy_id or not _portrait.has_creature():
		enemy_id = &""
		if not _portrait.show_enemy(id):
			clear()
			return false
		enemy_id = id
	_apply_silhouette()
	_fit()
	return true


## Empties the slot and stops the portrait rendering (the page closed, or the book is empty).
func clear() -> void:
	enemy_id = &""
	silhouette = false
	_portrait.clear()
	_portrait.visible = false


func has_creature() -> bool:
	return _portrait.has_creature()


## True when the portrait is drawn (a model on show and room for it).
func is_showing() -> bool:
	return _portrait.has_creature() and _portrait.visible


func portrait() -> CreaturePortrait:
	return _portrait


## The portrait's side: the slot's smaller side, capped at max_px.
func _fit() -> void:
	var side := minf(minf(size.x, size.y), HudLayout.num(_m, "max_px"))
	_portrait.visible = _portrait.has_creature() and side >= HudLayout.num(_m, "min_px")
	_portrait.size = Vector2(side, side)
	_portrait.position = size - _portrait.size


func _apply_silhouette() -> void:
	_portrait.material = _silhouette_mat if silhouette else null
