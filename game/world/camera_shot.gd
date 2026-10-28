class_name CameraShot
extends Resource
## One authored field camera shot (SPEC §6.6, M1-ARC-01; docs/kb/tech/field_camera.md).
##
## Modes:
##   FIXED       camera at `position`, looking at `look_at` (a composed, locked frame).
##   PAN_FOLLOW  camera at `position`; the aim moves from `look_at` toward the player by
##               `follow_weight`, limited to `max_pan_deg` away from the authored aim.
##   DOLLY       camera rides the Path3D `dolly_path` by the player's projected progress along
##               `track_path` (or along the dolly itself when unset), and aims at the player.
##   ORBIT       only honoured when the director's hub_orbit_enabled is set (hub zones); otherwise
##               the director treats it as PAN_FOLLOW and warns.
##   FOLLOW      camera rides behind the player at a fixed offset (ADR 0194, the big15 playtest's party
##               start): `follow_distance` back along the authored heading (`position` -> `look_at`, flat)
##               and `follow_height` up, smoothed by follow_smoothing, aiming at the player. The party stays
##               the same size on screen and the camera never swings.
## Positions are in the director's rail space (the level root by default). Paths resolve relative
## to that root too. Every mode that aims at the player aims at `aim_node` instead when it is set
## (cutscene two-shots and reaction shots, M1-ARC-05). FOV is vertical (Camera3D.keep_aspect =
## KEEP_HEIGHT); see the lens table in docs/kb/art/environments/haluna.md §5.

enum Mode { FIXED, PAN_FOLLOW, DOLLY, ORBIT, FOLLOW }

const USE_DEFAULT := -1.0

@export var id: StringName = &""
@export var mode: Mode = Mode.FIXED

@export_group("Framing")
@export var position: Vector3 = Vector3.ZERO
@export var look_at: Vector3 = Vector3.FORWARD
## Added to the player's position when a mode aims at the player (head height, look-ahead).
@export var target_offset: Vector3 = Vector3.ZERO
## Frame this node (an actor or a Marker3D mark) instead of the player: PAN_FOLLOW pans toward it,
## DOLLY tracks and aims at it, ORBIT circles it, and FIXED looks straight at it instead of
## `look_at`. Resolved from the director's rail root (absolute paths work too); empty = player.
@export var aim_node: NodePath
## Added to the aim node's global position (eye height, a two-shot's midpoint). World space.
@export var aim_offset: Vector3 = Vector3.ZERO
## Vertical FOV in degrees; USE_DEFAULT = field_camera.json default_fov_deg.
@export var fov_deg: float = USE_DEFAULT
## Roll in degrees around the view axis (dutch angle). Zero for almost every shot.
@export var roll_deg: float = 0.0

@export_group("Pan follow")
## 0 = locked on look_at, 1 = aim fully at the player.
@export_range(0.0, 1.0) var follow_weight: float = 0.6
## Largest angle the aim may swing away from the authored look_at.
@export var max_pan_deg: float = 25.0
## Exponential smoothing rate of the aim (per second); USE_DEFAULT = data default.
@export var follow_smoothing: float = USE_DEFAULT

@export_group("Dolly")
@export var dolly_path: NodePath
## The player's walk line; their projected progress along it drives the dolly. Empty = dolly_path.
@export var track_path: NodePath
## Maps track progress [0, 1] to dolly progress: dolly = offset + progress * scale, clamped.
@export var progress_scale: float = 1.0
@export var progress_offset: float = 0.0

@export_group("Follow")
## Metres back from the player along the shot's heading, and up.
@export var follow_distance: float = USE_DEFAULT
@export var follow_height: float = USE_DEFAULT

@export_group("Orbit (hub zones only)")
@export var orbit_distance: float = USE_DEFAULT
@export var orbit_height: float = USE_DEFAULT

@export_group("Depth of field")
@export var dof_far_enabled: bool = false
@export var dof_far_distance: float = 10.0
@export var dof_far_transition: float = 5.0
@export var dof_near_enabled: bool = false
@export var dof_near_distance: float = 2.0
@export var dof_near_transition: float = 1.0
@export var dof_blur_amount: float = 0.1

@export_group("Blend in")
## A hard cut: the camera jumps to this shot with no blend.
@export var hard_cut: bool = false
## Seconds; USE_DEFAULT = field_camera.json default_blend_sec.
@export var blend_sec: float = USE_DEFAULT
## Named ease from field_camera.json "eases"; empty = default_blend_ease.
@export var blend_ease: StringName = &""
## Optional custom curve (x = time 0..1, y = weight 0..1). Wins over blend_ease.
@export var blend_curve: Curve


func dof_dict() -> Dictionary:
	return {
		"far_enabled": dof_far_enabled,
		"far_distance": dof_far_distance,
		"far_transition": dof_far_transition,
		"near_enabled": dof_near_enabled,
		"near_distance": dof_near_distance,
		"near_transition": dof_near_transition,
		"amount": dof_blur_amount,
	}


## True when the camera moves with the player (DOLLY, ORBIT, FOLLOW): there is no fixed frame to judge.
func moves_with_player() -> bool:
	return mode in [Mode.DOLLY, Mode.ORBIT, Mode.FOLLOW]
