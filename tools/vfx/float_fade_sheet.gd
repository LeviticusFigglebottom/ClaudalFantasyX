extends Node
## act1_gpu_qa row 70 (the Lead's 11-03: "the party's damage numbers on foes are a faint translucent grey"). On the
## real stage and HUD, a party attack in `--enc` (default ch02_tideline), stills of its damage number through its
## life (DamageNumber: the pop, the rise, the fade), with the number's own alpha and colour in a JSON line each:
##   <out>/<enc>_t<ms>.png   1920x1080 by default
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://tools/vfx/float_fade_sheet.tscn -- --out=<abs dir> [--enc=ch02_tideline] [--at_ms=60,300,600,760,850]

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const SWEEP := preload("res://tools/vfx/encounter_sweep.gd")
const SEED := 20261103
const FRAME_SEC := 1.0 / 60.0


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var opts := _args()
	var out := str(opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var sz := str(opts.get("size", "1920x1080")).split("x")
	get_window().size = Vector2i(int(sz[0]), int(sz[1]))
	var enc := StringName(str(opts.get("enc", "ch02_tideline")))
	var at_ms: Array[int] = []
	for s in str(opts.get("at_ms", "60,300,600,760,850")).split(","):
		at_ms.append(int(s))
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
	ctl._begin_target(&"attack")
	for i in 10:
		await get_tree().process_frame
	var picked := ctl.picked_ids()
	ctl.pacing_scale = 1.0
	ctl.stage.choreo.speed = 1.0
	var layer := ctl.hud.get_node(^"%DamageLayer")
	var before := layer.get_child_count()
	ctl.act(&"attack", picked)
	var waited := 0.0
	while layer.get_child_count() <= before and waited < 8.0:
		ctl.tick(FRAME_SEC)
		await get_tree().process_frame
		waited += FRAME_SEC
	var num: DamageNumber = null
	for n in layer.get_children():
		if n is DamageNumber:
			num = n as DamageNumber
	if num == null:
		push_warning("float_fade_sheet: no damage number in %s" % enc)
		get_tree().quit()
		return
	num.tween.pause()  # stepped by hand from here: one still per moment, exactly
	var t_ms := 0
	for ms in at_ms:
		if ms > t_ms:
			num.tween.custom_step(float(ms - t_ms) / 1000.0)
			t_ms = ms
		await _capture(out.path_join("%s_t%03d.png" % [enc, ms]))
		var col := num.get_theme_color(&"font_color")
		if num.has_theme_color_override(&"font_color"):
			col = num.get_theme_color(&"font_color")
		print(
			(
				"FLOAT %s t=%d alpha=%.2f colour=%s outline=%d size=%d text=%s at=%s"
				% [
					enc,
					ms,
					num.modulate.a,
					col.to_html(false),
					num.get_theme_constant(&"outline_size"),
					num.get_theme_font_size(&"font_size"),
					num.text,
					num.global_position,
				]
			)
		)
	get_tree().quit()


func _capture(path: String) -> void:
	for i in 2:
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
