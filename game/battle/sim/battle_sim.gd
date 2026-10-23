class_name BattleSim
extends RefCounted
## Headless balancing simulator (M1-CMB-05, SPEC §6.9). Plays one encounter for N seeds under
## a pluggable party policy (SimPolicy) and aggregates win rate, turns, KOs and item use.
## Deterministic: seed s always plays the same battle. Driven by sim_main.gd (`godot -s`),
## which tools/balance/sim.py wraps, and by tests/integration/test_sandbox_battle.gd.

const POLICY_NAMES: Array[StringName] = [&"naive", &"lowest_hp", &"role_answer", &"smart"]
const CONFIG_PATH := "res://game/data/battle/sim_policies.json"

var db: BattleDB
var _config: Dictionary = {}


func _init(battle_db: BattleDB = null) -> void:
	db = battle_db if battle_db != null else BattleDB.load_default()
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
	_config = parsed if typeof(parsed) == TYPE_DICTIONARY else {}


## A fresh policy by name, configured from sim_policies.json. Null for an unknown name.
func make_policy(policy: StringName) -> SimPolicy:
	var p: SimPolicy = null
	match policy:
		&"naive":
			p = SimPolicyNaive.new()
		&"lowest_hp":
			p = SimPolicyLowestHp.new()
		&"role_answer":
			p = SimPolicyRoleAnswer.new()
		&"smart":
			p = SimPolicySmart.new()
		_:
			push_error("BattleSim: unknown policy '%s'" % policy)
			return null
	p.config = (_config.get("policies", {}) as Dictionary).get(String(policy), {})
	return p


## Plays one battle. Returns {seed, outcome, turns, party_turns, party_ko, items}. `turns`
## counts every action taken (both sides, automatic turns included; lost turns excluded).
## A battle that exceeds max_actions is recorded with outcome "timeout".
func run_one(
	encounter: StringName,
	active: Array[StringName],
	reserve: Array[StringName],
	policy: SimPolicy,
	rng_seed: int,
	party_modifier: Callable = Callable()
) -> Dictionary:
	var engine := BattleEngine.new()
	engine.party_modifier = party_modifier
	engine.setup(db, active, reserve, encounter, rng_seed)
	policy.reset()
	engine.begin()
	var limit := int(_config.get("max_actions", 0))
	var steps := 0
	while engine.outcome == &"" and steps < limit:
		steps += 1
		if engine.is_party_turn():
			policy.take_turn(engine)
		else:
			engine.run_enemy_turn()
	var party := engine.party_active + engine.party_reserve
	var turns := 0
	var party_turns := 0
	var ko := 0
	for c in party:
		party_turns += c.turns_taken
		if c.participated and not c.is_alive():
			ko += 1
	turns = party_turns
	for c in engine.enemies:
		turns += c.turns_taken
	return {
		"seed": rng_seed,
		"outcome": String(engine.outcome) if engine.outcome != &"" else "timeout",
		"turns": turns,
		"party_turns": party_turns,
		"party_ko": ko,
		"items": policy.items_used,
	}


## Runs seeds first_seed .. first_seed + seeds - 1 and aggregates them.
func run_many(
	encounter: StringName,
	active: Array[StringName],
	reserve: Array[StringName],
	policy_name: StringName,
	seeds: int,
	first_seed: int = 1,
	party_modifier: Callable = Callable()
) -> Dictionary:
	var policy := make_policy(policy_name)
	var runs: Array[Dictionary] = []
	for s in range(first_seed, first_seed + seeds):
		runs.append(run_one(encounter, active, reserve, policy, s, party_modifier))
	var out := summarize(runs)
	out["encounter"] = String(encounter)
	out["policy"] = String(policy_name)
	out["first_seed"] = first_seed
	return out


## Runs a command-line request (sim_main.gd): {encounter, active, reserve, policies, seeds,
## first-seed} as parsed by parse_args(). Returns {ok, error, results}; each result is a
## summarize() aggregate plus encounter, policy, first_seed and the per-seed "runs".
func run_cli(args: Dictionary) -> Dictionary:
	var encounter := StringName(str(args.get("encounter", "")))
	var active := split_ids(str(args.get("active", "")))
	var reserve := split_ids(str(args.get("reserve", "")))
	var policies := split_ids(str(args.get("policies", ",".join(POLICY_NAMES))))
	var seeds := int(args.get("seeds", "0"))
	var first := int(args.get("first-seed", "1"))
	var out := {"ok": false, "error": "", "results": []}
	if not db.encounters.has(encounter) or active.is_empty() or seeds <= 0:
		out["error"] = "need --encounter=<known id> --active=a,b --seeds=N (got %s)" % str(args)
		return out
	for p in policies:
		if not p in POLICY_NAMES:
			out["error"] = "unknown policy '%s'" % p
			return out
	var results: Array = []
	for p in policies:
		var policy := make_policy(p)
		var runs: Array[Dictionary] = []
		for s in range(first, first + seeds):
			runs.append(run_one(encounter, active, reserve, policy, s))
		var agg := summarize(runs)
		agg["encounter"] = String(encounter)
		agg["policy"] = String(p)
		agg["first_seed"] = first
		agg["runs"] = runs
		results.append(agg)
	out["ok"] = true
	out["results"] = results
	return out


## "--key=value" arguments to {key: value}; anything else is ignored.
static func parse_args(argv: PackedStringArray) -> Dictionary:
	var out: Dictionary = {}
	for a in argv:
		if a.begins_with("--") and a.contains("="):
			out[a.substr(2, a.find("=") - 2)] = a.substr(a.find("=") + 1)
	return out


## "a, b,,c" -> [&"a", &"b", &"c"].
static func split_ids(csv: String) -> Array[StringName]:
	var out: Array[StringName] = []
	for part in csv.split(",", false):
		if part.strip_edges() != "":
			out.append(StringName(part.strip_edges()))
	return out


## Aggregates run_one() results: n, wins, win_pct, mean/p90 turns, mean party KOs, items.
static func summarize(runs: Array[Dictionary]) -> Dictionary:
	var n := runs.size()
	var wins := 0
	var timeouts := 0
	var turns: Array[int] = []
	var ko_total := 0
	var items_total := 0
	for r in runs:
		if r["outcome"] == "victory":
			wins += 1
		elif r["outcome"] == "timeout":
			timeouts += 1
		turns.append(int(r["turns"]))
		ko_total += int(r["party_ko"])
		items_total += int(r["items"])
	turns.sort()
	return {
		"n": n,
		"wins": wins,
		"win_pct": 100.0 * wins / maxi(n, 1),
		"timeouts": timeouts,
		"mean_turns": _mean(turns),
		"p90_turns": percentile(turns, 90),
		"mean_party_ko": float(ko_total) / maxi(n, 1),
		"mean_items": float(items_total) / maxi(n, 1),
	}


## Nearest-rank percentile of an ascending list (0 when empty).
static func percentile(sorted_values: Array[int], pct: int) -> int:
	if sorted_values.is_empty():
		return 0
	var rank := ceili(pct / 100.0 * sorted_values.size())
	return sorted_values[clampi(rank - 1, 0, sorted_values.size() - 1)]


static func _mean(values: Array[int]) -> float:
	if values.is_empty():
		return 0.0
	var total := 0
	for v in values:
		total += v
	return float(total) / values.size()
