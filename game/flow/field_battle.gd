class_name FieldBattle
extends BattleController
## The battle a field zone opens (M2-FP-03; docs/kb/tech/first_playable_flow.md). field_battle.tscn
## is an inherited scene of the battle sandbox whose root uses this script, so the stage, HUD and
## controller are the sandbox's own; only the start and the way out differ:
##   start    the pending BattleRequest (BattleRequest.take() on the first start), live: the party's
##            carried HP/MP (BattleVitals), real inventory and Lattice. With no request pending it
##            falls back to the sandbox fight (battle_sandbox.json), so the scene opens on its own.
##   result   after a victory, an escape or a scripted escape (M3-CMB-01) the panel offers only
##            Return (a story fight is not replayed); after a defeat (M2-FP-05) it offers Fight again (the same start,
##            BattleVitals records nothing on a defeat) and Return to last save.
##   Return   sets the request's victory_flag (victory only, Game.set_flag) and sends the party to
##            the request's location and spawn (SceneRouter.world_return.go_to); a set piece's
##            objective_flag becomes objective_start + engine.objective_count (M3-C08-02: Ch8's
##            stair meter), and "Fight again" puts it back to objective_start; after an escape,
##            to the request's escape_spawn when it names one (Haluna: BeforeBattle, the beach side
##            of the trigger). A defeat never returns to the field, so a field trigger cannot be
##            walked past by losing. Without a request, Return goes to the title as in the sandbox.
##   Return to last save (defeat only) loads the newest readable save record, autosave included,
##            exactly as the title's Continue does (TitleSaveEntry.continue_game), and goes where
##            it continues; with no record it goes to the title. The row reads "Return to title"
##            then, so the player knows which it is before choosing.

## {outcome: [title key, subtitle key]} for the outcomes whose panel is re-shown with Return only.
const RETURN_ONLY := {
	BattleEngine.OUTCOME_VICTORY: ["HUD_VICTORY", "HUD_VICTORY_SUB"],
	BattleEngine.OUTCOME_ESCAPED: ["HUD_ESCAPED", "HUD_ESCAPED_SUB"],
	BattleEngine.OUTCOME_SCRIPTED_ESCAPE: ["HUD_SCRIPTED_ESCAPE", "HUD_SCRIPTED_ESCAPE_SUB"],
}

## Defeat row: load the newest save record (or go to the title when there is none).
const CHOICE_LAST_SAVE := &"last_save"
const KEY_LAST_SAVE := "FLOW_RESULT_LAST_SAVE"
const KEY_TO_TITLE := "FLOW_RESULT_TITLE"

## The fight being played (null while the sandbox fallback runs).
var request: BattleRequest
## How Return travels: (location_id: StringName, spawn: StringName) -> bool. Unset =
## SceneRouter.world_return.go_to. Tests set a recorder.
var travel: Callable = Callable()
## How a scene is opened instead of travelling (the title after a defeat with no record, or the
## request's return_scene): (scene_path: String). Unset = SceneRouter.change_scene. Tests record.
var open_title: Callable = Callable()
## Where save records are read (null = the SaveSystem autoload). Tests pass their own.
var save_system: Node
## True once Return (or Return to last save) has sent the party on (a second one does nothing).
var returned := false


## Starts the pending request (or the one already set on `request`); the sandbox fight otherwise.
func start_sandbox(rng_seed: int = -1, staged: bool = false) -> void:
	if request == null:
		request = BattleRequest.take()
	if request == null:
		await super(rng_seed, staged)
		return
	await start_request(request, rng_seed, staged)


## Starts `r` live. `rng_seed` < 0 uses the request's seed. `staged` spreads the build over frames
## behind the router's fade (start_battle_staged); await it to know when it is done.
func start_request(r: BattleRequest, rng_seed: int = -1, staged: bool = false) -> void:
	request = r
	returned = false
	fixture = null
	var s := r.rng_seed if rng_seed < 0 else rng_seed
	items = _live_items()
	var lattice := BattleStage.lattice_for(r.active + r.reserve, Game.state.lattice if persist_progress else {})
	if not staged:
		start_battle(r.active, r.reserve, r.encounter, s, lattice)
		return
	building = true
	await _wait_frame()
	await start_battle_staged(r.active, r.reserve, r.encounter, s, lattice)


## Ends the field battle: sets the victory flag after a win and sends the party back to the
## request's location and spawn. Returns false when there is nothing to return to, or once done.
## A defeat never returns to the field (see return_to_last_save).
func return_to_field() -> bool:
	if request == null or returned or engine == null or engine.outcome == &"":
		return false
	if engine.outcome == BattleEngine.OUTCOME_DEFEAT:
		return false
	returned = true
	if engine.outcome in BattleSpoils.SPOILS_OUTCOMES and request.victory_flag != &"":
		Game.set_flag(request.victory_flag)  # a set piece's scripted escape is its win (M3-CMB-01)
	if engine.outcome in BattleSpoils.SPOILS_OUTCOMES and request.objective_flag != &"":
		Game.set_flag(request.objective_flag, request.objective_start + engine.objective_count)
	if request.return_scene != "":
		_open_scene(request.return_scene)
		return true
	var spawn := request.return_spawn
	if engine.outcome == BattleEngine.OUTCOME_ESCAPED and request.escape_spawn != &"":
		spawn = request.escape_spawn
	return _travel(request.return_location, spawn)


## After a defeat: loads the newest readable save record into Game.state (TitleSaveEntry, as the
## title's Continue) and sends the party where it continues. In the game WorldReturn is armed and
## does that itself on EventBus.game_loaded; when it is not (a scene opened on its own, tests), this
## travels to WorldReturn.resolve(Game.state). With no record it opens the title. Returns OK, or why
## no record was loaded (the title is opened then); ERR_UNAVAILABLE when not after a defeat, or once
## done.
func return_to_last_save() -> Error:
	if returned or engine == null or engine.outcome != BattleEngine.OUTCOME_DEFEAT:
		return ERR_UNAVAILABLE
	returned = true
	var err := TitleSaveEntry.continue_game(save_system)
	if err != OK:
		_open_title()
		return err
	var wr := _world_return()
	if wr != null and not wr.enabled:
		var to := wr.resolve(Game.state)
		if not to.is_empty():
			_travel(StringName(str(to[LocationRegistry.KEY_LOCATION])), StringName(str(to[LocationRegistry.KEY_SPAWN])))
	return OK


## True when a save record exists for Return to last save (else it goes to the title).
func has_last_save() -> bool:
	return TitleSaveEntry.can_continue(save_system)


func _travel(location_id: StringName, spawn: StringName) -> bool:
	if travel.is_valid():
		return bool(travel.call(location_id, spawn))
	if not is_inside_tree():
		return false
	FlowRouting.go_to(location_id, spawn)  # waits for an idle router, so the change is never lost
	return true


func _open_title() -> void:
	_open_scene(RETURN_SCENE)


## Opens `path` through the router (tests record it through the `open_title` hook).
func _open_scene(path: String) -> void:
	if open_title.is_valid():
		open_title.call(path)
	elif is_inside_tree():
		FlowRouting.change_scene(path)


func _world_return() -> WorldReturn:
	if not is_inside_tree():
		return null
	return SceneRouter.world_return


func _show_result() -> void:
	super()
	if request == null:
		return
	if engine.outcome == BattleEngine.OUTCOME_DEFEAT:
		var back := KEY_LAST_SAVE if has_last_save() else KEY_TO_TITLE
		var rows: Array[Dictionary] = [
			{"id": CHOICE_RETRY, "label": tr("HUD_RESULT_RETRY"), "enabled": true},
			{"id": CHOICE_LAST_SAVE, "label": tr(back), "enabled": true},
		]
		hud.result.show_result(engine.outcome, tr("HUD_DEFEAT"), tr("HUD_DEFEAT_SUB"), hud.result.result_rows, rows)
		return
	if not RETURN_ONLY.has(engine.outcome):
		return
	_prepare_return()
	var keys: Array = RETURN_ONLY[engine.outcome]
	var title := str(keys[0])
	if engine.outcome in BattleSpoils.SPOILS_OUTCOMES:
		title = BattleMenus.victory_title_key(engine)  # "The Inquisitor yields." (M3-C06-02)
	var choices: Array[Dictionary] = [{"id": CHOICE_RETURN, "label": tr("HUD_RESULT_RETURN"), "enabled": true}]
	hud.result.show_result(engine.outcome, tr(title), tr(str(keys[1])), hud.result.result_rows, choices)


## While the result panel shows, the return's destination starts loading (ResidentLoads.prepare_return; not the
## resident field, not in a headless run).
func _prepare_return() -> void:
	var loads := ResidentLoads.shared()
	if (
		loads == null
		or not is_inside_tree()
		or (DisplayServer.get_name() == "headless" and not ResidentLoads.run_headless)
	):
		return
	loads.prepare_return(request, SceneRouter.resident_path())


func _on_result_choice(choice: StringName) -> void:
	if choice == CHOICE_RETRY and request != null and request.objective_flag != &"":
		Game.set_flag(request.objective_flag, request.objective_start)  # the meter as the fight began
	if choice == CHOICE_RETURN and request != null:
		return_to_field()
		return
	if choice == CHOICE_LAST_SAVE and request != null:
		return_to_last_save()
		return
	super(choice)
