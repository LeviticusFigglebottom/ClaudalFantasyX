class_name LatticeProgress
extends RefCounted
## The party's progress on one Lattice board (SPEC §6.4): each character's position,
## activations, and movement points, plus the gates anyone has opened. Headless and
## deterministic; persisted through to_dict()/from_dict() in GameStateData.lattice.
##
## Rules (docs/kb/design/lattice.md):
## - Stepping onto an adjacent node costs rules.move_cost movement points, or
##   rules.move_cost_activated if ANY character has activated it (or it is an opened gate).
## - A closed gate cannot be entered. Open it from an adjacent node with a Key Facet of exactly
##   its level; opened gates stay open for everyone.
## - Activating the node you stand on costs one Facet of the matching type and no movement.
##   Each character activates nodes separately; bonuses apply only to whoever activated them.
##
## M1-ARC-13 (QA review-sweep-I S1; ADR 0018 Amendment 5): saved progress is never dropped.
## - An activated node id the board does not know stays in the traveler's set (it grants nothing
##   and round-trips untouched); a lost position puts the traveler on their start, and the saved
##   position is written back until they move (LatticeTraveler.saved_position).
## - A character with no start on the board, and an opened gate the board has no gate for, are
##   kept as saved (kept_characters, kept_gates) and written back by to_dict.
## - While the board or the rules are broken (integrity_problem), from_dict places nobody: the
##   whole saved dict is frozen and to_dict returns it as it was.
## M1-ARC-14 (QA review-sweep-J S1/S2):
## - A save that names a board other than the one it is restored onto is frozen the same way: its
##   "board" field and positions are never rewritten. Writers load the board the save names
##   (board_for), so in practice only a save whose board id is not a valid id is frozen this way.
## - A lost position does not add the start to the saved activations: the start counts as
##   activated in memory (LatticeTraveler.implied_start) and joins `activated` on the first move.

const RESULT_OK := &"ok"
const ERR_UNKNOWN_CHARACTER := &"unknown_character"
const ERR_UNKNOWN_NODE := &"unknown_node"
const ERR_NOT_ADJACENT := &"not_adjacent"
const ERR_GATE_CLOSED := &"gate_closed"
const ERR_NO_MOVEMENT := &"no_movement_points"
const ERR_NOT_ACTIVATABLE := &"not_activatable"
const ERR_ALREADY_ACTIVATED := &"already_activated"
const ERR_NO_FACET := &"no_facet"
const ERR_NOT_A_GATE := &"not_a_gate"
const ERR_GATE_OPEN := &"gate_already_open"
const MOVE_ILLEGAL := -1

var board: LatticeBoard
var rules: LatticeRules
## Character id -> LatticeTraveler.
var travelers: Dictionary = {}
## Set of opened gate node ids (id -> true).
var opened_gates: Dictionary = {}
## Character id (String) -> the saved traveler dict, for characters this board has no start for.
var kept_characters: Dictionary = {}
## Saved opened-gate ids that are not gates on this board.
var kept_gates: Array[String] = []
## The saved gate order (to_dict keeps it, so a round trip changes nothing).
var _gate_order: Array[String] = []
## The whole saved dict while from_dict froze it ({} otherwise): see is_frozen.
var _frozen: Dictionary = {}
## True when from_dict froze the save (broken board or rules, or another board's save), even when
## the saved dict was empty.
var _frozen_flag := false


func _init(lattice_board: LatticeBoard = null, lattice_rules: LatticeRules = null) -> void:
	board = lattice_board if lattice_board != null else LatticeBoard.new()
	rules = lattice_rules if lattice_rules != null else LatticeRules.new()


## Places a character on their start node (which counts as activated by them). Returns false
## if the board has no start for them, or the progress is frozen (is_frozen). Calling it again
## for a known character is a no-op.
func add_character(cid: StringName) -> bool:
	if travelers.has(cid):
		return true
	if is_frozen():
		return false
	var start := board.start_of(cid)
	if start == &"":
		return false
	var t := LatticeTraveler.new()
	t.character_id = cid
	t.position = start
	t.activated[start] = true
	travelers[cid] = t
	return true


func traveler(cid: StringName) -> LatticeTraveler:
	return travelers.get(cid) as LatticeTraveler


func is_activated_by(cid: StringName, node_id: StringName) -> bool:
	var t := traveler(cid)
	return t != null and t.has_activated(node_id)


## True if any character activated the node, or it is a gate someone opened.
func is_activated_by_anyone(node_id: StringName) -> bool:
	if opened_gates.has(node_id):
		return true
	for t: LatticeTraveler in travelers.values():
		if t.has_activated(node_id):
			return true
	return false


func is_gate_open(node_id: StringName) -> bool:
	return opened_gates.has(node_id)


## Movement points needed to step onto `node_id` from anywhere next to it, or MOVE_ILLEGAL
## for an unknown node or a closed gate.
func entry_cost(node_id: StringName) -> int:
	var n := board.lattice_node(node_id)
	if n == null or (n.is_gate() and not is_gate_open(node_id)):
		return MOVE_ILLEGAL
	return rules.move_cost_activated if is_activated_by_anyone(node_id) else rules.move_cost


## Cost for `cid` to step from their position to the adjacent `to`; MOVE_ILLEGAL if they can't.
func move_cost(cid: StringName, to: StringName) -> int:
	var t := traveler(cid)
	if t == null or not board.are_adjacent(t.position, to):
		return MOVE_ILLEGAL
	return entry_cost(to)


## Steps `cid` onto the adjacent node `to`, spending movement points. Returns RESULT_OK or an ERR_*.
func move(cid: StringName, to: StringName) -> StringName:
	var t := traveler(cid)
	if t == null:
		return ERR_UNKNOWN_CHARACTER
	if not board.has_lattice_node(to):
		return ERR_UNKNOWN_NODE
	if not board.are_adjacent(t.position, to):
		return ERR_NOT_ADJACENT
	var cost := entry_cost(to)
	if cost == MOVE_ILLEGAL:
		return ERR_GATE_CLOSED
	if t.movement_points < cost:
		return ERR_NO_MOVEMENT
	t.movement_points -= cost
	t.position = to
	t.saved_position = &""
	if t.implied_start != &"":
		t.activated[t.implied_start] = true
		t.implied_start = &""
	return RESULT_OK


## Cheapest route for `cid` to `to` (0-1 BFS over entry costs, closed gates blocked), inclusive
## of both ends; [] if unreachable. Ties prefer fewer hops, then edge order (deterministic).
func cheapest_path(cid: StringName, to: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	var t := traveler(cid)
	if t == null or not board.has_lattice_node(to):
		return out
	var dist: Dictionary = {t.position: 0}
	var came: Dictionary = {}
	var deque: Array[StringName] = [t.position]
	while not deque.is_empty():
		var cur: StringName = deque.pop_front()
		for nb in board.neighbors(cur):
			var step := entry_cost(nb)
			if step == MOVE_ILLEGAL:
				continue
			var nd: int = int(dist[cur]) + step
			if not dist.has(nb) or nd < int(dist[nb]):
				dist[nb] = nd
				came[nb] = cur
				if step == 0:
					deque.push_front(nb)
				else:
					deque.push_back(nb)
	if not dist.has(to):
		return out
	var node := to
	while node != t.position:
		out.push_front(node)
		node = came[node]
	out.push_front(t.position)
	return out


## The Facet item id needed to activate the node `cid` stands on (&"" if it can't be activated).
func activation_facet(cid: StringName) -> StringName:
	var t := traveler(cid)
	if t == null:
		return &""
	var n := board.lattice_node(t.position)
	if n == null or not n.is_activatable():
		return &""
	return rules.facet_for(n)


## Why `cid` can't activate their current node right now, or RESULT_OK.
func activate_error(cid: StringName, inventory: FacetInventory) -> StringName:
	var t := traveler(cid)
	if t == null:
		return ERR_UNKNOWN_CHARACTER
	var n := board.lattice_node(t.position)
	if n == null or not n.is_activatable():
		return ERR_NOT_ACTIVATABLE
	if t.activated.has(n.id):
		return ERR_ALREADY_ACTIVATED
	if not inventory.has(rules.facet_for(n), rules.facet_cost(n)):
		return ERR_NO_FACET
	return RESULT_OK


## Activates the node `cid` stands on, consuming its Facet. Returns RESULT_OK or an ERR_*.
func activate(cid: StringName, inventory: FacetInventory) -> StringName:
	var err := activate_error(cid, inventory)
	if err != RESULT_OK:
		return err
	var t := traveler(cid)
	var n := board.lattice_node(t.position)
	inventory.consume(rules.facet_for(n), rules.facet_cost(n))
	t.activated[n.id] = true
	return RESULT_OK


## Why `cid` can't open `gate_id` right now, or RESULT_OK.
func open_gate_error(cid: StringName, gate_id: StringName, inventory: FacetInventory) -> StringName:
	var t := traveler(cid)
	if t == null:
		return ERR_UNKNOWN_CHARACTER
	var n := board.lattice_node(gate_id)
	var gate_err := _gate_state_error(n)
	if gate_err != RESULT_OK:
		return gate_err
	if not board.are_adjacent(t.position, gate_id):
		return ERR_NOT_ADJACENT
	if not inventory.has(rules.facet_for(n), rules.facet_cost(n)):
		return ERR_NO_FACET
	return RESULT_OK


## Opens an adjacent gate for everyone, consuming a Key Facet of its level. Returns RESULT_OK or ERR_*.
func open_gate(cid: StringName, gate_id: StringName, inventory: FacetInventory) -> StringName:
	var err := open_gate_error(cid, gate_id, inventory)
	if err != RESULT_OK:
		return err
	var n := board.lattice_node(gate_id)
	inventory.consume(rules.facet_for(n), rules.facet_cost(n))
	opened_gates[gate_id] = true
	return RESULT_OK


## Banks LP from one battle and converts it into movement points (formulas.md, Progression).
## `credited_xp` is what BattleEngine.xp_awards() gave this character. Returns points gained.
func award_battle(cid: StringName, credited_xp: int) -> int:
	var t := traveler(cid)
	if t == null:
		return 0
	t.lattice_points += ProgressionFormulas.lp_gain(credited_xp)
	var r := ProgressionFormulas.convert_lp(
		t.lattice_points, t.movement_earned, ProgressionFormulas.movement_room(t.movement_points)
	)
	t.movement_points += r.x
	t.movement_earned += r.x
	t.lattice_points = r.y
	return r.x


## Sum of activated stat-node bonuses for `cid`: stat name -> total.
func stat_bonuses(cid: StringName) -> Dictionary:
	var out: Dictionary = {}
	var t := traveler(cid)
	if t == null:
		return out
	for nid: StringName in t.activated:
		var n := board.lattice_node(nid)
		if n != null and n.kind == LatticeNode.KIND_STAT:
			out[n.stat] = int(out.get(n.stat, 0)) + n.value
	return out


## Skills from activated ability nodes, in activation order, without duplicates.
func learned_skills(cid: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	var t := traveler(cid)
	if t == null:
		return out
	for nid: StringName in t.activated:
		var n := board.lattice_node(nid)
		if n != null and n.kind == LatticeNode.KIND_ABILITY and not out.has(n.skill):
			out.append(n.skill)
	return out


## Layers this character's Lattice gains onto a freshly built combatant (base stats come from
## characters.json via BattleCombatant.from_dict). Call it ONCE per combatant: it adds.
func apply_to(c: BattleCombatant) -> void:
	var bonus := stat_bonuses(c.id)
	for stat: StringName in bonus:
		_add_stat(c, stat, int(bonus[stat]))
	for s in learned_skills(c.id):
		if not c.skills.has(s):
			c.skills.append(s)


func to_dict() -> Dictionary:
	if is_frozen():
		return _frozen.duplicate(true)
	var chars: Dictionary = {}
	for cid: StringName in travelers:
		chars[String(cid)] = (travelers[cid] as LatticeTraveler).to_dict()
	for key: String in kept_characters:
		if not chars.has(key):
			chars[key] = (kept_characters[key] as Dictionary).duplicate(true)
	var gates: Array[String] = []
	for g in _gate_order:
		if not gates.has(g) and (opened_gates.has(StringName(g)) or kept_gates.has(g)):
			gates.append(g)
	for gid: StringName in opened_gates:
		if not gates.has(String(gid)):
			gates.append(String(gid))
	return {"board": String(board.id), "characters": chars, "opened_gates": gates}


## Why this progress must not be written back over saved progress ("" when it may): its board or
## rules are broken (LatticeBoard / LatticeRules integrity_problem). BattleRewards and the F6
## cheat check it before writing Game.state.lattice.
func integrity_problem() -> String:
	var problem := board.integrity_problem()
	if problem == "":
		problem = rules.integrity_problem()
	return problem


## Writes this progress into `state.lattice`, unless its board or rules are broken (M1-ARC-13,
## review-sweep-I S1): then the state keeps its saved progress exactly as it was, with a
## push_error. Returns true when it wrote. BattleRewards and the F6 cheat write through this.
func save_into(state: GameStateData) -> bool:
	var problem := integrity_problem()
	if problem != "":
		push_error("LatticeProgress: the Lattice tables are broken (%s); saved Lattice progress is kept" % problem)
		return false
	state.lattice = to_dict()
	return true


## True when from_dict kept the saved dict as it was: the board or rules were broken, or the save
## names another board (M1-ARC-14). Also true for an empty saved dict, so nobody is added.
func is_frozen() -> bool:
	return _frozen_flag


## The board to restore `saved` (GameStateData.lattice) onto (M1-ARC-14, review-sweep-J S1): the
## board the save names, or `configured` when it names none. A save naming an id that is not a
## valid board id (LatticeBoard.is_valid_id) is refused: it gets `configured`, which from_dict then
## freezes it against, and no path is built from the id. BattleStage and the F6 cheat load through it.
static func board_for(saved: Dictionary, configured: StringName) -> LatticeBoard:
	var named := str(saved.get("board", ""))
	if named == "":
		return LatticeBoard.load_board(configured)
	if not LatticeBoard.is_valid_id(named):
		push_error("LatticeProgress: the save names an invalid Lattice board id '%s'; it is kept as saved" % named)
		return LatticeBoard.load_board(configured)
	return LatticeBoard.load_board(StringName(named))


## Restores progress onto `lattice_board`. Nothing saved is ever dropped (M1-ARC-13): see the
## class comment. While the board or rules are broken, or the save names another board
## (M1-ARC-14), the save is frozen whole, with a push_error.
static func from_dict(d: Dictionary, lattice_board: LatticeBoard, lattice_rules: LatticeRules) -> LatticeProgress:
	var p := LatticeProgress.new(lattice_board, lattice_rules)
	var problem := p.integrity_problem()
	if problem != "":
		problem = "the Lattice tables are broken (%s)" % problem
	var named := str(d.get("board", ""))
	if problem == "" and named != "" and StringName(named) != p.board.id:
		problem = "the save names board '%s', not '%s'" % [named, p.board.id]
	if problem != "":
		push_error("LatticeProgress: %s; saved progress is kept as it is" % problem)
		p._frozen = d.duplicate(true)
		p._frozen_flag = true
		return p
	var chars: Dictionary = d.get("characters", {})
	for key: Variant in chars:
		var cid := StringName(str(key))
		var t := LatticeTraveler.from_dict(cid, chars[key] as Dictionary)
		for nid: StringName in t.activated:
			if not p.board.has_lattice_node(nid):
				push_warning("LatticeProgress: %s keeps unknown node '%s'; it grants nothing" % [cid, nid])
		if not p.board.has_lattice_node(t.position):
			var start := p.board.start_of(cid)
			if start == &"":
				push_warning("LatticeProgress: %s has no start on board '%s'; kept as saved" % [cid, p.board.id])
				p.kept_characters[String(cid)] = (chars[key] as Dictionary).duplicate(true)
				continue
			push_warning(
				"LatticeProgress: %s stands on unknown node '%s'; on the start until moved" % [cid, t.position]
			)
			t.saved_position = t.position
			t.position = start
			if not t.activated.has(start):
				t.implied_start = start
		p.travelers[cid] = t
	for gid: Variant in d.get("opened_gates", []):
		var g := String(StringName(str(gid)))
		p._gate_order.append(g)
		var n := p.board.lattice_node(StringName(g))
		if n != null and n.is_gate():
			p.opened_gates[StringName(g)] = true
		elif not p.kept_gates.has(g):
			push_warning(
				"LatticeProgress: opened gate '%s' is not a gate on board '%s'; kept as saved" % [g, p.board.id]
			)
			p.kept_gates.append(g)
	return p


func _gate_state_error(n: LatticeNode) -> StringName:
	if n == null:
		return ERR_UNKNOWN_NODE
	if not n.is_gate():
		return ERR_NOT_A_GATE
	if is_gate_open(n.id):
		return ERR_GATE_OPEN
	return RESULT_OK


static func _add_stat(c: BattleCombatant, stat: StringName, amount: int) -> void:
	match stat:
		&"hp":
			c.max_hp += amount
			c.hp += amount
		&"mp":
			c.max_mp += amount
			c.mp += amount
		&"strength":
			c.strength += amount
		&"magic":
			c.magic += amount
		&"defense":
			c.defense += amount
		&"magic_defense":
			c.magic_defense += amount
		&"agility":
			c.agility += amount
		&"accuracy":
			c.accuracy += amount
		&"evasion":
			c.evasion += amount
		&"luck":
			c.luck += amount
		_:
			push_error("LatticeProgress: unknown stat '%s'" % stat)
