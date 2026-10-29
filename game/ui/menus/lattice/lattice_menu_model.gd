class_name LatticeMenuModel
extends RefCounted
## The words and the actions of the Lattice page (M2-MNU-01, SPEC §6.4, pillars 4 and 5), over a
## PartySheet. Node-free: tests read exactly what the page shows.
##
## It writes no rules of its own: every cost, path and refusal comes from LatticeProgress
## (entry_cost, cheapest_path, activate_error, open_gate_error and their ERR_* codes), every Facet
## from LatticeRules and FacetInventory (the party bag, in place). After a change it saves through
## PartySheet.save_lattice(), which LatticeProgress.save_into refuses while the tables are broken;
## the page then says so. While they are broken nothing is offered at all (broken_problem()).
##
## plan(node) answers "what would Confirm do here, what does it cost, and why not?" before anything
## is spent; act(node) does it. A plan: {action, error, path, cost, left, text, confirm, ok}.

const ACT_NONE := &"none"
const ACT_WALK := &"walk"
const ACT_ACTIVATE := &"activate"
const ACT_OPEN := &"open"
## How a node stands for the hero on show (the board view's look and the side panel's words).
const STATE_NEW := &"new"
const STATE_MINE := &"mine"
const STATE_TRODDEN := &"trodden"
const STATE_GATE_CLOSED := &"gate_closed"
const STATE_GATE_OPEN := &"gate_open"
const STATE_EMPTY := &"empty"
## Every LatticeProgress ERR_* code, in words (tests check that none is missing).
const ERR_KEYS := {
	LatticeProgress.ERR_UNKNOWN_CHARACTER: "LATTICE_MENU_ERR_UNKNOWN_CHARACTER",
	LatticeProgress.ERR_UNKNOWN_NODE: "LATTICE_MENU_ERR_UNKNOWN_NODE",
	LatticeProgress.ERR_NOT_ADJACENT: "LATTICE_MENU_ERR_NOT_ADJACENT",
	LatticeProgress.ERR_GATE_CLOSED: "LATTICE_MENU_ERR_GATE_CLOSED",
	LatticeProgress.ERR_NO_MOVEMENT: "LATTICE_MENU_ERR_NO_MOVEMENT",
	LatticeProgress.ERR_NOT_ACTIVATABLE: "LATTICE_MENU_ERR_NOT_ACTIVATABLE",
	LatticeProgress.ERR_ALREADY_ACTIVATED: "LATTICE_MENU_ERR_ALREADY_ACTIVATED",
	LatticeProgress.ERR_NO_FACET: "LATTICE_MENU_ERR_NO_FACET",
	LatticeProgress.ERR_NOT_A_GATE: "LATTICE_MENU_ERR_NOT_A_GATE",
	LatticeProgress.ERR_GATE_OPEN: "LATTICE_MENU_ERR_GATE_OPEN",
}
## The Lattice stats, each with its name key (hp and mp are the maxima a node raises).
const STAT_KEYS := {
	"hp": "LATTICE_MENU_STAT_HP",
	"mp": "LATTICE_MENU_STAT_MP",
	"strength": "STAT_STRENGTH",
	"magic": "STAT_MAGIC",
	"defense": "STAT_DEFENSE",
	"magic_defense": "STAT_MAGIC_DEFENSE",
	"agility": "STAT_AGILITY",
	"accuracy": "STAT_ACCURACY",
	"evasion": "STAT_EVASION",
	"luck": "STAT_LUCK",
}
const LIST_SEPARATOR := " · "

var sheet: PartySheet
## Index into heroes() of the hero on show.
var hero_index := 0


func _init(with_sheet: PartySheet = null) -> void:
	sheet = with_sheet if with_sheet != null else PartySheet.from_game()


# --- The party and the board -----------------------------------------------------------------------


func progress() -> LatticeProgress:
	return sheet.lattice


func board() -> LatticeBoard:
	return sheet.lattice.board


func rules() -> LatticeRules:
	return sheet.lattice.rules


## The party's Facets: the bag itself, in place.
func facets() -> FacetInventory:
	return sheet.goods.inventory.facets()


## The heroes who walk this board (a hero with no start on it has no Lattice path yet), in party order.
func heroes() -> Array[StringName]:
	var out: Array[StringName] = []
	for cid in sheet.heroes:
		if progress().traveler(cid) != null and not out.has(cid):
			out.append(cid)
	return out


## The hero on show (&"" when nobody walks the board).
func hero() -> StringName:
	var list := heroes()
	if list.is_empty():
		return &""
	return list[clampi(hero_index, 0, list.size() - 1)]


## Shows the next (delta 1) or previous (-1) hero, wrapping. False when there is no one else.
func switch_hero(delta: int) -> bool:
	var count := heroes().size()
	if count < 2:
		return false
	hero_index = posmod(hero_index + delta, count)
	return true


## Shows `cid` if they walk the board. Returns true when they do.
func show_hero(cid: StringName) -> bool:
	var at := heroes().find(cid)
	if at < 0:
		return false
	hero_index = at
	return true


func hero_name(cid: StringName = &"") -> String:
	return sheet.hero_name(cid if cid != &"" else hero())


func traveler() -> LatticeTraveler:
	return progress().traveler(hero())


## Where the hero on show stands (&"" when nobody walks the board).
func position() -> StringName:
	var t := traveler()
	return t.position if t != null else &""


func movement_points() -> int:
	var t := traveler()
	return t.movement_points if t != null else 0


## Why nothing on this page may change ("" when it may): the board or rules are broken.
func broken_problem() -> String:
	return progress().integrity_problem()


func title() -> String:
	var key := board().name_key
	return tr(key) if key != "" else tr("FIELD_MENU_LATTICE")


# --- Words for the panel ----------------------------------------------------------------------------


func points_text() -> String:
	return tr("LATTICE_MENU_POINTS_FMT").format({"n": movement_points()})


## Every Facet the party holds, in facets.json order ("Power Facet ×2 · ..."), or that none are held.
func facets_held_text() -> String:
	var parts: PackedStringArray = []
	var bag := facets()
	for fid: StringName in rules().facets:
		var n := bag.count(fid)
		if n > 0:
			parts.append(tr("LATTICE_MENU_FACET_HELD_FMT").format({"facet": facet_name(fid), "n": n}))
	if parts.is_empty():
		return tr("LATTICE_MENU_FACETS_NONE")
	return tr("LATTICE_MENU_FACETS_FMT").format({"list": LIST_SEPARATOR.join(parts)})


func facet_name(fid: StringName) -> String:
	var key := rules().facet_name_key(fid)
	return tr(key) if key != "" else String(fid)


func stat_name(stat: StringName) -> String:
	var key := str(STAT_KEYS.get(String(stat), ""))
	return tr(key) if key != "" else String(stat)


## What the node is, in a few words: "Agility +2", a skill's name, "Gate · Level 1", ...
func node_title(nid: StringName) -> String:
	var n := board().lattice_node(nid)
	if n == null:
		return ""
	match n.kind:
		LatticeNode.KIND_STAT:
			return tr("LATTICE_MENU_STAT_FMT").format({"stat": stat_name(n.stat), "n": n.value})
		LatticeNode.KIND_ABILITY:
			return _skill_name(n.skill)
		LatticeNode.KIND_GATE:
			return tr("LATTICE_MENU_GATE_FMT").format({"level": n.gate_level})
		LatticeNode.KIND_START:
			return tr("LATTICE_MENU_START_FMT").format({"name": hero_name(n.character)})
	return tr("LATTICE_MENU_EMPTY")


## What waking it gives (or what the node does), in a sentence.
func node_gives(nid: StringName) -> String:
	var n := board().lattice_node(nid)
	if n == null:
		return ""
	match n.kind:
		LatticeNode.KIND_STAT:
			return tr("LATTICE_MENU_GIVES_STAT_FMT").format({"stat": stat_name(n.stat), "n": n.value})
		LatticeNode.KIND_ABILITY:
			return tr("LATTICE_MENU_GIVES_SKILL_FMT").format(
				{"skill": _skill_name(n.skill), "help": skill_help(n.skill)}
			)
		LatticeNode.KIND_GATE:
			return tr("LATTICE_MENU_GIVES_GATE")
		LatticeNode.KIND_START:
			return tr("LATTICE_MENU_GIVES_START_FMT").format({"name": hero_name(n.character)})
	return tr("LATTICE_MENU_GIVES_EMPTY")


## The skill as the battle help line words it (kind and reach, what it inflicts, its delay), and its MP.
func skill_help(skill_id: StringName) -> String:
	var engine := BattleEngine.new()
	engine.db = sheet.battle_db
	var text := BattleMenus.new().skill_help(engine, skill_id, -1)
	var mp := int(sheet.battle_db.skill(skill_id).get("mp_cost", 0))
	if mp > 0:
		text += LIST_SEPARATOR + tr("LATTICE_MENU_SKILL_MP_FMT").format({"n": mp})
	return text


## Which Facet wakes or opens it, how many that takes and how many the party holds ("" for none).
func facet_line(nid: StringName) -> String:
	var n := board().lattice_node(nid)
	var fid := rules().facet_for(n)
	if fid == &"":
		return ""
	return tr("LATTICE_MENU_FACET_LINE_FMT").format(
		{"need": rules().facet_cost(n), "facet": facet_name(fid), "held": facets().count(fid)}
	)


## The heroes who woke it, in the board's traveler order (a start counts for its owner).
func woken_by(nid: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for cid: StringName in progress().travelers:
		if progress().is_activated_by(cid, nid):
			out.append(cid)
	return out


## M3-MNU-04: the first letter of each hero's name who woke it, in traveler order ("RA"; "" for
## none), for the overview's marks beside each woken node.
func woken_initials(nid: StringName) -> String:
	var out := ""
	for cid in woken_by(nid):
		out += hero_name(cid).left(1)
	return out


## Who woke it, in words; a gate says whether it stands open for everyone.
func woken_line(nid: StringName) -> String:
	var n := board().lattice_node(nid)
	if n == null:
		return ""
	if n.is_gate():
		return tr("LATTICE_MENU_GATE_OPEN") if progress().is_gate_open(nid) else tr("LATTICE_MENU_GATE_SEALED")
	if n.kind == LatticeNode.KIND_EMPTY:
		return ""
	var names: PackedStringArray = []
	for cid in woken_by(nid):
		names.append(hero_name(cid))
	if names.is_empty():
		return tr("LATTICE_MENU_WOKEN_NOBODY")
	return tr("LATTICE_MENU_WOKEN_BY_FMT").format({"names": ", ".join(names)})


## How the node stands for the hero on show (STATE_*).
func node_state(nid: StringName) -> StringName:
	var n := board().lattice_node(nid)
	if n == null:
		return STATE_EMPTY
	if n.is_gate():
		return STATE_GATE_OPEN if progress().is_gate_open(nid) else STATE_GATE_CLOSED
	if progress().is_activated_by(hero(), nid):
		return STATE_MINE
	if progress().is_activated_by_anyone(nid):
		return STATE_TRODDEN
	return STATE_EMPTY if n.kind == LatticeNode.KIND_EMPTY else STATE_NEW


## The page's key: each look a node can have and what it means, for the hero on show.
## [{kind, state, text}] (LatticeLegend draws each sample as the board does).
func legend_rows() -> Array[Dictionary]:
	return [
		{
			"kind": LatticeNode.KIND_STAT,
			"state": STATE_MINE,
			"marker": true,
			"text": tr("LATTICE_MENU_LEGEND_HERE_FMT").format({"name": hero_name()}),
		},
		{
			"kind": LatticeNode.KIND_STAT,
			"state": STATE_MINE,
			"text": tr("LATTICE_MENU_LEGEND_MINE_FMT").format({"name": hero_name()}),
		},
		{"kind": LatticeNode.KIND_STAT, "state": STATE_TRODDEN, "text": tr("LATTICE_MENU_LEGEND_TRODDEN")},
		{
			"kind": LatticeNode.KIND_STAT,
			"state": STATE_NEW,
			"text": tr("LATTICE_MENU_LEGEND_NEW_FMT").format({"n": rules().move_cost}),
		},
		{"kind": LatticeNode.KIND_ABILITY, "state": STATE_NEW, "text": tr("LATTICE_MENU_LEGEND_ABILITY")},
		{"kind": LatticeNode.KIND_GATE, "state": STATE_GATE_CLOSED, "text": tr("LATTICE_MENU_LEGEND_GATE")},
	]


## The words for an ERR_* code; `ctx` fills its {name}, {facet}, {held}, {need}, {cost}, {have}.
func error_text(code: StringName, ctx: Dictionary = {}) -> String:
	var full := {"name": hero_name()}
	full.merge(ctx, true)
	return tr(str(ERR_KEYS.get(code, "LATTICE_MENU_ERR_GENERIC"))).format(full)


# --- Plans and actions ------------------------------------------------------------------------------


## What Confirm on `nid` would do for the hero on show, what it costs, and why it can't be done.
## {action (ACT_*), error (RESULT_OK or an ERR_* / &"broken" / &"nothing"), ok, path, cost, left,
##  text (the line under the node's details), confirm (the confirm row's label); a walk beside a far sealed
##  gate (M2-MNU-10) also names its end, beside; a wake or a gate's opening that can be paid also names
##  its Facet cost, need and facet (the board's cost tag)}.
func plan(nid: StringName) -> Dictionary:
	var p := {
		"action": ACT_NONE,
		"error": LatticeProgress.RESULT_OK,
		"ok": false,
		"path": [] as Array[StringName],
		"cost": 0,
		"left": movement_points(),
		"text": "",
		"confirm": "",
	}
	if hero() == &"":
		return _refused(p, &"nothing", tr("LATTICE_MENU_NO_HEROES"))
	if broken_problem() != "":
		return _refused(p, &"broken", tr("LATTICE_MENU_BROKEN"))
	var n := board().lattice_node(nid)
	if n == null:
		return _refused(p, LatticeProgress.ERR_UNKNOWN_NODE, error_text(LatticeProgress.ERR_UNKNOWN_NODE))
	if nid == position():
		return _plan_here(p, n)
	if n.is_gate() and not progress().is_gate_open(nid):
		return _plan_gate(p, n)
	return _plan_walk(p, nid)


## Does what plan(nid) offers. Returns {ok, text}: what happened, or why nothing did, in words.
func act(nid: StringName) -> Dictionary:
	var p := plan(nid)
	if not bool(p["ok"]):
		return {"ok": false, "text": str(p["text"])}
	match StringName(str(p["action"])):
		ACT_WALK:
			return walk(p["path"] as Array[StringName])
		ACT_ACTIVATE:
			return activate()
		ACT_OPEN:
			return open_gate(nid)
	return {"ok": false, "text": str(p["text"])}


## Walks the hero along `path` (cheapest_path's, starting where they stand), one LatticeProgress.move
## a step, so each step costs exactly its entry cost. Stops at the first refusal and says why.
func walk(path: Array[StringName]) -> Dictionary:
	var before := movement_points()
	var steps := 0
	var err := LatticeProgress.RESULT_OK
	for i in range(1, path.size()):
		err = progress().move(hero(), path[i])
		if err != LatticeProgress.RESULT_OK:
			break
		steps += 1
	var text := ""
	if err != LatticeProgress.RESULT_OK:
		text = error_text(err, {"cost": path_cost(path), "have": before})
	else:
		text = tr("LATTICE_MENU_DONE_WALK_FMT").format(
			{"name": hero_name(), "steps": steps, "cost": before - movement_points(), "left": movement_points()}
		)
	return _saved(steps > 0, err == LatticeProgress.RESULT_OK, text)


## Wakes the node the hero stands on with its Facet.
func activate() -> Dictionary:
	var nid := position()
	var fid := progress().activation_facet(hero())
	var err := progress().activate(hero(), facets())
	if err != LatticeProgress.RESULT_OK:
		return {"ok": false, "text": error_text(err, _facet_ctx(board().lattice_node(nid)))}
	var text := tr("LATTICE_MENU_DONE_WAKE_FMT").format(
		{"name": hero_name(), "node": node_title(nid), "facet": facet_name(fid), "held": facets().count(fid)}
	)
	return _saved(true, true, text)


## Opens the gate `gid` next to the hero with its Key Facet, for everyone.
func open_gate(gid: StringName) -> Dictionary:
	var n := board().lattice_node(gid)
	var err := progress().open_gate(hero(), gid, facets())
	if err != LatticeProgress.RESULT_OK:
		return {"ok": false, "text": error_text(err, _facet_ctx(n))}
	var fid := rules().facet_for(n)
	var text := tr("LATTICE_MENU_DONE_OPEN_FMT").format({"facet": facet_name(fid), "held": facets().count(fid)})
	return _saved(true, true, text)


## Movement points a walk along `path` costs (the entry cost of every node after the first).
func path_cost(path: Array[StringName]) -> int:
	var total := 0
	for i in range(1, path.size()):
		total += progress().entry_cost(path[i])
	return total


## The node nearest `from` in the board direction `dir` (y grows downward): a neighbour inside the
## cone first, else any node inside it. Distance counts more the further a node slants off `dir`
## (`angle_weight`); `cone_cos` is the cosine of the widest angle allowed. `from` when none is.
func nearest_in_direction(from: StringName, dir: Vector2, cone_cos: float, angle_weight: float) -> StringName:
	var origin := board().lattice_node(from)
	if origin == null or dir == Vector2.ZERO:
		return from
	var best := _best_in_cone(origin, board().neighbors(from), dir, cone_cos, angle_weight)
	if best == &"":
		var every: Array[StringName] = []
		every.assign(board().nodes.keys())
		best = _best_in_cone(origin, every, dir, cone_cos, angle_weight)
	return best if best != &"" else from


func _best_in_cone(
	origin: LatticeNode, ids: Array[StringName], dir: Vector2, cone_cos: float, angle_weight: float
) -> StringName:
	var best := &""
	var best_score := INF
	var d := dir.normalized()
	for nid in ids:
		if nid == origin.id:
			continue
		var v := Vector2(board().lattice_node(nid).position - origin.position)
		var cos_a := v.normalized().dot(d)
		if cos_a < cone_cos:
			continue
		var score := v.length() * (1.0 + angle_weight * (1.0 - cos_a))
		if score < best_score:
			best_score = score
			best = nid
	return best


func _plan_here(p: Dictionary, n: LatticeNode) -> Dictionary:
	p["action"] = ACT_ACTIVATE
	var err := progress().activate_error(hero(), facets())
	if err != LatticeProgress.RESULT_OK:
		return _refused(p, err, error_text(err, _facet_ctx(n)))
	var fid := rules().facet_for(n)
	var ctx := {"name": hero_name(), "need": rules().facet_cost(n), "facet": facet_name(fid)}
	p["need"] = ctx["need"]
	p["facet"] = ctx["facet"]
	p["ok"] = true
	p["text"] = tr("LATTICE_MENU_PLAN_WAKE_FMT").format(ctx)
	p["confirm"] = tr("LATTICE_MENU_CONFIRM_WAKE_FMT").format(ctx)
	return p


func _plan_gate(p: Dictionary, n: LatticeNode) -> Dictionary:
	if not board().are_adjacent(position(), n.id):
		return _plan_walk_to_gate(p, n)
	p["action"] = ACT_OPEN
	var err := progress().open_gate_error(hero(), n.id, facets())
	if err != LatticeProgress.RESULT_OK:
		return _refused(p, err, error_text(err, _facet_ctx(n)))
	var ctx := {"need": rules().facet_cost(n), "facet": facet_name(rules().facet_for(n))}
	p["need"] = ctx["need"]
	p["facet"] = ctx["facet"]
	p["ok"] = true
	p["text"] = tr("LATTICE_MENU_PLAN_OPEN_FMT").format(ctx)
	p["confirm"] = tr("LATTICE_MENU_CONFIRM_OPEN_FMT").format(ctx)
	return p


## M2-MNU-10: a sealed gate away from the hero. The first step walks beside it: to the gate's
## neighbour that cheapest_path reaches for the fewest movement points (then the fewest steps, then
## the board's edge order). Confirm on the gate again then opens it (_plan_gate, now adjacent).
## Refused, in words, when no neighbour can be reached or the walk costs more than the hero has.
## {beside} names the neighbour.
func _plan_walk_to_gate(p: Dictionary, n: LatticeNode) -> Dictionary:
	p["action"] = ACT_WALK
	var best: Array[StringName] = []
	var best_cost := 0
	for nb in board().neighbors(n.id):
		var path := progress().cheapest_path(hero(), nb)
		if path.is_empty():
			continue
		var cost := path_cost(path)
		if best.is_empty() or cost < best_cost or (cost == best_cost and path.size() < best.size()):
			best = path
			best_cost = cost
	if best.is_empty():
		return _refused(p, LatticeProgress.ERR_GATE_CLOSED, tr("LATTICE_MENU_GATE_NO_WAY"))
	var have := movement_points()
	p["path"] = best
	p["beside"] = best[best.size() - 1]
	p["cost"] = best_cost
	p["left"] = have - best_cost
	var fid := rules().facet_for(n)
	var words := {
		"cost": best_cost,
		"have": have,
		"left": have - best_cost,
		"name": hero_name(),
		"need": rules().facet_cost(n),
		"facet": facet_name(fid),
		"held": facets().count(fid),
	}
	if best_cost > have:
		return _refused(p, LatticeProgress.ERR_NO_MOVEMENT, tr("LATTICE_MENU_GATE_TOO_FAR_FMT").format(words))
	var walk_line := tr("LATTICE_MENU_PLAN_GATE_WALK_FMT").format(words)
	p["confirm"] = tr("LATTICE_MENU_CONFIRM_GATE_WALK_FMT").format(words)
	if best_cost == 0:
		walk_line = tr("LATTICE_MENU_PLAN_GATE_WALK_FREE")
		p["confirm"] = tr("LATTICE_MENU_CONFIRM_GATE_WALK_FREE")
	var key_line := tr("LATTICE_MENU_PLAN_GATE_KEY_FMT").format(words)
	if not facets().has(fid, rules().facet_cost(n)):
		key_line = tr("LATTICE_MENU_PLAN_GATE_NO_KEY_FMT").format(words)
	p["ok"] = true
	p["text"] = walk_line + " " + key_line
	return p


func _plan_walk(p: Dictionary, nid: StringName) -> Dictionary:
	p["action"] = ACT_WALK
	var path := progress().cheapest_path(hero(), nid)
	if path.is_empty():
		return _refused(p, LatticeProgress.ERR_GATE_CLOSED, error_text(LatticeProgress.ERR_GATE_CLOSED))
	var cost := path_cost(path)
	p["path"] = path
	p["cost"] = cost
	p["left"] = movement_points() - cost
	if cost > movement_points():
		var ctx := {"cost": cost, "have": movement_points()}
		return _refused(p, LatticeProgress.ERR_NO_MOVEMENT, error_text(LatticeProgress.ERR_NO_MOVEMENT, ctx))
	var words := {"cost": cost, "steps": path.size() - 1, "left": movement_points() - cost}
	p["ok"] = true
	if cost == 0:
		p["text"] = tr("LATTICE_MENU_PLAN_WALK_FREE_FMT").format(words)
		p["confirm"] = tr("LATTICE_MENU_CONFIRM_WALK_FREE")
	else:
		p["text"] = tr("LATTICE_MENU_PLAN_WALK_FMT").format(words)
		p["confirm"] = tr("LATTICE_MENU_CONFIRM_WALK_FMT").format(words)
	return p


func _refused(p: Dictionary, err: StringName, text: String) -> Dictionary:
	p["error"] = err
	p["ok"] = false
	p["text"] = text
	return p


func _facet_ctx(n: LatticeNode) -> Dictionary:
	var fid := rules().facet_for(n)
	return {"facet": facet_name(fid), "need": rules().facet_cost(n), "held": facets().count(fid)}


## Saves after a change (`changed`) and adds a warning to `text` when the save is refused.
func _saved(changed: bool, ok: bool, text: String) -> Dictionary:
	if changed and not sheet.save_lattice():
		return {"ok": false, "text": text + " " + tr("LATTICE_MENU_SAVE_REFUSED")}
	return {"ok": ok, "text": text}


func _skill_name(skill_id: StringName) -> String:
	var key := str(sheet.battle_db.skill(skill_id).get("name_key", ""))
	return tr(key) if key != "" else String(skill_id)
