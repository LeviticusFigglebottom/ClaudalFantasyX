class_name FieldBattle
extends BattleController
## The battle a field zone opens (M2-FP-03; docs/kb/tech/first_playable_flow.md). field_battle.tscn
## is an inherited scene of the battle sandbox whose root uses this script, so the stage, HUD and
## controller are the sandbox's own; only the start and the way out differ:
##   start    the pending BattleRequest (BattleRequest.take() on the first start), live: the party's
##            carried HP/MP (BattleVitals), real inventory and Lattice. With no request pending it
##            falls back to the sandbox fight (battle_sandbox.json), so the scene opens on its own.
##   result   after a victory or an escape the panel offers only Return (a story fight is not
##            replayed); after a defeat it keeps Fight again (the same start, BattleVitals records
##            nothing on a defeat) and Return.
##   Return   sets the request's victory_flag (victory only, Game.set_flag) and sends the party to
##            the request's location and spawn (SceneRouter.world_return.go_to). After a defeat the
##            party returns with the vitals it had before the fight, the flag unset, so the field
##            can offer the fight again. Without a request, Return goes to the title as in the sandbox.

## {outcome: [title key, subtitle key]} for the outcomes whose panel is re-shown with Return only.
const RETURN_ONLY := {
	BattleEngine.OUTCOME_VICTORY: ["HUD_VICTORY", "HUD_VICTORY_SUB"],
	BattleEngine.OUTCOME_ESCAPED: ["HUD_ESCAPED", "HUD_ESCAPED_SUB"],
}

## The fight being played (null while the sandbox fallback runs).
var request: BattleRequest
## How Return travels: (location_id: StringName, spawn: StringName) -> bool. Unset =
## SceneRouter.world_return.go_to. Tests set a recorder.
var travel: Callable = Callable()
## True once Return has sent the party back (a second Return does nothing).
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
func return_to_field() -> bool:
	if request == null or returned or engine == null or engine.outcome == &"":
		return false
	returned = true
	if engine.outcome == BattleEngine.OUTCOME_VICTORY and request.victory_flag != &"":
		Game.set_flag(request.victory_flag)
	if travel.is_valid():
		return bool(travel.call(request.return_location, request.return_spawn))
	if not is_inside_tree():
		return false
	return SceneRouter.world_return.go_to(request.return_location, request.return_spawn)


func _show_result() -> void:
	super()
	if request == null or not RETURN_ONLY.has(engine.outcome):
		return
	var keys: Array = RETURN_ONLY[engine.outcome]
	var choices: Array[Dictionary] = [{"id": CHOICE_RETURN, "label": tr("HUD_RESULT_RETURN"), "enabled": true}]
	hud.result.show_result(engine.outcome, tr(str(keys[0])), tr(str(keys[1])), hud.result.result_rows, choices)


func _on_result_choice(choice: StringName) -> void:
	if choice == CHOICE_RETURN and request != null:
		return_to_field()
		return
	super(choice)
