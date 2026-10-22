class_name BattleStage
extends Node3D
## The 3D half of the battle sandbox: places FighterStandIns on the slot markers, shows ground
## rings, and projects fighters to screen space for the HUD. Reads engine state, never writes.

const CONFIG_PATH := "res://game/data/ui/battle_sandbox.json"

static var _config: Dictionary = {}

var _party_slots: Array[Marker3D] = []
var _enemy_slots: Array[Marker3D] = []
## Combatant id -> FighterStandIn.
var _fighters: Dictionary = {}

@onready var camera: Camera3D = %BattleCamera
@onready var _fighter_root: Node3D = %Fighters


static func config() -> Dictionary:
	if _config.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("BattleStage: could not read %s" % CONFIG_PATH)
			return {}
		_config = (parsed as Dictionary).get("battle_sandbox", {}) as Dictionary
	return _config


## Stand-in spec for a combatant id ("reef_crab#1" uses the "reef_crab" row), defaults merged.
static func stand_in_spec(cid: StringName) -> Dictionary:
	var cfg := config()
	var base := String(cid).get_slice("#", 0)
	var row: Dictionary = (cfg.get("stand_ins", {}) as Dictionary).get(base, {})
	return (cfg.get("stand_in_defaults", {}) as Dictionary).merged(row, true)


func _ready() -> void:
	for n in %PartySlots.get_children():
		_party_slots.append(n as Marker3D)
	for n in %EnemySlots.get_children():
		_enemy_slots.append(n as Marker3D)


func spawn(engine: BattleEngine) -> void:
	for f: FighterStandIn in _fighters.values():
		f.queue_free()
	_fighters.clear()
	for i in engine.party_active.size():
		_place(engine.party_active[i].id, _party_slots[i])
	for i in engine.enemies.size():
		_place(engine.enemies[i].id, _enemy_slots[mini(i, _enemy_slots.size() - 1)])


## Re-seats the active party after a swap (slot i shows party_active[i]).
func sync_party(engine: BattleEngine) -> void:
	for c in engine.party_reserve:
		if _fighters.has(c.id):
			(_fighters[c.id] as FighterStandIn).queue_free()
			_fighters.erase(c.id)
	for i in engine.party_active.size():
		var cid := engine.party_active[i].id
		if not _fighters.has(cid):
			_place(cid, _party_slots[i])


func refresh_ko(engine: BattleEngine) -> void:
	var cfg := config()
	for c in engine.party_active + engine.enemies:
		var f := stand_in(c.id)
		if f != null:
			f.set_ko(not c.is_alive(), float(cfg.get("ko_sink_m", 0.0)), float(cfg.get("ko_alpha", 1.0)))


func stand_in(cid: StringName) -> FighterStandIn:
	return _fighters.get(cid) as FighterStandIn


func has_fighter(cid: StringName) -> bool:
	return _fighters.has(cid)


## Screen position (canvas coordinates) just above the fighter's head.
func screen_pos(cid: StringName, extra_m: float = 0.0) -> Vector2:
	var f := stand_in(cid)
	if f == null or camera == null:
		return Vector2.ZERO
	return camera.unproject_position(f.head_position(extra_m))


func set_rings(ids: Array[StringName], hostile: Array[bool], ally_color: Color, foe_color: Color) -> void:
	for cid: StringName in _fighters:
		var i := ids.find(cid)
		var f := _fighters[cid] as FighterStandIn
		if i < 0:
			f.set_ring(FighterStandIn.RING_NONE, ally_color)
		elif hostile[i]:
			f.set_ring(FighterStandIn.RING_FOE, foe_color)
		else:
			f.set_ring(FighterStandIn.RING_ALLY, ally_color)


func clear_rings() -> void:
	for f: FighterStandIn in _fighters.values():
		f.set_ring(FighterStandIn.RING_NONE, Color.WHITE)


func ringed_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for cid: StringName in _fighters:
		if (_fighters[cid] as FighterStandIn).ring_mode_visible():
			out.append(cid)
	return out


func _place(cid: StringName, slot: Marker3D) -> void:
	var f := FighterStandIn.new()
	_fighter_root.add_child(f)
	f.setup(cid, stand_in_spec(cid), config().get("ring", {}) as Dictionary)
	f.global_transform = slot.global_transform
	_fighters[cid] = f
