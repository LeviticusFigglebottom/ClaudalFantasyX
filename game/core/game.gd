extends Node
## Autoload "Game": owns the live GameStateData, the flag registry, the play-time clock and the
## chapter counter.
##
## Play time (M1-ARC-03): `state.play_time_sec` grows by each frame's delta while the clock runs.
## Game processes with PROCESS_MODE_ALWAYS, so menus that pause the tree still count, as players
## expect. All logic is in advance_play_time(delta), which tests drive directly: the same
## deltas always give the same total. A single step is clamped to [0, PLAY_TIME_MAX_STEP_SEC],
## so a debugger break or a dragged window cannot add minutes at once. The title screen calls
## stop_play_clock(); new_game() and SaveSystem.load_into_game() start it again.
##
## Party vitals (M1-ARC-06): Game owns the live party's HP, MP and carried statuses between
## battles (state.party_vitals, rules in game/data/world/party_rest.json):
##   EventBus.party_full_heal_requested   -> heal_party(): full HP/MP, cures "shrine_cures"
##   EventBus.battle_party_returned       -> record_party(): writes HP/MP/carried statuses back
##   vitals_modifier()                    -> a BattleEngine.party_modifier that applies them; put
##                                           it LAST in EquipmentEffects.compose([...])

const FLAGS_PATH := "res://game/data/flags.tres"
## The largest single frame step counted towards play time, in seconds.
const PLAY_TIME_MAX_STEP_SEC := 1.0
const REST_RULES_PATH := "res://game/data/world/party_rest.json"

var state: GameStateData = GameStateData.new()
var registry: FlagRegistry
var play_clock_running := true
## party_rest.json: carried_statuses, carried_duration, shrine_cures.
var rest_rules: Dictionary = {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	registry = FlagRegistry.load_path(FLAGS_PATH)
	rest_rules = load_rest_rules()
	EventBus.party_full_heal_requested.connect(heal_party)
	EventBus.battle_party_returned.connect(record_party)


func _process(delta: float) -> void:
	advance_play_time(delta)


func get_flag(flag: StringName, default: Variant = false) -> Variant:
	_check_declared(flag)
	return state.flags.get(String(flag), default)


func set_flag(flag: StringName, value: Variant = true) -> void:
	_check_declared(flag)
	state.flags[String(flag)] = value
	EventBus.flag_changed.emit(flag, value)


func new_game() -> void:
	state = GameStateData.new()
	start_play_clock()
	EventBus.new_game_started.emit()


## Moves the story to `chapter`. Emits EventBus.chapter_changed only when the chapter actually
## changes, and returns true when it did. The slot-0 autosave it causes is NOT written here: it is
## requested and written on a later frame at a safe point (SaveSystem.request_autosave, M1-ARC-08),
## so a cutscene may call this at any beat. The sequencer holds the autosave for the whole cutscene
## (SaveSystem.hold_autosave / release_autosave) so the save shows the state after the last beat.
func set_chapter(chapter: int) -> bool:
	var previous := state.chapter
	if chapter == previous:
		return false
	state.chapter = chapter
	EventBus.chapter_changed.emit(chapter, previous)
	return true


# --- Play time ---------------------------------------------------------------------------------


## Adds one frame step to the play time when the clock runs. Returns the seconds counted.
func advance_play_time(delta: float) -> float:
	if not play_clock_running:
		return 0.0
	var step := clampf(delta, 0.0, PLAY_TIME_MAX_STEP_SEC)
	state.play_time_sec += step
	return step


func start_play_clock() -> void:
	play_clock_running = true


func stop_play_clock() -> void:
	play_clock_running = false


func play_time_sec() -> float:
	return state.play_time_sec


# --- Party vitals (M1-ARC-06) -------------------------------------------------------------------


static func load_rest_rules(path: String = REST_RULES_PATH) -> Dictionary:
	var parsed: Variant = null
	if FileAccess.file_exists(path):
		parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Game: could not read %s" % path)
		return {}
	return parsed as Dictionary


## Why `rules` (party_rest.json) cannot be trusted with saved vitals ("" when it can): it is empty
## (missing or unparseable) or lacks carried_statuses, carried_duration or shrine_cures. Without
## carried_statuses every carried status would be dropped from party_vitals after a battle, so
## record_party writes nothing and SaveSystem's data-tables gate refuses to save (M1-ARC-13).
static func rest_rules_problem(rules: Dictionary) -> String:
	if rules.is_empty():
		return "%s is missing, empty or could not be parsed" % REST_RULES_PATH
	if not (
		typeof(rules.get("carried_statuses")) == TYPE_ARRAY
		and typeof(rules.get("shrine_cures")) == TYPE_ARRAY
		and rules.has("carried_duration")
	):
		return "%s lacks carried_statuses, carried_duration or shrine_cures" % REST_RULES_PATH
	return ""


## Statuses that outlast a battle and are saved per member.
func carried_statuses() -> Array[StringName]:
	return _ids(rest_rules.get("carried_statuses", []))


## Statuses a save shrine's rest removes.
func shrine_cures() -> Array[StringName]:
	return _ids(rest_rules.get("shrine_cures", []))


## Duration a carried status comes back with at battle setup (the engine's "until cured").
func carried_duration() -> int:
	return int(rest_rules.get("carried_duration", 0))


## EventBus.party_full_heal_requested: fills every member's HP and MP and cures shrine_cures.
## Returns the members whose saved vitals changed.
func heal_party(_source_id: StringName = &"") -> Array[StringName]:
	return state.full_heal(shrine_cures())


## EventBus.battle_party_returned: writes each party combatant's HP, MP and carried statuses into
## state.party_vitals. Entries that are not BattleCombatants are ignored. While party_rest.json is
## broken (rest_rules_problem) nothing is written, so no carried status is dropped (M1-ARC-13).
func record_party(_encounter_id: StringName, _outcome: StringName, party: Array) -> void:
	var problem := rest_rules_problem(rest_rules)
	if problem != "":
		push_error("Game: not recording party vitals; %s" % problem)
		return
	var carried := carried_statuses()
	for v: Variant in party:
		if not v is BattleCombatant:
			continue
		var c: BattleCombatant = v
		var held: Array[StringName] = []
		for sid: StringName in c.statuses:
			held.append(sid)
		state.record_vitals(c.id, c.hp, c.max_hp, c.mp, c.max_mp, held, carried)


## A BattleEngine.party_modifier that applies `for_state`'s vitals (default: the live state at the
## time of the call). It holds the state, so it stays valid for the whole setup. Run it last:
##   engine.party_modifier = EquipmentEffects.compose([progress.apply_to, fx.modifier(),
##                                                     Game.vitals_modifier()])
func vitals_modifier(for_state: GameStateData = null) -> Callable:
	var st := for_state if for_state != null else state
	var duration := carried_duration()
	return func(c: BattleCombatant) -> void: st.apply_vitals_to(c, duration)


static func _ids(list: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	if typeof(list) == TYPE_ARRAY:
		for v: Variant in list:
			out.append(StringName(str(v)))
	return out


func _check_declared(flag: StringName) -> void:
	if not registry.is_declared(flag):
		push_error("Undeclared story flag '%s' (declare it in %s)" % [flag, FLAGS_PATH])
