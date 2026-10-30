class_name BattleAudio
extends Node
## A battle's sound (M2-AUD-02 music, M2-AUD-04 SFX; docs/kb/tech/audio_runtime.md). The Audio autoload builds
## one when a BattleVfx enters a BattleController's tree, and frees it when that view leaves (a retry builds a
## new one). **Listens only:** the engine's signals and the view's effect_played; it never writes combat state.
##
## - **Music:** the encounter's cue (music.json battle) cuts in at the start; an engine phase_changed id named in
##   battle.phases brings stems in or out (the Drownbell's Flood); the battle's end fades it out.
## - **Ambience:** the encounter's arena (encounters.json `arena`) plays its own beds (ambience.json `arenas`) in
##   place of the field's; the field's come back when this listener leaves.
## - **SFX:** game/data/audio/battle_sfx.json maps each BattleVfx effect id (as the view plays it) and each
##   engine moment that has no particle (the toll's ring, the Flood, Floodnet, the Vowbound's call and dismiss,
##   the opening stingers) to an sfx.json row on the Combat bus. Sections other than `vfx` are fallbacks: one is
##   dropped when the view already played the same sound within dedupe_ms. A vfx sound repeated within repeat_ms
##   (an action's other targets) plays as a softer layer (layer_db).
## - **Reduced audio** (UiSettings `reduced_audio`, followed live): one layer per action (the repeats are skipped),
##   `reduced` swaps a sound for its version without sub-bass, and the SFX bank plays at reduced_level while the
##   battle lasts (put back when this listener leaves).

const TABLE := "battle_sfx"
const REDUCED_AUDIO := &"reduced_audio"

var director: AudioDirector
var engine: BattleEngine
var vfx: BattleVfx
## battle_sfx.json.
var data: Dictionary = {}
## Every SFX id this listener played, in order (tests).
var played: Array[StringName] = []
## The reduced-audio setting in force (UiSettings, followed live).
var reduced := false
## The creatures' voices and movement (M3-AUD-14), a child listener.
var creatures: CreatureAudio
var _ctl: BattleController
var _settings: UiSettings
## The factor this listener applies to the SFX bank's level (taken back off on exit, so a retry's overlapping
## listeners compose instead of overwriting each other).
var _applied := 1.0
## sfx id -> [msec of its last play, whether the view's effect_played played it].
var _last: Dictionary = {}


func attach(dir: AudioDirector, controller: BattleController, eng: BattleEngine, view: BattleVfx) -> void:
	director = dir
	engine = eng
	vfx = view
	_ctl = controller
	data = AudioData.table(TABLE)
	_settings = UiSettings.shared()
	if _settings != null:
		_settings.changed.connect(_on_setting_changed)
	_apply_reduced()
	var cue := AudioData.battle_cue(dir.music_data, eng.encounter_id)
	if cue != &"":
		dir.play_music_async(cue, float(dir.music_cfg().get("battle_in_sec", 0.0)))
	_apply_arena_ambience()
	eng.phase_changed.connect(_on_phase_changed)
	eng.battle_finished.connect(_on_battle_finished)
	_connect_sfx()
	_attach_creatures(controller)


## The arena's beds (ambience.json `arenas`) in place of the field's; an arena with none keeps the field's.
func _apply_arena_ambience() -> void:
	if engine.db == null:
		return
	var enc := engine.db.encounters.get(engine.encounter_id, engine.db.encounters.get(String(engine.encounter_id), {}))
	var ids := AudioData.arena_beds(director.ambience_data, str((enc as Dictionary).get("arena", "")))
	if not ids.is_empty():
		director.set_arena_ambience(self, ids)


## M3-AUD-14: the creatures' voices and movement (creature_audio.gd, creature_voices.json).
func _attach_creatures(controller: Node) -> void:
	creatures = CreatureAudio.new()
	creatures.name = "CreatureAudio"
	add_child(creatures)
	creatures.attach(director, controller, engine, self)


## Plays the sound battle_sfx.json's section `table` names for `key` (a VFX effect id, a skill, an event, ...).
## `from_vfx`: the view played it (a repeat layers); otherwise it is a fallback (a repeat is dropped). Returns the
## sfx id played, or &"" when nothing played.
func play_key(table: String, key: String, from_vfx := false) -> StringName:
	var id := StringName(str((data.get(table, {}) as Dictionary).get(key, "")))
	if id == &"" or director == null or director.sfx == null:
		return &""
	if reduced:
		id = StringName(str((data.get("reduced", {}) as Dictionary).get(String(id), id)))
	var now := int(director.sfx.clock.call())
	var opts: Dictionary = {}
	if _last.has(id):
		var dt := now - int((_last[id] as Array)[0])
		var by_vfx := bool((_last[id] as Array)[1])
		if from_vfx and by_vfx and dt < int(data.get("repeat_ms", 0)):
			if reduced:
				return &""
			opts["volume_db"] = float(data.get("layer_db", 0.0))
		elif (not from_vfx or not by_vfx) and dt < int(data.get("dedupe_ms", 0)):
			return &""
	if director.play_sfx(id, opts) == null:
		return &""
	_last[id] = [now, from_vfx]
	played.append(id)
	return id


func _on_setting_changed(key: StringName) -> void:
	if key == REDUCED_AUDIO:
		_apply_reduced()


func _apply_reduced() -> void:
	reduced = _settings != null and bool(_settings.get_value(REDUCED_AUDIO))
	_set_factor(float(data.get("reduced_level", 1.0)) if reduced else 1.0)


func _set_factor(factor: float) -> void:
	if director == null or not is_instance_valid(director) or director.sfx == null or factor <= 0.0:
		return
	director.sfx.level = director.sfx.level / _applied * factor
	_applied = factor


func _exit_tree() -> void:
	if _settings != null and _settings.changed.is_connected(_on_setting_changed):
		_settings.changed.disconnect(_on_setting_changed)
	_set_factor(1.0)
	if director != null and is_instance_valid(director):
		director.release_arena_ambience(self)


func _connect_sfx() -> void:
	if data.is_empty():
		return
	if vfx != null:
		vfx.effect_played.connect(_on_effect_played)
	engine.action_resolved.connect(_on_action_resolved)
	engine.charge_broken.connect(_on_charge_broken)
	engine.field_cleared.connect(_on_field_cleared)
	engine.vowbound.called.connect(_on_called)
	engine.vowbound.departed.connect(_on_departed)
	var opening := String(engine.opening)
	if opening != String(BattleOpening.NORMAL):
		play_key.call_deferred("openings", opening)


func _on_effect_played(effect_id: StringName, _at: Vector3) -> void:
	play_key("vfx", String(effect_id), true)


func _on_action_resolved(result: ActionResult) -> void:
	if result != null and result.ok and result.skill_id != &"":
		play_key("skills", String(result.skill_id))


func _on_charge_broken(_enemy: BattleCombatant, _skill_id: StringName) -> void:
	play_key("events", "rim_break")


func _on_called(v: BattleCombatant) -> void:
	play_key("events", "vowbound_call")
	# The Vowbound's own sting (battle_sfx.json vowbound_stings; Ilun's is the ilun_summon music sting).
	if v != null:
		play_key("vowbound_stings", BattleVfx.base_id(v.id))


func _on_field_cleared(field_id: StringName, _fallen: Array[BattleCombatant]) -> void:
	play_key("fields_cleared", String(field_id))


func _on_departed(_v: BattleCombatant, fell: bool) -> void:
	play_key("events", "vowbound_fell" if fell else "vowbound_dismiss")


func _on_phase_changed(_enemy: BattleCombatant, phase_id: StringName) -> void:
	var phases := (director.music_data.get("battle", {}) as Dictionary).get("phases", {}) as Dictionary
	var row := phases.get(String(phase_id), {}) as Dictionary
	var sec := float(row.get("sec", 0.0))
	for i: Variant in row.get("stems_on", []):
		director.music.set_stem(int(i), true, sec)
	for i: Variant in row.get("stems_off", []):
		director.music.set_stem(int(i), false, sec)
	play_key("phases", String(phase_id))


func _on_battle_finished(outcome: StringName) -> void:
	play_key("outcomes", String(outcome))
	director.stop_music(float(director.music_cfg().get("battle_out_sec", 0.0)))
