extends Node
## FAST-TRACK 11-03: the status contact sheet. On the real stage (an Act I fight, the party and a foe at the rest
## frame), each of the 21 statuses in turn on the first hero AND the first foe at once, one still per status:
##   <out>/<nn>_<status>.png    (1920x1080 by default, --size=WxH)
##   <out>/stack.png            three statuses at once on each (icons in a row, the highest-priority overlay)
## Montage them with ImageMagick (docs/kb/tech/battle_status_looks.md).
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://tools/vfx/status_look_sheet.tscn -- --out=<abs dir> [--enc=ch01_scuttlers] [--only=poison,sleep]

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const SWEEP := preload("res://tools/vfx/encounter_sweep.gd")
const SEED := 20261103
const SETTLE_FRAMES := 45
const STACK: Array[StringName] = [&"poison", &"protect", &"slow"]
const STACK_FOE: Array[StringName] = [&"doom", &"armor_break", &"provoke"]


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var opts := _args()
	var out := str(opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var sz := str(opts.get("size", "1920x1080")).split("x")
	get_window().size = Vector2i(int(sz[0]), int(sz[1]))
	var enc := StringName(str(opts.get("enc", "ch01_scuttlers")))
	var ctl := (load(SCENE) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.persist_progress = false
	add_child(ctl)
	ctl.pacing_scale = 0.0
	ctl.set_meta(BattleBossIntro.META_PLAYED, String(enc))
	var party := SWEEP.party_for(enc)
	ctl.start_battle(party[0], party[1], enc, SEED)
	var guard := 0
	while not (ctl.engine.is_party_turn() and ctl.state == BattleController.STATE_COMMAND) and guard < 40:
		guard += 1
		if ctl.stage.choreo.playing():
			ctl.stage.choreo.finish()
		ctl.tick(0.2)
		await get_tree().process_frame
	var looks := ctl.stage.get_node(^"BattleStatusLooks") as BattleStatusLooks
	var hero := ctl.engine.party_active[0]
	var foe := ctl.engine.enemies[0]
	var only := str(opts.get("only", "")).split(",", false)
	var i := 0
	for sid: Variant in ctl.engine.db.statuses:
		i += 1
		if not only.is_empty() and not only.has(str(sid)):
			continue
		_set(ctl, hero, [StringName(str(sid))] as Array[StringName])
		_set(ctl, foe, [StringName(str(sid))] as Array[StringName])
		looks.refresh()
		await _capture(out.path_join("%02d_%s.png" % [i, sid]))
		print("STATUS_SHEET %s" % sid)
	_set(ctl, hero, STACK)
	_set(ctl, foe, STACK_FOE)
	looks.refresh()
	await _capture(out.path_join("stack.png"))
	get_tree().quit()


func _set(ctl: BattleController, c: BattleCombatant, ids: Array[StringName]) -> void:
	c.statuses.clear()
	for sid in ids:
		c.statuses[sid] = 3
	ctl.stage.refresh_ko(ctl.engine)  # Petrify's stone


func _capture(path: String) -> void:
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	img.save_png(path)


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--"):
			var kv := a.substr(2).split("=", true, 1)
			out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
