class_name CutsceneMemory
extends RefCounted
## M5-A3P-1600 (act2_ch16_direction.md K01-K08, Kesh's memory "desaturated to white, soft edges"; act3_ch20.md's six
## memory layers): `@memory on|off [sec] [look=<id>]` eases a screen-space layer over the picture, under the
## letterbox, the fade and the dialogue box (CutsceneOverlay's stack). The frame loses its colour, washes toward the
## look's colour and goes soft and pale toward the edges (cutscene_memory.gdshader). The looks are sequencer.json's
## `memory` rows; `on` with no look= takes default_look. The layer comes off when the scene ends, however it ends.

const SHADER := "res://game/cutscene/cutscene_memory.gdshader"
const NODE_NAME := "Memory"
const KEY := "memory"
const KEY_LOOKS := "looks"
const KEY_DEFAULT := "default_look"
const KEY_EASE := "ease"
const KEY_WASH_COLOR := "wash_color"
const MOTION := &"memory"
const SWITCH_ON := &"on"
## The look's numbers, each a shader uniform of the same name.
const PARAMS: Array[String] = ["desaturate", "wash", "edge_inner", "edge_outer", "edge_wash", "edge_blur_lod"]
## On the layer while a scene's end is waited for (one hookup per scene).
const META_ARMED := &"memory_armed"


## The layer under `overlay` (made once, at the bottom of its stack, off).
static func layer(overlay: CanvasLayer) -> ColorRect:
	var rect := overlay.get_node_or_null(NODE_NAME) as ColorRect
	if rect != null:
		return rect
	rect = ColorRect.new()
	rect.name = NODE_NAME
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load(SHADER) as Shader
	mat.set_shader_parameter(&"amount", 0.0)
	rect.material = mat
	rect.visible = false
	overlay.add_child(rect)
	overlay.move_child(rect, 0)
	return rect


## The memory amount now (0 off, 1 the full look).
static func amount(overlay: CanvasLayer) -> float:
	var rect := overlay.get_node_or_null(NODE_NAME) as ColorRect
	return float((rect.material as ShaderMaterial).get_shader_parameter(&"amount")) if rect != null else 0.0


## Eases the layer on or off over the step's sec, through `start_motion` (key, sec, apply(t)), and takes it off at
## `finished`. False (and nothing changes) when the look isn't in sequencer.json.
static func cue(
	overlay: CanvasLayer, step: DialogueStep, config: Dictionary, start_motion: Callable, finished: Signal
) -> bool:
	var cfg: Dictionary = config.get(KEY, {})
	var looks: Dictionary = cfg.get(KEY_LOOKS, {})
	var on := StringName(str(step.args[0])) == SWITCH_ON
	var look_id := str(step.kwargs.get("look", cfg.get(KEY_DEFAULT, "")))
	if on and not looks.has(look_id):
		return false
	var rect := layer(overlay)
	var mat := rect.material as ShaderMaterial
	if on:
		_set_look(mat, looks[look_id])
	var from := float(mat.get_shader_parameter(&"amount"))
	var to := 1.0 if on else 0.0
	var curve := float(cfg.get(KEY_EASE, 1.0))
	rect.visible = true
	start_motion.call(
		MOTION,
		float(step.args[1]) if step.args.size() > 1 else 0.0,
		func(t: float) -> void:
			if not is_instance_valid(rect):
				return
			mat.set_shader_parameter(&"amount", lerpf(from, to, CutsceneMotion.eased(t, curve)))
			if t >= 1.0 and to == 0.0:
				rect.visible = false
	)
	if not rect.has_meta(META_ARMED):
		rect.set_meta(META_ARMED, true)
		finished.connect(func(_id: StringName) -> void: clear(overlay), CONNECT_ONE_SHOT)
	return true


## Takes the layer off at once (the scene's end).
static func clear(overlay: CanvasLayer) -> void:
	if not is_instance_valid(overlay):
		return
	var rect := overlay.get_node_or_null(NODE_NAME) as ColorRect
	if rect == null:
		return
	(rect.material as ShaderMaterial).set_shader_parameter(&"amount", 0.0)
	rect.visible = false
	rect.remove_meta(META_ARMED)


static func _set_look(mat: ShaderMaterial, look: Dictionary) -> void:
	for p in PARAMS:
		mat.set_shader_parameter(StringName(p), float(look.get(p, 0.0)))
	mat.set_shader_parameter(&"wash_color", Color(str(look.get(KEY_WASH_COLOR, "#FFFFFF"))))
