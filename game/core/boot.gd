extends Node
## Boot scene. Until the title screen exists (M1 UI task) it shows the project name.
## Debug builds: installs the F1–F12 debug overlay (game/core/debug/, M1-ARC-02) under the tree
## root, where it survives scene changes. It is referenced only by path, so release exports can
## leave the whole debug folder out. F9 (battle sandbox) now lives in the overlay.

const DEBUG_OVERLAY_SCENE := "res://game/core/debug/debug_overlay.tscn"
const DEBUG_OVERLAY_NAME := "DebugOverlay"

@onready var _label: Label = $Label


func _ready() -> void:
	_label.text = "%s\n%s" % [ProjectSettings.get_setting("application/config/name"), "bootstrap build"]
	_install_debug_overlay()


func _install_debug_overlay() -> void:
	if not OS.is_debug_build() or not ResourceLoader.exists(DEBUG_OVERLAY_SCENE):
		return
	var root := get_tree().root
	if root.has_node(NodePath(DEBUG_OVERLAY_NAME)):
		return
	var overlay := (load(DEBUG_OVERLAY_SCENE) as PackedScene).instantiate()
	overlay.name = DEBUG_OVERLAY_NAME
	root.add_child.call_deferred(overlay)
