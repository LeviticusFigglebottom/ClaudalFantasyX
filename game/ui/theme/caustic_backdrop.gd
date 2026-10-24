class_name CausticBackdrop
extends ColorRect
## A full-screen layer of drifting caustic light behind a menu (ADR 0033; menu_caustics.gdshader):
## lamplight through water, faint enough that the panels stay the brightest thing on screen. The
## phase comes from its own elapsed time (deterministic under --fixed-fps captures) and holds
## still under reduced motion (UiSettings). Color: the theme's "caustic" role.

const SHADER := preload("res://game/ui/shaders/menu_caustics.gdshader")
## Phase units per second: a slow drift.
const DRIFT_PER_SEC := 0.12

var _t := 0.0
var _mat: ShaderMaterial


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	color = Color.WHITE
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	material = _mat
	_tint()


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED and _mat != null:
		_tint()


func _process(delta: float) -> void:
	if UiSettings.shared().reduced_motion():
		return
	_t += delta
	_mat.set_shader_parameter(&"phase", _t * DRIFT_PER_SEC * TAU)


func _tint() -> void:
	_mat.set_shader_parameter(&"tint", get_theme_color(&"caustic", HymnThemeBuilder.PALETTE_TYPE))
