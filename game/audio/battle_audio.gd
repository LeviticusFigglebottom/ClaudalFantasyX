class_name BattleAudio
extends Node
## A battle's sound (M2-AUD-02 music, M2-AUD-04 SFX; docs/kb/tech/audio_runtime.md). The Audio autoload builds
## one when a BattleVfx enters a BattleController's tree, and frees it when that view leaves (a retry builds a
## new one). **Listens only:** the engine's signals and the view's effect_played; it never writes combat state.
##
## - **Music:** the encounter's cue (music.json battle) cuts in at the start; an engine phase_changed id named in
##   battle.phases brings stems in or out (the Drownbell's Flood); the battle's end fades it out.
## - **SFX:** game/data/audio/battle_sfx.json maps each BattleVfx effect id (as the view plays it) and each
##   engine moment that has no particle (the toll's ring, the Flood, Floodnet, the Vowbound's call and dismiss,
##   the opening stingers) to an sfx.json row on the Combat bus.

const TABLE := "battle_sfx"

var director: AudioDirector
var engine: BattleEngine
var vfx: BattleVfx
## battle_sfx.json.
var data: Dictionary = {}
## Every SFX id this listener played, in order (tests).
var played: Array[StringName] = []
var _ctl: BattleController


func attach(dir: AudioDirector, controller: BattleController, eng: BattleEngine, view: BattleVfx) -> void:
	director = dir
	engine = eng
	vfx = view
	_ctl = controller
	data = AudioData.table(TABLE)
	var cue := AudioData.battle_cue(dir.music_data, eng.encounter_id)
	if cue != &"":
		dir.play_music(cue, float(dir.music_cfg().get("battle_in_sec", 0.0)))
	eng.phase_changed.connect(_on_phase_changed)
	eng.battle_finished.connect(_on_battle_finished)
	_connect_sfx()


## Plays battle_sfx.json's row for `key` (a VFX effect id or an event name) at fighter `target` ("" for none).
func play_key(table: String, key: String) -> StringName:
	var id := StringName(str((data.get(table, {}) as Dictionary).get(key, "")))
	if id == &"" or director == null or director.sfx == null:
		return &""
	if director.play_sfx(id) == null:
		return &""
	played.append(id)
	return id


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
	play_key("vfx", String(effect_id))


func _on_action_resolved(result: ActionResult) -> void:
	if result != null and result.ok and result.skill_id != &"":
		play_key("skills", String(result.skill_id))


func _on_charge_broken(_enemy: BattleCombatant, _skill_id: StringName) -> void:
	play_key("events", "rim_break")


func _on_called(_v: BattleCombatant) -> void:
	play_key("events", "vowbound_call")


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
