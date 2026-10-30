class_name ZoneStory
extends Node
## Plays a zone's story from the chapter data (M3-ARC-01; docs/kb/tech/chapter_flow.md). A child of
## a zone root (GreyboxZone) that provides `stage`, `location_id`, `place_at(spawn, yaw)` and
## `spawn_yaw_deg(spawn)`. The zone's block of the chapter file says:
##   party    the party and reserve ids, filled in on arrival while the party is empty.
##   arrive   a list of {when, steps}: begin() runs the first whose `when` holds.
##   beats    id -> {when, steps}: a trigger or interactable whose payload has {"beat": id} runs it.
##   barks    a list of {when, map}: a bark id is swapped for map[id] under the first `when` that holds.
##   overheard_hold_sec  how long an overheard bark's line stays up (optional).
## `when` is {"set": [flags], "unset": [flags]}, all of which must hold (missing = holds).
## Steps run in order, one key each:
##   {"play": id}       plays a compiled .dlg scene on the stage and waits for it. When the run hands
##                      off after it with no other scene between (only set, place, party or zone steps),
##                      it doesn't fade back in at its end (restore_fade): a scene that ends on black
##                      hands off on black (M3-C01-02: Ch1's rise to the surface and going under).
##   {"place": spawn}   puts Rhen on a spawn, facing its marker.
##   {"set": flag}      sets a declared flag through Game.set_flag.
##   {"chapter": n}     moves the story to chapter n (Game.set_chapter; the chapter autosave follows).
##   {"party": {"party": [...], "reserve": [...]}} replaces the party.
##   {"zone": method, "args": [...]} calls a method on the zone root, when it has it.
##   {"beat": id}       runs another beat's steps here (its `when` is not checked).
##   {"if_event": name, "steps": [...]} when the last scene played reported <<event name>>, runs
##                      those steps and stops (a "Not yet" choice stepping Rhen back).
##   {"battle": encounter, "return_spawn", "escape_spawn", "victory_flag"} opens the field battle,
##                      which returns to this zone; ends the run. Its party is the step's "party" and
##                      "reserve" when given, else the current party; "seed" overrides the rng seed;
##                      "objective_flag" names a numeric flag that carries a set piece's objective
##                      count across fights (BattleRequest.objective_flag; Ch8's stair meter).
##   {"go": {"location", "spawn"}} travels to another location; ends the run.
##   {"scene": path}    changes to a scene (a cutscene set, the end card); ends the run.
## Payloads with {"dialogue": id} play that bark (in-engine); with "overheard": true as well, it plays
## on its own sequencer as Rhen walks past, never blocking anything, and anything else cuts it off.

const KEY_DIALOGUE := "dialogue"
const KEY_OVERHEARD := "overheard"
const KEY_BEAT := "beat"
const KEY_OBJECTIVE_FLAG := "objective_flag"
const KIND_BATTLE := &"battle"
const KIND_GO := &"go"
const KIND_SCENE := &"scene"

## Go live on _ready when the zone is the current scene. Tests turn it off, set `active` and call
## begin() themselves.
@export var autostart := true

var sequencer: CutsceneSequencer
var overhear: CutsceneSequencer
## The zone's block of the chapter data.
var cfg: Dictionary = {}
## True while a run, a bark or a hand-off is under way: further triggers wait.
var busy := false
## Reacts to interactables and triggers only while true.
var active := false
## Tests record hand-offs here instead of leaving the zone: (kind, target). For a battle the target
## is the BattleRequest it would submit; for go, {"location", "spawn"}; for scene, the path.
var hand_off: Callable = Callable()
## True once a run has handed off (nothing else plays after it).
var handed_off := false

var _zone: Node


func _ready() -> void:
	_zone = get_parent()
	var loc := StringName(str(_zone.get(&"location_id"))) if _zone != null and "location_id" in _zone else &""
	var override := str(_zone.get(&"chapter_path")) if _zone != null and "chapter_path" in _zone else ""
	cfg = ChapterRegistry.zone(loc, override)
	sequencer = CutsceneSequencer.new()
	sequencer.name = "Sequencer"
	add_child(sequencer)
	overhear = _new_overhear(false)
	FieldEvents.connect_interacted(_on_interacted)
	FieldEvents.connect_trigger(_on_trigger)
	if autostart:
		_autostart.call_deferred()


## SceneRouter's resident field (kept through a fight, re-attached; nothing re-runs _ready): the zone arrives
## again as a fresh load would. The hand-off to the fight is over, and the arrival runs (a scripted win's scene).
func on_resident_return() -> void:
	handed_off = false
	busy = false
	active = false
	if autostart:
		_autostart()  # now, not deferred: it waits for the scene_changed the router emits after placing the party


func _exit_tree() -> void:
	for pair: Array in [[FieldEvents.INTERACTED, _on_interacted], [FieldEvents.TRIGGER_ENTERED, _on_trigger]]:
		if EventBus.is_connected(pair[0], pair[1]):
			EventBus.disconnect(pair[0], pair[1])


## Fills an empty party, then runs the first arrival whose `when` holds. Await it.
func begin() -> void:
	_join_party()
	for row: Dictionary in cfg.get("arrive", []):
		if holds(row.get("when", {})):
			await run(row.get("steps", []))
			return


## Runs beat `id` when its `when` holds. Returns false when it doesn't (or there is no such beat).
func play_beat(id: StringName) -> bool:
	var beat: Dictionary = (cfg.get("beats", {}) as Dictionary).get(String(id), {})
	if beat.is_empty() or not holds(beat.get("when", {})):
		return false
	await run(beat.get("steps", []))
	return true


## Runs `steps` (see the class comment). Await it.
func run(steps: Array) -> void:
	busy = true
	_hush()
	await _steps(steps)
	busy = handed_off


## True when nothing is playing and nothing has handed off: a field encounter may start.
func is_free() -> bool:
	return _free()


## Opens a random field battle (FieldEncounters): it returns to `spawn` here, win or escape.
func random_battle(encounter: StringName, spawn: StringName) -> void:
	_hand_off(
		KIND_BATTLE,
		_battle_request({"battle": String(encounter), "return_spawn": String(spawn), "escape_spawn": String(spawn)})
	)


## True when every flag in when.set is set and every flag in when.unset is not.
static func holds(when: Dictionary) -> bool:
	for f: Variant in when.get("set", []):
		if not bool(Game.get_flag(StringName(str(f)))):
			return false
	for f: Variant in when.get("unset", []):
		if bool(Game.get_flag(StringName(str(f)))):
			return false
	return true


## A bark's variant under the first `barks` row whose `when` holds, else the bark itself.
func variant(scene_id: StringName) -> StringName:
	for row: Dictionary in cfg.get("barks", []):
		if holds(row.get("when", {})):
			return StringName(str((row.get("map", {}) as Dictionary).get(String(scene_id), scene_id)))
	return scene_id


## Returns true when the run should stop (a hand-off, or an if_event that fired).
func _steps(steps: Array) -> bool:
	var stop := false
	for i in steps.size():
		var step: Dictionary = steps[i]
		if handed_off or stop:
			return true
		if _hands_off(step):
			return true
		if step.has("play"):
			sequencer.restore_fade = not _hands_off_after(steps, i)
			await sequencer.play(StringName(str(step["play"])), _stage())
			sequencer.restore_fade = true
		elif step.has("beat"):
			var beat: Dictionary = (cfg.get("beats", {}) as Dictionary).get(str(step["beat"]), {})
			stop = await _steps(beat.get("steps", []))
		elif step.has("if_event"):
			if _reported(StringName(str(step["if_event"]))):
				await _steps(step.get("steps", []))
				stop = true
		else:
			_apply(step)
	return stop or handed_off


## The steps that change state and return at once: place, set, chapter, party, zone.
func _apply(step: Dictionary) -> void:
	if step.has("place"):
		var spawn := StringName(str(step["place"]))
		_zone.call(&"place_at", spawn, _zone.call(&"spawn_yaw_deg", spawn))
	elif step.has("set"):
		Game.set_flag(StringName(str(step["set"])))
	elif step.has("chapter"):
		Game.set_chapter(int(step["chapter"]))
	elif step.has("party"):
		_set_party(step["party"])
	elif step.has("zone"):
		var method := StringName(str(step["zone"]))
		if _zone.has_method(method):
			_zone.callv(method, step.get("args", []))
	else:
		push_warning("ZoneStory: unknown step %s" % step)


## True when the steps after steps[i] reach a battle, go or scene step before any other scene could
## play (a play, beat or if_event step).
static func _hands_off_after(steps: Array, i: int) -> bool:
	for j in range(i + 1, steps.size()):
		var s: Dictionary = steps[j]
		if s.has("battle") or s.has("go") or s.has("scene"):
			return true
		if s.has("play") or s.has("beat") or s.has("if_event"):
			return false
	return false


## Hands off for a battle, go or scene step (true); false for any other step.
func _hands_off(step: Dictionary) -> bool:
	if step.has("battle"):
		_hand_off(KIND_BATTLE, _battle_request(step))
	elif step.has("go"):
		_hand_off(KIND_GO, step["go"])
	elif step.has("scene"):
		_hand_off(KIND_SCENE, str(step["scene"]))
	else:
		return false
	return true


func _battle_request(step: Dictionary) -> BattleRequest:
	var r := BattleRequest.make(
		StringName(str(step["battle"])),
		StringName(str(_zone.get(&"location_id"))),
		StringName(str(step.get("return_spawn", ""))),
		StringName(str(step.get("victory_flag", ""))),
		StringName(str(step.get("escape_spawn", "")))
	)
	if step.has("party"):
		r.active = FirstPlayableConfig.ids(step["party"])
		r.reserve = FirstPlayableConfig.ids(step.get("reserve", []))
	elif not Game.state.party_ids.is_empty():
		r.active = Game.state.party_ids.duplicate()
		r.reserve = Game.state.reserve_ids.duplicate()
	if step.has("seed"):
		r.rng_seed = int(step["seed"])
	if step.has(KEY_OBJECTIVE_FLAG):
		r.objective_flag = StringName(str(step[KEY_OBJECTIVE_FLAG]))
		r.objective_start = int(Game.get_flag(r.objective_flag, 0))
	return r


func _hand_off(kind: StringName, target: Variant) -> void:
	handed_off = true
	busy = true
	_hush()
	if hand_off.is_valid():
		hand_off.call(kind, target)
		return
	match kind:
		KIND_BATTLE:
			BattleRequest.submit(target as BattleRequest)
		KIND_GO:
			var to: Dictionary = target
			FlowRouting.go_to(StringName(str(to.get("location", ""))), StringName(str(to.get("spawn", ""))))
		_:
			FlowRouting.change_scene(str(target))


func _join_party() -> void:
	if not Game.state.party_ids.is_empty() or not cfg.has("party"):
		return
	_set_party(cfg["party"])


func _set_party(join: Dictionary) -> void:
	Game.state.party_ids.clear()
	Game.state.reserve_ids.clear()
	for id: Variant in join.get("party", []):
		Game.state.party_ids.append(StringName(str(id)))
	for id: Variant in join.get("reserve", []):
		Game.state.reserve_ids.append(StringName(str(id)))


func _autostart() -> void:
	if is_inside_tree() and get_tree().current_scene == _zone:
		# M3-CIN-1234: the router puts the party on the travel spawn the frame after the swap (then emits scene_changed),
		# so an arrival's own `place` step must run after it or be undone (Ch1's ScaleHull: Rhen stayed at Surface and
		# O02's over-the-shoulder framed an empty deck; most Act I arrivals place the party somewhere else).
		if SceneRouter.is_busy():
			await EventBus.scene_changed
		active = true
		await begin()


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	if not _free():
		return
	if payload.has(KEY_BEAT):
		play_beat(StringName(str(payload[KEY_BEAT])))
	elif payload.has(KEY_DIALOGUE):
		run([{"play": String(variant(StringName(str(payload[KEY_DIALOGUE]))))}])


func _on_trigger(_id: StringName, payload: Dictionary) -> void:
	if payload.has(KEY_DIALOGUE) and bool(payload.get(KEY_OVERHEARD, false)):
		if _free() and not overhear.is_playing():
			overhear.play(variant(StringName(str(payload[KEY_DIALOGUE]))), _stage())
		return
	if not _free():
		return
	if payload.has(KEY_BEAT):
		play_beat(StringName(str(payload[KEY_BEAT])))
	elif payload.has(KEY_DIALOGUE):
		run([{"play": String(variant(StringName(str(payload[KEY_DIALOGUE]))))}])


## True when the last scene the main sequencer played reported <<event `ev`>>.
func _reported(ev: StringName) -> bool:
	for e: Dictionary in sequencer.events:
		if StringName(str(e.get("name", ""))) == ev:
			return true
	return false


## Cuts an overheard bark off: a sequencer leaving the tree ends its scene at once, so it is swapped.
func _hush() -> void:
	if overhear == null or not overhear.is_playing():
		return
	var instant := overhear.instant
	remove_child(overhear)
	overhear.queue_free()
	overhear = _new_overhear(instant)


func _new_overhear(instant: bool) -> CutsceneSequencer:
	var seq := CutsceneSequencer.new()
	seq.name = "Overhear"
	seq.hold_player = false
	seq.auto_advance = true
	seq.auto_advance_hold_sec = float(cfg.get("overheard_hold_sec", seq.auto_advance_hold_sec))
	seq.auto_advance_read_cps = float(cfg.get("overheard_read_cps", 0.0))
	seq.instant = instant
	add_child(seq)
	return seq


func _free() -> bool:
	return (
		active
		and not busy
		and not handed_off
		and not sequencer.is_playing()
		and not (is_inside_tree() and SceneRouter.is_busy())
	)


func _stage() -> CutsceneStage:
	var s: Variant = _zone.get(&"stage") if _zone != null else null
	return s as CutsceneStage
