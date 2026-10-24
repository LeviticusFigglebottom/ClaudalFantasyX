extends Node
## Boot scene and minimal title (M1-ARC-06): the project name over a Continue / New Game / Load
## menu (TitleMenu, game/ui/title/), until the UI stream builds the real title screen.
## The title stops the play clock, and boot arms SceneRouter.world_return so a load from here
## (Continue or Load) returns the party to its respawn point. Nothing else arms it, so the test
## runner and screenshot captures never change scene on a load.
## Debug builds: installs the F1–F12 debug overlay (game/core/debug/, M1-ARC-02) under the tree
## root, where it survives scene changes. It is referenced only by path, so release exports can
## leave the whole debug folder out. F9 (battle sandbox) now lives in the overlay.
## M1-ARC-15: applies the saved (or default) graphics preset before anything renders, and arms
## SceneRouter's per-scene graphics hook (GraphicsRuntime).

const DEBUG_OVERLAY_SCENE := "res://game/core/debug/debug_overlay.tscn"
const DEBUG_OVERLAY_NAME := "DebugOverlay"

@onready var _label: Label = $Label


func _ready() -> void:
	GraphicsRuntime.boot(get_viewport())
	_label.text = "%s\n%s" % [ProjectSettings.get_setting("application/config/name"), "bootstrap build"]
	Game.stop_play_clock()
	arm_world_return()
	_install_debug_overlay()
	_install_autosave_toast.call_deferred()


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
