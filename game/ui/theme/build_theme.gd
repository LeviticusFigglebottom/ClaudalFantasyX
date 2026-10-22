extends SceneTree
## Regenerates game/ui/theme/hymn_theme.tres from game/data/ui/theme.json (docs/kb/tech/ui.md):
##   godot --headless --path . --script res://game/ui/theme/build_theme.gd


func _init() -> void:
	var cfg := HymnThemeBuilder.load_config()
	var out := str(cfg.get("output_path", ""))
	var theme := HymnThemeBuilder.build(cfg)
	var err := ResourceSaver.save(theme, out)
	if err != OK:
		printerr("build_theme: could not save %s: %s" % [out, error_string(err)])
		quit(1)
		return
	print("build_theme: wrote %s" % out)
	quit(0)
