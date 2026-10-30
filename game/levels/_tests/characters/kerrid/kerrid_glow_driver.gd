extends Node
## M4-A2P-054 look-dev: lights Kerrid's rope-burns on the stage this node sits under (KerridBurnGlow), after the stage
## has built and dressed the model.

@export var glow: float = 0.0
@export var lift: float = 0.0


func _ready() -> void:
	_apply.call_deferred()


func _apply() -> void:
	KerridBurnGlow.apply(get_parent(), glow, lift)
