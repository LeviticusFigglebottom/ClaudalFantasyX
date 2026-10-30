class_name HalunaKitSheet
extends Node3D
## A review sheet of every Haluna kit piece (M1-ENV-01): the pieces of kit_manifest.json laid out in
## rows on a flat ground, lit by the ch02_noon sun, with the same materials and LODs the zone uses.
## Not a registered screenshot (the baselines folder is near its budget); the review captures it once.

@export var dresser: HalunaDresser
@export_file("*.json") var manifest_path: String = "res://assets/environments/kits/haluna/kit_manifest.json"
@export var spacing_m: Vector2 = Vector2(16.0, 18.0)
@export var per_row: int = 6
## Pieces placed on their own (huge or tiny ones are skipped or scaled for the sheet).
@export var skip: PackedStringArray = PackedStringArray(["shell_shrine_massing", "dock_haluna", "banyan_hero"])
@export var sheet_scale: Dictionary = {"lintel_gull_a": 4.0, "lintel_gull_b": 4.0, "lintel_gull_c": 4.0}


func _ready() -> void:
	var manifest := HalunaDresser._load_json(manifest_path)
	var pieces: Dictionary = manifest.get("pieces", {})
	var names: Array = pieces.keys()
	names.sort()
	var i := 0
	for piece: String in names:
		if skip.has(piece):
			continue
		var node := dresser.instance_piece(piece)
		if node == null:
			continue
		var col := i % per_row
		var row := i / per_row
		var s := float(sheet_scale.get(piece, 1.0))
		node.transform = Transform3D(
			Basis.IDENTITY.scaled(Vector3.ONE * s), Vector3(col * spacing_m.x, 0.0, -row * spacing_m.y)
		)
		dresser.add_child(node)
		i += 1
