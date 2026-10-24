class_name BattleVfxProbe
extends Node
## Battle VFX on the GPU (M2-RND-03): key frames and the cost of the worst case. Real GPU and window:
##   godot --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync res://tools/gpu_bench/battle_vfx_probe.tscn -- \
##     --preset=high --res=1920x1080 --out=C:/abs/dir [--bench --frames=300 --reduced-motion --effect=<id>]
## Loads the battle sandbox (it starts its own battle), applies the preset as capture_preset does, and drives
## the scene's BattleVfx directly at its fighters.
## - Default: plays each key-frame group and saves <group>.png at the group's capture time.
## - --bench: prints the GPU time over --frames frames with no effects, then with the worst 3v3 burst
##   (a fire hit, a status and a KO on all three foes, and Shallows Verse on the party) replayed every
##   BURST_EVERY frames: "BATTLE_VFX_BENCH <label> median p99 max".

const SCENE := "res://game/battle/scene/battle_sandbox.tscn"
const SETTLE_FRAMES := 90
const BURST_EVERY := 30
## Key frames: [group, [[effect, side, index]...], seconds after the play to capture].
const GROUPS := [
	["elements", [["hit_fire", "foe", 0], ["hit_ice", "foe", 1], ["hit_lightning", "foe", 2]], 0.12],
	["water_holy", [["hit_water", "foe", 0], ["hit_holy", "foe", 1], ["status_apply", "foe", 2]], 0.15],
	["lamp_dive", [["lamp_dive", "foe", 0], ["hit_none", "foe", 0]], 0.18],
	["shallows_verse", [["shallows_verse", "party", 0], ["shallows_verse", "party", 1], ["heal", "party", 1]], 0.6],
	["read", [["read", "foe", 1]], 0.4],
	["ko", [["ko_release", "foe", 1]], 1.2],
	["ambush_flash", [["flash_ambush", "none", 0]], 0.09],
]

var _opts: Dictionary = {}


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	_opts = _args()
	var out := str(_opts.get("out", ""))
	DirAccess.make_dir_recursive_absolute(out)
	var res := str(_opts.get("res", "1920x1080")).split("x")
	var win := get_window()
	win.borderless = true
	win.position = DisplayServer.screen_get_position(win.current_screen)
	win.size = Vector2i(int(res[0]), int(res[1]))
	var preset := str(_opts.get("preset", "high"))
	var scene := (load(SCENE) as PackedScene).instantiate()
	add_child(scene)
	await get_tree().process_frame
	var gs := GraphicsSettings.new()
	gs.set_preset(preset)
	var envs := scene.find_children("*", "WorldEnvironment", true, false)
	gs.apply_current(get_viewport(), (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null)
	CharacterShaderTiers.apply_to_tree(scene, CharacterShaderTiers.tier_for_preset(preset))
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	var ctl_node := scene as BattleController  # the sandbox's root is the controller
	var vfx := ctl_node.stage.get_node_or_null(^"BattleVfx") as BattleVfx
	if vfx == null:
		push_error("BattleVfxProbe: no BattleVfx under the stage")
		get_tree().quit(1)
		return
	vfx.reduced_motion = _opts.has("reduced-motion")
	if _opts.has("bench"):
		await _bench(vfx, ctl_node.engine, preset)
	else:
		for g: Array in GROUPS:
			for e: Array in g[1]:
				vfx.play(StringName(e[0]), _target(ctl_node.engine, str(e[1]), int(e[2])))
			await get_tree().create_timer(float(g[2])).timeout
			await RenderingServer.frame_post_draw
			var img := get_viewport().get_texture().get_image()
			img.convert(Image.FORMAT_RGB8)
			img.save_png(out.path_join("%s.png" % g[0]))
			print("BATTLE_VFX_FRAME ok %s" % g[0])
			for i in 120:  # let it clear before the next group
				await get_tree().process_frame
	get_tree().quit()


func _bench(vfx: BattleVfx, engine: BattleEngine, preset: String) -> void:
	var rid := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	var frames := int(_opts.get("frames", 300))
	var label := (
		"%s%s%s"
		% [preset, "_reduced" if vfx.reduced_motion else "", "_" + str(_opts["effect"]) if _opts.has("effect") else ""]
	)
	for pass_name in ["idle", "burst"]:
		var times: Array[float] = []
		for i in frames:
			if pass_name == "burst" and i % BURST_EVERY == 0:
				if _opts.has("effect"):  # one effect on every foe: its own cost
					for f in engine.enemies:
						vfx.play(StringName(str(_opts["effect"])), f.id)
				else:
					for f in engine.enemies:
						vfx.play(&"hit_fire", f.id)
						vfx.play(&"status_apply", f.id)
						vfx.play(&"ko_release", f.id)
					for p in engine.party_active:
						vfx.play(&"shallows_verse", p.id)
			await get_tree().process_frame
			times.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
		times.sort()
		print(
			(
				"BATTLE_VFX_BENCH %s_%s %.3f %.3f %.3f"
				% [label, pass_name, times[times.size() / 2], times[int(times.size() * 0.99)], times[-1]]
			)
		)


static func _target(engine: BattleEngine, side: String, index: int) -> StringName:
	var list: Array[BattleCombatant] = engine.enemies if side == "foe" else engine.party_active
	if list.is_empty() or side == "none":
		return &""
	return list[mini(index, list.size() - 1)].id


func _args() -> Dictionary:
	var out := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out
