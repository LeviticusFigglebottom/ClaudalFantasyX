class_name HalunaStory
extends Node
## The first playable's story in the Haluna zone (M2-FP-04; docs/kb/tech/first_playable_flow.md).
## A child of the zone root (HalunaZone), which provides `stage` (a CutsceneStage) and
## `place_at(spawn)`. What it plays and where comes from first_playable.json "haluna".
##   arrival   while `ch02_met_asha` is unset: Rhen on the Beach spawn, Cutscene A
##             (ch02_girl_on_the_beach), then free play.
##   villagers an Interactable whose payload has "dialogue" plays that bark scene in-engine.
##   battle    a trigger whose payload has "battle" opens that field battle (BattleRequest), which
##             returns the party to BattleReturn and sets the victory flag on a win.
##   ending    a trigger whose payload has "cutscene" opens Cutscene B on its own set
##             (game/levels/ch03/first_verse/), which ends on the end card.
## The zone's interactables only author ids, payloads and flags; nothing in them knows this script.

const KEY_DIALOGUE := "dialogue"
const KEY_BATTLE := "battle"
const KEY_CUTSCENE := "cutscene"

## Go live on _ready when the zone is the current scene (the game). Tests turn it off, set
## `active` and call begin() themselves, so a zone instanced by a test never hands off.
@export var autostart := true

var sequencer: CutsceneSequencer
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
	FieldEvents.connect_interacted(_on_interacted)
	FieldEvents.connect_trigger(_on_trigger)
	if autostart:
		_autostart.call_deferred()


func _exit_tree() -> void:
	for pair: Array in [[FieldEvents.INTERACTED, _on_interacted], [FieldEvents.TRIGGER_ENTERED, _on_trigger]]:
		if EventBus.is_connected(pair[0], pair[1]):
			EventBus.disconnect(pair[0], pair[1])


## Plays the arrival when it has not happened yet. Await it.
func begin() -> void:
	if bool(Game.get_flag(StringName(str(cfg.get("intro_flag", ""))))):
		return
	busy = true
	_zone.call(&"place_at", StringName(str(cfg.get("intro_spawn", ""))))
	await sequencer.play(StringName(str(cfg.get("intro_scene_id", ""))), _stage())
	busy = false


func _autostart() -> void:
	if is_inside_tree() and get_tree().current_scene == _zone:
		active = true
		await begin()


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	if payload.has(KEY_DIALOGUE) and _free():
		_bark(StringName(str(payload[KEY_DIALOGUE])))


func _on_trigger(_id: StringName, payload: Dictionary) -> void:
	if not _free():
		return
	if payload.has(KEY_BATTLE):
		_go(KEY_BATTLE, str(payload[KEY_BATTLE]))
	elif payload.has(KEY_CUTSCENE):
		_go(KEY_CUTSCENE, str(cfg.get("ending_scene", "")))


func _bark(scene_id: StringName) -> void:
	busy = true
	await sequencer.play(scene_id, _stage())
	busy = false


func _go(kind: StringName, target: String) -> void:
	busy = true
	if hand_off.is_valid():
		hand_off.call(kind, target)
		return
	if kind == KEY_BATTLE:
		BattleRequest.start(
			StringName(target),
			StringName(str(cfg.get("location_id", ""))),
			StringName(str(cfg.get("battle_return_spawn", ""))),
			StringName(str(cfg.get("battle_victory_flag", "")))
		)
	else:
		SceneRouter.change_scene(target)


func _free() -> bool:
	return active and not busy and not sequencer.is_playing() and not (is_inside_tree() and SceneRouter.is_busy())


func _stage() -> CutsceneStage:
	var s: Variant = _zone.get(&"stage") if _zone != null else null
	return s as CutsceneStage
