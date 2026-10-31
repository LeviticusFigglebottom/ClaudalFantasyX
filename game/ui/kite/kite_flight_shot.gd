class_name KiteFlightShot
extends Control
## Capture driver for the kite_flight shot (M5-A3P-1711, tests/screenshots/shots.json): the flight card on the black
## of a covering fade, bound for Oruvel in the Low Reaches.


func _ready() -> void:
	var black := ColorRect.new()
	black.set_anchors_preset(Control.PRESET_FULL_RECT)
	black.color = Color(0, 0, 0, 1)
	add_child(black)
	var card := KiteFlightCard.new()
	card.data = KiteFlightCard.load_data()
	card.data["max_sec"] = 3600.0  # the capture runs longer than a flight; it must not go
	card.fade = func() -> float: return 1.0
	add_child(card)
	card.set_place(tr("LOCATION_CH01_ORUVEL"), tr("KITE_REGION_LOW_REACHES"))
