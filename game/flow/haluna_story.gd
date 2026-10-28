class_name HalunaStory
extends Node
## The first playable's story in the Haluna zone (M2-FP-04; docs/kb/tech/first_playable_flow.md).
## A child of the zone root (HalunaZone), which provides `stage` (a CutsceneStage) and
## `place_at(spawn)`. What it plays and where comes from first_playable.json "haluna".
##   arrival   while `ch02_met_asha` is unset: Rhen on the Beach spawn, Cutscene A
##             (ch02_girl_on_the_beach), then free play. Asha and Toma join Rhen there: once
##             `ch02_met_asha` is set, they join (PartyJoins: first_playable.json "party" joins, party and
##             reserve ids, M2 slice), which the field menu's Heroes page reads (M2-UI-04). Once the
##             tideline battle is won (its victory flag) and until after_battle_flag is set, an
##             arrival plays B02 instead (M2-FP-13): Rhen at the after_battle spawn and Neme's table in-engine.
##   villagers an Interactable whose payload has "dialogue" plays that bark scene in-engine.
##   overheard a touch trigger whose payload has "dialogue" and "overheard" (M2-FP-13, B03's four
##             "Cantor" fragments) plays that bark on its own sequencer as Rhen walks past: he is
##             not stopped, the lines advance by themselves, and it never blocks another trigger
##             (anything else that starts cuts it off).
##   battle    a trigger whose payload has "battle" opens that field battle (BattleRequest), which
##             returns the party to BattleReturn and sets the victory flag on a win; an escape
##             returns it to BeforeBattle, on the beach side of the trigger (M2-FP-05).
##   night     after the Drownbell (night_flag) and until sworn_flag (M2-FP-15, B11): Haluna at
##             night (HalunaZone.set_night), Rhen at night_spawn, the cast on the dock, the dock
##             scene in-engine, then night_end_scene (the end card). Once sworn, barks play their
##             night_barks variant.
##   ending    a trigger whose payload has "cutscene" plays the low-tide beat in-engine (M2-FP-13,
##             B05, before_ending_scene_id), then opens the Shell Shrine trial (ending_scene). B05
##             opens on "Go now" / "Not yet" (M2-FP-21): "Not yet" (ending_decline_event) steps
##             Rhen back to ending_decline_spawn and hands nothing off. Before the first save the
##             same box plays an overheard bark instead (M2-FP-20, Triggers/CausewayHeadUnsaved).
##   chapter   M2-FP-27: every arrival moves the story to cfg.chapter (2) when it is behind it, so
##             Haluna's saves read "Chapter 2" and the chapter autosave runs.
##   route     M2-FP-25: when cfg has ending_location, "Go now" travels there (the Saltgrass
##             Causeway, B06) at ending_spawn instead of opening ending_scene.
## The zone's interactables only author ids, payloads and flags; nothing in them knows this script.

const KEY_DIALOGUE := "dialogue"
const KEY_BATTLE := "battle"
const KEY_CUTSCENE := "cutscene"
const KEY_OVERHEARD := "overheard"
const KEY_GO := "go"

## Go live on _ready when the zone is the current scene (the game). Tests turn it off, set
## `active` and call begin() themselves, so a zone instanced by a test never hands off.
@export var autostart := true

var sequencer: CutsceneSequencer
## Plays the overheard barks: Rhen keeps walking and the lines advance by themselves.
var overhear: CutsceneSequencer
var cfg: Dictionary = {}
## True while a cutscene, a bark or a hand-off is under way: further triggers wait.
var busy := false
## Reacts to villagers and triggers only while true.
var active := false
## Tests record hand-offs here instead of changing scene: (kind: StringName, target: String).
var hand_off: Callable = Callable()

var _zone: Node


func _ready() -> void:
	_zone = get_parent()
	cfg = FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA)
	sequencer = CutsceneSequencer.new()
	sequencer.name = "Sequencer"
	add_child(sequencer)
	overhear = _new_overhear(false)
	FieldEvents.connect_interacted(_on_interacted)
	FieldEvents.connect_trigger(_on_trigger)
	if autostart:
		_autostart.call_deferred()


func _exit_tree() -> void:
	for pair: Array in [[FieldEvents.INTERACTED, _on_interacted], [FieldEvents.TRIGGER_ENTERED, _on_trigger]]:
		if EventBus.is_connected(pair[0], pair[1]):
			EventBus.disconnect(pair[0], pair[1])


## Plays the arrival (Cutscene A) or B02 when either is due. Await it.
func begin() -> void:
	var chapter := int(cfg.get("chapter", 0))
	if chapter > Game.state.chapter:
		Game.set_chapter(chapter)
	if not _flag(&"intro_flag"):
		busy = true
		_zone.call(&"place_at", StringName(str(cfg.get("intro_spawn", ""))))
		await sequencer.play(StringName(str(cfg.get("intro_scene_id", ""))), _stage())
		_join_party()
		busy = false
		return
	_join_party()
	if _flag(&"night_flag") and not _flag(&"sworn_flag"):
		await _night()
	elif _flag(&"battle_victory_flag") and not _flag(&"after_battle_flag"):
		# B02: noon at Neme's. The scene opens black, so the move to her door is never seen.
		busy = true
		var spawn := StringName(str(cfg.get("after_battle_spawn", "")))
		_zone.call(&"place_at", spawn, _zone.call(&"spawn_yaw_deg", spawn))
		await sequencer.play(StringName(str(cfg.get("after_battle_scene_id", ""))), _stage())
		busy = false


## Asha and Toma join when Cutscene A sets intro_flag (PartyJoins, first_playable.json "party" joins, through
## Game's flag hook). A save from before joins existed (the flag set, no party) joins them on its next arrival,
## through the same row, so they get their starting gear too.
func _join_party() -> void:
	if not _flag(&"intro_flag") or not Game.state.party_ids.is_empty():
		return
	PartyJoins.on_flag(Game.state, StringName(str(cfg.get("intro_flag", ""))), true)


func _autostart() -> void:
	if is_inside_tree() and get_tree().current_scene == _zone:
		active = true
		await begin()


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	if payload.has(KEY_DIALOGUE) and _free():
		_bark(_variant(StringName(str(payload[KEY_DIALOGUE]))))


func _on_trigger(_id: StringName, payload: Dictionary) -> void:
	if payload.has(KEY_DIALOGUE) and bool(payload.get(KEY_OVERHEARD, false)):
		if _free() and not overhear.is_playing():
			overhear.play(_variant(StringName(str(payload[KEY_DIALOGUE]))), _stage())
		return
	if not _free():
		return
	if payload.has(KEY_BATTLE):
		_go(KEY_BATTLE, str(payload[KEY_BATTLE]))
	elif payload.has(KEY_CUTSCENE):
		_end()


func _bark(scene_id: StringName) -> void:
	busy = true
	_hush()
	await _play_unstaged(scene_id)
	HalunaVillagers.end_talks(_zone)  # M2-FP-102: the villager turns back to its work
	busy = false


## M2-FP-107/110: a bark or B05 freezes Rhen but is no staged scene, so Asha and Toma stay beside him.
func _play_unstaged(scene_id: StringName) -> void:
	sequencer.hold_player = false
	sequencer.freeze_player = true
	await sequencer.play(scene_id, _stage())
	sequencer.hold_player = true
	sequencer.freeze_player = false


## B11 (M2-FP-15): the dock at night, then the end card.
func _night() -> void:
	busy = true
	_zone.call(&"set_night", cfg.get("night", {}), cfg.get("night_hide", []))
	var spawn := StringName(str(cfg.get("night_spawn", "")))
	_zone.call(&"place_at", spawn, _zone.call(&"spawn_yaw_deg", spawn))
	_zone.call(&"place_cast", cfg.get("night_cast", {}), cfg.get("night_marks", {}))
	sequencer.restore_fade = false
	await sequencer.play(StringName(str(cfg.get("night_scene_id", ""))), _stage())
	if is_inside_tree() or hand_off.is_valid():
		_go(KEY_CUTSCENE, str(cfg.get("night_end_scene", "")))


## A bark's night variant once Rhen is sworn (night_barks), else the bark itself.
func _variant(scene_id: StringName) -> StringName:
	if not _flag(&"sworn_flag"):
		return scene_id
	return StringName(str((cfg.get("night_barks", {}) as Dictionary).get(String(scene_id), scene_id)))


## B05 at the causeway head, then Cutscene B. B05 opens on a choice (M2-FP-21): when it reports
## ending_decline_event ("Not yet"), Rhen steps back to ending_decline_spawn, short of the trigger,
## and control returns with nothing handed off; the trigger stays armed for the next approach.
func _end() -> void:
	busy = true
	_hush()
	var low_tide := StringName(str(cfg.get("before_ending_scene_id", "")))
	if low_tide != &"":
		await _play_unstaged(low_tide)
		if _declined():
			var spawn := StringName(str(cfg.get("ending_decline_spawn", "")))
			_zone.call(&"place_at", spawn, _zone.call(&"spawn_yaw_deg", spawn))
			busy = false
			return
	if not is_inside_tree():
		return
	if str(cfg.get("ending_location", "")) != "":
		_go(KEY_GO, str(cfg["ending_location"]))
	else:
		_go(KEY_CUTSCENE, str(cfg.get("ending_scene", "")))


## True when the last scene reported ending_decline_event (B05's "Not yet").
func _declined() -> bool:
	var ev := StringName(str(cfg.get("ending_decline_event", "")))
	if ev == &"":
		return false
	for e: Dictionary in sequencer.events:
		if StringName(str(e.get("name", ""))) == ev:
			return true
	return false


## Cuts an overheard bark off (something else is starting): a sequencer that leaves the tree ends
## its scene at once (M2-FP-09), so it is swapped for a fresh one.
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


func _go(kind: StringName, target: String) -> void:
	busy = true
	_hush()
	if hand_off.is_valid():
		hand_off.call(kind, target)
		return
	if kind == KEY_BATTLE:
		BattleRequest.start(
			StringName(target),
			StringName(str(cfg.get("location_id", ""))),
			StringName(str(cfg.get("battle_return_spawn", ""))),
			StringName(str(cfg.get("battle_victory_flag", ""))),
			StringName(str(cfg.get("battle_escape_spawn", "")))
		)
	elif kind == KEY_GO:
		FlowRouting.go_to(StringName(target), StringName(str(cfg.get("ending_spawn", ""))))
	else:
		FlowRouting.change_scene(target)


## The story flag named by cfg[`key`] (false when the key is empty).
func _flag(key: StringName) -> bool:
	var f := StringName(str(cfg.get(String(key), "")))
	return f != &"" and bool(Game.get_flag(f))


func _free() -> bool:
	return active and not busy and not sequencer.is_playing() and not (is_inside_tree() and SceneRouter.is_busy())


func _stage() -> CutsceneStage:
	var s: Variant = _zone.get(&"stage") if _zone != null else null
	return s as CutsceneStage
