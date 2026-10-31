extends TestCase
## The readability pass (10-30, pillar 4): a damage float that would start inside a shown HUD panel (battle_hud.json
## damage.avoid) moves out of it by the shortest way on screen; one outside every panel stays put.

var hud: Control
var panel: Control


func before_each() -> void:
	hud = Control.new()
	hud.size = Vector2(1920, 1080)
	panel = Control.new()
	panel.name = "BossStatus"
	panel.position = Vector2(48, 156)
	panel.size = Vector2(480, 80)
	hud.add_child(panel)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(hud)


func after_each() -> void:
	hud.get_parent().remove_child(hud)
	hud.free()


func test_a_float_inside_a_panel_moves_out_by_the_shortest_way() -> void:
	var m := {"avoid": [{"node": "BossStatus"}], "avoid_margin_px": 28}
	var p := HudLayout.clear_of_panels(Vector2(500, 200), hud, m, Vector2(1920, 1080))
	var r := panel.get_global_rect().grow(28)
	assert_false(r.has_point(p) and not is_equal_approx(p.x, r.end.x), "out of the panel (%s)" % p)
	assert_between(p.x, 555.9, 556.1, "out its near (right) side")
	assert_eq(p.y, 200.0)


func test_a_float_clear_of_every_panel_stays_put() -> void:
	var m := {"avoid": [{"node": "BossStatus"}], "avoid_margin_px": 28}
	assert_eq(HudLayout.clear_of_panels(Vector2(900, 500), hud, m, Vector2(1920, 1080)), Vector2(900, 500))


func test_a_hidden_panel_is_no_obstacle() -> void:
	panel.visible = false
	var m := {"avoid": [{"node": "BossStatus"}], "avoid_margin_px": 28}
	assert_eq(HudLayout.clear_of_panels(Vector2(200, 200), hud, m, Vector2(1920, 1080)), Vector2(200, 200))
