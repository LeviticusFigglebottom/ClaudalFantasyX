extends TestCase
## M2-CMB-08: the vertical-slice party (Rhen, Asha, Toma; Ysolde joins later) can Read (SPEC §6.1).
## Rhen knows Read (battle_ctb.md § Read), so the slice's tideline fights fill the bestiary.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const TIDELINE := &"ch02_tideline"
const REEF := &"sandbox_reef"
const SLICE_PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]

var ctl: BattleController
var _saved_state: GameStateData


func before_each() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	ctl = null


func test_a_slice_hero_knows_read() -> void:
	var db := BattleDB.load_default()
	var readers: Array[StringName] = []
	for cid in SLICE_PARTY:
		for sid: Variant in db.characters[cid].get("skills", []):
			if BattleRead.is_read(db.skill(StringName(str(sid)))):
				readers.append(cid)
	assert_eq(readers, [&"rhen"] as Array[StringName], "Rhen reads; the slice never needs Ysolde for it")
	_done()


func test_rhen_reads_every_tideline_foe_into_the_bestiary() -> void:
	for encounter: StringName in [TIDELINE, REEF]:
		var e := _engine(encounter)
		var bb := BattleBestiary.new()
		bb.attach(e, false)
		e.begin()
		var read := _read_all(e)
		var want: Array[StringName] = []
		for foe in e.enemies:
			want.append(BattleEngine.enemy_id(foe))
		assert_eq(read, want, "%s: every foe read, in order" % encounter)
		assert_eq(str(bb.last_reveal.get("enemy_id", "")), String(want[-1]), "the HUD holds the latest")
		for eid in want:
			assert_true(bb.book.is_read(eid), "%s: %s logged" % [encounter, eid])
	_done()


func test_a_live_tideline_read_fills_the_saved_bestiary() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = true
	ctl.bestiary.roll_openings = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	ctl.start_battle(active, reserve, TIDELINE, SEED, null)
	var guard := 0
	while guard < 50 and not (ctl.engine.is_party_turn() and ctl.engine.current.id == &"rhen"):
		guard += 1
		if ctl.engine.is_party_turn():
			ctl.act(&"mend", [&"rhen"])
	assert_eq(ctl.current_actor_id(), &"rhen")
	var crab := ctl.engine.enemies[0]
	assert_true(ctl.act(&"read", [crab.id]).ok, "Rhen reads %s" % crab.id)
	assert_true(Bestiary.new(Game.state.bestiary).is_read(&"reef_crab"), "logged into the save")
	assert_eq(ctl.bestiary.last_reveal["lore_key"], "LORE_REEF_CRAB")
	_done()


# --- helpers -------------------------------------------------------------------------------------


func _engine(encounter: StringName) -> BattleEngine:
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	e.setup(BattleDB.load_default(), active, reserve, encounter, SEED)
	return e


## Rhen reads the first unread living foe on each of his turns; Asha mends him on hers, so nobody
## falls before it is read. Returns the enemy ids read, in order.
func _read_all(e: BattleEngine) -> Array[StringName]:
	var read: Array[StringName] = []
	var guard := 0
	while e.outcome == &"" and guard < 200 and read.size() < e.enemies.size():
		guard += 1
		if not e.is_party_turn():
			e.run_enemy_turn()
			continue
		var rhen := e.find(&"rhen")
		if e.current.id != &"rhen":
			assert_true(e.perform(&"mend", [rhen] as Array[BattleCombatant]).ok, "Asha mends")
			continue
		var next := e.enemies[read.size()]
		var r := e.perform(&"read", [next] as Array[BattleCombatant])
		assert_true(r.ok, "Rhen reads %s" % next.id)
		assert_true(r.hits[0].has("read"), "the hit carries the reveal")
		read.append(BattleEngine.enemy_id(next))
	return read


func _done() -> void:
	if ctl != null:
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null
	Game.state = _saved_state
