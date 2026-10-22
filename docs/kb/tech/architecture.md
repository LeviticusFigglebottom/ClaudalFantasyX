# Runtime Architecture (M0)

## Autoloads (`project.godot`)
| Name | Script | Purpose |
|---|---|---|
| `EventBus` | `game/core/event_bus.gd` | Decoupled signals: battle start/end, flag changes, dialogue events, scene change, save/load. |
| `Game` | `game/core/game.gd` | Owns the live `GameStateData` and the `FlagRegistry`. `get_flag` / `set_flag` reject undeclared flags at runtime, and the validator rejects them in CI. |
| `SaveSystem` | `game/core/save_system.gd` | Versioned JSON saves (`user://saves/slot_NN.json`) with chained migrations; slot 0 = chapter autosave. |
| `SceneRouter` | `game/core/scene_router.gd` | Threaded scene loads behind a fade; `prewarm_requested` hook for the shader-cache warmup (M1-RND-06). |

## State
- `GameStateData` (Resource): flags, party and reserve ids, inventory, currency, play time, location, chapter. `to_dict()` / `from_dict()` are the only serialization path.
- Bump `SaveSystem.SAVE_VERSION` on any schema change, and add a `_migrations[old_version]` step plus a test.

## Planned (M1+)
Built in M1: dialogue runner (`game/narrative/`, DialogueRunner) and text box (`game/ui/dialogue/`, DialogueBox); see tech/dialogue_format.md.

Still planned: field controller with camera rails (`game/world/`), dialogue runner (`game/narrative/`), battle scene glue (`game/battle/scene/`), Lattice (`game/progression/`), UI theme (`game/ui/`), and debug overlays F1–F12 (SPEC §5.4, task M1-ARC-02).
