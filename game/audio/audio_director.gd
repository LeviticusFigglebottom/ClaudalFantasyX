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
##   ambience; the Shell Shrine level gets a ShrineAudio listener (shrine_audio.gd); a FieldController gets a
##   FootstepAudio (footstep_audio.gd); the menus in ui_sfx.json are watched by a UiAudio (ui_audio.gd), and
##   Reefball's sphere and match in reefball_hooks.json by a ReefballAudio (reefball_audio.gd). Listeners
##   live under this node, not in the other scene's tree, and never write game state.
## - **Ambience (M2-AUD-05):** ambience.json's beds join music.json's, and its zone beds apply where music.json's
##   row names none; the wind bed's level follows the zone's wind speed (WeatherClock.zone_wind).
## - **Reverb (M2-AUD-10):** a WorldVerb puts an AudioEffectReverb on the World and Combat buses; the zone row's
##   `reverb` key picks a mix.json preset, ramped.
## - **Voices (M3-AUD-07):** each DialogueBox gets a VoiceAudio (voice_audio.gd): the speaker's own blips from
##   voices.json, and a recorded line when its file exists. A CutsceneSequencer's line_shown tells it each line.
## - **Battle stings (M3-AUD-18):** EventBus.dialogue_event's battle announcements (the tide-line stinger, the bark,
##   a boss intro) play battle_stings.json's rows through a StingAudio (sting_audio.gd).
## It runs while the tree is paused (PROCESS_MODE_ALWAYS), so a menu that pauses the field keeps its music and
## sounds; nothing it drives moves the game.
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
## ambience.json, and the bed rows of both tables (AudioData.bed_rows).
var ambience_data: Dictionary = {}
var bed_table: Dictionary = {}
## The wind bed's level offset for the zone applied last (dB).
var wind_db := 0.0
## footsteps.json (each FieldController's FootstepAudio).
var footstep_data: Dictionary = {}
## voices.json (each DialogueBox's VoiceAudio; M3-AUD-07).
var voice_data: Dictionary = {}
## The World and Combat reverb (M2-AUD-10).
var verb := WorldVerb.new()
var muffle := BusMuffle.new()
var ui: UiAudio
## Reefball's sphere and match, by listening (M3-AUD-17; reefball_audio.gd).
var reefball: ReefballAudio
## Villagers' talk and work and the wildlife, by listening (M3-AUD-814; life_audio.gd).
var life: LifeAudio
## A blow's weight and the KO slow-mo, on battle-presentation's BattleImpact (M3-AUD-816; impact_audio.gd).
var impact: ImpactAudio
## Cutscene foley on each sequencer's cues (M3-AUD-817; cutscene_audio.gd).
var cutscene: CutsceneAudio
## Field objects' own sounds when used (M3-AUD-864; interact_audio.gd).
var interact: InteractAudio
var stings := StingAudio.new()
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
## A cue waiting for its files to load on a worker thread: {cue, sec, files} ({} when none).
var _pending: Dictionary = {}
## M3-AUD-864 (the as-played pass): the zone returns on release. Every CutsceneSequencer seen, and how long the
## field has been silent with no scene or battle playing.
var _sequencers: Array[Node] = []
var _quiet_sec := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	setup(
		AudioData.table(AudioData.MIX),
		AudioData.table(AudioData.MUSIC),
		{"sfx": AudioData.sfx_rows()},
		AudioData.table(AudioData.AMBIENCE)
	)
	ui.configure(AudioData.table(AudioData.UI_SFX))
	reefball.configure(AudioData.table(AudioData.REEFBALL_HOOKS))
	life.configure(AudioData.table(AudioData.LIFE))
	life.footstep_data = AudioData.table(AudioData.FOOTSTEPS)
	impact.configure(AudioData.table(AudioData.IMPACT))
	cutscene.data = AudioData.table(AudioData.CUTSCENE_FOLEY)
	stings.data = AudioData.table(AudioData.BATTLE_STINGS)
	var bus := get_node_or_null(^"/root/EventBus")
	if bus != null and bus.has_signal(&"dialogue_event"):
		bus.connect(&"dialogue_event", stings.on_event)
	footstep_data = AudioData.table(AudioData.FOOTSTEPS)
	voice_data = AudioData.table(AudioData.VOICES)
	get_tree().node_added.connect(_on_node_added)
	var router := get_node_or_null(^"/root/SceneRouter")
	if router != null and router.has_signal(&"scene_swapping"):
		router.connect(&"scene_swapping", apply_zone)
	_apply_first_scene.call_deferred()
	follow_settings(UiSettings.shared())


## Builds the buses, the deck and the bank from the tables (tests call it with their own).
func setup(mix_table: Dictionary, music_table: Dictionary, sfx_table: Dictionary, amb_table: Dictionary = {}) -> void:
	mix = mix_table
	music_data = music_table
	ambience_data = amb_table
	bed_table = AudioData.bed_rows(music_data, ambience_data)
	if ui == null:
		ui = UiAudio.new()
		ui.name = "UiAudio"
		ui.player = func(id: StringName) -> void: play_sfx(id)
		add_child(ui)
	stings.player = func(id: StringName) -> void: play_sfx(id)
	stings.ducker = set_duck
	stings.reduced = func() -> bool: return _reduced_audio()
	if reefball == null:
		reefball = ReefballAudio.new()
		reefball.name = "ReefballAudio"
		reefball.bind_director(self)
		add_child(reefball)
	if life == null:
		life = LifeAudio.new()
		life.name = "LifeAudio"
		life.bind_director(self)
		add_child(life)
	if impact == null:
		impact = ImpactAudio.new()
		impact.name = "ImpactAudio"
		impact.bind_director(self)
		add_child(impact)
	if interact == null:
		interact = InteractAudio.new(AudioData.table(AudioData.INTERACT_SFX))
		interact.name = "InteractAudio"
		interact.bind_director(self)
		add_child(interact)
	if cutscene == null:
		cutscene = CutsceneAudio.new()
		cutscene.name = "CutsceneAudio"
		cutscene.bind_director(self)
		add_child(cutscene)
	build_buses(mix)
	verb.configure(mix)
	muffle.configure(mix)
	if music == null:
		music = MusicDeck.new()
		music.name = "Music"
		add_child(music)
	music.floor_db = float(music_cfg().get("floor_db", -60.0))
	music.beat_max_wait_sec = float(music_cfg().get("beat_sync_max_wait_sec", 0.0))
	if sfx == null:
		sfx = SfxBank.new()
		sfx.name = "Sfx"
		add_child(sfx)
	sfx.rows = sfx_table.get("sfx", {}) as Dictionary


## Stops every player under this node as the game quits: a playback still running when its player is freed
## outlives it in the AudioServer and is reported as a leak at exit (the boot smoke test's "resources still in use").
func _exit_tree() -> void:
	stop_all_players()
	var bus := get_node_or_null(^"/root/EventBus")
	if bus != null and bus.has_signal(&"dialogue_event") and bus.is_connected(&"dialogue_event", stings.on_event):
		bus.disconnect(&"dialogue_event", stings.on_event)


func stop_all_players() -> void:
	for p: Node in find_children("*", "AudioStreamPlayer", true, false):
		(p as AudioStreamPlayer).stop()
	for p: Node in find_children("*", "AudioStreamPlayer3D", true, false):
		(p as AudioStreamPlayer3D).stop()


func _process(delta: float) -> void:
	advance(delta)


func advance(delta: float) -> void:
	_poll_hooks()
	music.advance(delta)
	_step_zone_return(delta)
	for bed: FadeVoice in beds.values():
		bed.step(delta, music.floor_db)
	_step_ducks(delta)
	verb.advance(delta)
	muffle.advance(delta)
	_poll_pending()
	ui.step()
	reefball.advance(delta)
	life.advance(delta)
	if cutscene != null:
		cutscene.advance(delta)
	impact.advance(delta)
	stings.advance(delta)
	for l: Variant in listeners.values():
		if not is_instance_valid(l):
			continue
		if l is FootstepAudio:
			(l as FootstepAudio).advance(delta)
		elif l is VoiceAudio:
			(l as VoiceAudio).advance(delta)


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
	_pending = {}
	play_music(AudioData.SILENCE, sec)


## play_music without loading on the main thread: a cue whose files aren't cached yet loads on a worker thread
## (ResourceLoader.load_threaded_request) and starts once loaded, so a zone swap or a battle's first frames never
## carry the decode-and-load of a music file (the router's swap-frame budget). A later request replaces a pending one.
func play_music_async(cue_id: StringName, sec: float = -1.0) -> void:
	_pending = {}
	var row := AudioData.cue(music_data, cue_id)
	var files := AudioData.cue_files(row)
	var waiting: Array[String] = []
	for f in files:
		if ResourceLoader.exists(f) and not ResourceLoader.has_cached(f):
			if ResourceLoader.load_threaded_request(f, "AudioStream") == OK:
				waiting.append(f)
	if waiting.is_empty() or cue_id == AudioData.SILENCE:
		play_music(cue_id, sec)
		return
	_pending = {"cue": cue_id, "sec": sec, "files": waiting}


## The cue a threaded load is still waiting on (&"" for none).
func pending_cue() -> StringName:
	return StringName(_pending.get("cue", &""))


## Blocks until a pending cue has loaded and starts it (tests).
func flush_pending() -> void:
	if _pending.is_empty():
		return
	for f: String in _pending["files"]:
		ResourceLoader.load_threaded_get(f)
	var p := _pending
	_pending = {}
	play_music(p["cue"], float(p["sec"]))


func _poll_pending() -> void:
	if _pending.is_empty():
		return
	for f: String in _pending["files"]:
		var st := ResourceLoader.load_threaded_get_status(f)
		if st == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
			return
	flush_pending()


## M3-AUD-864 (the as-played pass): the zone returns on release. A scene that ends on `@music silence` or on a
## one-shot cue, or a battle that ends in the zone it started in (battle_out stops the music), would leave the field
## silent until the next scene swap. Once no cutscene plays, no battle is in the tree, no cue is loading and the deck
## has been silent for mix.json music.zone_return_sec, the zone's own cue comes back (resuming where it left off).
## A swap or a battle that follows at once starts its own cue first, so this never double-starts one.
func _step_zone_return(delta: float) -> void:
	var sec := float(music_cfg().get("zone_return_sec", 0.0))
	if sec <= 0.0 or not zone.has("music") or not _pending.is_empty() or not music.is_silent() or music.is_held():
		_quiet_sec = 0.0
		return
	_sequencers = _alive(_sequencers)
	_battles = _alive(_battles)
	for seq: Node in _sequencers:
		if (seq as CutsceneSequencer).is_playing():
			_quiet_sec = 0.0
			return
	if not _battles.is_empty():
		_quiet_sec = 0.0
		return
	_quiet_sec += delta
	if _quiet_sec >= sec:
		_quiet_sec = 0.0
		play_music(StringName(str(zone["music"])))


## Applies the zone row for `scene_path` (SceneRouter.scene_swapping calls this under the fade).
func apply_zone(scene_path: String) -> void:
	zone_path = scene_path
	zone = AudioData.merge_zone_beds(
		AudioData.zone_for(music_data, scene_path, _flag_reader()), ambience_data, scene_path, _flag_reader()
	)
	var w := WeatherClock.zone_wind(scene_path)
	wind_db = AudioData.wind_db(ambience_data, Vector3(w.x, w.y, w.z).length())
	var room := verb.preset_for(zone)
	if room != verb.preset:
		verb.apply(room)
	if zone.is_empty():
		zone_applied.emit(scene_path, zone)
		return
	if zone.has("music"):
		play_music_async(StringName(str(zone["music"])))
	if zone.has("ambience"):
		var ids: Array[StringName] = []
		for a: Variant in zone["ambience"]:
			ids.append(StringName(str(a)))
		set_ambience(ids)
	zone_applied.emit(scene_path, zone)


## The ambience beds that play now: these ids fade in (music.json and ambience.json rows), the others fade out.
func set_ambience(ids: Array[StringName], sec: float = -1.0) -> void:
	var fade := float(music_cfg().get("crossfade_sec", 0.0)) if sec < 0.0 else sec
	for id: StringName in beds.keys():
		if not ids.has(id):
			(beds[id] as FadeVoice).fade_to(0.0, fade)
	for id in ids:
		var row := bed_table.get(String(id), {}) as Dictionary
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
			beds[id] = bed
		bed.base_db = float(row.get("volume_db", 0.0)) + (wind_db if String(id) == wind_bed() else 0.0)
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


## Applies the player's volume settings (mix.json volume_settings: a UiSettings id, 0..1 -> its buses) and follows
## `settings` from now on. M2-AUD-06.
func follow_settings(settings: UiSettings) -> void:
	if settings == null:
		return
	apply_volume_settings(settings)
	if not settings.changed.is_connected(_on_setting_changed):
		settings.changed.connect(_on_setting_changed.bind(settings))


func apply_volume_settings(settings: UiSettings) -> void:
	var rows := mix.get("volume_settings", {}) as Dictionary
	for key: String in rows:
		var value: Variant = settings.get_value(StringName(key))
		if value == null:
			continue
		var v := clampf(float(value), 0.0, 1.0)
		for bus: Variant in rows[key]:
			set_user_volume(StringName(str(bus)), linear_to_db(v) if v > 0.0 else -80.0)


func _on_setting_changed(key: StringName, settings: UiSettings) -> void:
	if (mix.get("volume_settings", {}) as Dictionary).has(String(key)):
		apply_volume_settings(settings)


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
		# its players are routed as they enter (below); its lines tell the box's VoiceAudio who speaks
		var seq := node as CutsceneSequencer
		_sequencers.append(seq)
		if not seq.line_shown.is_connected(_on_line_shown):
			seq.line_shown.connect(_on_line_shown.bind(seq))
		if cutscene != null:
			cutscene.watch(seq)
	elif node is CutsceneStage:
		_later(attach_cast, node)
	elif node is AudioStreamPlayer and node.get_parent() is CutsceneSequencer:
		_route_sequencer_player(node as AudioStreamPlayer)
	elif node is DialogueBox:
		_boxes.append(node as CanvasItem)
		var blip := node.get_node_or_null(NodePath(String(BLIP_NODE))) as AudioStreamPlayer
		if blip != null:
			blip.bus = &"Voice"
		_later(attach_voice, node)
	elif node is BattleController:
		_battles.append(node)
	elif node is BattleVfx:
		_later(attach_battle, node)
	elif node is ShellShrineLevel:
		_later(attach_shrine, node)
	elif node is Ch05AshcrownZone:
		_later(attach_ashcrown, node)
	elif node is Ch08CoilspireZone:
		_later(attach_coilspire, node)
	elif node is FieldController:
		_later(attach_footsteps, node)
	elif reefball != null and reefball.wants(node):
		_later(reefball.watch, node)
	elif life != null and life.wants(node):
		_later(life.watch, node)
	elif impact != null and impact.wants(node):
		_later(impact.watch, node)
	elif ChoreoAudio.wants(node):  # M3-AUD-13: the battle choreography's layers (choreo_sfx.json hooks)
		_later(ChoreoAudio.attach_to.bind(self), node)
	elif node is Interactable:  # its own sound (InteractAudio) and the menu's soft touch (UiAudio)
		_later(interact.watch, node)
		if ui != null and ui.wants(node):
			_later(ui.watch, node)
	elif ui != null and ui.wants(node):
		_later(ui.watch, node)


## Calls `fn` with `node` at the end of the frame, if the node still exists then (a test may free it at once).
func _later(fn: Callable, node: Node) -> void:
	_call_if_alive.call_deferred(fn, node.get_instance_id())


func _call_if_alive(fn: Callable, id: int) -> void:
	var node := instance_from_id(id)
	if node != null and fn.is_valid():
		fn.call(node)


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
		# A scene that started music keeps the bed held to its end, even when its cue ends first.
		var seq := p.get_parent() as CutsceneSequencer
		if seq != null and seq.is_playing() and seq.music_track != &"":
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
	for key: Variant in listeners.keys():  # a key may be a freed view (a capture swaps battles)
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


## An AshcrownAudio for the Ashcrown zone `zone` (M3-AUD-825): the strike trial's sounds.
func attach_ashcrown(zone: Node) -> void:
	if not is_instance_valid(zone) or not zone.is_inside_tree() or listeners.has(zone):
		return
	var l := AshcrownAudio.new(AudioData.table(AudioData.ASHCROWN_SFX))
	l.name = "AshcrownAudio"
	l.bind_director(self)
	add_child(l)
	l.attach(zone as Node3D)
	listeners[zone] = l


## M3-AUD-864: Ch8's Coilspire flue-key trial (the keys turning, the coughs, each tier lit, the niche, the seized
## key), heard by the same listener as the Ashcrown trial from coilspire_sfx.json.
func attach_coilspire(zone: Node) -> void:
	if not is_instance_valid(zone) or not zone.is_inside_tree() or listeners.has(zone):
		return
	var l := AshcrownAudio.new(AudioData.table(AudioData.COILSPIRE_SFX))
	l.name = "CoilspireAudio"
	l.bind_director(self)
	add_child(l)
	l.attach(zone as Node3D)
	listeners[zone] = l


## A FootstepAudio for the field walker `walker`, on the surface of the zone applied last (else the running scene).
func attach_footsteps(walker: Node) -> void:
	if not is_instance_valid(walker) or not walker.is_inside_tree() or listeners.has(walker):
		return
	var l := FootstepAudio.new(footstep_data)
	l.name = "FootstepAudio"
	l.player = func(id: StringName, at: Vector3, opts: Dictionary) -> void: play_sfx_at(id, at, opts)
	add_child(l)
	var scene := get_tree().current_scene
	var path := zone_path if zone_path != "" or scene == null else scene.scene_file_path
	l.attach(walker as Node3D, path)
	listeners[walker] = l


## A FootstepAudio for every actor a cutscene stage can move (M3-AUD-817): their walks and runs step from their
## own foot contacts (or by distance), on the zone's ground. The player already has one; attach_footsteps skips it.
func attach_cast(stage: Node) -> void:
	if not is_instance_valid(stage) or not stage is CutsceneStage:
		return
	for actor: Node3D in (stage as CutsceneStage).cast():
		attach_footsteps(actor)
	if cutscene != null:
		cutscene.watch_lamps(stage)  # M3-AUD-847: a lit lamp on the stage crackles at the lamp


## A VoiceAudio for dialogue box `box` (once; M3-AUD-07). Its blips play through play_sfx.
func attach_voice(box: Node) -> VoiceAudio:
	if not is_instance_valid(box) or not box is DialogueBox:
		return null
	if listeners.has(box):
		return listeners[box] as VoiceAudio
	var l := VoiceAudio.new(voice_data)
	l.name = "VoiceAudio"
	l.player = func(id: StringName, opts: Dictionary) -> void: play_sfx(id, opts)
	add_child(l)
	l.attach(box as DialogueBox)
	listeners[box] = l
	return l


## A sequencer's line: its box's VoiceAudio learns the voice and looks for a recorded file.
func _on_line_shown(step: DialogueStep, seq: CutsceneSequencer) -> void:
	if not is_instance_valid(seq) or seq.overlay == null or not is_instance_valid(seq.overlay.box):
		return
	var l := attach_voice(seq.overlay.box)
	if l != null:
		l.on_line(step)


## ambience.json's wind bed id ("" when none).
func wind_bed() -> String:
	return str((ambience_data.get("wind", {}) as Dictionary).get("bed", ""))


## The first scene's zone row (a scene run on its own, or the main scene). Not on a headless run (no audio device:
## CI's boot smoke test quits after 60 frames, and a music playback still live in the dummy driver at exit is
## reported as leaked resources); tests call apply_zone themselves.
func _apply_first_scene() -> void:
	if DisplayServer.get_name() == "headless":
		return
	var scene := get_tree().current_scene
	if scene != null and zone_path == "" and scene.scene_file_path != "":
		apply_zone(scene.scene_file_path)


func _reduced_audio() -> bool:
	var settings := UiSettings.shared()
	return settings != null and bool(settings.get_value(&"reduced_audio"))


func _flag_reader() -> Callable:
	if flag_reader.is_valid():
		return flag_reader
	return func(flag: StringName) -> bool: return flag != &"" and bool(Game.get_flag(flag))


## mix.json's music timing.
func music_cfg() -> Dictionary:
	return mix.get("music", {}) as Dictionary
