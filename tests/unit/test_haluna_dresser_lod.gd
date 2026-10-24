extends TestCase
## M1-ENV-10: HalunaDresser.instance_piece chains `<piece>` as the visibility child of `<piece>-lod1`
## (LodChain), so a kit piece draws exactly one LOD at every distance: no hole for a still camera
## within the switch margin, no double draw while the camera moves.

const LodRangeModel := preload("res://tests/unit/lod_range_model.gd")
## The mood layout, then its home on the Haluna zone branch (M2-ENV-01 moves it): the first that exists.
const LAYOUTS: Array[String] = [
	"res://game/levels/_tests/haluna_mood/haluna_layout.json",
	"res://game/levels/ch02/haluna/haluna_layout.json",
]
const PIECES: Array[String] = ["dock_haluna", "tidewall_straight", "lintel_gull_a"]
## A per-placement switch distance (the layout's `lod1_from_m` on a piece spec), m.
const OVERRIDE_FROM_M := 40.0
## How far past the switch the sweep runs (the far end is the layout's lod_end_m, well beyond), m.
const SWEEP_PAST_M := 60.0


func _dresser() -> HalunaDresser:
	var dresser := HalunaDresser.new()
	for path in LAYOUTS:
		if FileAccess.file_exists(path):
			dresser.layout = HalunaDresser._load_json(path)
			break
	assert_false(dresser.layout.is_empty(), "the layout loads")
	return dresser


func _chain(node: Node3D, piece: String) -> Array[MeshInstance3D]:
	var chain: Array[MeshInstance3D] = []
	chain.append(node.find_child(piece, true, false) as MeshInstance3D)
	chain.append(node.find_child(piece + "-lod1", true, false) as MeshInstance3D)
	return chain


func test_each_piece_lod0_is_the_visibility_child_of_lod1() -> void:
	var dresser := _dresser()
	var node := dresser.instance_piece(PIECES[0])
	assert_true(node != null, "the kit piece instances")
	if node != null:
		var chain := _chain(node, PIECES[0])
		assert_true(chain[0].get_node_or_null(chain[0].visibility_parent) == chain[1], "LOD0 -> LOD1")
		assert_eq(chain[1].visibility_parent, NodePath(), "LOD1 ends the chain")
		var from := float(dresser.layout["lod1_from_m"])
		var margin := float(dresser.layout["lod_margin_m"])
		assert_eq(chain[1].visibility_range_begin, from, "LOD1 begins at lod1_from_m")
		assert_eq(chain[1].visibility_range_begin_margin, margin, "the switch's hysteresis is LOD1's begin margin")
		assert_eq(chain[1].visibility_range_end, float(dresser.layout["lod_end_m"]))
		assert_eq(chain[0].visibility_range_begin_margin, 0.0, "LOD0 keeps no margin of its own")
		assert_eq(chain[0].visibility_range_end_margin, 0.0, "LOD0 keeps no margin of its own")
		for mi in chain:
			assert_eq(mi.visibility_range_fade_mode, GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED, "hard switch")
		node.free()
	dresser.free()


## The layout's default switch and a per-placement override, still camera, moving in and moving out.
func test_a_distance_sweep_draws_exactly_one_lod() -> void:
	var dresser := _dresser()
	for piece: String in PIECES:
		for from: float in [-1.0, OVERRIDE_FROM_M]:
			var node := dresser.instance_piece(piece, {}, from)
			assert_true(node != null, "%s instances" % piece)
			if node == null:
				continue
			var switch_m := from if from > 0.0 else float(dresser.layout["lod1_from_m"])
			var chain := _chain(node, piece)
			var bad := LodRangeModel.hard_sweep_failures(chain, LodRangeModel.distances(switch_m + SWEEP_PAST_M))
			assert_eq(bad.size(), 0, "%s switching at %.0f m: %s" % [piece, switch_m, ", ".join(bad.slice(0, 6))])
			node.free()
	dresser.free()


## The far end of the chain: past lod_end_m (plus its margin) nothing draws.
func test_nothing_draws_past_the_last_lod() -> void:
	var dresser := _dresser()
	var node := dresser.instance_piece(PIECES[0])
	if node != null:
		var past := float(dresser.layout["lod_end_m"]) + float(dresser.layout["lod_margin_m"]) + 1.0
		assert_eq(LodRangeModel.draws(_chain(node, PIECES[0]), past, {}), [0, 0] as Array[int])
		node.free()
	dresser.free()
