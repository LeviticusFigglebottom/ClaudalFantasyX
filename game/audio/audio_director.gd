class_name AudioDirector
extends Node
## The game's audio runtime, the `Audio` autoload (M2-AUD-02; ADR 0031; docs/kb/tech/audio_runtime.md).
##
## - **Buses** from game/data/audio/mix.json, built on start when missing (mix.md §4).
## - **Music:** a MusicDeck (crossfades, stems, resume points). Zone music and ambience beds come from music.json
##   and switch on SceneRouter.scene_swapping, under the router's opaque fade; a scene run on its own gets its row
##   on the first frame.
## - **SFX:** play_sfx(id) / play_sfx_at(id, position) from sfx.json (SfxBank).
## - **Listen-only hooks.** Other roles' scenes are never edited: when their nodes enter the tree, this routes
##   them. The cutscene sequencer's music and @sfx players go to the Music and SFX buses, and the zone bed holds
##   while the sequencer's music plays; a DialogueBox's blip goes to Voice and an open box ducks the music; a
##   battle (BattleVfx under a BattleController) gets a BattleAudio listener (battle_audio.gd) and ducks the
##   ambience; the Shell Shrine level gets a ShrineAudio listener (shrine_audio.gd). Listeners live under this
##   node, not in the other scene's tree, and never write game state.
## Time passes only through advance(delta), which _process calls; tests call it directly.

signal zone_applied(scene_path: String, row: Dictionary)

const REASON_DIALOGUE := &"dialogue"
const REASON_BATTLE := &"battle"
const SEQ_MUSIC_NODE := &"Music"
const BLIP_NODE := &"Blip"
## How fast the zone bed gives way when a cutscene's music starts (s).
const CUTSCENE_TAKE_SEC := 0.5

var mix: Dictionary = {}
var music_data: Dictionary = {}
var music: MusicDeck
var sfx: SfxBank
## Ambience bed id -> FadeVoice.
var beds: Dictionary = {}
## The zone row applied last ({} for none) and its scene.
var zone: Dictionary = {}
var zone_path: String = ""
## Active duck reasons (reason -> true), and each bus's duck offset now (dB).
var ducks: Dictionary = {}
var bus_duck_db: Dictionary = {}
## The player's volume per bus (dB, M2-AUD-06 settings; 0 by default).
var user_db: Dictionary = {}
## (flag) -> bool; Game.get_flag unless a test sets it.
var flag_reader: Callable = Callable()
## Battle and shrine listeners (children of this node), by the scene node they listen to.
var listeners: Dictionary = {}
var _seq_players: Array[AudioStreamPlayer] = []
var _boxes: Array[CanvasItem] = []
var _battles: Array[Node] = []
var _seen_seq_music := false
var _seen_box_open := false
var _seen_battle := false


func _ready() -> void:
	setup(AudioData.table(AudioData.MIX), AudioData.table(AudioData.MUSIC), AudioData.table(AudioData.SFX))
	get_tree().node_added.connect(_on_node_added)
	var router := get_node_or_null(^"/root/SceneRouter")
	if router != null and router.has_signal(&"scene_swapping"):
		router.connect(&"scene_swapping", apply_zone)
	_apply_first_scene.call_deferred()


## Builds the buses, the deck and the bank from the tables (tests call it with their own).
func setup(mix_table: Dictionary, music_table: Dictionary, sfx_table: Dictionary) -> void:
	mix = mix_table
	music_data = music_table
	build_buses(mix)
	if music == null:
		music = MusicDeck.new()
		music.name = "Music"
		add_child(music)
	music.floor_db = float(music_cfg().get("floor_db", -60.0))
	if sfx == null:
		sfx = SfxBank.new()
		sfx.name = "Sfx"
		add_child(sfx)
	sfx.rows = sfx_table.get("sfx", {}) as Dictionary


func _process(delta: float) -> void:
	advance(delta)


func advance(delta: float) -> void:
	_poll_hooks()
	music.advance(delta)
	for bed: FadeVoice in beds.values():
		bed.step(delta, music.floor_db)
	_step_ducks(delta)


# --------------------------------------------------------------------------- music


## Plays music cue `cue_id` (music.json) with a crossfade of `sec` (< 0: mix.json's crossfade_sec).
## `silence` fades the bed out. False when the cue is unknown or its files are missing.
func play_music(cue_id: StringName, sec: float = -1.0) -> bool:
	var fade := float(music_cfg().get("crossfade_sec", 0.0)) if sec < 0.0 else sec
	if cue_id == AudioData.SILENCE or cue_id == &"":
		music.stop(fade)
		return true
	var row := AudioData.cue(music_data, cue_id)
	if row.is_empty():
		return false
	return music.play(cue_id, row, fade)


func stop_music(sec: float = -1.0) -> void:
	play_music(AudioData.SILENCE, sec)


## Applies the zone row for `scene_path` (SceneRouter.scene_swapping calls this under the fade).
func apply_zone(scene_path: String) -> void:
	zone_path = scene_path
	zone = AudioData.zone_for(music_data, scene_path, _flag_reader())
	if zone.is_empty():
		zone_applied.emit(scene_path, zone)
		return
	if zone.has("music"):
		play_music(StringName(str(zone["music"])))
	if zone.has("ambience"):
		var ids: Array[StringName] = []
		for a: Variant in zone["ambience"]:
			ids.append(StringName(str(a)))
		set_ambience(ids)
	zone_applied.emit(scene_path, zone)


## The ambience beds that play now: these ids fade in (music.json ambience rows), the others fade out.
func set_ambience(ids: Array[StringName], sec: float = -1.0) -> void:
	var fade := float(music_cfg().get("crossfade_sec", 0.0)) if sec < 0.0 else sec
	for id: StringName in beds.keys():
		if not ids.has(id):
			(beds[id] as FadeVoice).fade_to(0.0, fade)
	for id in ids:
		var row := (music_data.get("ambience", {}) as Dictionary).get(String(id), {}) as Dictionary
		var bed := beds.get(id) as FadeVoice
		if bed == null:
			var stream := MusicDeck.build_stream(row)
			if stream == null:
				continue
			var p := AudioStreamPlayer.new()
			p.name = "Bed_%s" % id
			p.bus = StringName(str(row.get("bus", "Ambience")))
			p.stream = stream
			add_child(p)
			bed = FadeVoice.new(p)
			bed.id = id
			bed.base_db = float(row.get("volume_db", 0.0))
			beds[id] = bed
		if not (bed.player as AudioStreamPlayer).playing:
			(bed.player as AudioStreamPlayer).play()
		bed.fade_to(1.0, fade)


# --------------------------------------------------------------------------- sfx


func play_sfx(id: StringName, opts: Dictionary = {}) -> AudioStreamPlayer:
	return sfx.play(id, opts)


func play_sfx_at(id: StringName, at: Vector3, opts: Dictionary = {}) -> AudioStreamPlayer3D:
	return sfx.play_at(id, at, opts)


# --------------------------------------------------------------------------- buses and ducks


## Creates mix.json's buses that are missing (in order, each sending to its `send`) and Master's limiter.
static func build_buses(mix_table: Dictionary) -> void:
	for row: Variant in mix_table.get("buses", []):
		var name := StringName(str((row as Dictionary).get("name", "")))
		if name == &"" or AudioServer.get_bus_index(name) >= 0:
			continue
		AudioServer.add_bus()
		var idx := AudioServer.bus_count - 1
		AudioServer.set_bus_name(idx, name)
		AudioServer.set_bus_send(idx, StringName(str((row as Dictionary).get("send", "Master"))))
	var lim := mix_table.get("master_limiter", {}) as Dictionary
	if lim.is_empty():
		return
	for i in AudioServer.get_bus_effect_count(0):
		if AudioServer.get_bus_effect(0, i) is AudioEffectHardLimiter:
			return
	var fx := AudioEffectHardLimiter.new()
	fx.ceiling_db = float(lim.get("ceiling_db", -1.0))
	fx.pre_gain_db = 0.0
	AudioServer.add_bus_effect(0, fx)


## Turns duck `reason` (mix.json ducks) on or off; it ramps in advance().
func set_duck(reason: StringName, on: bool) -> void:
	if on:
		ducks[reason] = true
	else:
		ducks.erase(reason)


## The duck offset (dB) mix.json asks for on `bus` with the active reasons.
func duck_target_db(bus: StringName) -> float:
	var db := 0.0
	for reason: StringName in ducks:
		var row := (mix.get("ducks", {}) as Dictionary).get(String(reason), {}) as Dictionary
		db += float((row.get("buses", {}) as Dictionary).get(String(bus), 0.0))
	return db


## Sets the player's volume for `bus` (dB) and applies it.
func set_user_volume(bus: StringName, db: float) -> void:
	user_db[bus] = db
	_apply_bus(bus)


func _step_ducks(delta: float) -> void:
	for row: Variant in mix.get("buses", []):
		var bus := StringName(str((row as Dictionary).get("name", "")))
		var want := duck_target_db(bus)
		var now := float(bus_duck_db.get(bus, 0.0))
		if now != want:
			var rate := _duck_rate(bus)
			bus_duck_db[bus] = want if rate <= 0.0 else move_toward(now, want, rate * delta)
		_apply_bus(bus)


## dB per second for `bus`: the largest |duck| on it over its reason's sec.
func _duck_rate(bus: StringName) -> float:
	var rate := 0.0
	for row: Dictionary in (mix.get("ducks", {}) as Dictionary).values():
		var db := absf(float((row.get("buses", {}) as Dictionary).get(String(bus), 0.0)))
		var sec := float(row.get("sec", 0.0))
		if db > 0.0:
			rate = maxf(rate, db / sec if sec > 0.0 else INF)
	return 0.0 if is_inf(rate) else rate


func _apply_bus(bus: StringName) -> void:
	var idx := AudioServer.get_bus_index(bus)
	if idx >= 0:
		AudioServer.set_bus_volume_db(idx, float(user_db.get(bus, 0.0)) + float(bus_duck_db.get(bus, 0.0)))


# --------------------------------------------------------------------------- hooks


func _on_node_added(node: Node) -> void:
	if node is CutsceneSequencer:
		pass  # its players are routed as they enter (below)
	elif node is AudioStreamPlayer and node.get_parent() is CutsceneSequencer:
		_route_sequencer_player(node as AudioStreamPlayer)
	elif node is DialogueBox:
		_boxes.append(node as CanvasItem)
		var blip := node.get_node_or_null(NodePath(String(BLIP_NODE))) as AudioStreamPlayer
		if blip != null:
			blip.bus = &"Voice"
	elif node is BattleController:
		_battles.append(node)
	elif node is BattleVfx:
		attach_battle.call_deferred(node)
	elif node is ShellShrineLevel:
		attach_shrine.call_deferred(node)


func _route_sequencer_player(p: AudioStreamPlayer) -> void:
	if p.name == SEQ_MUSIC_NODE:
		p.bus = &"Music"
		_seq_players.append(p)
	else:
		p.bus = &"SFX"


## Once a frame: the cutscene hold, the dialogue duck and the battle duck, from what is in the tree. Each is
## changed only when what the tree shows changes, so a caller's own set_hold / set_duck stands meanwhile.
func _poll_hooks() -> void:
	_seq_players = _alive(_seq_players)
	var seq_music := false
	for p: AudioStreamPlayer in _seq_players:
		if p.playing and p.volume_db > music.floor_db:
			seq_music = true
	if seq_music != _seen_seq_music:
		_seen_seq_music = seq_music
		music.set_hold(
			seq_music, CUTSCENE_TAKE_SEC if seq_music else float(music_cfg().get("cutscene_release_sec", 0.0))
		)
	_boxes = _alive(_boxes)
	var open := false
	for b: CanvasItem in _boxes:
		open = open or b.is_visible_in_tree()
	if open != _seen_box_open:
		_seen_box_open = open
		set_duck(REASON_DIALOGUE, open)
	_battles = _alive(_battles)
	if _battles.is_empty() == _seen_battle:
		_seen_battle = not _battles.is_empty()
		set_duck(REASON_BATTLE, _seen_battle)
	for key: Variant in listeners.keys():
		if not is_instance_valid(key) or not (key as Node).is_inside_tree():
			var l: Variant = listeners[key]
			listeners.erase(key)
			if is_instance_valid(l):
				(l as Node).queue_free()


## The nodes of `nodes` still in the tree (freed ones dropped), keeping the array's type.
static func _alive(nodes: Array) -> Array:
	var out := nodes.duplicate()
	out.clear()
	for n: Variant in nodes:
		if is_instance_valid(n) and (n as Node).is_inside_tree():
			out.append(n)
	return out


func attach_battle(vfx: Node) -> void:
	if not is_instance_valid(vfx) or not vfx.is_inside_tree():
		return
	var ctl := vfx.get_parent()
	while ctl != null and not ctl is BattleController:
		ctl = ctl.get_parent()
	if ctl == null or (ctl as BattleController).engine == null:
		return
	for key: Object in listeners.keys():
		if listeners[key] is BattleAudio:  # a retry replaces the VFX view: one battle listener at a time
			(listeners[key] as Node).queue_free()
			listeners.erase(key)
	var l := BattleAudio.new()
	l.name = "BattleAudio"
	add_child(l)
	l.attach(self, ctl as BattleController, (ctl as BattleController).engine, vfx as BattleVfx)
	listeners[vfx] = l


func attach_shrine(level: Node) -> void:
	if not is_instance_valid(level) or not level.is_inside_tree() or (level as ShellShrineLevel).trial == null:
		return
	var l := ShrineAudio.new()
	l.name = "ShrineAudio"
	add_child(l)
	l.attach(self, level as ShellShrineLevel)
	listeners[level] = l


func _apply_first_scene() -> void:
	var scene := get_tree().current_scene
	if scene != null and zone_path == "" and scene.scene_file_path != "":
		apply_zone(scene.scene_file_path)


func _flag_reader() -> Callable:
	if flag_reader.is_valid():
		return flag_reader
	return func(flag: StringName) -> bool: return flag != &"" and bool(Game.get_flag(flag))


## mix.json's music timing.
func music_cfg() -> Dictionary:
	return mix.get("music", {}) as Dictionary
