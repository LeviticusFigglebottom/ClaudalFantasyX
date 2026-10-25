extends SceneTree
## Command-line wrapper for the Reefball balance sim; tools/balance/reefball_sim.py runs it:
##   godot --headless --path . -s res://tools/balance/reefball_sim_main.gd -- \
##       --match=tidecup_opening --policies=naive,smart --seeds=1000 [--first-seed=1] [--out=/abs/path.json]
## Prints one line "REEFBALL_RESULT <json>" per policy and, with --out, writes them as a JSON array.
## Exit code 1 on bad arguments. All logic lives in ReefballSim (run_cli, parse_args), which the
## test suite covers; this file only does process I/O.

const PREFIX := "REEFBALL_RESULT "


func _initialize() -> void:
	var args := ReefballSim.parse_args(OS.get_cmdline_user_args())
	var res := ReefballSim.new().run_cli(args)
	if not res["ok"]:
		printerr("reefball_sim_main: %s" % res["error"])
		quit(1)
		return
	for r: Variant in res["results"]:
		print(PREFIX + JSON.stringify(r))
	if args.has("out"):
		var f := FileAccess.open(str(args["out"]), FileAccess.WRITE)
		if f == null:
			printerr("reefball_sim_main: cannot write %s" % args["out"])
			quit(1)
			return
		f.store_string(JSON.stringify(res["results"]))
		f.close()
	quit(0)
