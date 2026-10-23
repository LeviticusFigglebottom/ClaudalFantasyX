class_name DebugReadouts
extends RefCounted
## The logic behind each debug overlay page (M1-ARC-02), kept free of UI so tests can call it.
## Developer-facing text: not localized (the overlay never ships).

const DATA_PATH := "res://game/data/debug/debug_overlay.json"
## Keys an encounter provider's debug_encounter_state() may return (all optional).
const ENCOUNTER_KEYS: Array[String] = [
	"zone_id", "enabled", "danger", "threshold", "steps", "rate_per_step", "modifier", "table_id", "next_formation"
]
const NO_ENCOUNTERS := "no encounter provider in this scene (random encounters arrive with M2 zones)"
const NO_BATTLE := "no active battle (open the sandbox with F9)"
const FIGHTER_HEADER := "%-16s %-6s %-3s %9s %4s %5s %5s %6s %5s  %s"
const PREDICTED_PER_LINE := 6
## ticks_until for a reserve member, who is not on the timeline.
const RESERVE_TICKS := -1


static func config() -> Dictionary:
	return FieldInput.load_json(DATA_PATH)


# --- F2 turn order -------------------------------------------------------------------------------


## Everything CTB knows: clock, current actor, each fighter's timing inputs, and the prediction.
static func turn_order(engine: BattleEngine, preview: int) -> Dictionary:
	if engine == null:
		return {}
	var fighters: Array[Dictionary] = []
	for c in engine.party_active + engine.enemies + engine.party_reserve:
		fighters.append(_fighter(engine, c))
	fighters.sort_custom(_turn_order_before)
	var predicted: Array[Dictionary] = []
	for e in engine.timeline.predict(preview):
		predicted.append({"id": e.combatant_id, "time": e.time, "team": e.team, "skipped": e.skipped})
	return {
		"encounter": engine.encounter_id,
		"now": engine.now,
		"current": engine.current.id if engine.current != null else &"",
		"outcome": engine.outcome,
		"seed": engine.rng.seed,
		"fighters": fighters,
		"predicted": predicted,
	}


static func turn_order_lines(engine: BattleEngine, preview: int) -> PackedStringArray:
	var d := turn_order(engine, preview)
	var out := PackedStringArray()
	if d.is_empty():
		out.append(NO_BATTLE)
		return out
	out.append(
		"encounter %s  now t=%d  current %s  outcome %s" % [d["encounter"], d["now"], d["current"], d["outcome"]]
	)
	out.append(FIGHTER_HEADER % ["id", "team", "on", "hp", "agi", "spd", "delay", "next", "in", "status"])
	for f: Dictionary in d["fighters"]:
		out.append(_fighter_line(f))
	var order := PackedStringArray()
	for p: Dictionary in d["predicted"]:
		order.append("%s@%d%s" % [p["id"], p["time"], "(skip)" if p["skipped"] else ""])
	out.append("next %d:" % order.size())
	for i in range(0, order.size(), PREDICTED_PER_LINE):
		out.append("  " + "  ".join(order.slice(i, i + PREDICTED_PER_LINE)))
	return out


static func _fighter(engine: BattleEngine, c: BattleCombatant) -> Dictionary:
	var active := not engine.party_reserve.has(c)
	return {
		"id": c.id,
		"team": c.team,
		"active": active,
		"hp": c.hp,
		"max_hp": c.max_hp,
		"agility": c.agility,
		"speed_mult": c.speed_mult(),
		"base_delay": Formulas.base_delay(c.agility),
		"next_time": c.next_time,
		"ticks_until": c.next_time - engine.now if active else RESERVE_TICKS,
		"turns_taken": c.turns_taken,
		"statuses": c.statuses.duplicate(),
	}


## Fighters on the field by next turn time; reserves (off the timeline) last.
static func _turn_order_before(a: Dictionary, b: Dictionary) -> bool:
	if bool(a["active"]) != bool(b["active"]):
		return bool(a["active"])
	return int(a["next_time"]) < int(b["next_time"])


static func _fighter_line(f: Dictionary) -> String:
	var ticks := str(f["ticks_until"]) if bool(f["active"]) else "-"
	var values := [
		f["id"],
		f["team"],
		"yes" if f["active"] else "res",
		"%d/%d" % [f["hp"], f["max_hp"]],
		f["agility"],
		"%.2f" % f["speed_mult"],
		f["base_delay"],
		f["next_time"],
		ticks,
		_statuses(f["statuses"] as Dictionary),
	]
	return FIGHTER_HEADER % values


# --- F3 encounters -------------------------------------------------------------------------------


## Reads a provider's debug_encounter_state(); unknown keys are dropped, missing ones absent.
static func encounter_state(provider: Object) -> Dictionary:
	if provider == null or not provider.has_method(DebugHooks.METHOD_ENCOUNTERS):
		return {}
	var raw: Variant = provider.call(DebugHooks.METHOD_ENCOUNTERS)
	var out := {}
	if raw is Dictionary:
		for k: String in ENCOUNTER_KEYS:
			if (raw as Dictionary).has(k):
				out[k] = (raw as Dictionary)[k]
	return out


static func encounter_lines(provider: Object) -> PackedStringArray:
	var s := encounter_state(provider)
	var out := PackedStringArray()
	if s.is_empty():
		out.append(NO_ENCOUNTERS)
		return out
	for k: String in ENCOUNTER_KEYS:
		if s.has(k):
			out.append("%-15s %s" % [k, str(s[k])])
	if s.has("danger") and s.has("threshold") and float(s["threshold"]) > 0.0:
		out.append("%-15s %.0f%%" % ["meter", 100.0 * float(s["danger"]) / float(s["threshold"])])
	return out


# --- F4 flags ------------------------------------------------------------------------------------


## Every declared flag, sorted, with its current value (null = never set) and description.
static func flag_rows() -> Array[Dictionary]:
	var names: Array = Game.registry.flags.keys()
	names.sort()
	var out: Array[Dictionary] = []
	for n: Variant in names:
		var flag := StringName(str(n))
		var value: Variant = Game.get_flag(flag, null)
		var row := {
			"name": flag,
			"value": value,
			"description": Game.registry.description(flag),
			"toggleable": value == null or value is bool,
		}
		out.append(row)
	return out


## Flips a boolean (or unset) flag through Game.set_flag. Returns false for non-bool values.
static func toggle_flag(flag: StringName) -> bool:
	if not Game.registry.is_declared(flag):
		return false
	var value: Variant = Game.get_flag(flag, null)
	if value != null and not value is bool:
		return false
	Game.set_flag(flag, not bool(value))
	return true


# --- F5 teleports --------------------------------------------------------------------------------


## Valid teleport entries ({id, label, scene, spawn}); entries whose scene is missing are dropped.
static func teleports(path: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for row: Variant in FieldInput.load_json(path).get("teleports", []):
		var e := row as Dictionary
		var scene := str(e.get("scene", ""))
		if not ResourceLoader.exists(scene):
			push_warning("DebugReadouts: teleport '%s' points at a missing scene %s" % [e.get("id", ""), scene])
			continue
		var entry := {
			"id": StringName(str(e.get("id", ""))),
			"label": str(e.get("label", scene)),
			"scene": scene,
			"spawn": StringName(str(e.get("spawn", ""))),
		}
		out.append(entry)
	return out


# --- F6 Lattice cheat ----------------------------------------------------------------------------


## The progress to cheat on: the live source's, or one rebuilt from Game.state.lattice.
## Returns {progress: LatticeProgress, inventory: FacetInventory, persist: bool}.
static func lattice_target(source: Object, cfg: Dictionary) -> Dictionary:
	if source != null and source.has_method(DebugHooks.METHOD_LATTICE):
		var live := source.call(DebugHooks.METHOD_LATTICE) as LatticeProgress
		if live != null:
			var inv: FacetInventory = null
			if source.has_method(DebugHooks.METHOD_FACETS):
				inv = source.call(DebugHooks.METHOD_FACETS) as FacetInventory
			return {
				"progress": live,
				"inventory": inv if inv != null else FacetInventory.new(Game.state.inventory),
				"persist": false
			}
	var board := LatticeBoard.load_board(StringName(str(cfg.get("board", LatticeBoard.DEFAULT_BOARD))))
	var rules := LatticeRules.load_file()
	var progress: LatticeProgress
	if Game.state.lattice.is_empty():
		progress = LatticeProgress.new(board, rules)
	else:
		progress = LatticeProgress.from_dict(Game.state.lattice, board, rules)
	return {"progress": progress, "inventory": FacetInventory.new(Game.state.inventory), "persist": true}


## Party members to cheat for: the saved party and reserve, or the configured fallback list,
## keeping only characters with a start on the board.
static func lattice_characters(progress: LatticeProgress, cfg: Dictionary) -> Array[StringName]:
	var ids: Array[StringName] = []
	ids.append_array(Game.state.party_ids)
	ids.append_array(Game.state.reserve_ids)
	if ids.is_empty():
		for c: Variant in cfg.get("fallback_characters", []):
			ids.append(StringName(str(c)))
	var out: Array[StringName] = []
	for cid in ids:
		if progress.board.start_of(cid) != &"" and not out.has(cid):
			out.append(cid)
	return out


## Grants `points` movement points to `cid` (placing them on their start if new). Returns the new
## balance, or -1 if the character cannot join the board.
static func grant_movement(progress: LatticeProgress, cid: StringName, points: int) -> int:
	if not progress.add_character(cid):
		return -1
	var t := progress.traveler(cid)
	t.movement_points += points
	return t.movement_points


## Adds `amount` of every Facet type the rules define. Returns the ids granted.
static func grant_facets(progress: LatticeProgress, inventory: FacetInventory, amount: int) -> Array[StringName]:
	var out: Array[StringName] = []
	for fid: StringName in progress.rules.facets:
		inventory.add(fid, amount)
		out.append(fid)
	return out


## Applies the whole cheat (movement for every party member, Facets of every type) and writes
## rebuilt progress back to Game.state. Returns {characters: {id: balance}, facets: [ids]}.
static func apply_lattice_cheat(source: Object, cfg: Dictionary) -> Dictionary:
	var target := lattice_target(source, cfg)
	var progress := target["progress"] as LatticeProgress
	var balances := {}
	for cid in lattice_characters(progress, cfg):
		balances[cid] = grant_movement(progress, cid, int(cfg.get("movement_points", 0)))
	var facets := grant_facets(progress, target["inventory"] as FacetInventory, int(cfg.get("facets_each", 0)))
	if bool(target["persist"]):
		Game.state.lattice = progress.to_dict()
	return {"characters": balances, "facets": facets}


static func lattice_lines(source: Object, cfg: Dictionary) -> PackedStringArray:
	var target := lattice_target(source, cfg)
	var progress := target["progress"] as LatticeProgress
	var inv := target["inventory"] as FacetInventory
	var out := PackedStringArray()
	out.append("source: %s" % ("live screen" if not bool(target["persist"]) else "Game.state (saved progress)"))
	for cid in lattice_characters(progress, cfg):
		var t := progress.traveler(cid)
		if t == null:
			out.append("%-8s not on the board yet" % cid)
		else:
			out.append(
				(
					"%-8s at %-10s move %3d  lp %4d  nodes %d"
					% [cid, t.position, t.movement_points, t.lattice_points, t.activated.size()]
				)
			)
	var facets := PackedStringArray()
	for fid: StringName in progress.rules.facets:
		facets.append("%s %d" % [fid, inv.count(fid)])
	out.append("facets: %s" % ", ".join(facets))
	out.append(
		(
			"[Enter] grant +%d movement to each and +%d of every Facet"
			% [int(cfg.get("movement_points", 0)), int(cfg.get("facets_each", 0))]
		)
	)
	return out


# --- F7 camera -----------------------------------------------------------------------------------


static func camera_lines(director: FieldCameraDirector) -> PackedStringArray:
	var out := PackedStringArray()
	if director == null:
		out.append("no FieldCameraDirector in this scene")
		return out
	var s := director.state_snapshot()
	out.append("shot %s  volume %s  inside %d" % [s["shot"], s["volume"], s["inside"]])
	out.append("blending %s  weight %.2f  over %.2f s" % [s["blending"], s["blend_weight"], s["blend_sec"]])
	out.append("history: %s" % " > ".join(PackedStringArray(s["history"] as Array)))
	return out


static func _statuses(statuses: Dictionary) -> String:
	var parts := PackedStringArray()
	for sid: Variant in statuses:
		parts.append("%s:%s" % [sid, statuses[sid]])
	return ",".join(parts) if not parts.is_empty() else "-"
