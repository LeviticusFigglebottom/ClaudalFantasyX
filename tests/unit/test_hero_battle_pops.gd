extends TestCase
## M2-HER-1103 / M2-HER-1110: no pops in battle. On each real hero (the HeroBattleActor wrappers, with the clips
## the characters track ships), every clip change the battle makes is sampled on every bone at 60 Hz
## (HeroMotionGuard.clip_change): no change may jump well past the two clips' own motion, and none may be a cut.
## A clip a model lacks is skipped (the clips arrive per hero from claude/characters).

const WRAPPERS := {
	&"rhen": "res://game/hero_motion/battle/rhen_battle_actor.tscn",
	&"asha": "res://game/hero_motion/battle/asha_battle_actor.tscn",
	&"toma": "res://game/hero_motion/battle/toma_battle_actor.tscn",
	&"ysolde": "res://game/hero_motion/battle/ysolde_battle_actor.tscn",
	&"liss": "res://game/hero_motion/battle/liss_battle_actor.tscn",
	&"kerrid": "res://game/hero_motion/battle/kerrid_battle_actor.tscn",
}
## The changes the battle makes: a turn's readying and its action, each one-shot's return to idle, a KO and
## its revive, and the outro.
const CHANGES: Array[Array] = [
	[&"idle", &"ready"],
	[&"ready", &"attack"],
	[&"ready", &"cast"],
	[&"ready", &"item"],
	[&"ready", &"finisher"],
	[&"idle", &"attack"],
	[&"idle", &"cast"],
	[&"idle", &"defend"],
	[&"idle", &"read"],
	[&"idle", &"hit"],
	[&"idle", &"dodge"],
	[&"idle", &"ko"],
	[&"idle", &"victory"],
	[&"attack", &"idle"],
	[&"cast", &"idle"],
	[&"item", &"idle"],
	[&"defend", &"idle"],
	[&"read", &"idle"],
	[&"finisher", &"idle"],
	[&"hit", &"idle"],
	[&"dodge", &"idle"],
	[&"hit", &"ko"],
	[&"ko", &"idle"],
	[&"ko", &"revive"],
	[&"revive", &"idle"],
	[&"victory", &"idle"],
]

## Pops already handed to their owner, as "<hero>:<from>><to>": reported, not failed, until the fix lands. Empty:
## Ysolde's placeholder finisher flip (M2-HER-1114) is handled by HeroBattleActor (short-path keys, capped fades).
const KNOWN: Array[String] = []

var made: Array[Node] = []


## Frees what the test made (each test ends with it: the runner makes a new instance per test, so a before_each
## never sees the last one's nodes).
func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_no_battle_clip_change_pops_or_cuts() -> void:
	var data := HeroMotionGuard.load_data()
	var limits := data.get("clips", {}) as Dictionary
	var dt := HeroMotionGuard.frame_sec(data)
	var checked := 0
	for hero: StringName in WRAPPERS:
		var actor := _actor(hero)
		if actor.player == null:
			continue  # its model has not reached this branch yet (HeroBattleActor.model_path)
		BattleClips.player_of(actor)  # as a battle does: placeholder clips for any the model lacks
		actor.retune()  # what the actor's next frame does
		var p := actor.player
		var skel := actor.skeleton()
		assert_true(p != null and skel != null, "%s has a player and a skeleton" % hero)
		if p == null or skel == null:
			continue
		for pair in CHANGES:
			var from: StringName = pair[0]
			var to: StringName = pair[1]
			if not (p.has_animation(from) and p.has_animation(to)):
				continue
			var r := HeroMotionGuard.clip_change(p, skel, from, to, limits, dt)
			print(
				(
					"  %s %s -> %s: blend %.2f s, peak %.3f m/frame, own %.3f, gap %.2f m, allowed %.3f%s"
					% [
						hero,
						from,
						to,
						r["blend"],
						r["peak"],
						r["own"],
						r["gap"],
						r["allowed"],
						"  POP" if r["pop"] else ""
					]
				)
			)
			if KNOWN.has("%s:%s>%s" % [hero, from, to]):
				if bool(r["pop"]):
					print("  KNOWN: %s %s -> %s" % [hero, from, to])
				continue
			assert_false(bool(r["cut"]), "%s %s -> %s cross-fades (blend %.2f s)" % [hero, from, to, r["blend"]])
			assert_false(
				bool(r["pop"]), "%s %s -> %s: %.3f m/frame, over %.3f" % [hero, from, to, r["peak"], r["allowed"]]
			)
			checked += 1
	assert_true(checked > 0, "at least one hero ships the battle clips")
	_done()


func test_the_guard_flags_a_cut_and_passes_a_blend() -> void:
	var limits := {"step_ratio": 1.5, "slack_m": 0.01, "window_sec": 0.5, "min_blend_sec": 0.04}
	var rig := _fake_rig()
	var p := rig.get_node(^"Player") as AnimationPlayer
	var skel := rig.get_node(^"Skel") as Skeleton3D
	p.playback_default_blend_time = 0.0
	var cut := HeroMotionGuard.clip_change(p, skel, &"idle", &"far", limits, 1.0 / 60.0)
	assert_true(bool(cut["cut"]), "no blend is a cut")
	assert_true(bool(cut["pop"]), "and the bone jumps a metre in a frame")
	p.set_blend_time(&"idle", &"far", 0.4)
	var eased := HeroMotionGuard.clip_change(p, skel, &"idle", &"far", limits, 1.0 / 60.0)
	assert_false(bool(eased["cut"]))
	assert_false(bool(eased["pop"]), "a 0.4 s blend moves it %.3f m a frame" % eased["peak"])
	_done()


func test_a_cut_on_a_real_hero_is_flagged() -> void:
	# Not idle -> attack: the strike clips start on the idle pose, so even a cut into one barely moves a bone.
	var data := HeroMotionGuard.load_data()
	var actor := _actor(&"rhen")
	var p := actor.player
	if not (p.has_animation(&"idle") and p.has_animation(&"victory")):
		_done()
		return
	p.set_blend_time(&"idle", &"victory", 0.0)
	p.playback_default_blend_time = 0.0
	var r := HeroMotionGuard.clip_change(
		p, actor.skeleton(), &"idle", &"victory", data["clips"] as Dictionary, HeroMotionGuard.frame_sec(data)
	)
	assert_true(bool(r["cut"]), "no cross-fade is a cut")
	assert_true(bool(r["pop"]), "Rhen's idle cut into his victory pose pops (%.3f m/frame)" % r["peak"])

## The wrapper, in the tree (its _ready tunes the player and starts idle).
	_done()


func _actor(hero: StringName) -> HeroBattleActor:
	var a := (load(WRAPPERS[hero]) as PackedScene).instantiate() as HeroBattleActor
	_add(a)
	return a


## A one-bone skeleton whose clips hold the bone still: "idle" at the origin, "far" a metre away.
func _fake_rig() -> Node3D:
	var root := Node3D.new()
	var skel := Skeleton3D.new()
	skel.name = "Skel"
	skel.add_bone("b")
	root.add_child(skel)
	var p := AnimationPlayer.new()
	p.name = "Player"
	root.add_child(p)
	var lib := AnimationLibrary.new()
	for clip: StringName in [&"idle", &"far"]:
		var a := Animation.new()
		a.length = 1.0
		a.loop_mode = Animation.LOOP_LINEAR
		var t := a.add_track(Animation.TYPE_POSITION_3D)
		a.track_set_path(t, NodePath("Skel:b"))
		var at := Vector3.ZERO if clip == &"idle" else Vector3(1.0, 0.0, 0.0)
		a.position_track_insert_key(t, 0.0, at)
		a.position_track_insert_key(t, 1.0, at)
		lib.add_animation(clip, a)
	p.add_animation_library(&"", lib)
	_add(root)
	return root


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)
