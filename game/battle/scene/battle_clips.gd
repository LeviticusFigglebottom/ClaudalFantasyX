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


## The fighter's AnimationPlayer (the first under its model), or null for a primitive stand-in.
static func player_of(f: Node) -> AnimationPlayer:
	if f == null or not is_instance_valid(f):
		return null
	var found := f.find_children("*", "AnimationPlayer", true, false)
	return found[0] as AnimationPlayer if not found.is_empty() else null


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
