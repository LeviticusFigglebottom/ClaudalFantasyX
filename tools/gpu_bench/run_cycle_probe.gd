class_name RunCycleProbe
extends Node
## Human playtest check (c), 2026-10-30 (cloud QA pass 6): a hero's default run across one cycle, side and front.
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 res://tools/gpu_bench/run_cycle_probe.tscn -- \
##     --out=/abs/dir [--stage=res://game/levels/_tests/characters/rhen/rhen_stage.tscn --clip=run --phases=12 \
##     --cameras=Profile,Front --library=res://assets/characters/rhen/anim/rhen_clips.tres]
## The character look-dev stage poses the clip (asha_stage.gd's clip) at --phases even steps of its length; each
## camera renders each phase to <out>/<camera>_<nn>.png. Frames, not motion: the clip's own timing in the field is
## scaled by HeroLocomotion (run speed / run_clip_mps).

const SETTLE_FRAMES := 8

var _opts: Dictionary = {}


func _ready() -> void:
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := (get_script() as GDScript).new() as Node
		driver.name = "RunCycleProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_opts[kv[0]] = kv[1] if kv.size() > 1 else "true"
	var out_dir := str(_opts.get("out", "user://run_cycle"))
	DirAccess.make_dir_recursive_absolute(out_dir)
	var stage_path := str(_opts.get("stage", "res://game/levels/_tests/characters/rhen/rhen_stage.tscn"))
	var clip := StringName(str(_opts.get("clip", "run")))
	var stage := (load(stage_path) as PackedScene).instantiate()
	stage.set(&"clip", clip)
	stage.set(&"clip_library", load(str(_opts.get("library", "res://assets/characters/rhen/anim/rhen_clips.tres"))))
	get_tree().root.add_child(stage)
	await _settle()
	var ap := stage.find_children("*", "AnimationPlayer", true, false)
	if ap.is_empty() or not (ap[0] as AnimationPlayer).has_animation(clip):
		push_error("RunCycleProbe: no clip %s" % clip)
		get_tree().quit(1)
		return
	var player := ap[0] as AnimationPlayer
	var length := player.get_animation(clip).length
	print("RUN_CYCLE clip %s length %.3f s" % [clip, length])
	var phases := int(_opts.get("phases", 12))
	var cams := str(_opts.get("cameras", "Profile,Front")).split(",", false)
	# The player holds the pose the stage seeked to and ignores later seeks here (4.6.3), so it is switched off and
	# the clip's bone tracks are sampled straight onto the skeleton.
	player.active = false
	var anim := player.get_animation(clip)
	var base := player.get_node(player.root_node)
	for i in phases:
		_pose(anim, base, length * i / float(phases))
		for cam_name in cams:
			var cam := stage.get_node_or_null(NodePath("Cameras/" + cam_name)) as Camera3D
			if cam == null:
				continue
			cam.make_current()
			await _settle()
			var img := get_viewport().get_texture().get_image()
			img.save_png(out_dir.path_join("%s_%02d.png" % [cam_name, i]))
	get_tree().quit()


## Every bone transform track of `anim` at `time`, set on its skeleton (paths are relative to `base`).
static func _pose(anim: Animation, base: Node, time: float) -> void:
	for tr in anim.get_track_count():
		var path := anim.track_get_path(tr)
		var skel := base.get_node_or_null(NodePath(str(path).get_slice(":", 0))) as Skeleton3D
		if skel == null or path.get_subname_count() == 0:
			continue
		var bone := skel.find_bone(path.get_subname(0))
		if bone < 0:
			continue
		match anim.track_get_type(tr):
			Animation.TYPE_ROTATION_3D:
				skel.set_bone_pose_rotation(bone, anim.rotation_track_interpolate(tr, time))
			Animation.TYPE_POSITION_3D:
				skel.set_bone_pose_position(bone, anim.position_track_interpolate(tr, time))
			Animation.TYPE_SCALE_3D:
				skel.set_bone_pose_scale(bone, anim.scale_track_interpolate(tr, time))


func _settle() -> void:
	for i in SETTLE_FRAMES:
		await RenderingServer.frame_post_draw
