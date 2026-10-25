class_name ReefballFixture
extends RefCounted
## In-memory Reefball tables for the unit tests (M3-RBL-01): two sides of three, a short clock,
## and roles that hold fixed bands so a test can place divers by hand. The coefficients are the
## shipped rules.json ones written out, so the tests pin the formulas, not the tuning.

const MATCH := &"fixture"


## The tables, for a test that wants to change one before building the DB.
static func tables() -> Dictionary:
	var rules := {
		"bands": [{"id": "ring"}, {"id": "high"}, {"id": "mid"}, {"id": "low"}, {"id": "weep"}],
		"fetch_depth": 3,
		"stat_min": 1,
		"stat_max": 20,
		"odds_min": 0.05,
		"odds_max": 0.95,
		"clock": {"match_strokes": 10, "overtime_strokes": 2, "overtime_periods": 1},
		"actions":
		{
			"rise": {"strokes": 2, "breath": 2},
			"dive": {"strokes": 1, "breath": 0},
			"pass": {"strokes": 1, "breath": 0},
			"loft": {"strokes": 1, "breath": 1},
		},
		"rise": {"base": 0.8, "edge_k": 0.04, "crowd_k": 0.1},
		"pass": {"base": 0.62, "skill_k": 0.02, "dist_k": 0.07, "mark_k": 0.02, "crowd_k": 0.06, "open_reach": 1},
		"loft": {"base": 0.4, "skill_k": 0.03, "depth_k": 0.15, "ward_k": 0.02, "press_k": 0.06, "max_depth": 2},
		"breath": {"drain": 1, "ring_recover": 3, "winded_at": 3, "winded_penalty": 0.2, "rested_pct": 75},
		"swim": {"bands": 1, "fast_stroke": 14, "fast_bands": 2},
		"roles":
		[
			{
				"id": "chaser",
				"attack": {"rel": -1},
				"fetch": {"band": 3},
				"defend": {"rel": 0},
				"kickoff": {"attack": 3, "defend": 3}
			},
			{
				"id": "keeper",
				"attack": {"band": 1},
				"fetch": {"band": 1},
				"defend": {"band": 0},
				"kickoff": {"attack": 1, "defend": 0}
			},
		],
		"ai_profiles":
		[
			{
				"id": "test",
				"score_value": 10.0,
				"advance_value": 2.0,
				"fetch_value": 3.0,
				"fresh_value": 1.0,
				"turnover_cost": 3.0,
				"loft_min_odds": 0.3,
				"whim_pct": 0
			},
		],
	}
	var sides := [
		{
			"id": "east",
			"kickoff": "e_carry",
			"divers":
			[
				_diver("e_carry", "chaser", 12),
				_diver("e_mate", "chaser", 12),
				_diver("e_keep", "keeper", 12),
			]
		},
		{
			"id": "west",
			"kickoff": "w_carry",
			"divers":
			[
				_diver("w_carry", "chaser", 12),
				_diver("w_mate", "chaser", 12),
				_diver("w_keep", "keeper", 12),
			]
		},
	]
	var matches := [
		{"id": String(MATCH), "sides": ["east", "west"], "player_side": 0, "first_float": 0, "ai_profile": "test"}
	]
	return {"rules": rules, "sides": sides, "matches": matches}


## The tables with swimming switched off, so placed divers stay where a test put them.
static func still() -> Dictionary:
	var raw := tables()
	raw["rules"]["swim"] = {"bands": 0, "fast_stroke": 14, "fast_bands": 0}
	return raw


static func db(raw: Dictionary = {}) -> ReefballDB:
	return ReefballDB.from_tables(raw if not raw.is_empty() else tables())


## A set-up, begun fixture match (east holds the float at the weep).
static func begun(seed_value: int = 1, raw: Dictionary = {}) -> ReefballMatch:
	var m := ReefballMatch.new()
	m.setup(db(raw), MATCH, seed_value)
	m.begin()
	return m


## A diver row with every stat at `value`.
static func _diver(diver_id: String, role: String, value: int) -> Dictionary:
	var stats := {}
	for s in ReefballDiver.STATS:
		stats[s] = value
	return {"id": diver_id, "name_key": "RBL_TEST", "role": role, "stats": stats}


## A loose diver for formula tests.
static func diver(depth: int, stats: Dictionary = {}, side: int = 0, order: int = 0) -> ReefballDiver:
	var row := _diver("d%d" % order, "chaser", 10)
	(row["stats"] as Dictionary).merge(stats, true)
	var d := ReefballDiver.from_row(row, side)
	d.depth = depth
	d.order = order
	return d
