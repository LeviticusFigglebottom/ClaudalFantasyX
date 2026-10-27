class_name ReefballMatch
extends RefCounted
## One Reefball match (M3-RBL-01, SPEC §6.10, docs/kb/design/reefball.md). Headless and
## deterministic: no Nodes, and every roll goes through `rng`, seeded in setup(), so a seed always
## plays the same match for the same decisions.
##
## Play is turn-paused at contact moments: whoever holds the float decides one action (rise, dive,
## pass or loft). legal_actions() lists them with their exact odds; perform() resolves one, then the
## clock runs, breath drains or returns, and every other diver swims toward its role's band.
## The UI listens to the signals and never changes match state directly.

signal contact_started(holder_id: StringName, side: int)
signal action_resolved(result: Dictionary)
signal divers_moved(moves: Array)
signal float_scored(side: int, score: Array)
signal match_finished(outcome: StringName, score: Array)

const RISE := &"rise"
const DIVE := &"dive"
const PASS := &"pass"
const LOFT := &"loft"
const ACTIONS: Array[StringName] = [RISE, DIVE, PASS, LOFT]
const RING := 0
const WIN := &"win"
const LOSS := &"loss"
const DRAW := &"draw"
## refused_actions()' reason keys (loc, M3-RBL-201), by why an action is not legal.
const REFUSE_KEYS := {
	&"rise_unfetched": "RBL_REFUSE_RISE_UNFETCHED",
	&"dive_bed": "RBL_REFUSE_DIVE_BED",
	&"loft_unfetched": "RBL_REFUSE_LOFT_UNFETCHED",
	&"loft_deep": "RBL_REFUSE_LOFT_DEEP",
	&"pass_ring": "RBL_REFUSE_PASS_RING",
}

var db: ReefballDB
var rules: Dictionary = {}
var match_row: Dictionary = {}
var rng := RandomNumberGenerator.new()
## Both sides' divers, side 0 first, in sides.json order (ReefballDiver.order is the index).
var divers: Array[ReefballDiver] = []
var side_ids: Array[StringName] = []
var player_side := 0
var score: Array[int] = [0, 0]
var strokes_left := 0
var in_overtime := false
## 0 in regulation; 1.. for each overtime period played (clock.overtime_periods at most).
var overtime_period := 0
var finished := false
## From the player side's view: WIN, LOSS or DRAW once finished, &"" before.
var outcome: StringName = &""
var holder: ReefballDiver
## The holding side has taken the float to fetch_depth or below this possession (it may score).
var fetched := false
var contacts := 0
var ai: ReefballAI


## Whether the match row may be offered (ADR 0040): a row with "requires_item" needs the party to hold
## that key item (the Oruvel Float opens Oruvel's Act III league match). `holds`: (item id) -> bool, the
## flow's inventory check, so the match itself never reads the game.
static func is_open(row: Dictionary, holds: Callable) -> bool:
	var need := StringName(str(row.get("requires_item", "")))
	return need == &"" or bool(holds.call(need))


## Builds the match `match_id` from `database`, seeded with `seed_value`. False (and push_error)
## for an unknown match or side.
func setup(database: ReefballDB, match_id: StringName, seed_value: int) -> bool:
	db = database
	rules = db.rules
	if not db.matches.has(match_id):
		push_error("ReefballMatch: unknown match '%s'" % match_id)
		return false
	match_row = db.matches[match_id]
	rng.seed = seed_value
	divers.clear()
	side_ids.clear()
	for sid: Variant in match_row.get("sides", []):
		if not db.sides.has(StringName(str(sid))):
			push_error("ReefballMatch: unknown side '%s'" % sid)
			return false
		side_ids.append(StringName(str(sid)))
		for row: Variant in (db.sides[StringName(str(sid))] as Dictionary).get("divers", []):
			var d := ReefballDiver.from_row(row, side_ids.size() - 1)
			d.order = divers.size()
			divers.append(d)
	player_side = int(match_row.get("player_side", 0))
	ai = ReefballAI.new(db.ai_profiles.get(StringName(str(match_row.get("ai_profile", ""))), {}))
	return true


## Starts the clock and gives the first float to match.first_float at the weep.
func begin() -> void:
	score = [0, 0]
	strokes_left = int(_clock().get("match_strokes", 0))
	in_overtime = false
	overtime_period = 0
	finished = false
	outcome = &""
	contacts = 0
	var moves := _kickoff(int(match_row.get("first_float", 0)))
	divers_moved.emit(moves)
	contact_started.emit(holder.id, holder.side)


func bed() -> int:
	return (rules.get("bands", []) as Array).size() - 1


func fetch_depth() -> int:
	return int(rules.get("fetch_depth", bed()))


func holder_side() -> int:
	return holder.side if holder != null else -1


## True when the player's side holds the float and the match is live: the UI asks for a decision.
func is_player_contact() -> bool:
	return not finished and holder_side() == player_side


func diver(diver_id: StringName) -> ReefballDiver:
	for d in divers:
		if d.id == diver_id:
			return d
	return null


func side_divers(side: int) -> Array[ReefballDiver]:
	var out: Array[ReefballDiver] = []
	for d in divers:
		if d.side == side:
			out.append(d)
	return out


## The divers of the side that is not `side`, in `band`.
func opponents_at(side: int, band: int) -> Array[ReefballDiver]:
	var out: Array[ReefballDiver] = []
	for d in divers:
		if d.side != side and d.depth == band:
			out.append(d)
	return out


## Every action the holder may take now, each as preview() returns it, in ACTIONS order (passes by
## teammate order). Empty when the match is over.
func legal_actions() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if finished or holder == null:
		return out
	for action in ACTIONS:
		if action == PASS:
			for mate in side_divers(holder.side):
				var p := preview(PASS, mate.id)
				if not p.is_empty():
					out.append(p)
		else:
			var p := preview(action)
			if not p.is_empty():
				out.append(p)
	return out


## What `action` (on `target` for a pass) would do, without changing anything: {action, actor,
## target, odds, strokes, breath, scores (a success brings the float up), fail_to (the diver who
## takes the float on a miss, &"" when the action cannot miss), to_depth (the actor's or receiver's
## band on a success), against (the opponents counted in the odds: a rise's contesters, a pass's
## markers, a loft's wardens then pressers; M3-RBL-201), fetches (a success takes an unfetched float
## to fetch_depth or deeper)}. {} when the action is not legal now (refused_actions() says why).
func preview(action: StringName, target: StringName = &"") -> Dictionary:
	if finished or holder == null or not (rules.get("actions", {}) as Dictionary).has(String(action)):
		return {}
	var odds := -1.0
	var fail: ReefballDiver = null
	var to_depth := holder.depth
	var scores := false
	var against: Array[ReefballDiver] = []
	match action:
		RISE:
			if _refusal(RISE) != &"":
				return {}
			var contesters := _contesters()
			against = contesters
			odds = ReefballFormulas.rise_odds(rules, holder, contesters)
			fail = ReefballFormulas.best(contesters, "strip")
			to_depth = holder.depth - 1
			scores = to_depth == RING
		DIVE:
			if _refusal(DIVE) != &"":
				return {}
			odds = 1.0
			to_depth = holder.depth + 1
		PASS:
			var mate := diver(target)
			if mate == null or mate == holder or mate.side != holder.side or mate.depth == RING:
				return {}
			var markers := opponents_at(holder.side, mate.depth)
			against = markers
			odds = ReefballFormulas.pass_odds(rules, holder, mate, markers)
			fail = _nearest_opponent(mate.depth)
			to_depth = mate.depth
		LOFT:
			if _refusal(LOFT) != &"":
				return {}
			var wardens := opponents_at(holder.side, RING)
			var pressers := opponents_at(holder.side, holder.depth)
			against = wardens + pressers
			odds = ReefballFormulas.loft_odds(rules, holder, wardens, pressers)
			fail = _loft_catcher(wardens, pressers)
			scores = true
	var cost := _block("actions").get(String(action), {}) as Dictionary
	return {
		"action": action,
		"actor": holder.id,
		"target": target if action == PASS else &"",
		"odds": odds,
		"strokes": int(cost.get("strokes", 0)),
		"breath": int(cost.get("breath", 0)),
		"scores": scores,
		"fail_to": fail.id if fail != null and odds < 1.0 else &"",
		"to_depth": to_depth,
		"against": _ids(against),
		"fetches": not fetched and to_depth >= fetch_depth() and (action == DIVE or action == PASS),
	}


## The actions the holder may not take now, each {action, target, reason_key} (a loc key saying why), in
## ACTIONS order (passes by teammate order; the holder itself is never listed). Empty when the match is over.
func refused_actions() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if finished or holder == null:
		return out
	for action in ACTIONS:
		if action == PASS:
			for mate in side_divers(holder.side):
				if mate != holder and mate.depth == RING:
					out.append({"action": PASS, "target": mate.id, "reason_key": REFUSE_KEYS[&"pass_ring"]})
			continue
		var why := _refusal(action)
		if why != &"":
			out.append({"action": action, "target": &"", "reason_key": REFUSE_KEYS[why]})
	return out


## Resolves `action` for the holder with one roll of `rng`. Returns the preview fields plus
## {ok, roll, success, holder (after), scored, strokes_left}; {ok: false, error} when the action is
## not legal now (nothing changes and no roll is drawn).
func perform(action: StringName, target: StringName = &"") -> Dictionary:
	var p := preview(action, target)
	if p.is_empty():
		return {"ok": false, "error": "illegal action '%s' '%s'" % [action, target]}
	var actor := holder
	var roll := rng.randf()
	var success: bool = roll < float(p["odds"])
	actor.breath = maxi(0, actor.breath - int(p["breath"]))
	var scored := false
	if success:
		scored = _apply_success(action, target)
	else:
		_take_float(diver(p["fail_to"]))
	strokes_left -= int(p["strokes"])
	contacts += 1
	_breathe()
	var scoring_side := actor.side
	var moves: Array = []
	if scored:
		score[scoring_side] += 1
		moves = _kickoff(1 - scoring_side)
	else:
		moves = _swim()
	_check_clock(scored)
	var result := p.duplicate()
	result.merge(
		{
			"ok": true,
			"roll": roll,
			"success": success,
			"holder": holder.id,
			"scored": scored,
			"strokes_left": strokes_left
		}
	)
	action_resolved.emit(result)
	if scored:
		float_scored.emit(scoring_side, score.duplicate())
	divers_moved.emit(moves)
	if finished:
		match_finished.emit(outcome, score.duplicate())
	else:
		contact_started.emit(holder.id, holder.side)
	return result


## Lets the match AI decide the current contact (either side) and performs it.
func play_ai_contact(profile_ai: ReefballAI = null) -> Dictionary:
	var brain := profile_ai if profile_ai != null else ai
	var choice := brain.choose(self)
	if choice.is_empty():
		return {"ok": false, "error": "no legal action"}
	return perform(choice["action"], choice["target"])


## A plain-data view of the whole match for the UI, debug overlays and tests.
func snapshot() -> Dictionary:
	var ds: Array = []
	for d in divers:
		ds.append(d.snapshot())
	return {
		"sides": side_ids.duplicate(),
		"player_side": player_side,
		"score": score.duplicate(),
		"strokes_left": strokes_left,
		"in_overtime": in_overtime,
		"overtime_period": overtime_period,
		"finished": finished,
		"outcome": outcome,
		"holder": holder.id if holder != null else &"",
		"fetched": fetched,
		"contacts": contacts,
		"divers": ds,
	}


func _apply_success(action: StringName, target: StringName) -> bool:
	match action:
		RISE:
			holder.depth -= 1
			return holder.depth == RING
		DIVE:
			holder.depth += 1
			fetched = fetched or holder.depth >= fetch_depth()
		PASS:
			holder = diver(target)
			fetched = fetched or holder.depth >= fetch_depth()
		LOFT:
			return true
	return false


## A turnover: `taker` holds the float. Nobody holds it at the ring, so a taker there sinks a band.
func _take_float(taker: ReefballDiver) -> void:
	holder = taker
	holder.resting = false
	if holder.depth == RING:
		holder.depth = RING + 1
	fetched = holder.depth >= fetch_depth()


## Why the holder may not take `action` (RISE, DIVE or LOFT; passes are judged per receiver) now: a REFUSE_KEYS
## key, or &"" when it may.
func _refusal(action: StringName) -> StringName:
	match action:
		RISE:
			return &"rise_unfetched" if holder.depth - 1 == RING and not fetched else &""
		DIVE:
			return &"dive_bed" if holder.depth >= bed() else &""
	if not fetched:
		return &"loft_unfetched"
	return &"loft_deep" if holder.depth > int(_block("loft").get("max_depth", 0)) else &""


static func _ids(ds: Array[ReefballDiver]) -> Array[StringName]:
	var out: Array[StringName] = []
	for d in ds:
		out.append(d.id)
	return out


## Opponents in the holder's band and the band above (the band it would rise into).
func _contesters() -> Array[ReefballDiver]:
	var out := opponents_at(holder.side, holder.depth)
	out.append_array(opponents_at(holder.side, holder.depth - 1))
	return out


## Who catches a missed loft: the best warden at the ring, else the best presser, else the opponent
## nearest the ring.
func _loft_catcher(wardens: Array[ReefballDiver], pressers: Array[ReefballDiver]) -> ReefballDiver:
	if not wardens.is_empty():
		return ReefballFormulas.best(wardens, "ward")
	if not pressers.is_empty():
		return ReefballFormulas.best(pressers, "strip")
	return _nearest_opponent(RING)


## The holder's opponent nearest `band` (ties: higher strip, then lower order).
func _nearest_opponent(band: int) -> ReefballDiver:
	var top: ReefballDiver = null
	for d in divers:
		if d.side == holder.side:
			continue
		if top == null:
			top = d
			continue
		var dd := absi(d.depth - band)
		var td := absi(top.depth - band)
		if dd < td or (dd == td and d.stat("strip") > top.stat("strip")):
			top = d
	return top


## Breath after a contact: the ring gives breath back, any depth below it takes some. A diver who
## falls to winded_at goes up to rest; a rested one (rested_pct of max) comes back into play.
func _breathe() -> void:
	var b := _block("breath")
	for d in divers:
		if d.depth == RING:
			d.breath = mini(d.max_breath(), d.breath + int(b.get("ring_recover", 0)))
		else:
			d.breath = maxi(0, d.breath - int(b.get("drain", 0)))
		if d == holder:
			continue
		if ReefballFormulas.winded(rules, d):
			d.resting = true
		elif d.resting and d.depth == RING and d.breath * 100 >= d.max_breath() * int(b.get("rested_pct", 100)):
			d.resting = false


## Every diver but the holder swims toward its band (swim.bands a contact, fast_bands with a fast
## stroke). Returns [{id, from, to}] for the divers that moved.
func _swim() -> Array:
	var moves: Array = []
	var s := _block("swim")
	for d in divers:
		if d == holder:
			continue
		var speed := int(s["fast_bands"]) if d.stat("stroke") >= int(s["fast_stroke"]) else int(s["bands"])
		var target := _target_band(d)
		var to := d.depth + clampi(target - d.depth, -speed, speed)
		if to != d.depth:
			moves.append({"id": d.id, "from": d.depth, "to": to})
			d.depth = to
	return moves


## Where `d`'s role wants it: the ring while resting; else the role's attack band (fetch band while
## the float is unfetched) for the holding side, or its defend band. A spec is {"band": n} or
## {"rel": n} (relative to the holder). Attackers never wait at the ring: nobody receives there.
func _target_band(d: ReefballDiver) -> int:
	if d.resting:
		return RING
	var role := db.roles.get(d.role, {}) as Dictionary
	var spec: Dictionary
	var low := RING
	if d.side == holder.side:
		spec = role.get("attack" if fetched else "fetch", {})
		low = RING + 1
	else:
		spec = role.get("defend", {})
	var band := int(spec["band"]) if spec.has("band") else holder.depth + int(spec.get("rel", 0))
	return clampi(band, low, bed())


## Gives the float to `side`'s kickoff diver at the weep and sets both sides in their kickoff bands
## (resting divers stay at the ring). Returns the moves.
func _kickoff(side: int) -> Array:
	var moves: Array = []
	var row := db.sides[side_ids[side]] as Dictionary
	holder = diver(StringName(str(row.get("kickoff", ""))))
	fetched = true
	for d in divers:
		var to := RING
		if d == holder:
			to = bed()
			d.resting = false
		elif not d.resting:
			var kick := (db.roles.get(d.role, {}) as Dictionary).get("kickoff", {}) as Dictionary
			to = clampi(int(kick.get("attack" if d.side == side else "defend", RING)), RING, bed())
		if to != d.depth:
			moves.append({"id": d.id, "from": d.depth, "to": to})
			d.depth = to
	return moves


## Ends the match when the strokes run out, unless it is tied: then another overtime period of
## overtime_strokes is played (up to overtime_periods), where the next float up wins at once.
## A tie after the last period is a draw.
func _check_clock(scored: bool) -> void:
	if in_overtime and scored:
		_finish()
		return
	if strokes_left > 0:
		return
	var overtime := int(_clock().get("overtime_strokes", 0))
	if score[0] == score[1] and overtime_period < int(_clock().get("overtime_periods", 0)) and overtime > 0:
		in_overtime = true
		overtime_period += 1
		strokes_left = overtime
		return
	_finish()


func _finish() -> void:
	finished = true
	var mine := score[player_side]
	var theirs := score[1 - player_side]
	outcome = WIN if mine > theirs else (LOSS if mine < theirs else DRAW)


func _clock() -> Dictionary:
	return _block("clock")


func _block(key: String) -> Dictionary:
	return rules.get(key, {}) as Dictionary
