extends TestCase
## M2-HER-1103: HeroBattleActor tunes a hero battle model's AnimationPlayer (per-pair crossfades from
## battle_hero.json, the idle phase) so the existing BattleClips path crossfades each contract clip, and the
## wrapper scenes put it on Rhen, Asha and Toma.

const WRAPPERS := {
	&"rhen": "res://game/hero_motion/battle/rhen_battle_actor.tscn",
	&"asha": "res://game/hero_motion/battle/asha_battle_actor.tscn",
	&"toma": "res://game/hero_motion/battle/toma_battle_actor.tscn",
	&"ysolde": "res://game/hero_motion/battle/ysolde_battle_actor.tscn",
	&"liss": "res://game/hero_motion/battle/liss_battle_actor.tscn",
	&"kerrid": "res://game/hero_motion/battle/kerrid_battle_actor.tscn",
}
const RING := {"radius_factor": 1.4, "inner_soft_m": 0.25, "notches": 6}
## A clip in the fake player holds the body at this x for its whole length.
const X_BY_CLIP := {&"idle": 0.0, &"attack": 1.0, &"hit": 1.0, &"ko": 1.0, &"victory": 1.0}
const CLIP_SEC := 2.0
const EPS := 0.02
const FRAME_SEC := 1.0 / 60.0

var made: Array[Node] = []


## Frees what the test made (each test ends with it: the runner makes a new instance per test, so a before_each
## never sees the last one's nodes).
func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_rows_expand_any_and_a_later_named_pair_wins() -> void:
	var p := _fake().get_node(^"Player") as AnimationPlayer
	var n := HeroBattleActor.configure(
		p,
		{"default_sec": 0.25, "rows": [["*", "hit", 0.06], ["ko", "idle", 0.9], ["idle", "hit", 0.1], ["x", "idle", 1]]}
	)
	assert_eq(p.playback_default_blend_time, 0.25)
	assert_eq(n, X_BY_CLIP.size() - 1 + 1 + 1, "every other clip into hit, ko to idle, idle to hit again")
	assert_eq(p.get_blend_time(&"attack", &"hit"), 0.06)
	assert_eq(p.get_blend_time(&"idle", &"hit"), 0.1, "the named pair after the * row wins")
	assert_eq(p.get_blend_time(&"ko", &"idle"), 0.9)
	assert_eq(p.get_blend_time(&"hit", &"hit"), 0.0, "never a clip into itself")
	assert_eq(p.get_blend_time(&"attack", &"idle"), 0.0, "an unnamed pair keeps the default")
	_done()


func test_play_and_the_queued_idle_use_the_pair_blends() -> void:
	var body := _fake()
	var p := body.get_node(^"Player") as AnimationPlayer
	HeroBattleActor.configure(p, {"default_sec": 0.3, "rows": [["*", "hit", 0.06], ["ko", "idle", 0.9]]})
	p.play(&"idle")
	_run(p, 0.5)
	p.play(&"hit")
	_run(p, 0.1)
	assert_between(body.position.x, 1.0 - EPS, 1.0 + EPS, "the hit is in full after its 0.06 s blend")
	p.play(&"ko")
	_run(p, 0.5)
	p.play(&"idle")
	_run(p, 0.45)
	assert_between(body.position.x, 0.5 - 0.1, 0.5 + 0.1, "a revive is half way through its 0.9 s stand")
	p.play(&"attack")
	p.queue(&"idle")
	_run(p, CLIP_SEC + 0.15)
	assert_eq(StringName(p.current_animation), &"idle", "the one-shot went back to idle")
	assert_between(body.position.x, 0.5 - 0.1, 0.5 + 0.1, "through the default 0.3 s blend, not a pop")
	_done()


func test_the_data_reads_well() -> void:
	var data := HeroBattleActor.load_data()
	var blend := data.get("blend", {}) as Dictionary
	assert_eq(float(blend.get("default_sec", 0.0)), 0.3, "the import rule's default")
	var named := {}
	for row: Variant in blend.get("rows", []):
		var r := row as Array
		assert_eq(r.size(), 3)
		assert_true(float(r[2]) >= 0.0)
		named["%s>%s" % [r[0], r[1]]] = float(r[2])
	for clip: String in ["attack", "item", "defend"]:
		assert_true(float(named["*>" + clip]) < 0.33, "%s blends in before its contact" % clip)
	assert_true(float(named["ko>idle"]) > float(blend["default_sec"]), "a revive stands up slower than a cut")
	assert_true(float(named["*>hit"]) <= 0.1, "a hit reads on the contact")
	assert_eq(HeroBattleActor.idle_phase(data, &"asha"), 2.1)
	assert_eq(HeroBattleActor.idle_phase(data, &"nobody"), 0.0)
	_done()


func test_start_idle_wraps_its_phase() -> void:
	var p := _fake().get_node(^"Player") as AnimationPlayer
	HeroBattleActor.start_idle(p, CLIP_SEC + 0.5)
	assert_eq(StringName(p.current_animation), &"idle")
	assert_between(p.current_animation_position, 0.5 - EPS, 0.5 + EPS)
	_done()


func test_each_wrapper_tunes_its_hero_and_keeps_the_bc_path() -> void:
	var data := HeroBattleActor.load_data()
	for hero: StringName in WRAPPERS:
		var f := FighterStandIn.new()
		f.setup(hero, {"scene": WRAPPERS[hero], "height": 1.7, "yaw_deg": -90.0}, RING)
		_add(f)
		assert_true(f.has_actor(), "%s's wrapper is the actor" % hero)
		assert_true(f.actor() is HeroBattleActor)
		assert_eq(f.actor().get_meta(HeroBattleActor.META_ACTOR), hero)
		if (f.actor() as HeroBattleActor).player == null:  # its model has not landed: the stand-in's capsule shows
			assert_true(f.actor().get_node_or_null(^"StandIn") is MeshInstance3D, "%s shows a capsule meanwhile" % hero)
			continue
		var p := BattleClips.player_of(f)
		assert_true(p != null, "%s has a player" % hero)
		(f.actor() as HeroBattleActor).retune()  # its next frame does this in play (placeholder clips)
		assert_eq(StringName(p.current_animation), HeroBattleActor.IDLE, "%s idles" % hero)
		var phase := fposmod(HeroBattleActor.idle_phase(data, hero), p.get_animation(HeroBattleActor.IDLE).length)
		assert_between(p.current_animation_position, phase - EPS, phase + EPS, "%s keeps its idle phase" % hero)
		assert_false(f.actor().has_method(BattleClips.ACTOR_PLAY_METHOD), "BattleClips still queues idle itself")
		if p.has_animation(BattleClips.KO):
			assert_eq(p.get_blend_time(BattleClips.KO, BattleClips.IDLE), 0.9, "%s stands from a KO slowly" % hero)
		if p.has_animation(BattleClips.ATTACK):
			assert_true(BattleClips.play(f, BattleClips.ATTACK))
			assert_eq(Array(p.get_queue()), [BattleClips.IDLE] as Array, "%s idles after" % hero)
		assert_true((f.actor() as HeroBattleActor).skeleton() != null, "%s has a skeleton" % hero)
		assert_true(HeroMotion.micro_of(f.actor()) != null, "%s breathes (HeroIdleMicro)" % hero)

## Advances `p` by `sec` in 60 Hz steps, as frames would (a pose lands on the step after a play()).
	_done()


func _run(p: AnimationPlayer, sec: float) -> void:
	var left := sec
	while left > 0.0:
		var step := minf(left, FRAME_SEC)
		p.advance(step)
		left -= step


## A Node3D whose AnimationPlayer has one constant-x clip per X_BY_CLIP entry, in the tree.
func _fake() -> Node3D:
	var body := Node3D.new()
	var p := AnimationPlayer.new()
	p.name = "Player"
	body.add_child(p)
	var lib := AnimationLibrary.new()
	for clip: StringName in X_BY_CLIP:
		var a := Animation.new()
		a.length = CLIP_SEC
		var t := a.add_track(Animation.TYPE_POSITION_3D)
		a.track_set_path(t, NodePath("."))
		a.position_track_insert_key(t, 0.0, Vector3(float(X_BY_CLIP[clip]), 0.0, 0.0))
		a.position_track_insert_key(t, CLIP_SEC, Vector3(float(X_BY_CLIP[clip]), 0.0, 0.0))
		a.loop_mode = Animation.LOOP_LINEAR if clip == &"idle" else Animation.LOOP_NONE
		lib.add_animation(clip, a)
	p.add_animation_library(&"", lib)
	_add(body)
	return body


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)
