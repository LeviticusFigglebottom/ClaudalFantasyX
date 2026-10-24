class_name FieldHud
extends RefCounted
## The field's HUD pieces, attached by FieldController with one line (FieldHud.attach(self)): the
## objective line and its destination cue (ObjectiveHud, M2-UI-17/19) and the interaction prompt
## (InteractPrompt, M2-UI-20), the area title card (AreaTitleCard, M2-UI-21) and first-time tips
## (TipCard, M2-UI-24). Each brings its own
## CanvasLayer under the controller.


static func attach(c: FieldController) -> void:
	ObjectiveHud.attach(c)
	InteractPrompt.attach(c)
	AreaTitleCard.attach(c)
	TipCard.attach(c)
