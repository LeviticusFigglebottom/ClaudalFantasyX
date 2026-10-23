class_name BattleRequest
extends RefCounted
## A pending field battle (M2-FP-03; docs/kb/tech/first_playable_flow.md). Field code asks for a
## fight with BattleRequest.start(); the request waits here (one at a time) while SceneRouter
## swaps to the FieldBattle scene, which takes it on _ready, plays it live, and sends the party
## back to `return_location` / `return_spawn` (setting `victory_flag` on a win).
##
##   BattleRequest.start(&"ch02_tideline", &"ch02/haluna", &"Beach", &"ch02_tideline_won")
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

var encounter: StringName = &""
var active: Array[StringName] = []
var reserve: Array[StringName] = []
var rng_seed := 0
var return_location: StringName = &""
var return_spawn: StringName = &""
## Set through Game.set_flag on a victory (never on an escape or a defeat). &"" = none.
var victory_flag: StringName = &""


## A request with the data file's party and seed; nothing is recorded or opened.
static func make(
	encounter_id: StringName, location: StringName, spawn: StringName, flag: StringName = &""
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
	return r


## Records a field battle on `encounter_id` and opens the FieldBattle scene. When it ends (victory
## or escape, or Return after a defeat) the party goes back to `location` at `spawn`; a victory
## also sets `flag`. Returns the recorded request (callers may adjust its party or seed at once).
static func start(
	encounter_id: StringName, location: StringName, spawn: StringName, flag: StringName = &""
) -> BattleRequest:
	var r := make(encounter_id, location, spawn, flag)
	submit(r)
	return r


## Records `r` as the pending request and opens the field battle scene.
static func submit(r: BattleRequest) -> void:
	_pending = r
	var path := scene_path()
	if change_scene.is_valid():
		change_scene.call(path)
		return
	var tree := Engine.get_main_loop() as SceneTree
	var router := tree.root.get_node_or_null(^"SceneRouter") if tree != null else null
	if router == null:
		push_error("BattleRequest: no SceneRouter to open %s" % path)
		return
	router.call(&"change_scene", path)


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
