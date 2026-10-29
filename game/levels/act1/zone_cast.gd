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
## Two prefixes name other bodies: `"cast": "creature:<id>"` puts the creature's model (game/data/creatures/
## creatures.json `scene`, which faces +Z) on the actor, turned to its -Z, idling (the raid hound, the Cinder
## Matron); `"cast": "hero:<id>"` gives an actor whose id isn't the hero's own (Ch9's `vigil_asha`) that hero's
## field body (HeroFieldActor), nothing when the hero has none yet. A row's `"cast_still": true` holds the body on its
## idle's first frame with no breathing (Coilspire's Virel in the binding's F07: "perfectly still").

const VILLAGER_SCENE := "res://assets/characters/villagers/%s/%s_actor.tscn"
const CREATURES_PATH := "res://game/data/creatures/creatures.json"
const PREFIX_CREATURE := "creature:"
const PREFIX_HERO := "hero:"
const KEY_CAST := "cast"
const KEY_STILL := "cast_still"
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
		var row := rows[id] as Dictionary
		var villager := str(row.get(KEY_CAST, ""))
		if villager != "":
			shape(cast_actor(StringName(id), villager), row)


## Puts `villager` (or a "creature:" / "hero:" body) on the stage actor `id` and starts its idle; returns the
## model, or null when either is missing.
func cast_actor(id: StringName, villager: String) -> Node3D:
	var actor := zone.stage.actor(id)
	if actor != null and villager.begins_with(PREFIX_HERO):
		var body := HeroFieldActor.attach_actor(actor, StringName(villager.trim_prefix(PREFIX_HERO)))
		if body != null:
			cast[id] = body
		return body
	var path := scene_path(villager)
	if actor == null or path == "":
		push_warning("ZoneCast %s: cannot cast '%s' as %s" % [zone.location_id, villager, id])
		return null
	var model := (load(path) as PackedScene).instantiate() as Node3D
	model.name = CAST
	if villager.begins_with(PREFIX_CREATURE):
		model.rotation.y = PI  # a creature's model faces +Z; an actor faces its -Z
		# the battle root (CreatureActor) answers the battle's play_clip; a cutscene drives the AnimationPlayer
		model.set_script(null)
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


## Applies a layout row's `cast_still` to a cast body (null: nothing to shape).
static func shape(model: Node3D, row: Dictionary) -> void:
	if model == null:
		return
	if bool(row.get(KEY_STILL, false)):
		var micro := HeroMotion.micro_of(model)
		if micro != null:
			micro.active = false  # kept, inactive: the sequencer's add_micro_motion finds it and adds no other
		var anim := HeroMotion.player_of(model)
		if anim != null and anim.has_animation(CLIP_IDLE):
			anim.play(CLIP_IDLE)
			anim.seek(0.0, true)
			anim.pause()


## The villager's actor scene (or a "creature:" id's model scene), or "" when there is none. A "hero:" cast has no
## scene of its own (HeroFieldActor.scene_path).
static func scene_path(villager: String) -> String:
	if villager.begins_with(PREFIX_HERO):
		return HeroFieldActor.scene_path(StringName(villager.trim_prefix(PREFIX_HERO)))
	var path := VILLAGER_SCENE % [villager, villager]
	if villager.begins_with(PREFIX_CREATURE):
		var rows: Dictionary = GreyboxZone.read_json(CREATURES_PATH).get("creatures", {})
		path = str((rows.get(villager.trim_prefix(PREFIX_CREATURE), {}) as Dictionary).get("scene", ""))
	return path if path != "" and ResourceLoader.exists(path) else ""
