extends Node
## Boot scene. Until the title screen exists (M1 UI task) it shows the project name.

@onready var _label: Label = $Label


func _ready() -> void:
	_label.text = "%s\n%s" % [ProjectSettings.get_setting("application/config/name"), "bootstrap build"]
