---
id: M2-ENV-11
title: Per-encounter battle arenas at final quality (dawn tideline beach, sunset causeway disc)
role: environment
status: doing
owner_session: "env-art"
depends_on: []
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
M2-review blocker from the Lead: every fight uses the battle sandbox's greybox (sand, dais, sea). Build
per-encounter battle arenas at final quality, around the sandbox's slot layout:
- `tideline_dawn`: Haluna's beach at dawn, the first battle (`ch02` dawn, color script and haluna.md §0).
- `causeway_disc_sunset`: the Drownbell arena (haluna.md §2.2: a widened causeway disc 30 m across with a central
  sunk area; `ch03_boss` 18:15, the sun 2° over the western sea), with room and an anchor for the boss and the
  flood rig's water plane (battle_vfx.md "The Drownbell").

## Acceptance criteria
- [ ] The arena contract written in `docs/kb/tech/battle_arenas.md`.
- [ ] `assets/environments/arenas/tideline_dawn/tideline_dawn.tscn` and
      `assets/environments/arenas/causeway_disc_sunset/causeway_disc_sunset.tscn`, each with its own
      WorldEnvironment, Sun and dressing, a flat clear floor under every sandbox slot, and no camera.
- [ ] New geometry is kit modules in `assets_src/environments/kits/haluna/` (every other kit output
      byte-identical, `verify_blender_builds --job haluna_kit`), with PROVENANCE rows.
- [ ] Two shots (one per arena) on an Environment preview scene with the sandbox slot layout, camera framing and
      stand-ins; viewed and approved.
- [ ] Unit test: each arena loads, has WorldEnvironment + Sun, a clear floor over the slots, no camera.
- [ ] Swap-in note for battle-presentation and m2-slice.

## Notes

## Review log
