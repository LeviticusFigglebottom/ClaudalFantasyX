extends TestCase
## M3-C05-07: the Cinder Matron's Crust on the battle stage (BattlePartCues, battle_sandbox.json "part_cues"). It
## shows again when her `recrust` resolves and when a hit on her "reacted" (her quench in the Pour), and hides when
## Armor Break lands on her; each on the action's contact beat, through the real sequencer.
## enemies.json gives her no `model` yet (creatures' additive field), so the test lends her the model scene through
## CreatureModels' table for its own battles and takes it back after: the hook is ready for when the row lands.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const ENCOUNTER := &"ch05_cinder_matron"
const SEED := 20261024
const POUR := &"pour"
const MATRON := &"cinder_matron"
const MATRON_SCENE := "res://game/creatures/cinder_matron/cinder_matron_battle.tscn"

var ctl: BattleController
var matron: BattleCombatant
var crust: Node3D
var _saved_state: GameStateData
var _lent_model := false


func before_each() -> void:
	_free()


func test_the_crust_is_there_at_the_start_and_the_cue_reads_the_data() -> void:
	_start()
	assert_true(crust.visible, "she starts crusted")
	var cue: Dictionary = (BattleStage.config()["part_cues"] as Dictionary)["cinder_matron"]
	assert_eq(cue["parts"], ["Crust"])
	assert_true(ctl.stage.part_cues != null, "the stage hooked the cues to its sequencer")
	assert_true(ctl.stage.choreo.contact.is_connected(ctl.stage.part_cues.on_contact))
	_free()


func test_armor_break_landing_hides_the_crust() -> void:
	_start()
	var hero := ctl.engine.party_active[0]
	_resolve(hero.id, &"shell_breaker", [_hit({"statuses_added": [&"armor_break"]})])
	assert_false(crust.visible, "Armor Break cracks the crust off")
	assert_eq(ctl.stage.part_cues.shown[matron.id], false)
	_free()


func test_a_missed_armor_break_or_another_status_leaves_it() -> void:
	_start()
	var hero := ctl.engine.party_active[0]
	_resolve(hero.id, &"shell_breaker", [_hit({"hit": false, "statuses_added": [&"armor_break"]})])
	assert_true(crust.visible, "a miss changes nothing")
	_resolve(hero.id, &"sunder", [_hit({"statuses_added": [&"power_break"]})])
	assert_true(crust.visible, "only the statuses the data names")
	_free()


func test_recrust_resolving_shows_the_crust_again() -> void:
	_start()
	_pour()
	assert_false(crust.visible, "the Pour broke it off (the phase)")
	_resolve(matron.id, &"recrust", [_hit({"statuses_added": [&"protect"]})])
	assert_true(crust.visible, "recrust closes it again, with no phase change")
	assert_eq(ctl.stage.part_cues.shown[matron.id], true)
	_free()


func test_a_reacted_hit_shows_the_crust_again() -> void:
	_start()
	_pour()
	var hero := ctl.engine.party_active[0]
	var water := _hit({"element": "water", "amount": 10})
	var result := ActionResult.new()
	result.actor_id = hero.id
	result.skill_id = &"attack"
	result.hits.append(water)
	BossMechanics.after_action(ctl.engine, hero, {}, result)  # the engine's own reaction rule marks the hit
	assert_true(bool(water.get("reacted", false)), "water on her in the Pour reacts (enemies.json reactions)")
	ctl.engine.action_resolved.emit(result)
	assert_true(crust.visible, "the quench re-crusts her")
	_free()


func test_the_cue_waits_for_the_contact_beat() -> void:
	_start()
	ctl.pacing_scale = 1.0
	var choreo := ctl.stage.choreo
	choreo.live = false
	choreo.skip = false
	var hero := ctl.engine.party_active[0]
	_resolve(hero.id, &"shell_breaker", [_hit({"statuses_added": [&"armor_break"]})])
	assert_true(choreo.playing(), "the blow is being played")
	assert_true(crust.visible, "not before the blow lands")
	choreo.finish()
	assert_false(crust.visible, "on its contact")
	_free()


# --- helpers ----------------------------------------------------------------------------------


func _start() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	if not CreatureModels.models().has(String(MATRON)):
		CreatureModels.models()[String(MATRON)] = MATRON_SCENE
		_lent_model = true
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var reserve: Array[StringName] = []
	ctl.start_battle(active, reserve, ENCOUNTER, SEED, null)
	matron = ctl.engine.enemies[0]
	var actor := ctl.stage.stand_in(matron.id).creature()
	assert_true(actor != null and actor.creature_id == MATRON, "the Matron is her model")
	crust = actor.find_child("Crust", true, false) as Node3D
	assert_true(crust != null, "her model has a Crust")


## Puts her in the Pour, in the engine and on the stage (as phase_changed would).
func _pour() -> void:
	for i in matron.phases.size():
		if str((matron.phases[i] as Dictionary).get("id", "")) == String(POUR):
			matron.phase_index = i
	assert_eq(BossMechanics.phase_id(matron), String(POUR))
	ctl.stage.stand_in(matron.id).enter_phase(POUR)


func _hit(extra: Dictionary) -> Dictionary:
	var h := {"target_id": matron.id, "hit": true, "crit": false, "amount": 0, "statuses_added": []}
	h.merge(extra, true)
	return h


## Resolves an action through the engine's signal, so the sequencer plays it and fires its contact beat.
func _resolve(actor_id: StringName, skill_id: StringName, hits: Array[Dictionary]) -> void:
	var result := ActionResult.new()
	result.actor_id = actor_id
	result.skill_id = skill_id
	result.hits = hits
	ctl.engine.action_resolved.emit(result)


func _free() -> void:
	if ctl != null and is_instance_valid(ctl):
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		Game.state = _saved_state
	ctl = null
	if _lent_model:
		CreatureModels.models().erase(String(MATRON))
		_lent_model = false
	matron = null
	crust = null
