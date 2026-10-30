class_name DamageNumber
extends Label
## A popping number (docs/kb/art/ui.md §5): 6% scale pop in the first 80 ms, a 36 px ease-out
## rise over 700 ms, then a 250 ms fade. Damage to allies is ui_danger, healing ui_heal,
## damage to foes white; criticals use the larger DamageNumberCrit style. KIND_INFO is a word
## instead of a number ("Reflected", "Heal turns to harm"): smaller FloatText, no pop.
## `motion_scale` (UiSettings.motion_scale()) shrinks the rise under reduced motion; `speed`
## (UiSettings.battle_speed(), M2-UI-23) plays the whole pop faster or slower.

const KIND_DAMAGE := &"damage"
const KIND_HEAL := &"heal"
const KIND_MISS := &"miss"
const KIND_INFO := &"info"

## The pop's tween (tests step it).
var tween: Tween


## Shows `text` centred on `at` (HUD coordinates) and frees itself when done. `role` overrides
## the palette role (KIND_INFO uses it; &"" picks from the kind).
func pop(
	text_value: String,
	at: Vector2,
	kind: StringName,
	on_ally: bool,
	crit: bool,
	m: Dictionary,
	motion_scale: float = 1.0,
	role: StringName = &"",
	speed: float = 1.0
) -> void:
	var info := kind == KIND_INFO
	theme_type_variation = &"FloatText" if info else (&"DamageNumberCrit" if crit else &"DamageNumber")
	text = text_value
	horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_theme_color_override(&"font_color", get_theme_color(_role(kind, on_ally, role), HymnThemeBuilder.PALETTE_TYPE))
	reset_size()
	position = at - size * 0.5
	# Kept whole on the screen: a foe stood at its edge (the left rank at 4:3) floats its words inward.
	var view := get_viewport_rect()
	var edge := HudLayout.num(m, "edge_px")
	global_position.x = clampf(global_position.x, view.position.x + edge, maxf(view.end.x - size.x - edge, edge))
	pivot_offset = size * 0.5
	var rise := HudLayout.num(m, "rise_px") * motion_scale
	var rise_sec := HudLayout.num(m, "rise_sec")
	var tw := create_tween()
	tween = tw
	tw.set_speed_scale(speed)
	tw.set_parallel(true)
	tw.tween_property(self, "position:y", position.y - rise, rise_sec).set_trans(Tween.TRANS_CUBIC).set_ease(
		Tween.EASE_OUT
	)
	if not info and motion_scale >= 1.0:
		var pop_sec := HudLayout.num(m, "pop_sec")
		var big := HudLayout.num(m, "pop_scale")
		tw.tween_property(self, "scale", Vector2(big, big), pop_sec)
		tw.tween_property(self, "scale", Vector2.ONE, pop_sec).set_delay(pop_sec)
	tw.chain().tween_property(self, "modulate:a", 0.0, HudLayout.num(m, "fade_sec"))
	tw.chain().tween_callback(queue_free)


static func _role(kind: StringName, on_ally: bool, role: StringName) -> StringName:
	if role != &"":
		return role
	if kind == KIND_HEAL:
		return &"heal"
	if kind == KIND_DAMAGE and on_ally:
		return &"danger"
	if kind == KIND_MISS or kind == KIND_INFO:
		return &"text_dim"
	return &"text"
