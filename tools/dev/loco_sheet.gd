extends SceneTree
## Locomotion contact sheets (the human's run playtest, 2026-10-30): poses a hero's review stage at `phases` points
## of one cycle of `clip` and saves each camera's frame, for a side / front / three-quarter sheet.
##   godot-render --path . --script res://tools/dev/loco_sheet.gd -- --hero=asha --clip=run --phases=6 --out=DIR
## Writes DIR/<hero>_<clip>_<camera>_<phase>.png (480 x 540). Not a test: a review aid.

const CAMERAS: Array[String] = ["Profile", "Front", "ThreeQuarter"]


func _initialize() -> void:
	_run.call_deferred()


func _arg(name: String, fallback: String) -> String:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--%s=" % name):
			return a.split("=", true, 1)[1]
	return fallback


func _run() -> void:
	var hero := _arg("hero", "asha")
	var clip := _arg("clip", "run")
	var phases := int(_arg("phases", "6"))
	var out := _arg("out", "user://loco_sheet")
	DirAccess.make_dir_recursive_absolute(out)
	root.size = Vector2i(480, 540)
	var scene := load("res://game/levels/_tests/characters/%s/%s_stage.tscn" % [hero, hero]) as PackedScene
	var stage := scene.instantiate()
	stage.set(&"clip", StringName(clip))
	stage.set(&"clip_library", load("res://assets/characters/%s/anim/%s_clips.tres" % [hero, hero]))
	root.add_child(stage)
	for _i in 10:
		await process_frame
	var ap := stage.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var length := ap.get_animation(StringName(clip)).length
	for k in phases:
		ap.seek(length * k / phases, true)
		ap.pause()
		for cam_name: String in CAMERAS:
			var cam := stage.get_node("Cameras/" + cam_name) as Camera3D
			cam.current = true
			for _i in 4:
				await process_frame
			var img := root.get_texture().get_image()
			img.save_png("%s/%s_%s_%s_%d.png" % [out, hero, clip, cam_name, k])
	quit(0)
