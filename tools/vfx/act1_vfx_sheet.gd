extends Node
## ADR 0041: a contact sheet of the Act I abilities' own effects (tools/vfx/gen_act1_ability_vfx.py), so each one is
## viewed on the real battle stage. Loads the battle sandbox held at its first turn (three foes, three heroes), plays
## the mapped skill and item effects one per fighter (its id labelled beside it), and saves sheet_<n>.png `at` seconds
## (default 0.12) after the play. Run it like a
## capture (the software renderer or a GPU):
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://tools/vfx/act1_vfx_sheet.tscn -- --out=<abs dir> [--at=0.12] [--only=id,id]
##     [--encounter=<id> [--enemy_set]]   (an encounter's own arena; --enemy_set: its foes' effects)

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const SETTLE_FRAMES := 30
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const CLEAR_FRAMES := 150

var _opts: Dictionary = {}
var _engine: BattleEngine


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	get_window().size = Vector2i(1280, 720)
	var scene := (load(SCENE) as PackedScene).instantiate() as BattleController
	scene.auto_start = false
	scene.persist_progress = false
	add_child(scene)
	scene.pacing_scale = 0.0
	# held at the first turn: nobody acts. --encounter fights on that encounter's arena (its own foes).
	scene.set_meta(BattleBossIntro.META_PLAYED, str(_opts.get("encounter", "sandbox_reef")))
	scene.start_battle(PARTY, [], StringName(str(_opts.get("encounter", "sandbox_reef"))), 20261028)
	_engine = scene.engine
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	var vfx := scene.stage.get_node_or_null(^"BattleVfx") as BattleVfx
	var cam := scene.stage.get_viewport().get_camera_3d()
	var spots: Array[StringName] = []
	for c in scene.engine.enemies + scene.engine.party_active:
		spots.append(c.id)
	var ids := _effect_ids(vfx)
	var labels := CanvasLayer.new()
	labels.layer = 10
	add_child(labels)
	var sheet := 0
	while not ids.is_empty():
		var group := ids.slice(0, spots.size())  # one per fighter
		ids = ids.slice(spots.size())
		for n in labels.get_children():
			n.queue_free()
		for i in group.size():
			var target := spots[i % spots.size()]
			vfx.play(StringName(group[i]), target)
			var l := Label.new()
			l.text = group[i]
			l.add_theme_font_size_override(&"font_size", 18)
			l.add_theme_color_override(&"font_color", Color.YELLOW)
			l.add_theme_color_override(&"font_outline_color", Color.BLACK)
			l.add_theme_constant_override(&"outline_size", 6)
			l.position = cam.unproject_position(vfx.anchor(target, "head")) + Vector2(-40.0, -40.0)
			labels.add_child(l)
		await get_tree().create_timer(float(_opts.get("at", 0.12))).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		img.save_png(out.path_join("sheet_%02d.png" % sheet))
		print("ACT1_VFX_SHEET %d %s" % [sheet, ",".join(group)])
		sheet += 1
		for i in CLEAR_FRAMES:
			await get_tree().process_frame
	get_tree().quit()


## The skill and item effects to show: every map.skills/map.items effect, or --only's.
func _effect_ids(vfx: BattleVfx) -> Array[String]:
	var out: Array[String] = []
	if _opts.has("only"):
		for s in str(_opts["only"]).split(","):
			out.append(s)
		return out
	var map := vfx.data["map"] as Dictionary
	if _opts.has("enemy_set"):  # the hit, status and KO effects, then this fight's foes' own skills (an arena check)
		for e: String in ["hit_none", "status_apply", "ko_release"]:
			out.append(e)
		for c in _engine.enemies:
			for sid: StringName in c.skills:
				var eid := str((map["skills"] as Dictionary).get(String(sid), ""))
				if eid != "" and not out.has(eid):
					out.append(eid)
		return out
	for table: String in ["skills", "items"]:
		for k: String in map[table]:
			var eid := str((map[table] as Dictionary)[k])
			if not out.has(eid):
				out.append(eid)
	return out


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
