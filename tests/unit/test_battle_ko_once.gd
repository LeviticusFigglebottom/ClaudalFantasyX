extends TestCase
## M2-BPR-11 (the human's playtest, 2026-10-24): a felled foe's KO plays once, it fades out and is hidden, and later
## actions never replay it. The stage re-applies every fighter's stone and KO state after every action; a creature
## actor used to restart its finished KO clip on each of those (CreatureActor.set_frozen(false) called play()).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const LATER_ACTIONS := 3

var ctl: BattleController
var ko_starts := 0


func test_a_creature_foe_plays_its_ko_once_then_fades_out() -> void:
	_start(&"sandbox_reef")
	var foe := _first_foe()
	var f := ctl.stage.stand_in(foe.id)
	var cr := BattleClips.creature_of(f) as CreatureActor
	assert_true(cr != null, "the sandbox's foes are creature models")
	var player := BattleClips.player_of(f)
	player.animation_started.connect(_on_started)
	_fell(foe)
	assert_eq(ko_starts, 1, "the KO clip starts once")
	player.advance(cr.clip_length(BattleClips.KO) + 0.1)  # the clip plays out and holds its last frame
	assert_false(player.is_playing(), "held on its last frame")
	if cr._fade != null and cr._fade.is_valid():
		cr._fade.custom_step(60.0)  # the fade runs out
	_act_later()
	assert_eq(ko_starts, 1, "later actions never replay the KO")
	assert_false(player.is_playing(), "still held, not restarted")
	assert_false(cr.visible, "a fallen foe fades out and is hidden")
	assert_false(cr.play_clip(BattleClips.HIT), "a fallen foe plays nothing")
	_free()


func test_a_primitive_foe_falls_once_and_is_hidden() -> void:
	_start(&"ch01_underway_shoals")
	var foe := _first_foe()
	var f := ctl.stage.stand_in(foe.id)
	assert_true(BattleClips.creature_of(f) == null, "wickfry has no model: a primitive stand-in")
	_fell(foe)
	var body: Node3D = f._body
	var fallen := f.transform
	assert_false(body.visible, "a fallen foe is hidden")
	_act_later()
	assert_false(body.visible, "and stays hidden")
	assert_true(f.transform.is_equal_approx(fallen), "it never collapses again")
	_free()


func test_a_fallen_party_member_stays_faint_to_be_revived() -> void:
	_start(&"sandbox_reef")
	var rhen := ctl.engine.find(&"rhen")
	rhen.hp = 0
	ctl.stage.refresh_ko(ctl.engine)
	var body: Node3D = ctl.stage.stand_in(&"rhen")._body
	assert_true(body.visible, "the party keeps its ghost (battle_sandbox.json ko_alpha)")
	_free()


func test_a_revived_foe_shows_again() -> void:
	_start(&"sandbox_reef")
	var foe := _first_foe()
	var cr := BattleClips.creature_of(ctl.stage.stand_in(foe.id)) as CreatureActor
	cr.set_ko(true, 0.0)
	if cr._fade != null and cr._fade.is_valid():
		cr._fade.custom_step(60.0)
	assert_false(cr.visible)
	cr.set_ko(false, 0.0)
	assert_true(cr.visible, "a revive brings it back")
	_free()


func test_petrify_still_pauses_and_resumes_a_clip() -> void:
	_start(&"sandbox_reef")
	var cr := BattleClips.creature_of(ctl.stage.stand_in(_first_foe().id)) as CreatureActor
	var player := BattleClips.player_of(ctl.stage.stand_in(_first_foe().id))
	assert_true(cr.play_clip(BattleClips.ATTACK))
	cr.set_frozen(true)
	assert_false(player.is_playing(), "Petrify stops the clip where it is")
	cr.set_frozen(false)
	assert_true(player.is_playing(), "and it carries on after")
	_free()


## A revived hero stands up through its `revive` clip when it has one (characters' review), else straight to idle.
func test_a_revived_hero_stands_up_through_its_revive_clip() -> void:
	_start(&"sandbox_reef")
	for with_revive: bool in [true, false]:
		var f := Node3D.new()
		var player := AnimationPlayer.new()
		var lib := AnimationLibrary.new()
		var clips: Array[StringName] = [BattleClips.IDLE, BattleClips.KO]
		if with_revive:
			clips.append(BattleClips.REVIVE)
		for clip in clips:
			var a := Animation.new()
			a.length = 0.8
			lib.add_animation(clip, a)
		player.add_animation_library(&"", lib)
		f.add_child(player)
		ctl.add_child(f)
		assert_true(BattleClips.play_ko(f))
		BattleClips.ko_changed(f, false)
		var want := BattleClips.REVIVE if with_revive else BattleClips.IDLE
		assert_eq(str(player.current_animation), str(want), "stands up (revive clip: %s)" % with_revive)
		if with_revive:
			assert_eq(str(player.get_queue()), str([BattleClips.IDLE]), "then idles")
		f.free()
	_free()


func _on_started(clip: StringName) -> void:
	if clip == BattleClips.KO:
		ko_starts += 1


func _start(encounter: StringName) -> void:
	ko_starts = 0
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = []
	ctl.start_battle(active, reserve, encounter, SEED)
	ctl.stage.choreo.live = false


func _first_foe() -> BattleCombatant:
	return ctl.engine.enemies[0]


## The party fells `foe` with one blow on its next turn.
func _fell(foe: BattleCombatant) -> void:
	var guard := 0
	while ctl.engine.enemies.has(ctl.engine.current) and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	foe.hp = 1
	ctl.act(&"attack", [foe.id])
	assert_eq(foe.hp, 0, "felled")


## Three more actions by whoever is next (the party and the other foes).
func _act_later() -> void:
	for i in LATER_ACTIONS:
		var foes := ctl.engine.living_foes_of(ctl.engine.current)
		assert_false(foes.is_empty(), "the battle goes on")
		ctl.act(&"attack", [foes[0].id])


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
