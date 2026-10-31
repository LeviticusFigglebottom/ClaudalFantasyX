extends TestCase
## The human's playtest: "after a battle is won there's a long, multi-second black screen before you can see the
## screen and move again". The way back from a random fight keeps the same bar as an entry's hidden time (ADR 0042,
## ADR 0205): SceneRouter keeps the field zone resident through the fight and re-attaches it, so the return loads,
## instantiates and readies nothing. Measured in a child process (SceneSwapProbe --encounter --return: a real swap
## would replace the runner's scene) on an injected clock, so frame counts, not this machine's load, decide it.

const PROBE := "res://game/core/debug/scene_swap_probe.tscn"
const PROBE_TAG := "SCENE_SWAP_PROBE "
const ZONE := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn"
const ENCOUNTER := "ch03_causeway_shore"
## PC pass 7 row 74: a fight that returns to another zone (the Drownbell to Haluna) finds it built while it ran.
const CROSS := "res://game/levels/ch02/haluna/haluna.tscn"
const FRAME_USEC := 16667


func test_the_way_back_from_a_random_fight_is_the_resident_field() -> void:
	var stats := _probe(["--encounter=" + ENCOUNTER, "--return=" + ZONE, "--frame-usec=%d" % FRAME_USEC])
	if stats.is_empty():
		return
	assert_true(bool(stats.get("resident", false)), "the field kept through the fight comes back: %s" % stats)
	assert_eq(float(stats.get("instantiate_ms", -1.0)), 0.0, "nothing is instantiated on the way back")
	assert_true(
		float(stats.get("entry_ms", INF)) <= SceneRouter.HIDDEN_FRAME_BUDGET_MS,
		(
			"the return is under the fade at most %.0f ms (%s ms)"
			% [SceneRouter.HIDDEN_FRAME_BUDGET_MS, stats.get("entry_ms")]
		)
	)
	assert_false(bool(stats.get("over_budget", true)), "no hidden frame over 1 s")
	assert_true(bool(stats.get("covered", false)), "the swap is under the fade")


func test_a_cross_zone_return_is_built_while_the_fight_runs() -> void:
	var stats := _probe(
		["--encounter=" + ENCOUNTER, "--return=" + ZONE, "--cross-return=" + CROSS, "--frame-usec=%d" % FRAME_USEC]
	)
	if stats.is_empty():
		return
	assert_eq(str(stats.get("scene_path", "")), CROSS, "the change measured is to the other zone")
	assert_true(bool(stats.get("parked", false)), "the return scene was built while the fight ran: %s" % stats)
	assert_eq(float(stats.get("instantiate_ms", -1.0)), 0.0, "nothing is instantiated on the way back")
	assert_false(bool(stats.get("over_budget", true)), "no hidden frame over 1 s")
	assert_true(bool(stats.get("covered", false)), "the swap is under the fade")


func _probe(user_args: Array[String]) -> Dictionary:
	var output: Array = []
	var args := PackedStringArray(["--headless", "--path", ProjectSettings.globalize_path("res://"), PROBE, "--"])
	args.append_array(PackedStringArray(user_args))
	var code := OS.execute(_godot(), args, output, true)
	for chunk: Variant in output:
		for line in str(chunk).split("\n"):
			if line.begins_with(PROBE_TAG):
				var parsed: Variant = JSON.parse_string(line.trim_prefix(PROBE_TAG))
				if parsed is Dictionary:
					return parsed as Dictionary
	fail("the probe printed no stats (exit %d, %s)" % [code, user_args])
	return {}


static func _godot() -> String:
	return GodotBinary.path()
