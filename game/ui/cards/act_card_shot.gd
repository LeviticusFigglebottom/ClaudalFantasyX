class_name ActCardShot
extends Control
## Capture driver for the cutscene_act_card shot (M3-C09-05, tests/screenshots/shots.json): Act
## II's card (act1_ch09.md B11, "Act II: The Truth") held in on black.

const ACT := 2

var card: ActCard


func _ready() -> void:
	UiSettings.set_shared(UiSettings.new())
	card = ActCard.new()
	add_child(card)
	card.show_act(ACT)
	card.advance(float(ActCard.load_data()["in_sec"]))
	card.set_process(false)  # stays held for the capture
