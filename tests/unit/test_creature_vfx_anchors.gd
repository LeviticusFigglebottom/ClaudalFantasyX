extends TestCase
## M3-CRE-651: spawn and death VFX hooks. Every Act I regular (ADR 0041) names a `core` bone, and most a `wound` bone,
## in creatures.json `vfx_anchors`; CreatureActor.vfx_anchor() gives their world positions, on the body, following the
## clip playing. A row without a wound falls back to its core; a row without anchors answers Vector3.INF.

const DIR := "res://game/creatures/%s/%s_battle.tscn"
## The regulars (tools/tests/test_creatures.py ACT1_REGULARS); wickfry fights as the glassfry model.
const REGULARS: Array[String] = [
	"ashwing",
	"flue_moth",
	"gull_harrier",
	"lantern_eel",
	"oil_slug",
	"raid_hound",
	"reef_crab",
	"sail_leech",
	"scuttler",
	"shoal_skipper",
	"slag_tortoise",
	"squall_wing",
	"stormgull",
	"tide_crawler",
	"tower_limpet",
	"vein_sparker",
	"wall_polyp",
	"wallcrab",
	"glassfry",
	"wreck_crab",
]
## An anchor sits on the body: within this distance of the actor's origin (the largest regular, the gull harrier with
## its hover, stays well inside it).
const BODY_REACH_M := 3.0
## How far into the attack the anchors are read again, and how far the core of a creature that lunges moves by then.
const ATTACK_SEC := 0.4
const MOVED_M := 0.005

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func _actor(id: String) -> CreatureActor:
	var a := (load(DIR % [id, id]) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


func test_every_regular_has_its_anchors_on_its_body() -> void:
	for id in REGULARS:
		var a := _actor(id)
		var core := a.vfx_anchor(CreatureActor.ANCHOR_CORE)
		var wound := a.vfx_anchor(CreatureActor.ANCHOR_WOUND)
		assert_true(core != Vector3.INF, "%s has a core" % id)
		assert_true(wound != Vector3.INF, "%s has a wound (or falls back to its core)" % id)
		assert_true(core.distance_to(a.global_position) < BODY_REACH_M, "%s's core is on its body" % id)
		assert_true(wound.distance_to(a.global_position) < BODY_REACH_M, "%s's wound is on its body" % id)
	before_each()


func test_a_row_without_a_wound_uses_its_core() -> void:
	var a := _actor("flue_moth")
	if not (CreatureActor.row_for(&"flue_moth").get("vfx_anchors", {}) as Dictionary).has("wound"):
		assert_eq(a.vfx_anchor(CreatureActor.ANCHOR_WOUND), a.vfx_anchor(CreatureActor.ANCHOR_CORE))
	assert_eq(a.vfx_anchor(&"nowhere"), Vector3.INF, "an anchor the row doesn't name")
	before_each()


func test_the_anchor_follows_the_clip() -> void:
	var a := _actor("raid_hound")
	var rest := a.vfx_anchor(CreatureActor.ANCHOR_CORE)
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.play(&"attack", 0.0)  # no blend from the idle: the seek lands on the attack's own pose
	player.seek(ATTACK_SEC, true)
	player.advance(0.0)
	var lunge := a.vfx_anchor(CreatureActor.ANCHOR_CORE)
	assert_true(rest.distance_to(lunge) > MOVED_M, "the hound's chest moves with its lunge")
	before_each()


## M3-HER-1142: a GreyboxZone stage actor's `model` can be a creature (the raid hound in Brine Shoals): the stage
## plays it through HeroMotion like a villager body, with no script error.
func test_a_creature_plays_as_a_field_stage_model() -> void:
	var body := _actor("raid_hound")
	assert_true(HeroMotion.play(body, &"idle", 0.0), "HeroMotion plays its idle")
	assert_true(HeroMotion.add_micro_motion(body, &"hound") != null, "and breathes")
	before_each()


## big14 gate: a foe whose enemies.json row names no `model` still gets its creatures.json row's scene of the same id
## (cord_moth), so a built creature never fights as a capsule.
func test_a_foe_without_a_model_line_uses_its_creature_row() -> void:
	var spec := CreatureModels.stand_in_overrides("cord_moth")
	assert_eq(str(spec.get("scene", "")), "res://game/creatures/cord_moth/cord_moth_battle.tscn")
	assert_eq(CreatureModels.stand_in_overrides("no_such_foe"), {}, "and a foe with neither has none")
	before_each()
