class_name ReefballSim
extends RefCounted
## Headless Reefball balance simulator (M3-RBL-01, SPEC §6.9). Plays one match for N seeds with the
## player's side under a policy and the other side under the match's AI profile, and aggregates
## wins, draws, scores and contacts. Seed s always plays the same match. Driven by
## tools/balance/reefball_sim_main.gd (`godot -s`), which tools/balance/reefball_sim.py wraps.
##
## Policies: "naive" (the masher: carry it yourself, never pass or loft) or any rules.json
## ai_profiles id (for example "smart", which weighs every previewed odds).

const NAIVE := &"naive"

var db: ReefballDB


func _init(database: ReefballDB = null) -> void:
	db = database if database != null else ReefballDB.load_default()


## True for a policy this sim can play.
func has_policy(policy: StringName) -> bool:
	return policy == NAIVE or db.ai_profiles.has(policy)


## Plays `match_id` once with seed `seed_value`. {outcome, score_for, score_against, contacts,
## turnovers}. Every action costs at least one stroke (validate_data), so a match always ends
## within the clock's strokes; `stalled` reports a run that somehow did not.
func play(match_id: StringName, policy: StringName, seed_value: int) -> Dictionary:
	var m := ReefballMatch.new()
	if not m.setup(db, match_id, seed_value):
		return {}
	var brain: ReefballAI = null if policy == NAIVE else ReefballAI.new(db.ai_profiles.get(policy, {}))
	var clock := db.rules.get("clock", {}) as Dictionary
	var cap := (
		int(clock.get("match_strokes", 0))
		+ int(clock.get("overtime_strokes", 0)) * int(clock.get("overtime_periods", 0))
		+ 1
	)
	var turnovers := 0
	m.begin()
	while not m.finished and m.contacts < cap:
		var side := m.holder_side()
		var res: Dictionary
		if not m.is_player_contact():
			res = m.play_ai_contact()
		elif brain != null:
			res = m.play_ai_contact(brain)
		else:
			var pick := naive_choice(m)
			res = m.perform(pick["action"], pick["target"])
		if res.get("ok", false) and not res["scored"] and m.holder_side() != side:
			turnovers += 1
	return {
		"outcome": m.outcome,
		"score_for": m.score[m.player_side],
		"score_against": m.score[1 - m.player_side],
		"contacts": m.contacts,
		"turnovers": turnovers,
		"stalled": not m.finished,
	}


## The masher's pick: carry the float yourself. Dive until it is fetched, then rise; a pass only when
## neither is legal.
static func naive_choice(m: ReefballMatch) -> Dictionary:
	var options := m.legal_actions()
	var order := [ReefballMatch.RISE, ReefballMatch.DIVE] if m.fetched else [ReefballMatch.DIVE, ReefballMatch.RISE]
	for want: StringName in order:
		for o in options:
			if o["action"] == want:
				return o
	return options[0]


## Aggregates `seeds` plays from `first_seed`: {match, policy, n, wins, draws, losses, win_pct,
## draw_pct, mean_for, mean_against, mean_contacts, mean_turnovers, stalled}.
func run(match_id: StringName, policy: StringName, seeds: int, first_seed: int = 1) -> Dictionary:
	var agg := {
		"match": String(match_id),
		"policy": String(policy),
		"n": 0,
		"wins": 0,
		"draws": 0,
		"losses": 0,
		"stalled": 0,
	}
	var sums := {"for": 0.0, "against": 0.0, "contacts": 0.0, "turnovers": 0.0}
	for s in range(first_seed, first_seed + seeds):
		var r := play(match_id, policy, s)
		agg["n"] += 1
		match r["outcome"]:
			ReefballMatch.WIN:
				agg["wins"] += 1
			ReefballMatch.DRAW:
				agg["draws"] += 1
			_:
				agg["losses"] += 1
		agg["stalled"] += 1 if r["stalled"] else 0
		sums["for"] += r["score_for"]
		sums["against"] += r["score_against"]
		sums["contacts"] += r["contacts"]
		sums["turnovers"] += r["turnovers"]
	var n := float(maxi(1, agg["n"]))
	agg["win_pct"] = 100.0 * agg["wins"] / n
	agg["draw_pct"] = 100.0 * agg["draws"] / n
	agg["mean_for"] = sums["for"] / n
	agg["mean_against"] = sums["against"] / n
	agg["mean_contacts"] = sums["contacts"] / n
	agg["mean_turnovers"] = sums["turnovers"] / n
	return agg


## Parses `--match=id --policies=a,b --seeds=N [--first-seed=S] [--out=path]` into a dictionary.
static func parse_args(args: PackedStringArray) -> Dictionary:
	var out := {}
	for a in args:
		if a.begins_with("--") and a.contains("="):
			var kv := a.substr(2).split("=", true, 1)
			out[kv[0]] = kv[1]
	return out


## Runs the parsed CLI request: {ok, error?, results: [run() per policy]}.
func run_cli(args: Dictionary) -> Dictionary:
	var match_id := StringName(str(args.get("match", "")))
	if not db.matches.has(match_id):
		return {"ok": false, "error": "unknown match '%s'" % match_id}
	var seeds := int(args.get("seeds", "0"))
	if seeds <= 0:
		return {"ok": false, "error": "--seeds must be a positive int"}
	var results: Array = []
	for p in str(args.get("policies", "")).split(",", false):
		if not has_policy(StringName(p)):
			return {"ok": false, "error": "unknown policy '%s'" % p}
		results.append(run(match_id, StringName(p), seeds, int(args.get("first-seed", "1"))))
	if results.is_empty():
		return {"ok": false, "error": "--policies is empty"}
	return {"ok": true, "results": results}
