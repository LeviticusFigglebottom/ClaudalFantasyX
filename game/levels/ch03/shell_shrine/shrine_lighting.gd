class_name ShrineLighting
extends RefCounted
## The Shell Shrine's VoxelGI states (M2-ENV-10, ADR 0029): the door-up and door-down lighting ship as
## baked VoxelGIData (room.gi_data in game/data/trials/shell_shrine.json, made offline by
## tools/shrine/bake_shrine_gi.tscn). ShellShrineLevel only loads them at entry.


## state -> VoxelGIData for every shipped state whose file exists.
static func load_states(paths: Dictionary) -> Dictionary:
	var out := {}
	for state: String in paths.keys():
		var path := str(paths[state])
		if ResourceLoader.exists(path):
			out[state] = load(path) as VoxelGIData
	return out


## The door's height for a bake: sunk when the door is open, standing (half its height) when shut.
static func door_height(room: Dictionary, open: bool) -> float:
	return float(room["door_sink"]) if open else float((room["door"] as Array)[1]) * 0.5


## The room's GI settings on freshly baked data: interior (the oculi's sun and its bounce only, no
## sky through the vault), two bounces, and the room's energy and propagation.
static func tune(data: VoxelGIData, room: Dictionary) -> VoxelGIData:
	if data != null:
		data.interior = true
		data.use_two_bounces = true
		data.energy = float(room.get("gi_energy", 1.0))
		data.propagation = float(room.get("gi_propagation", 0.5))
	return data
