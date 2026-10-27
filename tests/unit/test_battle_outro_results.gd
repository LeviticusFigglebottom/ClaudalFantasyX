extends TestCase
## M3-BPR-415: the victory beat hands off to the result panel. The panel waits for the real heroes' one-shot victory
## clips in full (up to outro.victory.clip_max_sec), not only the stand-ins' hop time; a scripted escape (the Reach
## survived, ADR 0100) plays the escape walk-off instead of cutting to the panel.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027
const CLIP_SEC := 2.0

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var none: Array[StringName] = []
	ctl.start_battle(active, none, &"sandbox_reef", SEED)
	ctl.stage.choreo.live = false
	ctl.stage.choreo.outro.live = false


func test_the_panel_waits_for_the_victory_pose() -> void:
	for cid: StringName in [&"rhen", &"asha"]:
		var f := ctl.stage.stand_in(cid)
		var player := BattleClips.player_of(f)
		if player == null:
			player = AnimationPlayer.new()
			player.add_animation_library(&"", AnimationLibrary.new())
			f.add_child(player)
		player.stop()  # never swap a library under a playing player (M2-HER-1114)
		var lib := player.get_animation_library(&"").duplicate(true) as AnimationLibrary  # this player's own copy
		player.remove_animation_library(&"")
		player.add_animation_library(&"", lib)
		var a := Animation.new()
		a.length = CLIP_SEC
		a.loop_mode = Animation.LOOP_NONE
		if lib.has_animation(BattleClips.VICTORY):
			lib.remove_animation(BattleClips.VICTORY)
		lib.add_animation(BattleClips.VICTORY, a)
	var outro := ctl.stage.choreo.outro
	var cap := float(outro.cfg(BattleOutro.VICTORY)["clip_max_sec"])
	assert_between(outro.clip_sec(BattleOutro.VICTORY), minf(CLIP_SEC, cap) - 0.001, minf(CLIP_SEC, cap) + 0.001)
	assert_true(outro.duration(BattleOutro.VICTORY) >= CLIP_SEC, "the panel waits for the whole pose")
	var long := ctl.stage.stand_in(&"rhen")
	BattleClips.player_of(long).get_animation(BattleClips.VICTORY).length = 9.0
	assert_between(outro.clip_sec(BattleOutro.VICTORY), cap - 0.001, cap + 0.001, "but never past the cap")
	_free()


func test_a_scripted_escape_walks_the_party_off() -> void:
	ctl.pacing_scale = 1.0
	var outro := ctl.stage.choreo.outro
	ctl.engine.battle_finished.emit(BattleEngine.OUTCOME_SCRIPTED_ESCAPE)
	assert_eq(outro.playing, BattleOutro.ESCAPE, "the party goes, as from an Escape")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
