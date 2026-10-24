class_name BattleClips
extends RefCounted
## The battle clip contract (M2-BPR-02; docs/kb/tech/battle_presentation.md "Clip contract"). A fighter's model
## plays a named clip when it has one: a hero actor's AnimationPlayer (M2-UI-07) or a creature actor's
## (M2-CRE-03, through its own play_clip so it idles again after). A primitive stand-in has none, and
## BattleChoreo moves it procedurally instead (lunge, recoil, collapse). Presentation only.

const IDLE := &"idle"
const READY := &"ready"
const ATTACK := &"attack"
const CAST := &"cast"
const ITEM := &"item"
const READ := &"read"
const DEFEND := &"defend"
const FINISHER := &"finisher"
const HIT := &"hit"
const DODGE := &"dodge"
const KO := &"ko"
const VICTORY := &"victory"
## Every name in the contract, in the order the doc lists them.
const ALL: Array[StringName] = [IDLE, READY, ATTACK, CAST, ITEM, READ, DEFEND, FINISHER, HIT, DODGE, KO, VICTORY]
## A creature actor plays clips through this method, so it idles again afterwards.
const ACTOR_PLAY_METHOD := &"play_clip"
## The creature track's API (M2-CRE-03, claude/creatures): FighterStandIn.creature() -> CreatureActor, with
## clip_for(skill, kind), play_action(skill, kind) and contact_time(clip). Called by name so this works before and
## after that branch merges.
const STAND_IN_CREATURE := &"creature"
const CREATURE_CLIP_FOR := &"clip_for"
const CREATURE_PLAY_ACTION := &"play_action"
const CREATURE_CONTACT := &"contact_time"


## The fighter's AnimationPlayer (the first under its model), or null for a primitive stand-in. The first time it
## finds a skinned model's player, the contract clips the model lacks get placeholders (BattlePlaceholderClips,
## M2-BPR-10; real clips always win).
static func player_of(f: Node) -> AnimationPlayer:
	if f == null or not is_instance_valid(f):
		return null
	var found := f.find_children("*", "AnimationPlayer", true, false)
	if found.is_empty():
		return null
	var p := found[0] as AnimationPlayer
	BattlePlaceholderClips.ensure(f, p)
	return p


static func has_clip(f: Node, clip: StringName) -> bool:
	var p := player_of(f)
	return p != null and p.has_animation(clip)


## Plays `clip` on the fighter's model at `speed`; false when it has no such clip (the caller moves it
## procedurally). A one-shot clip on a hero actor queues idle after it.
static func play(f: Node, clip: StringName, speed: float = 1.0) -> bool:
	if clip == &"" or not has_clip(f, clip):
		return false
	var p := player_of(f)
	var actor := p.get_parent()
	while actor != null and actor != f and not actor.has_method(ACTOR_PLAY_METHOD):
		actor = actor.get_parent()
	if actor != null and actor != f and actor.has_method(ACTOR_PLAY_METHOD):
		p.speed_scale = speed
		return bool(actor.call(ACTOR_PLAY_METHOD, clip))
	p.speed_scale = speed
	p.play(clip)
	if clip != IDLE and clip != KO and p.has_animation(IDLE):
		p.queue(IDLE)
	return true


## A felled fighter's KO on its collapse beat: true when its model has a KO clip (the stage then applies the KO
## without the procedural collapse). A hero actor plays it here and holds its last frame; a creature actor plays its
## own in its set_ko, so it is left alone.
static func play_ko(f: Node, speed: float = 1.0) -> bool:
	if not has_clip(f, KO):
		return false
	if creature_of(f) == null:
		play(f, KO, speed)
	return true


## The stage's KO state for a fighter: on a revive, a hero actor still holding its KO clip stands into idle.
static func ko_changed(f: Node, ko: bool) -> void:
	if ko or creature_of(f) != null:
		return
	var p := player_of(f)
	if p != null and p.assigned_animation == KO and p.has_animation(IDLE):
		p.play(IDLE)


## The fighter's creature actor (claude/creatures' CreatureActor), or null.
static func creature_of(f: Node) -> Node:
	if f == null or not is_instance_valid(f) or not f.has_method(STAND_IN_CREATURE):
		return null
	return f.call(STAND_IN_CREATURE) as Node


## The clip a creature plays for an action (its clip_by_skill, else clip_by_kind); "" for anything else, or when
## the creature has no such clip.
static func action_clip(f: Node, skill_id: StringName, kind: StringName) -> StringName:
	var cr := creature_of(f)
	if cr == null or not cr.has_method(CREATURE_CLIP_FOR):
		return &""
	var clip := StringName(str(cr.call(CREATURE_CLIP_FOR, skill_id, kind)))
	return clip if has_clip(f, clip) else &""


## Plays an action's strike: a creature's own clip for it, else the style's `clip` (the contract name).
static func play_action(f: Node, skill_id: StringName, kind: StringName, clip: StringName, speed: float = 1.0) -> bool:
	var cr := creature_of(f)
	if cr != null and action_clip(f, skill_id, kind) != &"":
		player_of(f).speed_scale = speed
		return bool(cr.call(CREATURE_PLAY_ACTION, skill_id, kind))
	return play(f, clip, speed)


## Seconds into `clip` where its blow lands, from the creature's data; -1 when the fighter can't say.
static func contact_sec(f: Node, clip: StringName) -> float:
	var cr := creature_of(f)
	if cr == null or not cr.has_method(CREATURE_CONTACT):
		return -1.0
	return float(cr.call(CREATURE_CONTACT, clip))
