class_name LampMote
extends ColorRect
## The breathing focus dot that replaces a cursor glyph (docs/kb/art/ui.md §3). Its phase comes
## from its own elapsed time, so a capture of a freshly built scene is deterministic.

const SHADER := preload("res://game/ui/shaders/lamp_mote.gdshader")

var period_sec := 2.4
var alpha_min := 0.75
var breathing := true

var _t := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	color = Color.WHITE
	var mat := ShaderMaterial.new()
	mat.shader = SHADER
	mat.set_shader_parameter(&"glow_color", get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE))
	mat.set_shader_parameter(&"core_color", get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE))
	mat.set_shader_parameter(&"alpha_min", alpha_min)
	mat.set_shader_parameter(&"breathing", breathing)
	material = mat


func _process(delta: float) -> void:
	_t += delta
	if breathing and material != null and period_sec > 0.0:
		(material as ShaderMaterial).set_shader_parameter(&"phase", fposmod(_t / period_sec, 1.0))
