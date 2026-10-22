class_name WaveSet
extends Resource
## The authored wave field of one body of water (M1-RND-01): up to GerstnerWaves.MAX_WAVES
## components. GerstnerWaves.from_set() packs it for the shader and for height queries, so the
## material and gameplay always see the same numbers. Docs: docs/kb/tech/water.md.

@export var components: Array[WaveComponent] = []
## Scales every amplitude (a calm-to-swell knob for weather). Steepness is unaffected.
@export_range(0.0, 4.0, 0.01) var amplitude_scale: float = 1.0
