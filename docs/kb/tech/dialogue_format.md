# `.dlg` Dialogue Format Reference

The syntax and rationale are in [ADR 0004](../decisions/0004-dialogue-format.md). This page grows with the cue vocabulary as Cinematics adds cues.

## Cue vocabulary (initial)
| Cue | Args | Meaning |
|---|---|---|
| `@camera` | `shot_id [blend=sec]` | Cut or blend to an authored shot |
| `@anim` | `actor clip [loop]` | Play a body animation |
| `@mark` | `actor mark_id [walk|run]` | Move an actor to a scene mark |
| `@face` | `actor expression [sec]` | Override the facial expression (otherwise from `[emotion]`) |
| `@fade` | `in|out sec [color]` | Screen fade |
| `@letterbox` | `on|off` | Cinematic bars |
| `@music` | `cue_id [fade=sec]` | Music change |
| `@vfx` | `effect_id at=actor|mark` | Trigger VFX |
| `@wait` | `sec` | Pause the sequence |

## Emotion tags (initial set; expand with the Character face rig)
`neutral, soft_smile, smile, laugh, worried, sad, grief, angry, cold, surprised, afraid, determined, tender, guilty, exhausted`
