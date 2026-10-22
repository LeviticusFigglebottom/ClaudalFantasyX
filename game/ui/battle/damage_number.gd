class_name DamageNumber
extends Label
## A popping number (docs/kb/art/ui.md §5): 6% scale pop in the first 80 ms, a 36 px ease-out
## rise over 700 ms, then a 250 ms fade. Damage to allies is ui_danger, healing ui_heal,
## damage to foes white; criticals use the larger DamageNumberCrit style.

const KIND_DAMAGE := &"damage"
const KIND_HEAL := &"heal"
const KIND_MISS := &"miss"


## Shows `text` centred on `at` (HUD coordinates) and frees itself when done.
func pop(text_value: String, at: Vector2, kind: StringName, on_ally: bool, crit: bool, m: Dictionary) -> void:
	theme_type_variation = &"DamageNumberCrit" if crit else &"DamageNumber"
	text = text_value
	horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var role := &"text"
	if kind == KIND_HEAL:
		role = &"heal"
	elif kind == KIND_DAMAGE and on_ally:
		role = &"danger"
	elif kind == KIND_MISS:
		role = &"text_dim"
	add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))
	reset_size()
	position = at - size * 0.5
	pivot_offset = size * 0.5
	var rise := HudLayout.num(m, "rise_px")
	var rise_sec := HudLayout.num(m, "rise_sec")
	var pop_sec := HudLayout.num(m, "pop_sec")
	var big := HudLayout.num(m, "pop_scale")
	var tw := create_tween()
	tw.set_parallel(true)
	tw.tween_property(self, "position:y", position.y - rise, rise_sec).set_trans(Tween.TRANS_CUBIC).set_ease(
		Tween.EASE_OUT
	)
	tw.tween_property(self, "scale", Vector2(big, big), pop_sec)
	tw.tween_property(self, "scale", Vector2.ONE, pop_sec).set_delay(pop_sec)
	tw.chain().tween_property(self, "modulate:a", 0.0, HudLayout.num(m, "fade_sec"))
	tw.chain().tween_callback(queue_free)
