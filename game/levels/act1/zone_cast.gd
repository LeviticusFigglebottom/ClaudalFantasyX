class_name ZoneCast
extends Node
## Puts the villager models on an Act I greybox zone's stage actors (queue item "real casts"; ADR 0200's
## companion for people). A child of a GreyboxZone root, instanced in the zone's .tscn as `Cast`. The zone builds
## its stage in _enter_tree, so the actors exist when this node is ready.
##
## A stage actor row in the zone layout may name a villager: `"cast": "<villager>"` loads
## `assets/characters/villagers/<villager>/<villager>_actor.tscn` (the model turned to face the actor's -Z, as the
## cutscene sequencer turns actors) as the actor's child `Cast`, and hides its capsule. The villager's AnimationPlayer
## plays `idle` from a phase of its own (a hash of the actor id, as FieldNpc does), with HeroIdleMicro's breathing
## and weight shift on top, so two villagers never move in step; the cutscene's `@anim` lines find the same player.
## Heroes are not cast here: HeroFieldActor.attach_stage gives the hero actors their bodies (hero-integration).

const VILLAGER_SCENE := "res://assets/characters/villagers/%s/%s_actor.tscn"
const KEY_CAST := "cast"
const CAST := &"Cast"
const STAND_IN := &"StandIn"
const CLIP_IDLE := &"idle"
const SALT_IDLE := "idle_clip"

var zone: GreyboxZone
## Actor id -> its villager model.
var cast: Dictionary = {}


func _ready() -> void:
	zone = get_parent() as GreyboxZone
	if zone == null or zone.stage == null:
		push_warning("ZoneCast: not under a built GreyboxZone")
		return
	var rows: Dictionary = zone.layout.get("actors", {})
	for id: String in rows.keys():
		var villager := str((rows[id] as Dictionary).get(KEY_CAST, ""))
		if villager != "":
			cast_actor(StringName(id), villager)


## Puts `villager` on the stage actor `id` and starts its idle; returns the model, or null when either is missing.
func cast_actor(id: StringName, villager: String) -> Node3D:
	var actor := zone.stage.actor(id)
	var path := scene_path(villager)
	if actor == null or path == "":
		push_warning("ZoneCast %s: cannot cast '%s' as %s" % [zone.location_id, villager, id])
		return null
	var model := (load(path) as PackedScene).instantiate() as Node3D
	model.name = CAST
	actor.add_child(model)
	var stand_in := actor.get_node_or_null(NodePath(String(STAND_IN))) as Node3D
	if stand_in != null:
		stand_in.visible = false
	var anim := HeroMotion.player_of(model)
	if anim != null and anim.has_animation(CLIP_IDLE):
		anim.play(CLIP_IDLE)
		anim.seek(HeroIdleMicro.share(id, SALT_IDLE) * anim.get_animation(CLIP_IDLE).length, true)
	HeroMotion.add_micro_motion(model, id)
	cast[id] = model
	return model


## The villager's actor scene, or "" when there is none.
static func scene_path(villager: String) -> String:
	var path := VILLAGER_SCENE % [villager, villager]
	return path if ResourceLoader.exists(path) else ""
