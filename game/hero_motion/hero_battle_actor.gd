class_name HeroBattleActor
extends Node3D
## A hero's battle actor (M2-HER-1103, ADR 0190): the root of game/hero_motion/battle/<hero>_battle_actor.tscn,
## which instances the characters track's game/characters/heroes/<hero>_battle.tscn. FighterStandIn instances it
## (battle_sandbox.json "scene") and BattleClips plays the clip contract on its AnimationPlayer as before; this
## node only tunes that player, so the existing path picks the tuning up with no code change:
## - per-pair crossfades (AnimationPlayer blend times, game/data/hero_motion/battle_hero.json "blend"), which
##   p.play(clip) and the queued return to idle both use, placeholder clips included (retune());
## - the hero's idle phase, so the party does not breathe in step;
## - the idle micro-motion (HeroMotion.add_micro_motion, M2-HER-1104: breathing, weight shift, the head leading a
##   turn), under the model's Skeleton3D, layered after whatever clip plays.
## It does not define play_clip (BattleClips would then skip its idle queue). Presentation only.

const DATA_PATH := "res://game/data/hero_motion/battle_hero.json"
const IDLE := &"idle"
## In a blend row, every clip the model has.
const ANY := "*"
## FighterStandIn tests read this on the actor root (the characters' scene carries it too).
const META_ACTOR := &"hymn_battle_actor"

@export var hero_id: StringName = &""
## Breathing and weight shift on top of the clips (HeroIdleMicro).
@export var micro_motion := true

var player: AnimationPlayer

var _blend: Dictionary = {}
## How many clips the player had when its blends were last set.
var _tuned_clips := 0


func _ready() -> void:
	set_meta(META_ACTOR, hero_id)
	var found := find_children("*", "AnimationPlayer", true, false)
	if found.is_empty():
		push_warning("HeroBattleActor %s: no AnimationPlayer under the model" % hero_id)
		return
	player = found[0] as AnimationPlayer
	var data := load_data()
	_blend = data.get("blend", {}) as Dictionary
	# The placeholder clips for whatever the model lacks go in now, on a stopped player (BattlePlaceholderClips
	# swaps the library; under a playing player that crashes, M2-HER-1114), so BattleClips' later lookup finds them
	# installed and the blends below cover them.
	player.stop()
	BattlePlaceholderClips.ensure(self, player)
	retune()
	start_idle(player, idle_phase(data, hero_id))
	if micro_motion:
		HeroMotion.add_micro_motion(self, hero_id)


## A model missing part of the contract gets placeholder clips on BattleClips' first lookup (BattlePlaceholderClips),
## after _ready; the next frame tunes their pairs too, or a placeholder KO would stand up in a single frame.
func _process(_delta: float) -> void:
	retune()


## Sets the blends again when the player has gained clips since they were last set. Returns true when it did.
func retune() -> bool:
	if player == null or player.get_animation_list().size() == _tuned_clips:
		return false
	configure(player, _blend)
	_tuned_clips = player.get_animation_list().size()
	return true


## The model's skeleton (where an idle micro-motion modifier goes), or null.
func skeleton() -> Skeleton3D:
	var found := find_children("*", "Skeleton3D", true, false)
	return null if found.is_empty() else found[0] as Skeleton3D


static func load_data(path: String = DATA_PATH) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("HeroBattleActor: cannot read %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


## Sets `p`'s default blend and its per-pair blend times from `blend` ({default_sec, rows: [[from, to, sec]]});
## "*" expands to every clip `p` has, and a pair naming a clip it lacks is skipped. Returns the pairs set.
static func configure(p: AnimationPlayer, blend: Dictionary) -> int:
	p.playback_default_blend_time = float(blend.get("default_sec", p.playback_default_blend_time))
	var clips := p.get_animation_list()
	var count := 0
	for row: Variant in blend.get("rows", []):
		var r := row as Array
		for from: StringName in _expand(str(r[0]), clips):
			for to: StringName in _expand(str(r[1]), clips):
				if from != to:
					p.set_blend_time(from, to, float(r[2]))
					count += 1
	return count


## The clips a row's end names: every clip for "*", else that one clip if the model has it.
static func _expand(name: String, clips: PackedStringArray) -> Array[StringName]:
	var out: Array[StringName] = []
	for c in clips:
		if name == ANY or c == name:
			out.append(StringName(c))
	return out


## Seconds into the idle loop `hero` starts at (0 when the data names none).
static func idle_phase(data: Dictionary, hero: StringName) -> float:
	return float((data.get("idle_phase_sec", {}) as Dictionary).get(String(hero), 0.0))


## Plays idle from `phase` seconds (wrapped to the loop) with no blend: the battle's first frame.
static func start_idle(p: AnimationPlayer, phase: float) -> void:
	if not p.has_animation(IDLE):
		return
	var length := p.get_animation(IDLE).length
	p.play(IDLE, 0.0)
	if length > 0.0:
		p.seek(fposmod(phase, length), true)
