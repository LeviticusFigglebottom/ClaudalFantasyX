class_name VoiceAudio
extends Node
## The dialogue voice of one DialogueBox (M3-AUD-07; ADR 0031; docs/kb/tech/audio_runtime.md "Voices"), by
## listening: the director attaches one to each box and never edits the box's script or scene.
## - **Blips.** The box counts each blip it asks for (`blips_played`). Once a frame this reads the count; for a new
##   blip it plays the speaker's own blip set from game/data/audio/voices.json (a row per timbre, pitch, jitter, a
##   minimum gap `rate_ms`) on the Voice bus, and it keeps the box's shared Blip player silent. The box already
##   leaves out sung lines, skipped reveals and (unless text_box.json says otherwise) narration, so this does too.
## - **Pace (M3-AUD-21).** voices.json `pace`: `syllable` (the default) blips once per syllable, on the box's
##   mouth_flap opening (each vowel group, the same edge the lip sync follows), so the blips rest through the reveal's
##   comma and full-stop pauses and keep time with the mouth; `letter` keeps one blip per blip the box counts.
## - **Level.** Each blip plays at the voice's volume_db + voices.json `mix_db` (M3-AUD-23's mix pass) + the box's
##   blip_volume_db.
## - **The speaker.** A CutsceneSequencer's line_shown step gives it exactly (the speaker, else the narrator
##   identity). A box shown without a sequencer reports only mouth_flap(speaker), at its first vowel, so until then
##   the previous voice stands; a request task asks the box for a public voice signal (M3-ARC-03).
## - **Recorded lines (VO).** A line with a line id looks for its file (the step's `voice`, else voices.json
##   vo.pattern). When it exists it plays on the Voice bus and the line's blips stay silent; a missing file falls
##   back to the blips. The next line, or the box closing, stops it.
## Time passes only through advance(delta) (AudioDirector.advance; tests call it directly).

## The level that keeps the box's own Blip player silent (dB).
const MUTE_DB := -80.0
const BLIP_NODE := ^"Blip"
const SEED := 20261107
const MS_PER_SEC := 1000.0
const NARRATOR := "narrator"
const PACE_SYLLABLE := &"syllable"
const PACE_LETTER := &"letter"

## voices.json.
var data: Dictionary = {}
## Plays a blip row: (id: StringName, opts: Dictionary) -> void (AudioDirector.play_sfx in the game).
var player: Callable = Callable()
## (path: String) -> AudioStream, null when there is no such file. Tests pass their own.
var vo_loader: Callable = Callable()
var box: DialogueBox
## The speakers.json id whose voice the box speaks in now (&"" before the first line).
var voice: StringName = &""
## The current line's recorded file ("" when it has none) and the player it plays on.
var vo_path: String = ""
var vo: AudioStreamPlayer
## Blips played and dropped (the rate limit or a VO line) by this listener; tests read them.
var blips := 0
var dropped := 0
## Every blip played, in order: [row id, pitch] (tests).
var history: Array = []
var _seen := 0
var _clock := 0.0
var _last_blip := -INF
var _cycle := 0
var _rng := RandomNumberGenerator.new()
## The mouth as the box last reported it (a syllable is its opening edge).
var _open := false


func _init(table: Dictionary = {}) -> void:
	data = table
	_rng.seed = SEED


## Starts listening to `node`.
func attach(node: DialogueBox) -> void:
	box = node
	_seen = node.blips_played
	if not node.mouth_flap.is_connected(_on_mouth_flap):
		node.mouth_flap.connect(_on_mouth_flap)
	if vo == null:
		vo = AudioStreamPlayer.new()
		vo.name = "Vo"
		add_child(vo)
	vo.bus = StringName(str(vo_cfg().get("bus", "Voice")))
	_mute_box()


## A line the box has just been given (CutsceneSequencer.line_shown): its voice, and its recorded file if any.
func on_line(step: DialogueStep) -> void:
	if step == null or not step.is_line():
		return
	voice = step.speaker if step.speaker != &"" else step.narrator
	stop_vo()
	if is_instance_valid(box):
		_seen = box.blips_played
	var path := vo_file(data, step)
	var stream := _load_vo(path) if path != "" else null
	if stream == null:
		return
	vo_path = path
	vo.stream = stream
	vo.volume_db = float(vo_cfg().get("volume_db", 0.0))
	if vo.is_inside_tree():
		vo.play()


func stop_vo() -> void:
	vo_path = ""
	if vo != null:
		vo.stop()


## True while the current line has a recorded file (and so plays no blips, with vo.suppress_blips).
func has_vo() -> bool:
	return vo_path != ""


## Reads the box once: plays the voice's blip for a new blip, and stops the VO when the box has closed.
func advance(delta: float) -> void:
	_clock += delta
	if not is_instance_valid(box) or not box.is_inside_tree():
		return
	_mute_box()
	if has_vo() and not box.is_visible_in_tree():
		stop_vo()
	var count := box.blips_played
	if count <= _seen:
		_seen = count
		return
	_seen = count
	if pace() == PACE_LETTER:
		_blip()


## How the blips are paced: voices.json `pace` (syllable unless it says letter).
func pace() -> StringName:
	return PACE_LETTER if str(data.get("pace", PACE_SYLLABLE)) == String(PACE_LETTER) else PACE_SYLLABLE


func _blip() -> void:
	if has_vo() and bool(vo_cfg().get("suppress_blips", true)):
		dropped += 1
		return
	var row := voice_row(data, voice)
	if (_clock - _last_blip) * MS_PER_SEC < float(row.get("rate_ms", 0.0)):
		dropped += 1
		return
	_play_blip(row)


func _play_blip(row: Dictionary) -> void:
	var set_ids: Array = row.get("blips", [])
	if set_ids.is_empty():
		return
	var id := StringName(str(set_ids[_cycle % set_ids.size()]))
	_cycle += 1
	var jitter := float(row.get("jitter", 0.0))
	var pitch := float(row.get("pitch", 1.0)) * (1.0 + (_rng.randf_range(-jitter, jitter) if jitter > 0.0 else 0.0))
	var level := float(row.get("volume_db", 0.0)) + float(data.get("mix_db", 0.0))
	if is_instance_valid(box) and box.settings != null:
		level += box.settings.blip_volume_db
	_last_blip = _clock
	blips += 1
	history.append([id, pitch])
	if player.is_valid():
		player.call(id, {"pitch": pitch, "volume_db": level})


## voices.json's row for `who`: its speakers row over the default row (the default alone for an unknown voice).
static func voice_row(table: Dictionary, who: StringName) -> Dictionary:
	var out := (table.get("default", {}) as Dictionary).duplicate(true)
	out.merge((table.get("speakers", {}) as Dictionary).get(String(who), {}) as Dictionary, true)
	return out


## The recorded file a line would play: its compiled `voice` field, else vo.pattern with {speaker} and {line_id};
## "" for a line without a line id (and no voice field).
static func vo_file(table: Dictionary, step: DialogueStep) -> String:
	if step.voice != "":
		return step.voice
	var cfg := table.get("vo", {}) as Dictionary
	var pattern := str(cfg.get("pattern", ""))
	if pattern == "" or step.line_id == &"":
		return ""
	var who := step.speaker if step.speaker != &"" else step.narrator
	var speaker := String(who) if who != &"" else str(cfg.get("narrator", NARRATOR))
	return pattern.format({"speaker": speaker, "line_id": String(step.line_id)})


func vo_cfg() -> Dictionary:
	return data.get("vo", {}) as Dictionary


func _load_vo(path: String) -> AudioStream:
	if vo_loader.is_valid():
		return vo_loader.call(path) as AudioStream
	if not ResourceLoader.exists(path):
		return null
	return load(path) as AudioStream


func _on_mouth_flap(speaker: StringName, open: bool) -> void:
	if speaker != &"":
		voice = speaker
	var opening := open and not _open
	_open = open
	if not opening or pace() != PACE_SYLLABLE:
		return
	if speaker == &"" and is_instance_valid(box) and box.settings != null and not box.settings.narration_blip:
		return
	_blip()


func _mute_box() -> void:
	var b := box.get_node_or_null(BLIP_NODE) as AudioStreamPlayer
	if b != null and b.volume_db != MUTE_DB:
		b.volume_db = MUTE_DB
