extends SceneTree
## M4-A2P-1980: saves a hero's text clip library (hero_clips.py's build) as a binary, compressed AnimationLibrary
## (.res), so the libraries have room past test_hero_clips' text bound. Run headless:
##   godot --headless --path . --script res://tools/characters/clips_to_res.gd -- <in.tres> <out.res>
## Paths may be absolute. hero_clips.py calls it.


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 2:
		push_error("usage: -- <in.tres> <out.res>")
		quit(2)
		return
	var lib := ResourceLoader.load(args[0], "AnimationLibrary", ResourceLoader.CACHE_MODE_IGNORE) as AnimationLibrary
	if lib == null:
		push_error("not an AnimationLibrary: %s" % args[0])
		quit(1)
		return
	lib.resource_path = ""  # the saved bytes then depend on the clips and the output path only, not the input's path
	var err := ResourceSaver.save(lib, args[1], ResourceSaver.FLAG_COMPRESS)
	print("CLIPS_TO_RES %s -> %s err=%d" % [args[0], args[1], err])
	quit(0 if err == OK else 1)
