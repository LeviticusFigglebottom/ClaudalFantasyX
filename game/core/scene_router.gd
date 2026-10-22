extends Node
## Autoload "SceneRouter": async scene loading behind a fade, with a shader-prewarm hook.

signal prewarm_requested(scene_path: String)

const FADE_SEC := 0.35

var _fade_layer: CanvasLayer
var _fade_rect: ColorRect
var _busy := false


func _ready() -> void:
	_fade_layer = CanvasLayer.new()
	_fade_layer.layer = 128
	add_child(_fade_layer)
	_fade_rect = ColorRect.new()
	_fade_rect.color = Color(0, 0, 0, 0)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade_layer.add_child(_fade_rect)
	ShaderPrewarm.install(self)


func is_busy() -> bool:
	return _busy


func change_scene(scene_path: String) -> void:
	if _busy:
		push_warning("SceneRouter: change already in progress, ignoring %s" % scene_path)
		return
	_busy = true
	ResourceLoader.load_threaded_request(scene_path)
	await _fade_to(1.0)
	while ResourceLoader.load_threaded_get_status(scene_path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
		await get_tree().process_frame
	var packed := ResourceLoader.load_threaded_get(scene_path) as PackedScene
	if packed == null:
		push_error("SceneRouter: failed to load %s" % scene_path)
	else:
		prewarm_requested.emit(scene_path)
		get_tree().change_scene_to_packed(packed)
		await get_tree().process_frame
		EventBus.scene_changed.emit(scene_path)
	await _fade_to(0.0)
	_busy = false


func _fade_to(alpha: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", alpha, FADE_SEC)
	await tween.finished
