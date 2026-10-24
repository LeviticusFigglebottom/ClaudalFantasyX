class_name RoutePreviewDresser
extends HalunaDresser
## Places a route layout's kit pieces on the zone's already-built terrain (M2-ENV-08). Unlike its base,
## it never rebuilds the terrain: it only reads heights from it, so it can sit beside the zone's own
## Dresser in a preview scene that inherits the Haluna world.


func dress() -> void:
	layout = _load_json(layout_path)
	if layout.is_empty():
		push_error("RoutePreviewDresser: cannot read %s" % layout_path)
		return
	for spec: Dictionary in layout.get("pieces", []):
		_place_piece(spec)
	dressed.emit()
