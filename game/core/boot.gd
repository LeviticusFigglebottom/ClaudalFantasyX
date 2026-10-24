extends Node
## Boot scene and title (M1-ARC-06): the title screen (TitleMenu, game/ui/title/: since M2-UI-22 it
## draws the logotype, the animated backdrop and the debug-only build label itself).
## The title stops the play clock, and boot arms SceneRouter.world_return so a load from here
## (Continue or Load) returns the party to its respawn point. Nothing else arms it, so the test
## runner and screenshot captures never change scene on a load.
## Debug builds: installs the F1–F12 debug overlay (game/core/debug/, M1-ARC-02) under the tree
## root, where it survives scene changes. It is referenced only by path, so release exports can
## leave the whole debug folder out. F9 (battle sandbox) now lives in the overlay.
## M1-ARC-15: applies the saved (or default) graphics preset before anything renders, and arms
## SceneRouter's per-scene graphics hook (GraphicsRuntime).
## M1-RND-22: starts the shader warm-up of the preset's resident shaders (ShaderPrewarm.spawn_resident)
## under the tree root, so their compile happens here, under the boot screen, not in a transition.
## M2-ARC-03: the boot screen is a BootCard over the title. When boot runs as the game's scene (launch, or a
## SceneRouter change back to the title), the card covers the title, which takes no keys, while the resident
## warm-up and the theme font warm-up (SceneRouter.warm_fonts_now) run; the title fades in once both are
## done, and the router measures the visible window from that fade (SceneRouter.measure_reveal). Reached
## through a change, the card also holds the router's reveal (hold_reveal), so the router's opaque fade is
## the cover and lifts instead. Elsewhere (the boot_title capture, tests) boot is not the current scene:
## no card, and the warm-up starts as before.
## M2-ARC-08: the card waits while the warm-up progresses (no fixed cap), and on a first launch shows a quiet
## cue (BootCard.show_first_run_cue).

const DEBUG_OVERLAY_SCENE := "res://game/core/debug/debug_overlay.tscn"
const DEBUG_OVERLAY_NAME := "DebugOverlay"

## The boot screen while the warm-up runs (null when boot is not the game's scene, and after it lifts).
var _card: BootCard

@onready var _title: Control = $TitleMenu


func _ready() -> void:
	ControlsModel.apply_saved(UiSettings.CONFIG_PATH)  # M2-UI-13: saved key and pad bindings
	GraphicsRuntime.boot(get_viewport())
	if is_game_scene():
		_cover_until_warm()
	else:
		GraphicsRuntime.warm_resident_shaders.call_deferred(get_tree().root)
	Game.stop_play_clock()
	arm_world_return()
	_install_debug_overlay()
	_install_autosave_toast.call_deferred()


## True when boot is the game's running scene (launch or a SceneRouter change), not a capture's or test's child.
func is_game_scene() -> bool:
	return is_inside_tree() and get_tree().current_scene == self


## The boot card while it covers the title (null once lifted, or when there is none).
func boot_card() -> BootCard:
	return _card if _card != null and not _card.is_lifted() else null


## M2-ARC-03: covers the title with an opaque BootCard and blocks its keys until the warm-ups finish.
func _cover_until_warm() -> void:
	var router := get_tree().root.get_node_or_null(^"SceneRouter")
	var via_change := router != null and bool(router.call(&"is_busy"))
	# Under a change the router's opaque fade is the cover: the card is cut, and the router lifts its fade.
	_card = BootCard.cover(self, 0.0, 0.0 if via_change or router == null else SceneRouter.FADE_SEC)
	if via_change:
		_card.hold_reveal_of(router)
	_title.set_process_unhandled_input(false)
	_card.opened.connect(_on_card_opened.bind(router, via_change), CONNECT_ONE_SHOT)
	_card.revealed.connect(_on_card_revealed, CONNECT_ONE_SHOT)
	_start_warm.call_deferred(router)


## Deferred: at launch the root is still adding its children.
func _start_warm(router: Node) -> void:
	var warm := GraphicsRuntime.warm_resident_shaders(get_tree().root)
	_card.wait_for_node(warm)
	# M2-ARC-08: a first launch builds every pipeline here, for seconds; the card says so, quietly.
	if warm != null and warm.first_run:
		_card.show_first_run_cue()
	if router != null:
		router.call(&"warm_fonts_now")
		_card.wait_until(Callable(router, &"fonts_ready"), Callable(router, &"font_warm_progress"))
	_card.arm()


func _on_card_opened(stats: Dictionary, router: Node, via_change: bool) -> void:
	_title.set_process_unhandled_input(true)
	if router != null and not via_change and not bool(router.call(&"is_busy")):
		router.call(&"measure_reveal", scene_file_path, Callable(_card, &"is_lifted"), stats)


func _on_card_revealed() -> void:
	_card.queue_free()
	_card = null


## M1-UI-09: the notice for a skipped chapter autosave lives under the tree root, so it outlives the
## title and every zone change (deferred: the root is still adding its children during boot).
func _install_autosave_toast() -> void:
	AutosaveToast.install(get_tree().root)


## Lets loads made from the title move the party into the world (WorldReturn).
static func arm_world_return() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var router := tree.root.get_node_or_null(^"SceneRouter") if tree != null else null
	var wr: Variant = router.get(&"world_return") if router != null else null
	if wr is WorldReturn:
		(wr as WorldReturn).enabled = true


func _install_debug_overlay() -> void:
	if not OS.is_debug_build() or not ResourceLoader.exists(DEBUG_OVERLAY_SCENE):
		return
	var root := get_tree().root
	if root.has_node(NodePath(DEBUG_OVERLAY_NAME)):
		return
	var overlay := (load(DEBUG_OVERLAY_SCENE) as PackedScene).instantiate()
	overlay.name = DEBUG_OVERLAY_NAME
	root.add_child.call_deferred(overlay)
