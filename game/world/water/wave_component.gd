class_name WaveComponent
extends Resource
## One Gerstner wave of a WaveSet (M1-RND-01). Authored in a .tres; docs/kb/tech/water.md.
## direction_deg is the azimuth the wave travels toward, clockwise from world north (-Z), the same
## convention as the color script's sun azimuth: 90 = east (+X), 180 = south (+Z).

@export_range(0.0, 360.0, 0.1, "degrees") var direction_deg: float = 0.0
@export_range(0.1, 500.0, 0.01, "suffix:m") var wavelength_m: float = 10.0
@export_range(0.0, 5.0, 0.001, "suffix:m") var amplitude_m: float = 0.1
## 0 = sine wave, 1 = the sharpest crest the set allows without looping (shared across the set).
@export_range(0.0, 1.0, 0.01) var steepness: float = 0.5
@export_range(0.0, 6.2832, 0.0001, "radians") var phase_rad: float = 0.0
