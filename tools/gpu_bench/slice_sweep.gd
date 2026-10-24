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
## --override=key=value,...: GraphicsSettings overrides on top of --preset (M2-RND-14; e.g. aa=fxaa, TAA off).
## Diagnosis (M2-RND-15): --pipeline-trace prints SLICE_PIPE for every frame over 50 ms or with a draw-time pipeline
## compile, with the frame's Performance pipeline-compilation counts (canvas, mesh, surface, draw, specialization).
## --budget (M2-RND-19): checks every segment against ADR 0029 as amended by ADR 0037 and prints SLICE_BUDGET; the
## run exits 1 if one is over. A hidden frame drawn behind the boot card's first-run cue (a cold first launch) may
## take 1.7 s, any other hidden frame 1 s, a visible frame 50 ms. tools/gpu_bench/run_cold_launch.sh runs it cold.
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
## The launch waits for the boot card this long (M2-RND-15): a cold first launch (an empty driver cache) holds the
## card for 30-36 s, and at the 30 s transition timeout the sweep's "visible" window used to start under the card,
## reporting a hidden first-run frame (825 ms) as a visible one.
const LAUNCH_TIMEOUT_S := 300.0
const FLOOD_HP_SHARE := 0.4
## ADR 0037: a hidden frame behind the boot card's first-run cue (a cold first launch only).
const FIRST_RUN_HIDDEN_MAX_MS := 1700.0
## ADR 0029: every other hidden frame, and every visible frame.
const HIDDEN_MAX_MS := 1000.0
const VISIBLE_MAX_MS := 50.0
## --pipeline-trace: frames over this (ms) are printed, and any frame with a draw-time pipeline compile.
const PIPELINE_TRACE_MS := 50.0
const PIPELINE_MONITORS: Array[Performance.Monitor] = [
	Performance.PIPELINE_COMPILATIONS_CANVAS,
	Performance.PIPELINE_COMPILATIONS_MESH,
	Performance.PIPELINE_COMPILATIONS_SURFACE,
	Performance.PIPELINE_COMPILATIONS_DRAW,
	Performance.PIPELINE_COMPILATIONS_SPECIALIZATION,
]
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
var _pipe_prev := PackedInt64Array()
var _segment_id := ""
## Per hidden frame of the current segment: drawn behind the boot card's first-run cue (ADR 0037). _frames_until
## fills _last_cued for its frames; the segment keeps the hidden window's.
var _hidden_cued := PackedByteArray()
var _last_cued := PackedByteArray()
var _over_budget: Array[String] = []
var _cue: Node


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
	# --override=key=value,... (M2-RND-14): a player's settings on top of the preset, e.g. aa=fxaa (TAA off).
	for pair in str(_opts.get("override", "")).split(",", false):
		var kv := pair.split("=", true, 1)
		if kv.size() == 2:
			gs.set_override(kv[0], kv[1].to_float() if kv[1].is_valid_float() else kv[1])
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
	if _opts.has("budget") and not _over_budget.is_empty():
		printerr("SLICE_BUDGET over in: %s" % ", ".join(_over_budget))
		get_tree().quit(1)
		return
	get_tree().quit()


func _segment(seg: Array, preset: String) -> void:
	var id := str(seg[0])
	_segment_id = id
	_hidden_cued.clear()
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
			_hidden_cued = _last_cued.duplicate()
			EventBus.scene_changed.disconnect(on_swap)
			visible = await _frames_until(func() -> bool: return not bool(router.call(&"is_busy")))
			visible.append_array(await _frames(VISIBLE_FRAMES))
			# The router's own record of the change (M1-ARC-16 visible window, M2-ARC-03 reveal fields).
			print("SLICE_SWAP_STATS %s %s" % [id, JSON.stringify(router.get(&"last_swap_stats"))])
			print(
				(
					"SLICE_MEM %s video %.0f MB texture %.0f MB"
					% [
						id,
						RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_VIDEO_MEM_USED) / 1048576.0,
						RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED) / 1048576.0
					]
				)
			)
		"launch":
			# As the game launches (boot.tscn is the main scene; no router change): the boot card holds the
			# title until the warm-ups end, then SceneRouter.measure_reveal records the window (M2-ARC-03).
			var router := get_tree().root.get_node(^"SceneRouter")
			get_tree().change_scene_to_file(str(seg[2]))
			hidden = await _frames_until(
				func() -> bool: return bool((router.get(&"last_swap_stats") as Dictionary).get("reveal", false)),
				LAUNCH_TIMEOUT_S
			)
			_hidden_cued = _last_cued.duplicate()
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
	if _opts.has("budget"):
		_check_budget(id, hidden, visible)


## ADR 0029 / 0037 for one segment: the worst cued hidden frame, the worst other hidden frame, the worst visible.
func _check_budget(id: String, hidden: PackedFloat64Array, visible: PackedFloat64Array) -> void:
	var cued := 0.0
	var other := 0.0
	for i in hidden.size():
		if i < _hidden_cued.size() and _hidden_cued[i] == 1:
			cued = maxf(cued, hidden[i])
		else:
			other = maxf(other, hidden[i])
	var vis := _pct(visible, 1.0)
	var ok := cued <= FIRST_RUN_HIDDEN_MAX_MS and other <= HIDDEN_MAX_MS and vis <= VISIBLE_MAX_MS
	print(
		(
			"SLICE_BUDGET %s %s | first-run hidden max %.1f / %.0f (%d) | hidden max %.1f / %.0f | visible max %.1f / %.0f"
			% [
				id,
				"ok" if ok else "OVER",
				cued,
				FIRST_RUN_HIDDEN_MAX_MS,
				_hidden_cued.count(1),
				other,
				HIDDEN_MAX_MS,
				vis,
				VISIBLE_MAX_MS,
			]
		)
	)
	if not ok:
		_over_budget.append(id)


## True while the boot card shows its first-run cue (BootCard.show_first_run_cue, M2-ARC-08): the frames ADR 0037
## lets take 1.7 s. Found by name, wherever the card is (at launch the boot isn't the current scene yet).
func _first_run_cue_showing() -> bool:
	if not is_instance_valid(_cue) or not _cue.is_inside_tree():
		_cue = get_tree().root.find_child("FirstRunCue", true, false)
	return _cue != null and _cue.is_inside_tree()


## True while something holds the router's fade opaque after its swap (SceneRouter.hold_reveal, M2-ARC-03).
static func _reveal_held(router: Node) -> bool:
	return router.has_method(&"reveal_holders") and not (router.call(&"reveal_holders") as Array).is_empty()


## Wall time of every frame until `done` is true (or `timeout_s` passes, which is reported: the frames after it
## are not the visible window the caller then measures).
func _frames_until(done: Callable, timeout_s: float = TRANSITION_TIMEOUT_S) -> PackedFloat64Array:
	var out := PackedFloat64Array()
	_last_cued.clear()
	var start := Time.get_ticks_usec()
	var prev := start
	while not bool(done.call()):
		if float(Time.get_ticks_usec() - start) / 1e6 >= timeout_s:
			push_warning("SLICE_TIMEOUT %s: gave up waiting after %.0f s" % [_segment_id, timeout_s])
			break
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		out.append(float(now - prev) / 1000.0)
		prev = now
		# A frame's cue state is read after it's drawn: the card lifts (and frees its cue) on a frame of its own.
		_last_cued.append(1 if _first_run_cue_showing() else 0)
		_trace_pipelines("hidden", out.size() - 1, out[-1])
	return out


func _frames(n: int) -> PackedFloat64Array:
	var out := PackedFloat64Array()
	var prev := Time.get_ticks_usec()
	for i in n:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		out.append(float(now - prev) / 1000.0)
		prev = now
		_trace_pipelines("visible", i, out[-1])
	return out


## --pipeline-trace (M2-RND-15): the frame's pipeline compiles by source, from Performance's counters.
func _trace_pipelines(window: String, i: int, ms: float) -> void:
	if not _opts.has("pipeline-trace"):
		return
	var now := PackedInt64Array()
	for m in PIPELINE_MONITORS:
		now.append(int(Performance.get_monitor(m)))
	var d := PackedInt64Array()
	for k in now.size():
		d.append(now[k] - (_pipe_prev[k] if _pipe_prev.size() == now.size() else 0))
	_pipe_prev = now
	if ms > PIPELINE_TRACE_MS or d[3] > 0:
		print(
			(
				"SLICE_PIPE %s %s f=%d ms=%.1f canvas=%d mesh=%d surface=%d draw=%d spec=%d"
				% [_segment_id, window, i, ms, d[0], d[1], d[2], d[3], d[4]]
			)
		)


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
