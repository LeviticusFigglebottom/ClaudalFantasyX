class_name PlaythroughProbe
extends Node
## A fresh-profile Act I smoke playthrough, headless (cloud QA, the Lead's ask 2026-10-30): New Game through Ch1 to the
## Haluna arrival, logging any soft-lock, stuck dialogue or missing transition.
##   XDG_DATA_HOME=<empty dir> godot --headless --path . --audio-driver Dummy \
##     res://tools/gpu_bench/playthrough_probe.tscn -- [--until=ch02/haluna --secs=3600]
## It plays as a guided player: the title's New Game; ui_accept tapped every TAP_S whenever the field isn't taking
## input (dialogue, cutscenes, cards); in the field, the hero hops HOP_M a physics frame toward the objective line's
## target (ObjectiveHud.target_position: the game's own "where next") and, near it, interacts. Fights are won live
## (foes held at 1 HP, Attack each party turn, Return on the result). Not a navigation test: hops pass through walls.
## Lines: PLAY_SCENE (each scene change), PLAY_FLAG (each flag raised), PLAY_STUCK_DIALOGUE (the field not taking input
## for STUCK_S with no flag or scene change), PLAY_SOFTLOCK (no flag or scene change for SOFTLOCK_S while the field
## takes input), PLAY_TELEPORT (hops held back by the zone's guards: the hero jumps beside the target),
## PLAY_SWEEP (at the target with no progress: it steps onto each trigger near it),
## PLAY_SKIP (a soft-lock on a puzzle: the objective's until flag raised so the smoke goes on; the step is unplayed),
## PLAY_HOLD (a hold prompt showed: its action is held until the prompt goes), PLAY_SKIP_SCENE (stuck in a cutscene
## for STUCK_S: ui_cancel is held, the sequencer's skip),
## PLAY_FELL (the hero fell out of the world after a hop: put back on the ground; no fall recovery in the game),
## PLAY_NO_TARGET (the field takes input but the objective names no target), PLAY_ARRIVED / PLAY_TIMEOUT.

const BOOT := "res://game/core/boot.tscn"
const CHAPTER_SELECT := "res://game/data/debug/chapter_select.json"
const TAP_S := 1.5
const HOP_M := 0.25
const NEAR_M := 1.0
const INTERACT_S := 1.0
const STUCK_S := 90.0
const CANCEL_AFTER_S := 30.0
const SOFTLOCK_S := 180.0
const RESULT_READ_S := 1.0
const SETTLE_INPUT_S := 1.0
const STALL_S := 4.0
const STALL_GAIN_M := 0.5
const SWEEP_AFTER_S := 15.0
const SWEEP_DWELL_S := 2.0
const SWEEP_RADIUS_M := 20.0
## A teleport settles the hero's origin a hair under the deck (y -0.0004), under a touch box that starts exactly at
## deck height, so the sweep lands him this far above the trigger's floor and lets him drop into it.
const SWEEP_LIFT_M := 0.3
const STEP_OFF_M := 5.0
## A hero under this height has fallen out of the world (Ashcrown's stair foot is at -81 m, so a target-relative
## test misfires).
const OUT_OF_WORLD_Y := -500.0
## Jumps find the ground with a ray from this high above the spot.
const GROUND_RAY_M := 40.0
const TRIGGER_RAY_M := 2.0
const FLOOR_SEARCH_M := 4

var _opts: Dictionary = {}
var _skip_holding := false
var _t0 := 0
var _last_progress := 0.0
var _flags: Array[String] = []


func _ready() -> void:
	if get_parent() != get_tree().root or get_tree().current_scene == self:
		var driver := (get_script() as GDScript).new() as Node
		driver.name = "PlaythroughProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_opts[kv[0]] = kv[1] if kv.size() > 1 else "true"
	var until := str(_opts.get("until", "ch02/haluna"))
	var secs := float(_opts.get("secs", 3600))
	_t0 = Time.get_ticks_msec()
	EventBus.flag_changed.connect(_on_flag)
	get_tree().change_scene_to_file(BOOT)
	var menu: TitleMenu = null
	while menu == null and _now() < 300.0:
		await get_tree().process_frame
		var found := get_tree().root.find_children("*", "TitleMenu", true, false)
		if not found.is_empty():
			menu = found[0] as TitleMenu
	await get_tree().create_timer(2.0).timeout
	var chapter := str(_opts.get("chapter", ""))
	if chapter == "":
		print("PLAY_NEWGAME %s" % error_string(menu.start_new_game() if menu != null else ERR_UNAVAILABLE))
	else:
		# --chapter=chNN: start as the F8 chapter select does (the story so far, the party), from the title.
		for start: Dictionary in DebugReadouts.chapter_starts(CHAPTER_SELECT):
			if str(start["id"]) == chapter:
				DebugReadouts.apply_chapter_start(start)
				FlowRouting.go_to(StringName(str(start["location"])), StringName(str(start["spawn"])))
				print("PLAY_CHAPTER_START %s" % chapter)
	var router := get_tree().root.get_node(^"SceneRouter")
	var last_scene := ""
	var next_tap := 0.0
	var next_interact := 0.0
	var busy_since := -1.0
	var stuck_logged := false
	var softlock_logged := false
	var no_target_logged := ""
	var result_at := -1.0
	var best_dist := INF
	var best_at := 0.0
	var last_target := Vector3.INF
	var sweep: Array = []
	var hold_until := 0.0
	_last_progress = _now()
	while _now() < secs:
		await get_tree().physics_frame
		var t := _now()
		var cur := get_tree().current_scene
		var path := cur.scene_file_path if cur != null else "-"
		if path != last_scene:
			last_scene = path
			_progress("PLAY_SCENE %.1f %s" % [t, path])
			if path.contains(until) and _player(cur) == null:
				# A non-field goal (the Act I end card): reaching the scene is arriving.
				print("PLAY_ARRIVED %.1f %s (flags raised: %d)" % [t, path, _flags.size()])
				get_tree().quit()
				return
			stuck_logged = false
			softlock_logged = false
		if cur is FieldBattle:
			_skip_hold(false)
			result_at = await _battle_step(cur as FieldBattle, result_at, t)
			continue
		result_at = -1.0
		var p := _player(cur)
		var live := (
			p != null
			and p.accepts_input
			and not bool(router.call(&"is_busy"))
			and not get_tree().paused
			and not _story_busy(cur)
		)
		if not live:
			if busy_since < 0.0:
				busy_since = t
			# A hold prompt (Ch9: "Hold to raise the staff") wants its action held, not tapped.
			var held := _held_prompt_action()
			if held != &"":
				if not Input.is_action_pressed(held):
					print("PLAY_HOLD %.1f %s" % [t, held])
				Input.action_press(held)
				continue
			# Past STUCK_S, a cutscene is held to skip (ui_cancel held: the sequencer's skip), as a stuck player would.
			if t - _last_progress > STUCK_S and _skip_hold(true):
				print("PLAY_SKIP_SCENE %.1f %s: ui_cancel held to skip the cutscene" % [t, path])
			if t >= next_tap and not _skip_holding:
				# Past CANCEL_AFTER_S with no progress, every other tap is ui_cancel: a menu the hero opened closes.
				var cancel := t - _last_progress > CANCEL_AFTER_S and int(t / TAP_S) % 2 == 1
				_tap(&"ui_cancel" if cancel else &"ui_accept")
				next_tap = t + TAP_S
			if not stuck_logged and t - _last_progress > STUCK_S and p != null:
				stuck_logged = true
				print(
					(
						"PLAY_STUCK_DIALOGUE %.1f %s: %.0f s with the field not taking input and no progress"
						% [t, path, t - _last_progress]
					)
				)
			continue
		_skip_hold(false)
		if busy_since >= 0.0 and t - busy_since < SETTLE_INPUT_S:
			continue
		busy_since = -1.0
		if path.contains(until):
			print("PLAY_ARRIVED %.1f %s (flags raised: %d)" % [t, path, _flags.size()])
			get_tree().quit()
			return
		if t < hold_until:
			continue  # standing on a swept trigger
		var target := _target()
		if target != last_target:
			last_target = target
			sweep.clear()
			best_dist = INF
			best_at = t
		if target == Vector3.INF:
			if no_target_logged != path:
				no_target_logged = path
				print("PLAY_NO_TARGET %.1f %s: the field takes input and the objective names no target" % [t, path])
			if t >= next_tap:
				_tap(&"ui_accept")
				next_tap = t + TAP_S * 2.0
			# No objective (Ch6 and Ch8 have no rows): step onto the zone's available story triggers in turn, from the
			# nearest, as a player exploring would.
			if t - _last_progress > SWEEP_AFTER_S and t >= next_interact:
				if sweep.is_empty():
					sweep = _triggers_near(cur, p.global_position, INF)
					print(
						(
							"PLAY_SWEEP %.1f %s: no objective target; %d available triggers in the zone"
							% [t, path, sweep.size()]
						)
					)
				if not sweep.is_empty():
					var a: Node3D = _next_alive(sweep)
					if a == null:
						continue
					p.velocity = Vector3.ZERO
					await _step_onto(p, a)
					p.interact.call_deferred()
					next_interact = t + SWEEP_DWELL_S
					hold_until = t + SWEEP_DWELL_S
					print("PLAY_SWEEP_STEP %.1f %s" % [t, a.name])
		else:
			var to := Vector3(target.x - p.global_position.x, 0, target.z - p.global_position.z)
			if to.length() > NEAR_M:
				# Hops cross water or walls in a straight line; when the zone's guards (FieldShore, edge walls) hold
				# the hero back for STALL_S, jump beside the target instead (a probe limit, not a game soft-lock).
				if to.length() < best_dist - STALL_GAIN_M:
					best_dist = to.length()
					best_at = t
				elif t - best_at > STALL_S:
					print(
						(
							"PLAY_TELEPORT %.1f %s: hops held back at %s, jumped to %s"
							% [t, path, p.global_position, target]
						)
					)
					p.velocity = Vector3.ZERO
					p.global_position = _on_ground(
						p, Vector3(target.x, target.y, target.z) - to.normalized() * (NEAR_M * 0.5)
					)
					best_dist = INF
					best_at = t
					continue
				p.velocity = Vector3.ZERO
				if p.global_position.y < OUT_OF_WORLD_Y:
					# Fell out of the world (a hop or a jump under the ground): back on the ground near the target.
					print("PLAY_FELL %.1f %s: at %s, put back near %s" % [t, path, p.global_position, target])
					p.global_position = _on_ground(p, target - to.normalized() * NEAR_M)
					continue
				p.global_position += to.normalized() * minf(HOP_M, to.length())
			elif t >= next_interact:
				p.interact()
				_tap(&"ui_accept")
				next_interact = t + INTERACT_S
				# At the target and nothing happens: the beat may sit on a touch trigger on the way (Kell's is on her
				# bridge, not at her). Step onto each trigger near the target in turn, nearest first.
				if t - _last_progress > SWEEP_AFTER_S:
					if sweep.is_empty():
						sweep = _triggers_near(cur, target)
						print(
							(
								"PLAY_SWEEP %.1f %s: at the target with no progress; %d triggers near it"
								% [t, path, sweep.size()]
							)
						)
					if not sweep.is_empty():
						var a: Node3D = _next_alive(sweep)
						if a == null:
							continue
						p.velocity = Vector3.ZERO
						await _step_onto(p, a)
						p.interact.call_deferred()
						next_interact = t + SWEEP_DWELL_S
						hold_until = t + SWEEP_DWELL_S
						print("PLAY_SWEEP_STEP %.1f %s" % [t, a.name])
		if not softlock_logged and t - _last_progress > SOFTLOCK_S:
			softlock_logged = true
			# A puzzle the guided hops can't solve (the Shell Shrine's basins): raise the objective's own `until` flag so
			# the smoke goes on, and say so (PLAY_SKIP: that step was not played).
			var skip := _skip_objective()
			print(
				(
					'PLAY_SOFTLOCK %.1f %s: %.0f s with no flag or scene change; at %s, target %s, objective "%s"'
					% [t, path, t - _last_progress, p.global_position, target, _objective_text()]
				)
			)
			if skip != "":
				print("PLAY_SKIP %.1f %s: raised the objective's until flag %s" % [t, path, skip])
				Game.set_flag(StringName(skip))
				softlock_logged = false
	print("PLAY_TIMEOUT %.1f %s (flags raised: %d)" % [_now(), last_scene, _flags.size()])
	get_tree().quit(1)


## One frame of a live fight: foes held at 1 HP, Attack on the first foe each party turn, Return on the result.
func _battle_step(ctl: FieldBattle, result_at: float, t: float) -> float:
	if ctl.engine == null:
		return result_at
	for foe in ctl.engine.enemies:
		foe.hp = mini(foe.hp, 1)
	if ctl.state == BattleController.STATE_COMMAND and ctl.engine.is_party_turn():
		_party_act(ctl)
		return result_at
	if ctl.state == BattleController.STATE_RESULT:
		if result_at < 0.0:
			return t
		if t - result_at > RESULT_READ_S:
			ctl.hud.result.accept()
			return t + 1000.0
		return result_at
	if int(t / TAP_S) != int((t - 0.02) / TAP_S) and ctl.state not in [BattleController.STATE_TARGET]:
		_tap(&"ui_accept")
	return result_at


## Attack the first foe; when Attack is refused (Ch6: Toma won't strike the Stillguard), any other skill that takes, on
## a foe or on the actor himself, as a player would use his lent Brace or Shield Wall.
func _party_act(ctl: FieldBattle) -> void:
	var actor := ctl.engine.current
	var foes := ctl.engine.living_foes_of(actor)
	if foes.is_empty():
		return
	var res := ctl.act(&"attack", [foes[0].id])
	if res == null or res.ok:
		return
	for skill: StringName in actor.skills:
		if not ctl.engine.is_party_turn() or ctl.engine.current != actor:
			return
		for target: StringName in [foes[0].id, actor.id]:
			var r := ctl.act(skill, [target])
			if r != null and r.ok:
				return


func _on_flag(flag: StringName, value: Variant) -> void:
	if value and not _flags.has(String(flag)):
		_flags.append(String(flag))
		_progress("PLAY_FLAG %.1f %s" % [_now(), flag])


func _progress(line: String) -> void:
	_last_progress = _now()
	print(line)


func _story_busy(cur: Node) -> bool:
	var story: Variant = cur.get(&"story") if cur != null else null
	return story is ZoneStory and not (story as ZoneStory).is_free()


func _target() -> Vector3:
	var huds := get_tree().root.find_children("*", "ObjectiveHud", true, false)
	for h in huds:
		var pos := (h as ObjectiveHud).target_position()
		if pos != Vector3.INF:
			return pos
	return Vector3.INF


## The available Interactables (the zone's touch triggers, NPCs, shrines: Interactable.GROUP) within SWEEP_RADIUS_M of
## `at`, nearest first.
func _triggers_near(_cur: Node, at: Vector3, radius: float = SWEEP_RADIUS_M) -> Array:
	var out: Array = []
	for n in get_tree().get_nodes_in_group(Interactable.GROUP):
		var it := n as Interactable
		# Shops and inns open a menu the probe can't use (and never move the story).
		var services := it != null and (it.payload.has("shop") or it.payload.has("inn"))
		if (
			it != null
			and not services
			and it.is_inside_tree()
			and it.is_available()
			and it.global_position.distance_to(at) <= radius
		):
			out.append(it)
	out.sort_custom(
		func(a: Node3D, b: Node3D) -> bool: return a.global_position.distance_to(at) < b.global_position.distance_to(at)
	)
	return out


## `at` moved onto the ground under it (a ray down from GROUND_RAY_M above), lifted SWEEP_LIFT_M; `at` if none.
func _on_ground(p: FieldController, at: Vector3, from_up: float = GROUND_RAY_M) -> Vector3:
	var q := PhysicsRayQueryParameters3D.create(at + Vector3.UP * from_up, at + Vector3.DOWN * GROUND_RAY_M)
	q.exclude = [p.get_rid()]
	var hit := p.get_world_3d().direct_space_state.intersect_ray(q)
	return ((hit["position"] as Vector3) if not hit.is_empty() else at) + Vector3.UP * SWEEP_LIFT_M


## The current objective's `until` flag in the field's zone ("" when none).
func _skip_objective() -> String:
	for h in get_tree().root.find_children("*", "ObjectiveHud", true, false):
		var hud := h as ObjectiveHud
		if hud.tracker != null:
			return str(hud.tracker.current(hud.zone).get("until", ""))
	return ""


## Steps the hero off `a` for a few frames, then onto it: a touch fires on entering, so standing in it already (or
## having entered it while the story was busy) never fires it again.
func _step_onto(p: FieldController, a: Node3D) -> void:
	# A trigger has its true height: ray from just above it, or a floor overhead (the Coilspire's gallery over its crown)
	# takes the hero.
	p.global_position = _on_ground(p, a.global_position + Vector3(STEP_OFF_M, 0, 0), TRIGGER_RAY_M)
	for i in 3:
		await get_tree().physics_frame
	p.velocity = Vector3.ZERO
	p.global_position = _floor_in(p, a)


## A floor point inside trigger `a` near its height. A trigger can span a void (the Coilspire crown's spans the spire's
## well), so its own point is tried first, then a ring of points out to FLOOR_SEARCH_M.
func _floor_in(p: FieldController, a: Node3D) -> Vector3:
	var it := a as Interactable
	for r in range(0, FLOOR_SEARCH_M + 1):
		for dx in range(-r, r + 1):
			for dz in range(-r, r + 1):
				if maxi(absi(dx), absi(dz)) != r:
					continue
				var at := a.global_position + Vector3(dx, 0, dz)
				var q := PhysicsRayQueryParameters3D.create(
					at + Vector3.UP * TRIGGER_RAY_M, at + Vector3.DOWN * TRIGGER_RAY_M
				)
				q.exclude = [p.get_rid()]
				var hit := p.get_world_3d().direct_space_state.intersect_ray(q)
				if hit.is_empty():
					continue
				var on := (hit["position"] as Vector3) + Vector3.UP * SWEEP_LIFT_M
				if it == null or it.contains_point(on):
					return on
	return _on_ground(p, a.global_position, TRIGGER_RAY_M)


## Presses (true) or releases (false) ui_cancel as a held key; true when that changed the hold.
func _skip_hold(on: bool) -> bool:
	if _skip_holding == on:
		return false
	_skip_holding = on
	var ev := InputEventAction.new()
	ev.action = &"ui_cancel"
	ev.pressed = on
	Input.parse_input_event(ev)
	return true


## The action of a showing HoldPrompt (&"" when none); every other held prompt action is released.
func _held_prompt_action() -> StringName:
	var out := &""
	for n in get_tree().root.find_children("*", "HoldPrompt", true, false):
		var hp := n as HoldPrompt
		if hp.action == &"":
			continue
		if hp.is_inside_tree() and hp.is_showing():
			out = hp.action
		elif Input.is_action_pressed(hp.action):
			Input.action_release(hp.action)
	return out


## The next swept trigger still in the tree (one-shot triggers free themselves), or null.
static func _next_alive(sweep: Array) -> Node3D:
	while not sweep.is_empty():
		var n: Variant = sweep.pop_front()
		if is_instance_valid(n) and (n as Node3D).is_inside_tree():
			return n as Node3D
	return null


func _objective_text() -> String:
	var huds := get_tree().root.find_children("*", "ObjectiveHud", true, false)
	return (huds[0] as ObjectiveHud).line_text() if not huds.is_empty() else ""


func _player(cur: Node) -> FieldController:
	if cur == null:
		return null
	if cur.get(&"player") is FieldController:
		return cur.get(&"player") as FieldController
	var found := cur.find_children("*", "FieldController", true, false)
	return found[0] as FieldController if not found.is_empty() else null


func _tap(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	var up := InputEventAction.new()
	up.action = action
	Input.parse_input_event(up)


func _now() -> float:
	return float(Time.get_ticks_msec() - _t0) / 1000.0
