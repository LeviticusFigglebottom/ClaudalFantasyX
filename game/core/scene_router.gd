extends Node
## Autoload "SceneRouter": async scene loading behind a fade, with a shader-prewarm hook.
##
## Public API (stable since M0, additions below): change_scene(path), is_busy(), signal
## prewarm_requested(path), FADE_SEC.
## M1-ARC-06: change_scene(path, spawn) also places the player on Spawns/<spawn> once the new scene
## is in the tree (still under the opaque fade), and `world_return` (a WorldReturn child) returns
## the party to its respawn point on EventBus.game_loaded once boot.gd arms it.
## Added in the M1-RND-06 fix: signal swap_measured(stats) and last_swap_stats (see below).
## M1-ARC-15: when the new scene's root is ready (main thread, in the tree, before its first draw),
## the player's graphics settings are applied to it (attach_graphics_hook; only after boot armed it).
## M1-RND-15 / M1-RND-23 (review-sweep-J S2):
##   - signal scene_swapping(scene_path): under the opaque fade, just before the new scene enters the
##     tree. Zone render globals reset on it (ShaderGlobals.install connects ShaderGlobals.ZONE_GLOBALS:
##     the zone sea-glow and the water level go back to their project defaults), so the router names
##     no system that owns a global.
##   - hold_swap(holder) / release_swap(holder) / swap_holders(): while anything holds the swap, the
##     new scene waits under the opaque fade, at most PREWARM_WAIT_MAX_FRAMES frames (the time-sliced
##     ShaderPrewarm stage holds it while staging). Callers can see a change take up to that many
##     frames (2 s at 60 fps) longer; the wait is recorded in last_swap_stats["prewarm_wait_frames"].
## M2-ARC-02: WeatherClock.install(self) adds the weather clock's owner as a child (it advances
##   hymn_wind_time every frame and writes the zone's hymn_wind on scene_swapping), the same way.
##
## SPEC §4.2 allows no frame over 50 ms in a transition, so the expensive steps are kept out of the
## frame that shows the new scene (docs/kb/tech/architecture.md, "Scene-swap hitch"):
##   1. The threaded load runs while the screen fades out. Meanwhile, the theme's fonts are
##      rasterized a few (font, size) pairs per frame under the opaque fade (FontWarmer), because
##      first-use glyph rasterization was the largest CPU cost of a cold swap.
##   2. prewarm_requested fires before the swap, so the ShaderPrewarm stage is built (scene load,
##      material load, shader front-end compile) in a frame of its own. The stage then feeds its draws
##      in a few per frame (M1-RND-15) and holds the swap (hold_swap) while it is staging, up
##      to PREWARM_WAIT_MAX_FRAMES, so pipelines compile in small slices under the opaque fade.
##   3. The PackedScene is instantiated on a WorkerThreadPool thread (the node is not in the tree
##      yet, which Godot 4 allows), never on the main thread, and only once the swap's holders are done
##      (row 67: its load() calls must not wait on a threaded load of the same file in flight).
##   4. The old scene is unloaded one frame before the new one is added, so freeing it and
##      entering the new scene's _ready never share a frame.
## Each swap records its phase costs and frame times in last_swap_stats, emits swap_measured, and
## warns when a frame is over its budget.
## M1-ARC-16 (ADR 0029, SPEC §4.2 v1.3): two windows, each against its own budget.
##   - Hidden: the MEASURE_FRAMES frames after the new scene is handed to the tree, still under the opaque
##     fade (frame_ms, max_frame_ms), against HIDDEN_FRAME_BUDGET_MS (1 s). The whole change, from
##     change_scene() to the fade starting to lift (entry_ms), is against ENTRY_BUDGET_MS (3 s).
##   - Visible: every frame while the fade lifts, then the first VISIBLE_MEASURE_FRAMES after it has lifted
##     (visible_frame_ms, max_visible_frame_ms), against SWAP_BUDGET_MS (50 ms). These finish after
##     change_scene() returns: is_measuring() is true until then, and visible_measured(stats) fires
##     with the same dictionary, completed. A new change_scene() cuts the window short
##     (visible_complete false).
## M2-ARC-03 (ADR 0029: the boot warm-up runs under a boot screen, before the title shows):
##   - hold_reveal(holder) / release_reveal(holder) / reveal_holders(): while anything holds the reveal, a
##     change keeps its fade opaque after the swap (the boot title holds it while its warm-up runs) until a
##     stall or the safety cap (M2-ARC-08, below); the visible window starts when the fade starts to lift,
##     after the hold. The wait is hidden loading time, recorded apart from entry_ms (reveal_wait_ms,
##     reveal_wait_frames, reveal_wait_max_frame_ms), each frame against HIDDEN_FRAME_BUDGET_MS.
##   - measure_reveal(scene_path, lifted): the same visible window for a reveal the router does not own (the
##     BootCard lifting off the title at launch, when no change ran). It becomes last_swap_stats and ends with
##     visible_measured.
##   - warm_fonts_now() / fonts_ready(): the theme font warm-up outside a change (boot runs it under its card).
##   - cancel_visible_window(): ends the window being measured (change_scene() and measure_reveal() call it).
## M2-ARC-08: the reveal hold waits while its holders make progress, not for a fixed 10 s. A ProgressWait
##   (game/data/settings/boot_card.json) is fed each frame and holders_progress() (the holders' wait_progress(),
##   a BootCard's sums its work); the fade lifts on a stall (stall_timeout_ms with no progress) or the absolute
##   cap (max_wait_ms), recorded as reveal_wait_end. font_warm_progress() reports the font warm-up's progress.
## ADR 0111 (Lead 2026-10-28, the PC's 1.3-3 s hidden frames): signal change_started(scene_path) fires as a change
##   begins, before the fade; ResidentLoads.install(self) loads the hero bodies there on worker threads and holds the
##   swap until they are in, so the new scene's first frame finds them cached.
## M2-ARC-05: every window's frames are wall time, timed by a FrameClock (Time.get_ticks_usec between
## frames), never the process `delta`, which Godot caps at about 150 ms.

signal prewarm_requested(scene_path: String)
## ADR 0111: emitted when change_scene() starts (before the fade): ResidentLoads starts its threaded loads here.
signal change_started(scene_path: String)
## Emitted under the opaque fade with the new scene's root once it is instantiated (on the worker thread, when
## instantiate_on_thread), before it enters the tree: a profiler can watch its nodes' ready (SceneSwapProbe
## --ready-profile; slice-polish's Haluna add-to-tree frame).
signal scene_instantiated(node: Node)
## Emitted under the opaque fade, just before the new scene enters the tree (zone globals reset here).
signal scene_swapping(scene_path: String)
## Emitted after each successful swap with the same dictionary stored in last_swap_stats.
signal swap_measured(stats: Dictionary)
## M1-ARC-16: emitted when the visible window ends (same dictionary, now with the visible_* keys).
signal visible_measured(stats: Dictionary)

const FADE_SEC := 0.35
const FADE_LAYER := 128
## SPEC §4.2: no visible hitch over 50 ms (the visible window, ADR 0029).
const SWAP_BUDGET_MS := 50.0
## Frames measured after the new scene is handed to the tree (its _ready and first draw land here).
## They are under the opaque fade: loading time (ADR 0029).
const MEASURE_FRAMES := 4
## SPEC §4.2 / ADR 0029: no single frame hidden behind the fade over 1 s.
const HIDDEN_FRAME_BUDGET_MS := 1000.0
## SPEC §4.2 / ADR 0029: a zone entry (change_scene() until the fade starts to lift) under 3 s.
const ENTRY_BUDGET_MS := 3000.0
## ADR 0029: "the first 60 frames after any fade lifts" are visible frames (the frames while it lifts
## are measured too).
const VISIBLE_MEASURE_FRAMES := 60
## Upper bound on frames a swap waits for its holders (hold_swap), e.g. a time-sliced ShaderPrewarm
## stage (M1-RND-15).
const PREWARM_WAIT_MAX_FRAMES := 120
## ADR 0111: past PREWARM_WAIT_MAX_FRAMES a held swap waits on while its holders make progress, until they stall this
## long (ms of wall time) or the wait reaches SWAP_WAIT_CAP_MS (the hidden loading time stays in short frames).
const SWAP_STALL_MS := 3000.0
const SWAP_WAIT_CAP_MS := 15000.0
const USEC_PER_MSEC := 1000.0
const LOG_PREFIX := "SceneRouter"
## The scenes a field zone stays resident through (see keep_field_resident).
const RESIDENT_THROUGH: Array[String] = ["res://game/flow/field_battle.tscn"]
## Called on every node of a resident zone when it comes back (ZoneStory, HalunaStory, GreyboxZone implement it).
const RESIDENT_RETURN_METHOD := &"on_resident_return"
## Frames the resident zone may take to be back in the tree before its arrival runs anyway (a safety cap).
const RESIDENT_ENTER_MAX_FRAMES := 30

## Tuning switches (all on in the game; tests and the profiler flip them to compare).
var instantiate_on_thread := true
var warm_fonts := true
var split_swap := true
## Last swap: {scene_path, instantiate_ms, instantiated_on_thread, unload_ms, prewarm_ms, fonts_warmed,
## font_warm_ms, frame_ms: Array[float] (MEASURE_FRAMES hidden frames from the swap), max_frame_ms,
## budget_ms (HIDDEN_FRAME_BUDGET_MS), over_budget (a hidden frame over it), entry_ms, entry_budget_ms,
## entry_over_budget, cover_alpha_min, covered (ADR 0042 §4: the swap and its hidden frames under the opaque fade)},
## then, once the visible window ends (M1-ARC-16): {visible_frame_ms: Array[float],
## lift_frames (how many of them were while the fade lifted), max_visible_frame_ms, visible_budget_ms,
## visible_over_budget, visible_complete}.
var last_swap_stats: Dictionary = {}
## Return-to-world on load (M1-ARC-06). Disabled until boot.gd sets world_return.enabled.
var world_return: WorldReturn
## The field kept resident through a random fight (the human's playtest: seconds of black after every won battle,
## the whole zone loaded, instantiated and readied again on the way back). A change from a field zone into one of
## RESIDENT_THROUGH for a fight (BattleRequest.pending(), random or scripted) detaches the zone instead of freeing
## it, with its zone shader globals and its outside links (zone_links); the change back to that zone re-attaches the
## same instance (no load, no instantiate, no _ready), restores its links, calls RESIDENT_RETURN_METHOD through it (its
## story arrives again: a scripted win's scene plays; its flag states are applied) and puts the party on its spawn.
## A fight that returns elsewhere builds that scene off the tree while it runs (ReturnPark, park_return). Any other
## change, or a loaded game, frees the kept zone.
var keep_field_resident := true
## Build a fight's cross-zone return scene while the fight runs (ReturnPark; PC pass 7 row 74).
var park_return := true
var return_park: ReturnPark
var _resident: Node = null
var _resident_path := ""
var _resident_globals := {}
var _resident_links := {}

var _fade_layer: CanvasLayer
var _fade_rect: ColorRect
var _busy := false
var _font_warmer: FontWarmer
var _fonts_warm := false
## instance id -> WeakRef of each object holding the swap (hold_swap).
var _swap_holds: Dictionary = {}
## instance id -> WeakRef of each object holding the reveal (hold_reveal, M2-ARC-03).
var _reveal_holds: Dictionary = {}
## Bumped by every change_scene(): a visible window from an older change stops at its next frame.
var _visible_generation := 0
var _measuring_visible := false
## Frame clocks of the reveal wait and the hidden swap frames. Owned by the router, not coroutine locals: a quit
## that lands mid-await leaves the coroutine suspended, and a FrameClock it held stayed in use past Godot's exit
## check ("1 resources still in use at exit", boot smoke; M2-ARC-05 fix).
var _reveal_clock := FrameClock.new()
var _swap_clock := FrameClock.new()
## M2-MNU-06: the time source every window measures with (entry, prewarm, unload, instantiate, the swap frames,
## the reveal wait and the visible window); invalid (the default) reads Time.get_ticks_usec(). The scene-swap
## probe sets a fake per-frame clock (set_measure_clock) so its test judges the real swap deterministically.
## The font warmer's per-frame work slice is not a measurement and stays on the real clock.
var _measure_now := Callable()
## The reveal hold's stall and cap (M2-ARC-08); a member for the same reason as the clocks.
var _reveal_wait: ProgressWait


func _ready() -> void:
	_fade_layer = CanvasLayer.new()
	_fade_layer.layer = FADE_LAYER
	add_child(_fade_layer)
	_fade_rect = ColorRect.new()
	_fade_rect.color = Color(0, 0, 0, 0)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade_layer.add_child(_fade_rect)
	ShaderPrewarm.install(self)
	ShaderGlobals.install(self)
	WeatherClock.install(self)
	ResidentLoads.install(self)
	world_return = WorldReturn.new()
	world_return.name = "WorldReturn"
	add_child(world_return)
	return_park = ReturnPark.new(get_tree())
	EventBus.game_loaded.connect(func(_slot: int) -> void: drop_resident())  # a loaded game reloads its zone


## The opaque fade's alpha now (0 clear, 1 covering the screen).
func fade_alpha() -> float:
	return _fade_rect.color.a


func is_busy() -> bool:
	return _busy


## True while the last change's visible window (M1-ARC-16) is still being measured.
func is_measuring() -> bool:
	return _measuring_visible


## Holds the next swap under the opaque fade until release_swap(holder), until `holder` is freed, or
## for at most PREWARM_WAIT_MAX_FRAMES frames. Holding twice with the same object is one hold.
func hold_swap(holder: Object) -> void:
	if holder != null:
		_swap_holds[holder.get_instance_id()] = weakref(holder)


func release_swap(holder: Object) -> void:
	if holder != null:
		_swap_holds.erase(holder.get_instance_id())


## The live objects holding the swap (freed holders are dropped here).
func swap_holders() -> Array[Object]:
	return _live_holders(_swap_holds)


## M2-ARC-03: keeps the running (or next) change's fade opaque after its swap until release_reveal(holder),
## until `holder` is freed, or until the hold stalls or hits its cap (M2-ARC-08). Holding twice with the same
## object is one hold.
func hold_reveal(holder: Object) -> void:
	if holder != null:
		_reveal_holds[holder.get_instance_id()] = weakref(holder)


func release_reveal(holder: Object) -> void:
	if holder != null:
		_reveal_holds.erase(holder.get_instance_id())


## The live objects holding the reveal (freed holders are dropped here).
func reveal_holders() -> Array[Object]:
	return _live_holders(_reveal_holds)


static func _live_holders(holds: Dictionary) -> Array[Object]:
	var out: Array[Object] = []
	for id: Variant in holds.keys():
		var o: Variant = (holds[id] as WeakRef).get_ref()
		if o == null:
			holds.erase(id)
		else:
			out.append(o as Object)
	return out


## `spawn` (optional): a marker under the new scene's Spawns node to place the player on
## (WorldReturn.place_player) before the fade lifts.
func change_scene(scene_path: String, spawn: StringName = &"") -> void:
	if _busy:
		push_warning("SceneRouter: change already in progress, ignoring %s" % scene_path)
		return
	_busy = true
	cancel_visible_window()
	var entry_start := _now_usec()
	var stats := {"scene_path": scene_path, "budget_ms": HIDDEN_FRAME_BUDGET_MS}
	var keep := keeps_resident(scene_path)
	var fight := BattleRequest.pending() if keep else null  # the battle takes it once in
	var back := _resident != null and is_instance_valid(_resident) and scene_path == _resident_path
	stats["resident"] = back
	stats["parked"] = return_park.holds(scene_path)
	if not return_park.holds(scene_path) and not RESIDENT_THROUGH.has(scene_path):
		return_park.drop()  # gone somewhere else: the scene built for the fight's return isn't wanted
	if not back and not return_park.holds(scene_path):
		ResourceLoader.load_threaded_request(scene_path)
	change_started.emit(scene_path)
	_start_font_warm(stats)
	await _fade_to(1.0)
	if keep:
		_detach_resident()
		_prewarm_return()
	var parked: Node = null
	if not back:
		parked = await return_park.take(scene_path)
	if back:
		await _swap_resident(scene_path, stats, spawn, entry_start)
		await _wait_for_reveal(stats)
	elif parked != null:
		await _swap(null, scene_path, stats, spawn, entry_start, parked)
		await _wait_for_reveal(stats)
	else:
		while ResourceLoader.load_threaded_get_status(scene_path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
			await get_tree().process_frame
		var packed := ResourceLoader.load_threaded_get(scene_path) as PackedScene
		if packed == null:
			push_error("SceneRouter: failed to load %s" % scene_path)
		else:
			await _swap(packed, scene_path, stats, spawn, entry_start)
			await _wait_for_reveal(stats)
	if not keep and not back:
		drop_resident()  # gone anywhere else: the field kept for the fight isn't coming back
	if stats.has("frame_ms"):
		_measure_visible(stats, _fade_lifted)
	await _fade_to(0.0)
	_busy = false
	if keep and park_return:
		_park_return(fight)


## True when the change to `scene_path` keeps the current field zone resident (see keep_field_resident).
func keeps_resident(scene_path: String) -> bool:
	if not keep_field_resident or not RESIDENT_THROUGH.has(scene_path) or not is_inside_tree():
		return false
	var cur := get_tree().current_scene
	if cur == null or cur.scene_file_path == "" or cur.find_children("*", "FieldController", true, false).is_empty():
		return false
	return BattleRequest.pending() != null  # a fight: random or scripted (its return re-runs the zone's arrival)


## The resident field zone (null when none is kept) and its scene path.
func resident() -> Node:
	return _resident if _resident != null and is_instance_valid(_resident) else null


func resident_path() -> String:
	return _resident_path


## Frees the resident field zone, if one is kept.
func drop_resident() -> void:
	if not is_busy():
		return_park.drop()  # a loaded game (not the return that just took it, nor one mid-change)
	if _resident != null and is_instance_valid(_resident):
		_resident.queue_free()
	_resident = null
	_resident_path = ""
	_resident_globals = {}
	_resident_links = {}


## What `zone` wires up outside itself and drops when it leaves the tree: its nodes' EventBus connections and its
## shrines in the ShrineNetwork. Many nodes let these go in _exit_tree and take them in _ready, which a resident zone
## re-attached never re-runs (every ZoneStory's interactions and triggers went dead after a fight).
static func zone_links(zone: Node) -> Dictionary:
	var conns: Array = []
	for s: Dictionary in EventBus.get_signal_list():
		for c: Dictionary in EventBus.get_signal_connection_list(str(s["name"])):
			var target: Variant = (c["callable"] as Callable).get_object()
			if target is Node and (target == zone or zone.is_ancestor_of(target as Node)):
				conns.append([StringName(str(s["name"])), c["callable"], int(c.get("flags", 0))])
	var shrines: Array = []
	for shrine: Variant in ShrineNetwork.loaded_shrines().values():
		if shrine is Node and is_instance_valid(shrine) and zone.is_ancestor_of(shrine as Node):
			shrines.append(shrine)
	return {"connections": conns, "shrines": shrines}


## Puts back what zone_links() saw and the zone's _exit_tree let go (after it is in the tree again).
static func restore_links(links: Dictionary) -> void:
	for c: Array in links.get("connections", []):
		var callable := c[1] as Callable
		if callable.is_valid() and not EventBus.is_connected(c[0] as StringName, callable):
			EventBus.connect(c[0] as StringName, callable, int(c[2]))
	for shrine: Variant in links.get("shrines", []):
		if is_instance_valid(shrine):
			ShrineNetwork.register(shrine as SaveShrine)


## A fight that returns somewhere other than the field kept for it (BattleRequest.return_scene, or another
## location): that scene starts loading on a worker thread now, so the way back after the victory panel finds it
## in. Its change drops the kept field as usual.
func _prewarm_return() -> void:
	var dest := _return_scene(BattleRequest.pending())
	if dest != "" and dest != _resident_path and ResourceLoader.exists(dest):
		ResourceLoader.load_threaded_request(dest)


## The fight `r`'s return scene ("" when none resolves).
func _return_scene(r: BattleRequest) -> String:
	if r == null:
		return ""
	var dest := r.return_scene
	if dest == "" and r.return_location != &"" and world_return != null and world_return.registry != null:
		dest = world_return.registry.scene_of(r.return_location)
	return dest


## The fight is in: a return elsewhere than the resident field is built off the tree while it runs (ReturnPark).
func _park_return(fight: BattleRequest) -> void:
	var dest := _return_scene(fight)
	if dest == "" or dest == _resident_path:
		return
	var loads := ResidentLoads.shared()
	if DisplayServer.get_name() == "headless" and not ResidentLoads.run_headless:
		loads = null  # as the victory panel's prepare_return: no zone loads in a headless run
	return_park.start(dest, loads, fight, _resident_path)


## Takes the current scene out of the tree, kept (not freed), with its zone shader globals.
func _detach_resident() -> void:
	drop_resident()
	var cur := get_tree().current_scene
	if cur == null:
		return
	_resident_globals = ShaderGlobals.zone_snapshot()
	_resident_links = zone_links(cur)
	_resident_path = cur.scene_file_path
	cur.get_parent().remove_child(cur)
	get_tree().current_scene = null
	_resident = cur


## The swap back to the resident field zone: the same instance re-enters the tree (no load, no instantiate, no
## _ready), its zone globals are given back after the swap's reset, and the party is put on `spawn`.
func _swap_resident(scene_path: String, stats: Dictionary, spawn: StringName, entry_start_usec: int) -> void:
	var node := _resident
	var globals := _resident_globals
	var links := _resident_links
	_resident = null
	_resident_path = ""
	_resident_globals = {}
	_resident_links = {}
	stats["instantiate_ms"] = 0.0
	var frames: Array[float] = []
	_swap_clock.reset_at(_now_usec())
	scene_swapping.emit(scene_path)
	ShaderGlobals.restore_zone(globals)
	var cover: Array[float] = [fade_alpha()]
	get_tree().change_scene_to_node(node)
	var arrived := false
	var i := 0
	while i < MEASURE_FRAMES or not arrived:
		await get_tree().process_frame
		if i < MEASURE_FRAMES:
			frames.append(_swap_clock.lap())
			cover.append(fade_alpha())
		i += 1
		# The battle scene is replaced at the end of a frame, so the zone may not be in yet on the first one: its
		# links, its arrival and the spawn wait for it (they did not, and a scripted win's arrival never ran).
		if not arrived and (node.is_inside_tree() or i > RESIDENT_ENTER_MAX_FRAMES):
			arrived = true
			restore_links(links)  # before the spawn and scene_changed: the zone's story hears what follows
			node.propagate_call(RESIDENT_RETURN_METHOD)  # the zone arrives again (its story, its flag states)
			if spawn != &"" and node.is_inside_tree():
				WorldReturn.place_player(node, spawn)
			EventBus.scene_changed.emit(scene_path)
	if entry_start_usec >= 0:
		judge_entry(stats, _ms_since(entry_start_usec))
	for w in judge_cover(stats, cover):
		push_warning("%s: %s: %s" % [LOG_PREFIX, w, scene_path])
	_record(stats, frames)


## M2-ARC-03: keeps the fade opaque while anything holds the reveal (boot's warm-up), recording the wait.
func _wait_for_reveal(stats: Dictionary) -> void:
	var start := _now_usec()
	_reveal_clock.reset_at(start)
	_reveal_wait = ProgressWait.from_settings()
	var frames := 0
	var worst := 0.0
	var end := ProgressWait.Verdict.WAITING
	while not reveal_holders().is_empty() and end == ProgressWait.Verdict.WAITING:
		await get_tree().process_frame
		var frame_ms := _reveal_clock.lap()
		worst = maxf(worst, frame_ms)
		frames += 1
		end = _reveal_wait.step(frame_ms, holders_progress(reveal_holders()))
	stats["reveal_wait_end"] = "done" if reveal_holders().is_empty() else ProgressWait.verdict_name(end)
	if not reveal_holders().is_empty():
		push_warning(
			(
				"%s: lifting after %.0f ms with the reveal still held (%s)"
				% [LOG_PREFIX, _ms_since(start), stats["reveal_wait_end"]]
			)
		)
	for w in judge_reveal_wait(stats, frames, _ms_since(start), worst):
		push_warning("%s: %s: %s" % [LOG_PREFIX, w, stats.get("scene_path", "")])


## ADR 0111: the summed swap_wait_progress() of the swap `holders` that report loading work (ResidentLoads), or -1
## when none does. Only such a holder keeps a swap waiting past PREWARM_WAIT_MAX_FRAMES; ShaderPrewarm's
## wait_progress() counts frames (the reveal's stall check), not work, so it never extends the swap.
static func swap_progress(holders: Array[Object]) -> int:
	var total := -1
	for h in holders:
		if h != null and h.has_method(&"swap_wait_progress"):
			var p := int(h.call(&"swap_wait_progress"))
			if p >= 0:  # -1: not loading now (ShaderPrewarm outside a zone feed)
				total = maxi(total, 0) + p
	return total


## M2-ARC-08: the summed wait_progress() of `holders` that report one (a BootCard; others count 0).
static func holders_progress(holders: Array[Object]) -> int:
	var total := 0
	for h in holders:
		if h != null and h.has_method(&"wait_progress"):
			total += int(h.call(&"wait_progress"))
	return total


## The reveal wait's stats (hidden frames, ADR 0029): writes reveal_wait_frames, reveal_wait_ms and
## reveal_wait_max_frame_ms into `stats` and returns the warnings to raise (a frame over 1 s).
static func judge_reveal_wait(stats: Dictionary, frames: int, wait_ms: float, worst_ms: float) -> Array[String]:
	stats["reveal_wait_frames"] = frames
	stats["reveal_wait_ms"] = wait_ms
	stats["reveal_wait_max_frame_ms"] = worst_ms
	var out: Array[String] = []
	if worst_ms > HIDDEN_FRAME_BUDGET_MS:
		out.append(
			(
				"hidden reveal-wait frame %.1f ms over the %.0f ms hidden-frame budget (ADR 0029)"
				% [worst_ms, HIDDEN_FRAME_BUDGET_MS]
			)
		)
	return out


## M2-ARC-03: ADR 0029's visible window for a reveal the router does not run (the BootCard lifting off the
## title at launch). Call it on the frame the reveal starts; `lifted` returns true once nothing covers the
## screen (a freed object's Callable counts as lifted). `extra` (e.g. the card's wait stats) is copied into
## the stats. A change_scene() cuts it short, as it does a change's window. Returns the stats dictionary,
## which is also last_swap_stats, completed when visible_measured fires.
func measure_reveal(scene_path: String, lifted: Callable, extra: Dictionary = {}) -> Dictionary:
	cancel_visible_window()
	var stats := extra.duplicate()
	stats["scene_path"] = scene_path
	stats["reveal"] = true
	last_swap_stats = stats
	_measure_visible(stats, lifted)
	return stats


## With split_swap off this reproduces the M0 router (prewarm, instantiate, free and add in one
## frame), which the profiler uses as the "before" case.
## `prebuilt`: the scene's root already instantiated (ReturnPark), in place of instantiating `packed`.
func _swap(
	packed: PackedScene,
	scene_path: String,
	stats: Dictionary,
	spawn: StringName = &"",
	entry_start_usec: int = -1,
	prebuilt: Node = null
) -> void:
	while _font_warmer != null and not _font_warmer.done:
		await get_tree().process_frame
	var t := _now_usec()
	var swap_frame_start := t
	prewarm_requested.emit(scene_path)
	stats["prewarm_ms"] = _ms_since(t)
	if split_swap:
		await get_tree().process_frame
	# PC pass 4 row 67 (big19: one fresh Brine Shoals entry never finished): the holders (ResidentLoads' threaded
	# loads, the prewarm) are waited on before the zone is instantiated, so the zone's own load() calls on the worker
	# thread find every resource already in, and never wait on a threaded load of the same file in flight.
	var waited := 0
	var wait_start := _now_usec()
	var last_move := wait_start
	var progress := swap_progress(swap_holders())
	while not swap_holders().is_empty():
		var now := swap_progress(swap_holders())
		var clock := _now_usec()
		if now != progress:
			progress = now
			last_move = clock
		var stalled_ms := (clock - last_move) / USEC_PER_MSEC if now >= 0 else INF  # no loader: the frame cap only
		if not swap_wait_continues(waited, stalled_ms, (clock - wait_start) / USEC_PER_MSEC):
			break
		await get_tree().process_frame
		waited += 1
	stats["prewarm_wait_frames"] = waited
	var node: Node = prebuilt if prebuilt != null else await _instantiate(packed, stats)
	if prebuilt != null:
		stats["instantiate_ms"] = 0.0
	if node == null:
		push_error("SceneRouter: failed to instantiate %s" % scene_path)
		return
	scene_instantiated.emit(node)
	if split_swap:
		if get_tree().current_scene != null:
			t = _now_usec()
			get_tree().unload_current_scene()
			await get_tree().process_frame
			stats["unload_ms"] = _ms_since(t)
		await get_tree().process_frame
		swap_frame_start = _now_usec()
	else:
		swap_frame_start = frame0_start(swap_frame_start, waited, _now_usec())
	var frames: Array[float] = []
	_swap_clock.reset_at(swap_frame_start)
	# Zone render globals (M1-RND-15) reset on this signal: the new zone starts from the project
	# defaults, so one that never writes them does not inherit the last zone's sea-glow or tide line.
	scene_swapping.emit(scene_path)
	var cover: Array[float] = [fade_alpha()]
	attach_graphics_hook(node, stats)
	get_tree().change_scene_to_node(node)
	for i in MEASURE_FRAMES:
		await get_tree().process_frame
		frames.append(_swap_clock.lap())
		cover.append(fade_alpha())
		if i == 0:
			if spawn != &"" and node.is_inside_tree():
				WorldReturn.place_player(node, spawn)
			EventBus.scene_changed.emit(scene_path)
	if entry_start_usec >= 0:
		judge_entry(stats, _ms_since(entry_start_usec))
	for w in judge_cover(stats, cover):
		push_warning("%s: %s: %s" % [LOG_PREFIX, w, scene_path])
	_record(stats, frames)


## Whether a swap held by its holders (hold_swap) waits another frame: always up to PREWARM_WAIT_MAX_FRAMES;
## past that only while a loading holder still makes progress (its swap_wait_progress() moved within the last
## SWAP_STALL_MS of wall time; ADR 0111: a zone's threaded loads, ResidentLoads, where one model can take a second
## and more), and never past SWAP_WAIT_CAP_MS in all. Wall time, not frames: frames under the fade are uncapped.
static func swap_wait_continues(waited: int, stalled_ms: float, waited_ms: float) -> bool:
	if waited < PREWARM_WAIT_MAX_FRAMES:
		return true
	return waited_ms < SWAP_WAIT_CAP_MS and stalled_ms < SWAP_STALL_MS


## Without split_swap, where the first measured frame starts: at the swap's start, unless frames were
## waited for the prewarm. Those were rendered (and are counted in prewarm_wait_frames), so frame 0
## starts after them, not before (review-sweep-J S1, M1-RND-22).
static func frame0_start(swap_start_usec: int, waited_frames: int, now_usec: int) -> int:
	return now_usec if waited_frames > 0 else swap_start_usec


## M1-ARC-15: applies the graphics settings' per-scene part to `node` when its root is ready, i.e. in
## the tree, on the main thread, after every child's _ready (HalunaZone has finished its worker-thread
## prebuild by then) and before the first frame draws it. No-op until boot arms GraphicsRuntime.
## Records the operation count in stats["graphics_ops"].
func attach_graphics_hook(node: Node, stats: Dictionary) -> void:
	node.ready.connect(func() -> void: stats["graphics_ops"] = GraphicsRuntime.on_scene_entered(node), CONNECT_ONE_SHOT)


## Instantiates off the main thread when allowed; falls back to the main thread otherwise.
func _instantiate(packed: PackedScene, stats: Dictionary) -> Node:
	var t := _now_usec()
	var holder: Array[Node] = []
	stats["instantiated_on_thread"] = instantiate_on_thread
	if instantiate_on_thread:
		ShaderGlobals.hold_writes()  # M3-HER-1151: no global write while the thread creates the zone's materials
		var task := WorkerThreadPool.add_task(func() -> void: holder.append(built_scene(packed)))
		while not WorkerThreadPool.is_task_completed(task):
			await get_tree().process_frame
		WorkerThreadPool.wait_for_task_completion(task)
		ShaderGlobals.release_writes()
	else:
		holder.append(packed.instantiate())
	stats["instantiate_ms"] = _ms_since(t)
	return holder[0] if not holder.is_empty() else null


## On the worker thread: the scene instantiated, with its big meshes' occlusion triangles built (row 74: Haluna's
## dresser meshes cost 0.5 s on the add frame otherwise; FieldCameraDirector.warm_triangles).
static func built_scene(packed: PackedScene) -> Node:
	var node := packed.instantiate()
	FieldCameraDirector.warm_triangles(node)
	return node


func _record(stats: Dictionary, frames: Array[float]) -> void:
	stats["fonts_warmed"] = _fonts_warm
	last_swap_stats = stats
	for w in judge_hidden(stats, frames):
		push_warning("%s: %s: %s" % [LOG_PREFIX, w, stats])
	if bool(stats.get("entry_over_budget", false)):
		push_warning(
			(
				"%s: zone entry %.0f ms over the %.0f ms entry budget (ADR 0029): %s"
				% [LOG_PREFIX, float(stats["entry_ms"]), ENTRY_BUDGET_MS, stats]
			)
		)
	swap_measured.emit(stats)


## ADR 0029's hidden window: writes frame_ms, max_frame_ms, budget_ms and over_budget (against
## HIDDEN_FRAME_BUDGET_MS) into `stats` and returns the warnings to raise (empty when in budget).
static func judge_hidden(stats: Dictionary, frames: Array[float]) -> Array[String]:
	var worst := _max_of(frames)
	stats["frame_ms"] = frames
	stats["max_frame_ms"] = worst
	stats["budget_ms"] = HIDDEN_FRAME_BUDGET_MS
	stats["over_budget"] = worst > HIDDEN_FRAME_BUDGET_MS
	var out: Array[String] = []
	if worst > HIDDEN_FRAME_BUDGET_MS:
		out.append(
			(
				"hidden swap frame %.1f ms over the %.0f ms hidden-frame budget (ADR 0029)"
				% [worst, HIDDEN_FRAME_BUDGET_MS]
			)
		)
	return out


## ADR 0042 §4: the fade's alpha at the swap and at each hidden frame after it (`cover`). Writes cover_alpha_min and
## covered (every one fully opaque) into `stats` and returns the warnings to raise (empty when covered).
static func judge_cover(stats: Dictionary, cover: Array[float]) -> Array[String]:
	var low := 1.0
	for a in cover:
		low = minf(low, a)
	stats["cover_alpha_min"] = low
	stats["covered"] = not cover.is_empty() and low >= 1.0
	if bool(stats["covered"]):
		return []
	return ["a hidden swap frame was not under the opaque fade (alpha %.2f; ADR 0042 §4)" % low]


## ADR 0029's entry limit: writes entry_ms, entry_budget_ms and entry_over_budget into `stats`.
static func judge_entry(stats: Dictionary, entry_ms: float) -> void:
	stats["entry_ms"] = entry_ms
	stats["entry_budget_ms"] = ENTRY_BUDGET_MS
	stats["entry_over_budget"] = entry_ms > ENTRY_BUDGET_MS


## ADR 0029's visible window: writes the visible_* keys from `window` into `stats` and returns the warnings
## to raise (empty when in budget).
static func judge_visible(stats: Dictionary, window: VisibleWindow) -> Array[String]:
	var worst := _max_of(window.frame_ms)
	stats["visible_frame_ms"] = window.frame_ms
	stats["lift_frames"] = window.lift_frames
	stats["max_visible_frame_ms"] = worst
	stats["visible_budget_ms"] = SWAP_BUDGET_MS
	stats["visible_over_budget"] = worst > SWAP_BUDGET_MS
	stats["visible_complete"] = window.is_complete()
	var out: Array[String] = []
	if worst > SWAP_BUDGET_MS:
		var at := window.frame_ms.find(worst)
		out.append("visible frame %d of the lift: %.1f ms over the %.0f ms budget" % [at, worst, SWAP_BUDGET_MS])
	return out


## Ends the visible window being measured, if any (it is judged on its frames at its next frame, and
## visible_measured fires with visible_complete false). change_scene() and measure_reveal() call it.
func cancel_visible_window() -> void:
	_visible_generation += 1
	_measuring_visible = false


## Samples one frame time per process frame from the moment the fade starts to lift until
## VISIBLE_MEASURE_FRAMES frames after it has lifted (`lifted` true at the frame's end), or until another
## change_scene() (or measure_reveal()) starts.
func _measure_visible(stats: Dictionary, lifted: Callable) -> void:
	var generation := _visible_generation
	_measuring_visible = true
	var window := VisibleWindow.new(_now_usec())
	while generation == _visible_generation:
		await get_tree().process_frame
		if generation != _visible_generation:
			break
		if window.tick(_now_usec(), not lifted.is_valid() or bool(lifted.call())):
			break
	for w in judge_visible(stats, window):
		push_warning("%s: %s: %s" % [LOG_PREFIX, w, stats.get("scene_path", "")])
	if generation == _visible_generation:
		_measuring_visible = false
	visible_measured.emit(stats)


func _fade_lifted() -> bool:
	return _fade_rect.color.a <= 0.0


static func _max_of(frames: Array[float]) -> float:
	var worst := 0.0
	for f in frames:
		worst = maxf(worst, f)
	return worst


## M2-ARC-03: starts the theme font warm-up now, outside a change (boot runs it under its card). Once per
## run, like a change's; a no-op when it already ran or is running, or warm_fonts is off.
func warm_fonts_now() -> void:
	_start_font_warm({})


## True once the theme fonts are warm, or when warm_fonts is off (nothing will warm them).
func fonts_ready() -> bool:
	return _fonts_warm or not warm_fonts


## M2-ARC-08: the font warm-up's units drawn so far (it moves while the warm-up runs), for BootCard.wait_until.
func font_warm_progress() -> int:
	return _font_warmer.progress() if _font_warmer != null else 0


## Starts rasterizing the project theme's fonts under the fade (once per run; spread over frames).
func _start_font_warm(stats: Dictionary) -> void:
	if not warm_fonts or _fonts_warm or _font_warmer != null:
		return
	_font_warmer = FontWarmer.new()
	_font_warmer.pairs = FontWarmer.theme_pairs(ThemeDB.get_project_theme())
	_font_warmer.finished.connect(_on_fonts_warm.bind(stats))
	_fade_layer.add_child(_font_warmer)
	_fade_layer.move_child(_font_warmer, 0)


func _on_fonts_warm(total_ms: float, stats: Dictionary) -> void:
	stats["font_warm_ms"] = total_ms
	_fonts_warm = true
	_font_warmer.queue_free()
	_font_warmer = null


func _fade_to(alpha: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", alpha, FADE_SEC)
	await tween.finished


func _ms_since(t_usec: int) -> float:
	return FrameClock.ms_between(t_usec, _now_usec())


## M2-MNU-06: measures every window with `now_usec` (a Callable returning microseconds) from the next change on;
## an invalid Callable goes back to the wall clock. Tests and the scene-swap probe only.
func set_measure_clock(now_usec: Callable) -> void:
	_measure_now = now_usec
	_reveal_clock = FrameClock.new(now_usec)
	_swap_clock = FrameClock.new(now_usec)


func _now_usec() -> int:
	return int(_measure_now.call()) if _measure_now.is_valid() else Time.get_ticks_usec()


## M1-ARC-16: ADR 0029's visible window, fed one timestamp per frame (an injected clock, so tests can drive
## it). Frames that end before the fade has fully lifted count as lift_frames; the window is complete after
## VISIBLE_MEASURE_FRAMES frames that end with the fade lifted.
class VisibleWindow:
	extends RefCounted

	var frame_ms: Array[float] = []
	var lift_frames := 0
	var lifted_frames := 0
	## A plain usec mark, not a FrameClock: a window lives in a coroutine that a quit can leave suspended,
	## and a script object it holds would outlive Godot's exit check (boot smoke, M2-ARC-05 fix).
	var _last_usec := 0

	func _init(start_usec: int) -> void:
		_last_usec = start_usec

	## Records the frame that ended at `now_usec`; `lifted`: the fade was fully lifted when it ended.
	## Returns true once the window is complete.
	func tick(now_usec: int, lifted: bool) -> bool:
		frame_ms.append(FrameClock.ms_between(_last_usec, now_usec))
		_last_usec = now_usec
		if lifted:
			lifted_frames += 1
		else:
			lift_frames += 1
		return is_complete()

	func is_complete() -> bool:
		return lifted_frames >= VISIBLE_MEASURE_FRAMES


## Draws every (font, size, outline) the project theme uses with a fixed character set, in small
## units (one CHUNK_CHARS slice of one pair) until FRAME_BUDGET_USEC is spent each frame, so the
## TextServer glyph cache is filled before a scene needs it. It sits under the fade rect with zero
## alpha, so nothing it draws is ever seen. MSDF fonts are skipped: msdfgen costs ~7 ms per glyph on
## this CPU, far too slow to warm inside a transition (see architecture.md, "Scene-swap hitch").
class FontWarmer:
	extends Control

	signal finished(total_ms: float)

	## Printable ASCII plus the typographic marks the loc tables use.
	const CHARSET := (
		" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
		+ "\u2026\u2014\u2013\u2018\u2019\u201C\u201D\u00B7\u00D7\u00E9"
	)
	const CHUNK_CHARS := 16
	const FRAME_BUDGET_USEC := 4000
	const OUTLINE_CONSTANT := "outline_size"

	var pairs: Array[Dictionary] = []
	var done := false
	var _units: Array[Dictionary] = []
	var _next := 0
	var _spent_usec := 0

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		self_modulate = Color(1, 1, 1, 0)
		_units = units_for(pairs)
		if _units.is_empty():
			_finish.call_deferred()

	func _process(_delta: float) -> void:
		if not done:
			queue_redraw()

	## Units drawn so far (M2-ARC-08: the boot card's progress count).
	func progress() -> int:
		return _next

	func _draw() -> void:
		var start := Time.get_ticks_usec()
		while _next < _units.size() and Time.get_ticks_usec() - start < FRAME_BUDGET_USEC:
			var u := _units[_next]
			var font := u["font"] as Font
			var size := int(u["size"])
			var text := String(u["text"])
			var at := Vector2(0, size)
			draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size)
			if int(u["outline"]) > 0:
				draw_string_outline(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, int(u["outline"]))
			_next += 1
		_spent_usec += Time.get_ticks_usec() - start
		if _next >= _units.size() and not done:
			_finish.call_deferred()

	func _finish() -> void:
		if done:
			return
		done = true
		finished.emit(_spent_usec / USEC_PER_MSEC)

	## Splits each pair into CHARSET slices so no single unit can blow the frame budget.
	static func units_for(warm_pairs: Array[Dictionary]) -> Array[Dictionary]:
		var out: Array[Dictionary] = []
		for p in warm_pairs:
			for i in range(0, CHARSET.length(), CHUNK_CHARS):
				var u := p.duplicate()
				u["text"] = CHARSET.substr(i, CHUNK_CHARS)
				out.append(u)
		return out

	## Every distinct non-MSDF (font, size, outline) a theme can produce: each type's fonts paired
	## with that type's sizes and outline constant, plus the theme defaults. The engine fallback font
	## is included only when the theme has no default font (themed Controls never reach it).
	static func theme_pairs(theme: Theme) -> Array[Dictionary]:
		var out: Array[Dictionary] = []
		var seen: Dictionary = {}
		if theme == null or not theme.has_default_font():
			_add(out, seen, ThemeDB.fallback_font, ThemeDB.fallback_font_size, 0)
		if theme == null:
			return out
		var default_font: Font = theme.default_font if theme.has_default_font() else ThemeDB.fallback_font
		var default_size := theme.default_font_size if theme.has_default_font_size() else ThemeDB.fallback_font_size
		_add(out, seen, default_font, default_size, 0)
		for type in theme.get_type_list():
			var fonts: Array[Font] = []
			for fname in theme.get_font_list(type):
				fonts.append(theme.get_font(fname, type))
			if fonts.is_empty():
				fonts.append(default_font)
			var sizes: Array[int] = []
			for sname in theme.get_font_size_list(type):
				sizes.append(theme.get_font_size(sname, type))
			if sizes.is_empty():
				sizes.append(default_size)
			var outline := (
				theme.get_constant(OUTLINE_CONSTANT, type) if theme.has_constant(OUTLINE_CONSTANT, type) else 0
			)
			for f in fonts:
				for sz in sizes:
					_add(out, seen, f, sz, outline)
		return out

	## True for a font whose glyphs are multichannel signed distance fields (directly or via a
	## FontVariation chain).
	static func is_msdf(font: Font) -> bool:
		var f := font
		while f is FontVariation:
			f = (f as FontVariation).base_font
		return f is FontFile and (f as FontFile).multichannel_signed_distance_field

	static func _add(out: Array[Dictionary], seen: Dictionary, font: Font, size: int, outline: int) -> void:
		if font == null or size <= 0 or is_msdf(font):
			return
		var key := "%d:%d:%d" % [font.get_instance_id(), size, outline]
		if seen.has(key):
			return
		seen[key] = true
		out.append({"font": font, "size": size, "outline": outline})
