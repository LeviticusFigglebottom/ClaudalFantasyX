extends TestCase
## M2-RND-11 (review-sweep-R): Ultra draws its body through the compute effect at full resolution, so the sea
## reflects the body's own pixels as High's does, and the warm compute pipelines are released with the tree.


func test_only_ultra_runs_the_compute_body_by_its_tier_flag() -> void:
	var state := UndertowState.new()
	assert_true(bool(state.quality_plan("ultra")["compute_body"]), "Ultra: a texture the sea can reflect")
	assert_eq(float(state.quality_plan("ultra")["body_scale"]), 0.5, "the 4 ms budget (M2-RND-12)")
	for tier in ["low", "medium", "high"]:
		assert_false(bool(state.quality_plan(tier)["compute_body"]), "%s: by its body_scale alone" % tier)


func test_releasing_the_warm_pipelines_is_safe_and_empties_them() -> void:
	var path := UndertowBodyEffect.compute_path_for("res://game/shaders/undertow/undertow_body.gdshader")
	assert_ne(path, "", "the body has a compute twin")
	# Headless has no RenderingDevice: warming fails cleanly, and releasing an empty set is a no-op.
	if RenderingServer.get_rendering_device() == null:
		assert_false(UndertowBodyEffect.warm_pipeline(path))
	UndertowBodyEffect.release_warm()
	assert_false(UndertowBodyEffect.is_warm(path), "nothing held after the release")
	UndertowBodyEffect.release_warm()
	assert_false(UndertowBodyEffect.is_warm(path), "a second release is harmless")
