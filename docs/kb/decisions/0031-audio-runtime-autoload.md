# 0031 — An `Audio` autoload that routes other roles' sounds by listening

- **Status:** accepted
- **Date:** 2026-10-24
- **Roles affected:** audio, architect (project.godot autoloads), cinematics (the cutscene sequencer), ui (the
  dialogue box, menus), combat (battle scenes), rendering (BattleVfx)
- **Author role:** audio

## Context
SPEC §9 asks for adaptive music, ambience, SFX and a mix. Until now nothing in play routed sound: there was no bus
layout, no zone or battle music, menus were silent, and the cutscene sequencer played its music and `@sfx` on
Master. The slice (SPEC §10 M2) needs all of it, and the scenes that need sound belong to other roles
(docs/kb/ownership.md: m2-slice owns Haluna and the cutscenes, Combat the battle controller, UI the menus).
`battle_controller.gd` is also at about 994 of gdlint's 1000 lines.

## Options
1. Each owner adds audio calls to its own scripts (request tasks to five roles, and lines in a full controller).
2. Audio nodes instanced into each scene (scene edits in other roles' scenes).
3. One autoload that **listens**: it watches `SceneTree.node_added` for known node types and connects to their
   public signals, routes their players to buses, and keeps its own listeners as its own children.

## Decision
Option 3. `Audio` (`game/audio/audio_director.gd`) is an autoload after SceneRouter. It builds the buses from
`game/data/audio/mix.json`, switches zone music and ambience on `SceneRouter.scene_swapping` from
`game/data/audio/music.json`, and plays sfx.json rows. When a `BattleVfx` enters a `BattleController` it builds a
`BattleAudio` listener (battle music, phase stems, battle SFX from `battle_sfx.json`); a `ShellShrineLevel` gets a
`ShrineAudio` listener; the cutscene sequencer's music and `@sfx` players go to the Music and SFX buses, and the
zone bed holds while the sequencer's music plays; a `DialogueBox`'s blip goes to Voice and an open box ducks the
music. The listeners never write game or combat state, and no other role's file is edited. The engine stays
headless (CLAUDE.md §3): BattleAudio only connects to the engine's signals.

Where a direct call would be cleaner (the sequencer asking `Audio.play_music` instead of owning a player), Audio
files a request task; the listener stays as the fallback.

## Consequences
- Every role gets sound without touching its scripts; a new hook is one `elif` in `_on_node_added` and one listener.
- The hooks depend on class names and public signals (`BattleVfx.effect_played`, `ShellShrineTrial`'s signals,
  `CutsceneSequencer.music`). Renaming one silently drops its sounds, so `tests/unit/test_audio_*.gd` exercise each
  hook on the real classes.
- Time passes through `advance(delta)`, so fades and ducks are unit-testable; the full suite runs with the
  autoload live (1441 tests, 0 failures at its introduction).
- Bus volumes are the player's settings plus ducks; assets ship at their loudness targets, so the faders stay at 0
  (mix.md §4).
