class_name SliceSweep
extends Node
## The first playable's thread end to end on a real GPU (the M2 slice perf sweep). Real GPU and window:
##   godot --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/slice_sweep.tscn -- \
##     --preset=high --res=2560x1440 --csv=C:/abs/slice.csv [--dwell=8 --segments=title,haluna_beach,...]
## Boots as the game does: GraphicsRuntime with --preset (never saved), then boot.tscn through
## SceneRouter, so the boot warm-up runs. Then it walks SEGMENTS in the thread's order, each a SceneRouter
## change (the real prewarm, fade and graphics hook), a battle request, or a step inside the current
## scene. The story flags that would start a cutscene are set first, so every view is the playable one,
## and autosaves are held (nothing is written to the saves).
## Per segment it records:
## - hidden: the frames from the request until the new scene is in (under the opaque fade), and while it
##   holds the fade (the title's boot warm-up, SceneRouter.hold_reveal, M2-ARC-03);
## - visible: the frames from then until 60 frames after the fade has lifted (ADR 0029's window);
## - dwell: --dwell seconds at the view, the wall and GPU time of every frame.
## It prints "SLICE_SWEEP <segment> ..." and appends one row per segment to --csv: perf_baseline.csv's
## columns (scene = "slice:<segment>", camera = the spawn) plus gpu_mean_ms, frame_max_ms,
## hidden_max_ms, hidden_total_ms (the whole load under the fade) and visible_max_ms.
## Diagnosis (M2-RND-07): --flood-trace prints the Flood's first 12 frames; --flood-variant=no_boss_vfx forces
## the phase without the set piece (BattleBossVfx freed first).

const BOOT_SCENE := "res://game/core/boot.tscn"
const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const SHELL_SHRINE := "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"
const HALUNA_ID := &"ch02/haluna"
## Flags whose cutscenes would otherwise play on arrival (first_playable.json; flags.tres).
const SEEN_FLAGS: Array[StringName] = [&"prologue_seen", &"ch02_met_asha", &"ch02_tideline_won", &"ch02_ate_at_nemes"]
## [segment id, kind, argument, spawn]. Kinds: launch (boot.tscn as the main scene, no router change: the
## boot card and the router's reveal window, M2-ARC-03; only as the first segment), scene (change to a scene
## path), place (move the player to
## a spawn of the current scene), battle (a field battle on an encounter), flood (the Drownbell's Flood
## phase, forced in the current battle).
const SEGMENTS := [
	["launch", "launch", BOOT_SCENE, ""],
	["title", "scene", BOOT_SCENE, ""],
	["haluna_beach", "scene", HALUNA, "Beach"],
	["haluna_village", "place", "", "Village"],
	["haluna_causeway", "place", "", "CausewayHead"],
	["tideline_battle", "battle", "ch02_tideline", "BattleReturn"],
	["shell_shrine", "scene", SHELL_SHRINE, ""],
	["drownbell_battle", "battle", "drownbell", ""],
	["drownbell_flood", "flood", "", ""],
]
const VISIBLE_FRAMES := 60
const TRANSITION_TIMEOUT_S := 30.0
const FLOOD_HP_SHARE := 0.4
const CSV_FIELDS := [
	"scene",
	"camera",
	"preset",
	"res_w",
	"res_h",
	"internal_w",
	"internal_h",
	"gpu_median_ms",
	"gpu_p99_ms",
	"cpu_median_ms",
	"frame_median_ms",
	"frame_p99_ms",
	"adapter",
	"driver",
	"gpu_mean_ms",
	"frame_max_ms",
	"hidden_max_ms",
	"hidden_total_ms",
	"visible_max_ms"
]

var _opts: Dictionary = {}
var _rid: RID


func _ready() -> void:
	# The sweep outlives every scene change: it runs from the tree root, not from this scene.
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := SliceSweep.new()
		driver.name = "SliceSweepDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	var res := str(_opts.get("res", "2560x1440")).split("x")
	win.size = Vector2i(int(res[0]), int(res[1]))
	var gs := GraphicsSettings.new()
	gs.set_preset(str(_opts.get("preset", "high")))
	GraphicsRuntime.set_settings(gs)
	_rid = get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_rid, true)
	var saves := get_tree().root.get_node_or_null(^"SaveSystem")
	if saves != null and saves.has_method(&"hold_autosave"):
		saves.call(&"hold_autosave", self)
	var wanted := str(_opts.get("segments", "")).split(",", false)
	for seg: Array in SEGMENTS:
		if not wanted.is_empty() and not wanted.has(str(seg[0])):
			continue
		if str(seg[0]) == "haluna_beach":
			for f in SEEN_FLAGS:
				Game.set_flag(f)
		await _segment(seg, gs.preset_id)
	get_tree().quit()


func _segment(seg: Array, preset: String) -> void:
	var id := str(seg[0])
	var kind := str(seg[1])
	var spawn := StringName(str(seg[3]))
	var hidden := PackedFloat64Array()
	var visible := PackedFloat64Array()
	match kind:
		"scene", "battle":
			var router := get_tree().root.get_node(^"SceneRouter")
			var swapped := [false]
			var on_swap := func(_p: String) -> void: swapped[0] = true
			EventBus.scene_changed.connect(on_swap)
			if kind == "scene":
				router.call(&"change_scene", str(seg[2]), spawn)
			else:
				BattleRequest.start(StringName(str(seg[2])), HALUNA_ID, spawn if spawn != &"" else &"BattleReturn")
			# M2-ARC-03: the title's warm-up holds the router's reveal; its frames are under the fade too.
			hidden = await _frames_until(func() -> bool: return bool(swapped[0]) and not _reveal_held(router))
			EventBus.scene_changed.disconnect(on_swap)
			visible = await _frames_until(func() -> bool: return not bool(router.call(&"is_busy")))
			visible.append_array(await _frames(VISIBLE_FRAMES))
			# The router's own record of the change (M1-ARC-16 visible window, M2-ARC-03 reveal fields).
			print("SLICE_SWAP_STATS %s %s" % [id, JSON.stringify(router.get(&"last_swap_stats"))])
		"launch":
			# As the game launches (boot.tscn is the main scene; no router change): the boot card holds the
			# title until the warm-ups end, then SceneRouter.measure_reveal records the window (M2-ARC-03).
			var router := get_tree().root.get_node(^"SceneRouter")
			get_tree().change_scene_to_file(str(seg[2]))
			hidden = await _frames_until(
				func() -> bool: return bool((router.get(&"last_swap_stats") as Dictionary).get("reveal", false))
			)
			visible = await _frames(VISIBLE_FRAMES)
			# The router closes its visible window a little after the card lifts; wait for its record.
			await _frames_until(
				func() -> bool: return (router.get(&"last_swap_stats") as Dictionary).has("max_visible_frame_ms")
			)
			print("SLICE_SWAP_STATS %s %s" % [id, JSON.stringify(router.get(&"last_swap_stats"))])
		"place":
			WorldReturn.place_player(get_tree().current_scene, spawn)
			visible = await _frames(VISIBLE_FRAMES)
		"flood":
			var ctl := get_tree().current_scene as BattleController
			if ctl != null and ctl.engine != null and not ctl.engine.enemies.is_empty():
				# --flood-variant=no_boss_vfx (diagnosis, M2-RND-07): without the set piece, what the polyps cost.
				if str(_opts.get("flood-variant", "")) == "no_boss_vfx":
					var bv := ctl.stage.find_child("BossVfx", true, false)
					if bv != null:
						bv.queue_free()
						await get_tree().process_frame
				var bell := ctl.engine.enemies[0]
				var vfx_node := ctl.stage.get_node_or_null(^"BattleVfx") as BattleVfx
				var variant := str(_opts.get("flood-variant", ""))
				if vfx_node != null and variant.begins_with("warm_"):  # play one effect first, then let it finish
					vfx_node.play(StringName(variant.trim_prefix("warm_")), bell.id)
					await _frames(180)
				bell.hp = int(bell.max_hp * FLOOD_HP_SHARE)
				BossMechanics.check_phases(ctl.engine)
			visible = await _frames(VISIBLE_FRAMES)
			if _opts.has("flood-trace"):
				print(
					(
						"SLICE_FLOOD_TRACE %s"
						% " ".join(Array(visible.slice(0, 12)).map(func(v: float) -> String: return "%.1f" % v))
					)
				)
	var dwell_us := float(_opts.get("dwell", 8.0)) * 1e6
	var walls := PackedFloat64Array()
	var gpus := PackedFloat64Array()
	var cpus := PackedFloat64Array()
	var start := Time.get_ticks_usec()
	var prev := start
	while float(Time.get_ticks_usec() - start) < dwell_us or walls.size() < VISIBLE_FRAMES:
		await RenderingServer.frame_post_draw
		var now := Time.get_ticks_usec()
		walls.append(float(now - prev) / 1000.0)
		prev = now
		gpus.append(RenderingServer.viewport_get_measured_render_time_gpu(_rid))
		cpus.append(RenderingServer.viewport_get_measured_render_time_cpu(_rid))
	var vp := get_viewport()
	var internal := Vector2(vp.size) * vp.scaling_3d_scale
	var row := {
		"scene": "slice:" + id,
		"camera": str(spawn) if spawn != &"" else "default",
		"preset": preset,
		"res_w": vp.size.x,
		"res_h": vp.size.y,
		"internal_w": roundi(internal.x),
		"internal_h": roundi(internal.y),
		"gpu_median_ms": "%.3f" % _pct(gpus, 0.5),
		"gpu_p99_ms": "%.3f" % _pct(gpus, 0.99),
		"cpu_median_ms": "%.3f" % _pct(cpus, 0.5),
		"frame_median_ms": "%.3f" % _pct(walls, 0.5),
		"frame_p99_ms": "%.3f" % _pct(walls, 0.99),
		"adapter": RenderingServer.get_video_adapter_name(),
		"driver": RenderingServer.get_video_adapter_api_version(),
		"gpu_mean_ms": "%.3f" % _mean(gpus),
		"frame_max_ms": "%.1f" % _pct(walls, 1.0),
		"hidden_max_ms": "%.1f" % _pct(hidden, 1.0),
		"hidden_total_ms": "%.0f" % (_mean(hidden) * hidden.size()),
		"visible_max_ms": "%.1f" % _pct(visible, 1.0),
	}
	print(
		(
			(
				"SLICE_SWEEP %s %s gpu med %s mean %s p99 %s | frame med %s p99 %s max %s"
				+ " | hidden max %s total %s (%d) | visible max %s (%d) | scene %s"
			)
			% [
				id,
				preset,
				row["gpu_median_ms"],
				row["gpu_mean_ms"],
				row["gpu_p99_ms"],
				row["frame_median_ms"],
				row["frame_p99_ms"],
				row["frame_max_ms"],
				row["hidden_max_ms"],
				row["hidden_total_ms"],
				hidden.size(),
				row["visible_max_ms"],
				visible.size(),
				get_tree().current_scene.scene_file_path if get_tree().current_scene != null else "-",
			]
		)
	)
	_write_csv(row)


## True while something holds the router's fade opaque after its swap (SceneRouter.hold_reveal, M2-ARC-03).
static func _reveal_held(router: Node) -> bool:
	return router.has_method(&"reveal_holders") and not (router.call(&"reveal_holders") as Array).is_empty()


## Wall time of every frame until `done` is true (or TRANSITION_TIMEOUT_S passes).
func _frames_until(done: Callable) -> PackedFloat64Array:
	var out := PackedFloat64Array()
	var start := Time.get_ticks_usec()
	var prev := start
	while not bool(done.call()) and float(Time.get_ticks_usec() - start) / 1e6 < TRANSITION_TIMEOUT_S:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		out.append(float(now - prev) / 1000.0)
		prev = now
	return out


func _frames(n: int) -> PackedFloat64Array:
	var out := PackedFloat64Array()
	var prev := Time.get_ticks_usec()
	for i in n:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		out.append(float(now - prev) / 1000.0)
		prev = now
	return out


func _write_csv(row: Dictionary) -> void:
	var path := str(_opts.get("csv", ""))
	if path == "":
		return
	var fresh := not FileAccess.file_exists(path)
	var f := FileAccess.open(path, FileAccess.READ_WRITE if not fresh else FileAccess.WRITE)
	if f == null:
		push_error("SliceSweep: cannot write %s" % path)
		return
	f.seek_end()
	if fresh:
		f.store_line(",".join(CSV_FIELDS))
	f.store_line(",".join(CSV_FIELDS.map(func(k: String) -> String: return str(row.get(k, "")))))
	f.close()


static func _pct(values: PackedFloat64Array, q: float) -> float:
	if values.is_empty():
		return 0.0
	var s := values.duplicate()
	s.sort()
	return s[clampi(int(q * (s.size() - 1)), 0, s.size() - 1)]


static func _mean(values: PackedFloat64Array) -> float:
	var acc := 0.0
	for v in values:
		acc += v
	return acc / maxf(values.size(), 1.0)


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
