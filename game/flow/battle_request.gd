class_name BattleRequest
extends RefCounted
## A pending field battle (M2-FP-03; docs/kb/tech/first_playable_flow.md). Field code asks for a
## fight with BattleRequest.start(); the request waits here (one at a time) while SceneRouter
## swaps to the FieldBattle scene, which takes it on _ready, plays it live, and sends the party
## back to `return_location` / `return_spawn` (setting `victory_flag` on a win; an escape goes to
## `escape_spawn` when set; a defeat retries or loads the last save, M2-FP-05).
##
##   BattleRequest.start(&"ch02_tideline", &"ch02/haluna", &"BattleReturn", &"ch02_tideline_won", &"BeforeBattle")
##
## The party and the rng seed default to game/data/flow/first_playable.json "field_battle".

## The field battle scene start() opens when the data file names none.
const DEFAULT_SCENE := "res://game/flow/field_battle.tscn"
const KEY_SCENE := "scene"
const KEY_ACTIVE := "active"
const KEY_RESERVE := "reserve"
const KEY_SEED := "seed"

## The one request waiting for a FieldBattle (null when none).
static var _pending: BattleRequest
## How start() changes scene: (scene_path: String). Unset = SceneRouter.change_scene. Tests set a
## recorder and reset it to Callable() afterwards.
static var change_scene: Callable = Callable()
## How submit() plays the encounter stinger in the field before the router's change (M2-BPR-05): a
## Callable() awaited with no arguments. Unset = BattleStinger.play. Skipped when change_scene is set.
## Tests set a recorder and reset it to Callable() afterwards.
static var play_stinger: Callable = Callable()

var encounter: StringName = &""
var active: Array[StringName] = []
var reserve: Array[StringName] = []
var rng_seed := 0
var return_location: StringName = &""
var return_spawn: StringName = &""
## Set through Game.set_flag on a victory (never on an escape or a defeat). &"" = none.
var victory_flag: StringName = &""
## Where an escape returns the party (M2-FP-05): the near side of the field trigger, so fleeing
## never carries the party past it. &"" = return_spawn.
var escape_spawn: StringName = &""
## After a victory or an escape, open this scene instead of travelling to return_location (M2-FP-06:
## the Drownbell is the last fight of the first playable and goes to the end card). "" = travel.
var return_scene: String = ""
## A set piece's carried meter (M3-C08-02: Ch8's stair meter, ch08_stair_groups_up): a numeric flag.
## FieldBattle sets it to objective_start + the engine's objective_count after a win or a scripted
## escape, and back to objective_start on "Fight again". &"" = none.
var objective_flag: StringName = &""
## The meter's value when the fight was asked for (ZoneStory reads it off the flag).
var objective_start := 0


## A request with the data file's party and seed; nothing is recorded or opened.
static func make(
	encounter_id: StringName,
	location: StringName,
	spawn: StringName,
	flag: StringName = &"",
	escape_at: StringName = &""
) -> BattleRequest:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_FIELD_BATTLE)
	var r := BattleRequest.new()
	r.encounter = encounter_id
	r.active = FirstPlayableConfig.ids(cfg.get(KEY_ACTIVE, []))
	r.reserve = FirstPlayableConfig.ids(cfg.get(KEY_RESERVE, []))
	r.rng_seed = int(cfg.get(KEY_SEED, 0))
	r.return_location = location
	r.return_spawn = spawn
	r.victory_flag = flag
	r.escape_spawn = escape_at
	return r


## Records a field battle on `encounter_id` and opens the FieldBattle scene. After a victory the
## party goes back to `location` at `spawn` and `flag` is set; after an escape it goes to
## `escape_at` (or `spawn` when empty); after a defeat it retries or returns to the last save
## (FieldBattle). Returns the recorded request (callers may adjust its party or seed at once).
static func start(
	encounter_id: StringName,
	location: StringName,
	spawn: StringName,
	flag: StringName = &"",
	escape_at: StringName = &""
) -> BattleRequest:
	var r := make(encounter_id, location, spawn, flag, escape_at)
	submit(r)
	return r


## Records `r` as the pending request and opens the field battle scene: the encounter stinger plays
## first (BattleStinger, in the field), then the router fades and builds the battle as before.
static func submit(r: BattleRequest) -> void:
	_pending = r
	var path := scene_path()
	if change_scene.is_valid():
		change_scene.call(path)
		return
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null or tree.root.get_node_or_null(^"SceneRouter") == null:
		push_error("BattleRequest: no SceneRouter to open %s" % path)
		return
	await _stinger(r.encounter)
	FlowRouting.change_scene(path)  # waits for an idle router, so the request is always opened


## The encounter stinger before the change (play_stinger, else BattleStinger.play).
static func _stinger(encounter: StringName = &"") -> void:
	if play_stinger.is_valid():
		await play_stinger.call()
		return
	await BattleStinger.play(null, encounter)


## The field battle scene (first_playable.json field_battle.scene).
static func scene_path() -> String:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_FIELD_BATTLE)
	return str(cfg.get(KEY_SCENE, DEFAULT_SCENE))


static func pending() -> BattleRequest:
	return _pending


## Returns the pending request and forgets it (FieldBattle takes it once).
static func take() -> BattleRequest:
	var r := _pending
	_pending = null
	return r


static func clear() -> void:
	_pending = null
