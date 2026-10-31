extends Node
## The Lead's Act I readability pass (10-30, pillar 4: the player always knows who acts next and what an action
## costs). For each Act I encounter, at 1920x1080 and each text scale (accessibility.json text_scale), on the real
## stage and HUD:
##   <enc>_<scale>_target.png   a party turn's target pick (the cursor and rings, the action's cost on the timeline)
##   <enc>_<scale>_hit.png      the contact of that action, its damage number shown
## and checks.json per encounter:
##   overflow   HUD labels whose text needs more room than they have (clipped or overrunning)
##   floats     damage numbers and float words drawn over the turn order (timeline) or the party panel
## The 3D VFX draw under the HUD's CanvasLayers (and the flashes on a layer below it, effects.json safety), so no
## effect can cover the turn order; the floats share the HUD's layers and are checked here.
##   godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver vulkan \
##     res://tools/vfx/readability_sheet.tscn -- --out=<abs dir> [--only=<enc,...>] [--scales=1.0,1.3]

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const SWEEP := preload("res://tools/vfx/encounter_sweep.gd")
const SEED := 20261030
const SIZE := Vector2i(1920, 1080)
const SETTLE_FRAMES := 24
const FLOAT_WAIT_SEC := 0.25

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	get_window().size = SIZE
	var scales: Array[float] = []
	for s in str(_opts.get("scales", "1.0,1.3")).split(","):
		scales.append(float(s))
	var only := str(_opts.get("only", "")).split(",", false)
	var summary := {}
	for enc: StringName in SWEEP.act_one_encounters():
		if not only.is_empty() and not only.has(String(enc)):
			continue
		var checks := {"overflow": [], "floats": []}
		for sc in scales:
			await _one(enc, sc, out, checks)
		var f := FileAccess.open(out.path_join("%s_checks.json" % enc), FileAccess.WRITE)
		f.store_string(JSON.stringify(checks, "  "))
		f.close()
		summary[String(enc)] = {
			"overflow": (checks["overflow"] as Array).size(), "floats": (checks["floats"] as Array).size()
		}
		print("READABILITY %s %s" % [enc, summary[String(enc)]])
	var sf := FileAccess.open(out.path_join("summary.json"), FileAccess.WRITE)
	sf.store_string(JSON.stringify(summary, "  "))
	sf.close()
	get_tree().quit()


func _one(enc: StringName, text_scale: float, out: String, checks: Dictionary) -> void:
	var ctl := (load(SCENE) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.persist_progress = false
	add_child(ctl)
	ctl.pacing_scale = 0.0
	ctl.set_meta(BattleBossIntro.META_PLAYED, String(enc))
	var party := SWEEP.party_for(enc)
	ctl.start_battle(party[0], party[1], enc, SEED)
	var settings := UiSettings.shared()  # the game's own settings (the HUD's rows read the shared text scale)
	settings.set_value(UiSettings.TEXT_SCALE, text_scale)
	ctl.hud.apply_settings(settings)
	var guard := 0
	while not (ctl.engine.is_party_turn() and ctl.state == BattleController.STATE_COMMAND) and guard < 40:
		guard += 1
		if ctl.engine.outcome != &"":
			break
		if ctl.stage.choreo.playing():
			ctl.stage.choreo.finish()
		ctl.tick(0.2)
		await get_tree().process_frame
	var tag := "%s_%.2f" % [enc, text_scale]
	if ctl.engine.is_party_turn() and ctl.engine.outcome == &"":
		ctl._begin_target(&"attack")
		for i in SETTLE_FRAMES:
			await get_tree().process_frame
		_check_labels(ctl, tag, "target", checks)
		await _capture(out.path_join(tag + "_target.png"))
		var picked := ctl.picked_ids()
		ctl.pacing_scale = 1.0
		ctl.stage.choreo.speed = 1.0
		var hits_before := ctl.hud.get_node(^"%DamageLayer").get_child_count()
		ctl.act(&"attack", picked)
		var waited := 0.0
		while ctl.hud.get_node(^"%DamageLayer").get_child_count() <= hits_before and waited < 6.0:
			ctl.tick(1.0 / 60.0)
			await get_tree().process_frame
			waited += 1.0 / 60.0
		await get_tree().create_timer(FLOAT_WAIT_SEC).timeout
		_check_floats(ctl, tag, checks)
		_check_labels(ctl, tag, "hit", checks)
		await _capture(out.path_join(tag + "_hit.png"))
	remove_child(ctl)
	ctl.queue_free()
	await get_tree().process_frame


## Labels under the HUD whose text needs more room than they are given (clip_text or not, the text is cut or spills).
func _check_labels(ctl: BattleController, tag: String, moment: String, checks: Dictionary) -> void:
	for n in ctl.hud.find_children("*", "Label", true, false):
		var l := n as Label
		if not l.is_visible_in_tree() or l.text.strip_edges() == "" or l is DamageNumber:
			continue
		if l.autowrap_mode != TextServer.AUTOWRAP_OFF:
			if l.max_lines_visible > 0 and l.get_line_count() > l.max_lines_visible:
				(checks["overflow"] as Array).append(
					{
						"at": tag,
						"moment": moment,
						"label": str(l.get_path()),
						"text": l.text,
						"lines": l.get_line_count()
					}
				)
			continue
		var need := (
			l
			. get_theme_font(&"font")
			. get_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, l.get_theme_font_size(&"font_size"))
			. x
		)
		if need > l.size.x + 1.0 and l.text_overrun_behavior == TextServer.OVERRUN_NO_TRIMMING:
			(checks["overflow"] as Array).append(
				{"at": tag, "moment": moment, "label": str(l.get_path()), "text": l.text, "need": need, "has": l.size.x}
			)


## Damage numbers and float words over the turn order or the party panel.
func _check_floats(ctl: BattleController, tag: String, checks: Dictionary) -> void:
	var keep := {}  # every panel the floats keep clear of (battle_hud.json damage.avoid), as shown
	for row: Variant in HudLayout.section(&"damage").get("avoid", []):
		var r := HudLayout.panel_rect(row as Dictionary, ctl.hud)
		if r.has_area():
			keep[str((row as Dictionary).get("node", ""))] = r
	for n in ctl.hud.get_node(^"%DamageLayer").get_children():
		var d := n as Control
		if d == null or not d.visible:
			continue
		var r := Rect2(d.global_position, d.size * d.scale)
		for k: String in keep:
			if r.intersects(keep[k] as Rect2):
				(checks["floats"] as Array).append(
					{"at": tag, "float": (d as Label).text if d is Label else "", "over": k, "rect": str(r)}
				)


func _capture(path: String) -> void:
	for i in 3:
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
